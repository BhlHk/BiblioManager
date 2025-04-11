from flask import Blueprint, render_template, redirect, url_for, request, flash
from app import db
from models import Book
from sqlalchemy import or_

book_bp = Blueprint('books', __name__, url_prefix='/books')

@book_bp.route('/')
def index():
    """Display all books with optional search functionality."""
    search_term = request.args.get('search', '')
    category = request.args.get('category', '')
    
    # Query books based on search parameters
    query = Book.query
    
    if search_term:
        query = query.filter(
            or_(
                Book.title.ilike(f'%{search_term}%'),
                Book.author.ilike(f'%{search_term}%'),
                Book.isbn.ilike(f'%{search_term}%')
            )
        )
    
    if category:
        query = query.filter(Book.category == category)
    
    books = query.order_by(Book.title).all()
    
    # Get unique categories for filter dropdown
    categories = db.session.query(Book.category).distinct().order_by(Book.category).all()
    categories = [cat[0] for cat in categories if cat[0]]  # Remove None values
    
    return render_template('books/index.html', 
                          books=books, 
                          search_term=search_term, 
                          selected_category=category,
                          categories=categories)

@book_bp.route('/create', methods=['GET', 'POST'])
def create():
    """Create a new book."""
    if request.method == 'POST':
        # Extract form data
        title = request.form.get('title')
        author = request.form.get('author')
        isbn = request.form.get('isbn')
        category = request.form.get('category')
        publication_year = request.form.get('publication_year')
        description = request.form.get('description')
        
        # Validate required fields
        if not title or not author:
            flash('Title and author are required!', 'danger')
            return render_template('books/create.html')
        
        # Convert publication_year to integer if provided
        if publication_year:
            try:
                publication_year = int(publication_year)
            except ValueError:
                flash('Publication year must be a number!', 'danger')
                return render_template('books/create.html')
        
        # Check if ISBN already exists
        if isbn and Book.query.filter_by(isbn=isbn).first():
            flash('A book with this ISBN already exists!', 'danger')
            return render_template('books/create.html')
        
        # Create new book
        new_book = Book(
            title=title,
            author=author,
            isbn=isbn,
            category=category,
            publication_year=publication_year,
            description=description,
            available=True
        )
        
        db.session.add(new_book)
        db.session.commit()
        
        flash('Book added successfully!', 'success')
        return redirect(url_for('books.show', id=new_book.id))
    
    return render_template('books/create.html')

@book_bp.route('/<int:id>')
def show(id):
    """Show details of a specific book."""
    book = Book.query.get_or_404(id)
    return render_template('books/show.html', book=book)

@book_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    """Edit an existing book."""
    book = Book.query.get_or_404(id)
    
    if request.method == 'POST':
        # Extract form data
        book.title = request.form.get('title')
        book.author = request.form.get('author')
        book.isbn = request.form.get('isbn')
        book.category = request.form.get('category')
        book.description = request.form.get('description')
        
        # Convert publication_year to integer if provided
        publication_year = request.form.get('publication_year')
        if publication_year:
            try:
                book.publication_year = int(publication_year)
            except ValueError:
                flash('Publication year must be a number!', 'danger')
                return render_template('books/edit.html', book=book)
        else:
            book.publication_year = None
        
        # Check if ISBN already exists and belongs to another book
        if book.isbn:
            existing_book = Book.query.filter_by(isbn=book.isbn).first()
            if existing_book and existing_book.id != book.id:
                flash('A book with this ISBN already exists!', 'danger')
                return render_template('books/edit.html', book=book)
        
        db.session.commit()
        flash('Book updated successfully!', 'success')
        return redirect(url_for('books.show', id=book.id))
    
    return render_template('books/edit.html', book=book)

@book_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    """Delete a book."""
    book = Book.query.get_or_404(id)
    
    # Check if the book has active loans
    if any(not loan.returned for loan in book.loans):
        flash('Cannot delete a book that is currently on loan!', 'danger')
        return redirect(url_for('books.show', id=book.id))
    
    db.session.delete(book)
    db.session.commit()
    
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('books.index'))
