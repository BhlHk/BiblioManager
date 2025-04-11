from flask import Blueprint, jsonify, request
from app import db
from models import Book, Member, Loan
from datetime import datetime, timedelta
from sqlalchemy import or_

api_bp = Blueprint('api', __name__)

# Book API endpoints
@api_bp.route('/books', methods=['GET'])
def get_books():
    """Get all books with optional search parameters."""
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    available_only = request.args.get('available', '').lower() == 'true'
    
    query = Book.query
    
    if search:
        query = query.filter(
            or_(
                Book.title.ilike(f'%{search}%'),
                Book.author.ilike(f'%{search}%'),
                Book.isbn.ilike(f'%{search}%')
            )
        )
    
    if category:
        query = query.filter(Book.category == category)
    
    if available_only:
        query = query.filter(Book.available == True)
    
    books = query.all()
    return jsonify({
        'success': True,
        'count': len(books),
        'books': [book.to_dict() for book in books]
    })

@api_bp.route('/books/<int:id>', methods=['GET'])
def get_book(id):
    """Get a specific book by ID."""
    book = Book.query.get_or_404(id)
    return jsonify({
        'success': True,
        'book': book.to_dict()
    })

@api_bp.route('/books', methods=['POST'])
def create_book():
    """Create a new book."""
    data = request.get_json()
    
    required_fields = ['title', 'author']
    for field in required_fields:
        if field not in data:
            return jsonify({
                'success': False,
                'error': f'Missing required field: {field}'
            }), 400
    
    # Check if ISBN exists if provided
    if 'isbn' in data and data['isbn']:
        existing_book = Book.query.filter_by(isbn=data['isbn']).first()
        if existing_book:
            return jsonify({
                'success': False,
                'error': 'A book with this ISBN already exists'
            }), 400
    
    # Create new book
    new_book = Book(
        title=data.get('title'),
        author=data.get('author'),
        isbn=data.get('isbn'),
        category=data.get('category'),
        publication_year=data.get('publication_year'),
        description=data.get('description'),
        available=True
    )
    
    db.session.add(new_book)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Book created successfully',
        'book': new_book.to_dict()
    }), 201

@api_bp.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    """Update an existing book."""
    book = Book.query.get_or_404(id)
    data = request.get_json()
    
    # Update fields if provided
    if 'title' in data:
        book.title = data['title']
    if 'author' in data:
        book.author = data['author']
    if 'isbn' in data:
        # Check if ISBN exists and belongs to another book
        if data['isbn']:
            existing_book = Book.query.filter_by(isbn=data['isbn']).first()
            if existing_book and existing_book.id != book.id:
                return jsonify({
                    'success': False,
                    'error': 'A book with this ISBN already exists'
                }), 400
        book.isbn = data['isbn']
    if 'category' in data:
        book.category = data['category']
    if 'publication_year' in data:
        book.publication_year = data['publication_year']
    if 'description' in data:
        book.description = data['description']
    if 'available' in data:
        book.available = data['available']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Book updated successfully',
        'book': book.to_dict()
    })

@api_bp.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    """Delete a book."""
    book = Book.query.get_or_404(id)
    
    # Check if the book has active loans
    active_loans = Loan.query.filter_by(book_id=id, returned=False).count()
    if active_loans > 0:
        return jsonify({
            'success': False,
            'error': 'Cannot delete a book that is currently on loan'
        }), 400
    
    db.session.delete(book)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Book deleted successfully'
    })

# Member API endpoints
@api_bp.route('/members', methods=['GET'])
def get_members():
    """Get all members with optional search parameters."""
    search = request.args.get('search', '')
    active_only = request.args.get('active', '').lower() == 'true'
    
    query = Member.query
    
    if search:
        query = query.filter(
            or_(
                Member.first_name.ilike(f'%{search}%'),
                Member.last_name.ilike(f'%{search}%'),
                Member.email.ilike(f'%{search}%')
            )
        )
    
    if active_only:
        query = query.filter(Member.active == True)
    
    members = query.all()
    return jsonify({
        'success': True,
        'count': len(members),
        'members': [member.to_dict() for member in members]
    })

@api_bp.route('/members/<int:id>', methods=['GET'])
def get_member(id):
    """Get a specific member by ID."""
    member = Member.query.get_or_404(id)
    return jsonify({
        'success': True,
        'member': member.to_dict()
    })

@api_bp.route('/members', methods=['POST'])
def create_member():
    """Create a new member."""
    data = request.get_json()
    
    required_fields = ['first_name', 'last_name', 'email']
    for field in required_fields:
        if field not in data:
            return jsonify({
                'success': False,
                'error': f'Missing required field: {field}'
            }), 400
    
    # Check if email exists
    if Member.query.filter_by(email=data['email']).first():
        return jsonify({
            'success': False,
            'error': 'A member with this email already exists'
        }), 400
    
    # Create new member
    new_member = Member(
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        email=data.get('email'),
        phone=data.get('phone'),
        address=data.get('address'),
        active=True
    )
    
    db.session.add(new_member)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Member created successfully',
        'member': new_member.to_dict()
    }), 201

@api_bp.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    """Update an existing member."""
    member = Member.query.get_or_404(id)
    data = request.get_json()
    
    # Update fields if provided
    if 'first_name' in data:
        member.first_name = data['first_name']
    if 'last_name' in data:
        member.last_name = data['last_name']
    if 'email' in data:
        # Check if email exists and belongs to another member
        if data['email']:
            existing_member = Member.query.filter_by(email=data['email']).first()
            if existing_member and existing_member.id != member.id:
                return jsonify({
                    'success': False,
                    'error': 'A member with this email already exists'
                }), 400
        member.email = data['email']
    if 'phone' in data:
        member.phone = data['phone']
    if 'address' in data:
        member.address = data['address']
    if 'active' in data:
        member.active = data['active']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Member updated successfully',
        'member': member.to_dict()
    })

@api_bp.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    """Delete a member."""
    member = Member.query.get_or_404(id)
    
    # Check if the member has active loans
    active_loans = Loan.query.filter_by(member_id=id, returned=False).count()
    if active_loans > 0:
        return jsonify({
            'success': False,
            'error': 'Cannot delete a member who has active loans'
        }), 400
    
    db.session.delete(member)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Member deleted successfully'
    })

# Loan API endpoints
@api_bp.route('/loans', methods=['GET'])
def get_loans():
    """Get all loans with optional filters."""
    status = request.args.get('status', 'all')
    member_id = request.args.get('member_id')
    book_id = request.args.get('book_id')
    
    query = Loan.query
    
    if status == 'active':
        query = query.filter_by(returned=False)
    elif status == 'returned':
        query = query.filter_by(returned=True)
    elif status == 'overdue':
        now = datetime.utcnow()
        query = query.filter(Loan.returned==False, Loan.due_date < now)
    
    if member_id:
        query = query.filter_by(member_id=member_id)
    
    if book_id:
        query = query.filter_by(book_id=book_id)
    
    loans = query.all()
    return jsonify({
        'success': True,
        'count': len(loans),
        'loans': [loan.to_dict() for loan in loans]
    })

@api_bp.route('/loans/<int:id>', methods=['GET'])
def get_loan(id):
    """Get a specific loan by ID."""
    loan = Loan.query.get_or_404(id)
    return jsonify({
        'success': True,
        'loan': loan.to_dict()
    })

@api_bp.route('/loans', methods=['POST'])
def create_loan():
    """Create a new loan."""
    data = request.get_json()
    
    required_fields = ['book_id', 'member_id']
    for field in required_fields:
        if field not in data:
            return jsonify({
                'success': False,
                'error': f'Missing required field: {field}'
            }), 400
    
    book_id = data['book_id']
    member_id = data['member_id']
    loan_days = data.get('loan_days', 14)
    
    # Check if book exists and is available
    book = Book.query.get(book_id)
    if not book:
        return jsonify({
            'success': False,
            'error': 'Book not found'
        }), 404
    
    if not book.available:
        return jsonify({
            'success': False,
            'error': 'This book is not available for loan'
        }), 400
    
    # Check if member exists and is active
    member = Member.query.get(member_id)
    if not member:
        return jsonify({
            'success': False,
            'error': 'Member not found'
        }), 404
    
    if not member.active:
        return jsonify({
            'success': False,
            'error': 'This member is not active'
        }), 400
    
    # Create new loan
    loan_date = datetime.utcnow()
    due_date = loan_date + timedelta(days=loan_days)
    
    new_loan = Loan(
        book_id=book_id,
        member_id=member_id,
        loan_date=loan_date,
        due_date=due_date,
        returned=False,
        notes=data.get('notes')
    )
    
    # Update book availability
    book.available = False
    
    db.session.add(new_loan)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Loan created successfully',
        'loan': new_loan.to_dict()
    }), 201

@api_bp.route('/loans/<int:id>/return', methods=['POST'])
def api_return_book(id):
    """Process a book return via API."""
    loan = Loan.query.get_or_404(id)
    
    if loan.returned:
        return jsonify({
            'success': False,
            'error': 'This book has already been returned'
        }), 400
    
    # Process the return
    loan.returned = True
    loan.return_date = datetime.utcnow()
    
    # Update book availability
    book = Book.query.get(loan.book_id)
    if book:
        book.available = True
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Book returned successfully',
        'loan': loan.to_dict(),
        'fine': loan.calculate_fine() if loan.is_overdue() else 0
    })

@api_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Get library statistics."""
    total_books = Book.query.count()
    available_books = Book.query.filter_by(available=True).count()
    total_members = Member.query.count()
    active_members = Member.query.filter_by(active=True).count()
    
    total_loans = Loan.query.count()
    active_loans = Loan.query.filter_by(returned=False).count()
    overdue_loans = Loan.query.filter(
        Loan.returned == False,
        Loan.due_date < datetime.utcnow()
    ).count()
    
    return jsonify({
        'success': True,
        'statistics': {
            'books': {
                'total': total_books,
                'available': available_books,
                'on_loan': total_books - available_books
            },
            'members': {
                'total': total_members,
                'active': active_members,
                'inactive': total_members - active_members
            },
            'loans': {
                'total': total_loans,
                'active': active_loans,
                'overdue': overdue_loans,
                'returned': total_loans - active_loans
            }
        }
    })
