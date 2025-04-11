from flask import Blueprint, render_template, redirect, url_for, request, flash
from app import db
from models import Member, Loan
from sqlalchemy import or_

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
