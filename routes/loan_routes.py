from flask import Blueprint, render_template, redirect, url_for, request, flash
from app import db
from models import Loan, Book, Member
from utils.notifications import send_notification
from datetime import datetime, timedelta
from sqlalchemy import or_

loan_bp = Blueprint('loans', __name__, url_prefix='/loans')

@loan_bp.route('/')
def index():
    """Display all loans with optional filters."""
    status = request.args.get('status', 'all')
    search_term = request.args.get('search', '')
    
    # Query loans based on filters
    query = Loan.query
    
    if status == 'active':
        query = query.filter_by(returned=False)
    elif status == 'returned':
        query = query.filter_by(returned=True)
    elif status == 'overdue':
        now = datetime.utcnow()
        query = query.filter(Loan.returned==False, Loan.due_date < now)
    
    # Search by book title or member name
    if search_term:
        query = query.join(Book).join(Member).filter(
            or_(
                Book.title.ilike(f'%{search_term}%'),
                Member.first_name.ilike(f'%{search_term}%'),
                Member.last_name.ilike(f'%{search_term}%')
            )
        )
    
    loans = query.order_by(Loan.loan_date.desc()).all()
    
    return render_template('loans/index.html', 
                          loans=loans, 
                          status=status,
                          search_term=search_term)

@loan_bp.route('/create', methods=['GET', 'POST'])
def create():
    """Create a new loan."""
    if request.method == 'POST':
        # Extract form data
        book_id = request.form.get('book_id')
        member_id = request.form.get('member_id')
        loan_days = request.form.get('loan_days', '14')
        
        # Validate required fields
        if not book_id or not member_id:
            flash('Book and member are required!', 'danger')
            books = Book.query.filter_by(available=True).order_by(Book.title).all()
            members = Member.query.filter_by(active=True).order_by(Member.last_name).all()
            return render_template('loans/create.html', books=books, members=members)
        
        # Validate loan days
        try:
            loan_days = int(loan_days)
            if loan_days < 1:
                raise ValueError("Loan days must be positive")
        except ValueError:
            flash('Loan period must be a positive number!', 'danger')
            books = Book.query.filter_by(available=True).order_by(Book.title).all()
            members = Member.query.filter_by(active=True).order_by(Member.last_name).all()
            return render_template('loans/create.html', books=books, members=members)
        
        # Check if book exists and is available
        book = Book.query.get(book_id)
        if not book:
            flash('Book not found!', 'danger')
            return redirect(url_for('loans.create'))
        
        if not book.available:
            flash('This book is not available for loan!', 'danger')
            return redirect(url_for('loans.create'))
        
        # Check if member exists and is active
        member = Member.query.get(member_id)
        if not member:
            flash('Member not found!', 'danger')
            return redirect(url_for('loans.create'))
        
        if not member.active:
            flash('This member is not active!', 'danger')
            return redirect(url_for('loans.create'))
        
        # Create new loan
        loan_date = datetime.utcnow()
        due_date = loan_date + timedelta(days=loan_days)
        
        new_loan = Loan(
            book_id=book_id,
            member_id=member_id,
            loan_date=loan_date,
            due_date=due_date,
            returned=False
        )
        
        # Update book availability
        book.available = False
        
        db.session.add(new_loan)
        db.session.commit()
        
        # Send notification to member about the loan
        send_notification(
            member.email,
            'Book Loan Confirmation',
            f'Dear {member.full_name()},\n\n'
            f'You have borrowed "{book.title}" by {book.author}.\n'
            f'Due date: {due_date.strftime("%Y-%m-%d")}.\n\n'
            f'Thank you for using our library services.'
        )
        
        flash('Loan created successfully!', 'success')
        return redirect(url_for('loans.show', id=new_loan.id))
    
    # GET request - display form
    books = Book.query.filter_by(available=True).order_by(Book.title).all()
    members = Member.query.filter_by(active=True).order_by(Member.last_name).all()
    
    return render_template('loans/create.html', books=books, members=members)

@loan_bp.route('/<int:id>')
def show(id):
    """Show details of a specific loan."""
    loan = Loan.query.get_or_404(id)
    return render_template('loans/show.html', loan=loan)

@loan_bp.route('/<int:id>/return', methods=['POST'])
def return_book(id):
    """Process a book return."""
    loan = Loan.query.get_or_404(id)
    
    if loan.returned:
        flash('This book has already been returned!', 'warning')
        return redirect(url_for('loans.show', id=loan.id))
    
    # Process the return
    loan.returned = True
    loan.return_date = datetime.utcnow()
    
    # Update book availability
    book = Book.query.get(loan.book_id)
    if book:
        book.available = True
    
    db.session.commit()
    
    # Calculate fine if overdue
    fine = loan.calculate_fine()
    if fine > 0:
        # Send notification about the fine
        member = Member.query.get(loan.member_id)
        send_notification(
            member.email,
            'Overdue Book Return - Fine Notice',
            f'Dear {member.full_name()},\n\n'
            f'You have returned "{book.title}" by {book.author} {loan.days_overdue()} days late.\n'
            f'A fine of ${fine:.2f} has been applied to your account.\n\n'
            f'Thank you for using our library services.'
        )
        flash(f'Book returned successfully! A fine of ${fine:.2f} has been applied for {loan.days_overdue()} days overdue.', 'warning')
    else:
        flash('Book returned successfully!', 'success')
    
    return redirect(url_for('loans.show', id=loan.id))

@loan_bp.route('/overdue-check')
def overdue_check():
    """Check for overdue loans and send notifications."""
    now = datetime.utcnow()
    overdue_loans = Loan.query.filter(
        Loan.returned == False,
        Loan.due_date < now
    ).all()
    
    notification_count = 0
    
    for loan in overdue_loans:
        book = Book.query.get(loan.book_id)
        member = Member.query.get(loan.member_id)
        
        days_overdue = loan.days_overdue()
        fine = loan.calculate_fine()
        
        if days_overdue > 0:
            send_notification(
                member.email,
                'Overdue Book Notice',
                f'Dear {member.full_name()},\n\n'
                f'The book "{book.title}" by {book.author} is overdue by {days_overdue} days.\n'
                f'Current fine: ${fine:.2f}\n\n'
                f'Please return the book as soon as possible to avoid additional fines.'
            )
            notification_count += 1
    
    flash(f'Sent {notification_count} overdue notifications.', 'info')
    return redirect(url_for('loans.index'))

@loan_bp.route('/upcoming-due')
def upcoming_due():
    """Check for loans due soon and send reminders."""
    now = datetime.utcnow()
    soon = now + timedelta(days=3)  # Books due in the next 3 days
    
    upcoming_loans = Loan.query.filter(
        Loan.returned == False,
        Loan.due_date > now,
        Loan.due_date <= soon
    ).all()
    
    notification_count = 0
    
    for loan in upcoming_loans:
        book = Book.query.get(loan.book_id)
        member = Member.query.get(loan.member_id)
        
        days_remaining = (loan.due_date - now).days
        
        send_notification(
            member.email,
            'Book Due Date Reminder',
            f'Dear {member.full_name()},\n\n'
            f'This is a reminder that the book "{book.title}" by {book.author} is due in {days_remaining} days.\n'
            f'Due date: {loan.due_date.strftime("%Y-%m-%d")}\n\n'
            f'Please return the book on time to avoid fines.'
        )
        notification_count += 1
    
    flash(f'Sent {notification_count} due date reminders.', 'info')
    return redirect(url_for('loans.index'))
