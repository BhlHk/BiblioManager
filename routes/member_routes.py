from flask import Blueprint, render_template, redirect, url_for, request, flash
from app import db
from models import Member, Loan, Book
from sqlalchemy import or_, func, desc
from datetime import datetime, timedelta

member_bp = Blueprint('members', __name__, url_prefix='/members')

@member_bp.route('/')
def index():
    """Display all members with optional search functionality."""
    search_term = request.args.get('search', '')
    
    # Query members based on search parameters
    query = Member.query
    
    if search_term:
        query = query.filter(
            or_(
                Member.first_name.ilike(f'%{search_term}%'),
                Member.last_name.ilike(f'%{search_term}%'),
                Member.email.ilike(f'%{search_term}%')
            )
        )
    
    members = query.order_by(Member.last_name, Member.first_name).all()
    
    return render_template('members/index.html', 
                          members=members, 
                          search_term=search_term)

@member_bp.route('/create', methods=['GET', 'POST'])
def create():
    """Create a new member."""
    if request.method == 'POST':
        # Extract form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        # Validate required fields
        if not first_name or not last_name or not email:
            flash('First name, last name, and email are required!', 'danger')
            return render_template('members/create.html')
        
        # Check if email already exists
        if Member.query.filter_by(email=email).first():
            flash('A member with this email already exists!', 'danger')
            return render_template('members/create.html')
        
        # Create new member
        new_member = Member(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            address=address,
            active=True
        )
        
        db.session.add(new_member)
        db.session.commit()
        
        flash('Member added successfully!', 'success')
        return redirect(url_for('members.show', id=new_member.id))
    
    return render_template('members/create.html')

@member_bp.route('/<int:id>')
def show(id):
    """Show details of a specific member."""
    member = Member.query.get_or_404(id)
    
    # Get loan history for this member
    loans = Loan.query.filter_by(member_id=member.id).order_by(Loan.loan_date.desc()).all()
    
    # Count active loans and overdue loans
    active_loans = sum(1 for loan in loans if not loan.returned)
    overdue_loans = sum(1 for loan in loans if not loan.returned and loan.is_overdue())
    
    return render_template('members/show.html', 
                          member=member, 
                          loans=loans,
                          active_loans=active_loans,
                          overdue_loans=overdue_loans)

@member_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    """Edit an existing member."""
    member = Member.query.get_or_404(id)
    
    if request.method == 'POST':
        # Extract form data
        member.first_name = request.form.get('first_name')
        member.last_name = request.form.get('last_name')
        member.email = request.form.get('email')
        member.phone = request.form.get('phone')
        member.address = request.form.get('address')
        member.active = 'active' in request.form
        
        # Validate required fields
        if not member.first_name or not member.last_name or not member.email:
            flash('First name, last name, and email are required!', 'danger')
            return render_template('members/edit.html', member=member)
        
        # Check if email already exists and belongs to another member
        existing_member = Member.query.filter_by(email=member.email).first()
        if existing_member and existing_member.id != member.id:
            flash('A member with this email already exists!', 'danger')
            return render_template('members/edit.html', member=member)
        
        db.session.commit()
        flash('Member updated successfully!', 'success')
        return redirect(url_for('members.show', id=member.id))
    
    return render_template('members/edit.html', member=member)

@member_bp.route('/dashboard')
def dashboard():
    """Display a dashboard with member statistics."""
    # Get basic member stats
    total_members = Member.query.count()
    active_members = Member.query.filter_by(active=True).count()
    
    # Members with most active loans
    top_borrowers = db.session.query(
        Member, func.count(Loan.id).label('loan_count')
    ).join(Loan).filter(
        Loan.returned == False
    ).group_by(
        Member
    ).order_by(
        desc('loan_count')
    ).limit(5).all()
    
    # Members with overdue books
    members_with_overdue = db.session.query(
        Member, func.count(Loan.id).label('overdue_count')
    ).join(Loan).filter(
        Loan.returned == False, 
        Loan.due_date < datetime.utcnow()
    ).group_by(
        Member
    ).order_by(
        desc('overdue_count')
    ).limit(5).all()
    
    # Recent registrations
    recent_members = Member.query.order_by(Member.registration_date.desc()).limit(10).all()
    
    # Popular book categories among members (based on loans)
    popular_categories = db.session.query(
        Book.category, func.count(Loan.id).label('loan_count')
    ).join(Loan, Loan.book_id == Book.id).group_by(
        Book.category
    ).filter(
        Book.category.isnot(None)
    ).order_by(
        desc('loan_count')
    ).limit(5).all()
    
    # Member activity over time (last 6 months)
    today = datetime.utcnow()
    six_months_ago = today - timedelta(days=180)
    monthly_registrations = db.session.query(
        func.date_trunc('month', Member.registration_date).label('month'),
        func.count(Member.id).label('count')
    ).filter(
        Member.registration_date >= six_months_ago
    ).group_by(
        'month'
    ).order_by(
        'month'
    ).all()
    
    # Format dates for chart
    months = []
    registration_counts = []
    for month, count in monthly_registrations:
        if month:
            months.append(month.strftime('%b %Y'))
            registration_counts.append(count)
    
    return render_template(
        'members/dashboard.html',
        total_members=total_members,
        active_members=active_members,
        inactive_members=total_members - active_members,
        top_borrowers=top_borrowers,
        members_with_overdue=members_with_overdue,
        recent_members=recent_members,
        popular_categories=popular_categories,
        months=months,
        registration_counts=registration_counts
    )

@member_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    """Delete a member."""
    member = Member.query.get_or_404(id)
    
    # Check if the member has active loans
    if any(not loan.returned for loan in member.loans):
        flash('Cannot delete a member who has active loans!', 'danger')
        return redirect(url_for('members.show', id=member.id))
    
    db.session.delete(member)
    db.session.commit()
    
    flash('Member deleted successfully!', 'success')
    return redirect(url_for('members.index'))
