from datetime import datetime, timedelta
from app import db

class Book(db.Model):
    """Model representing a book in the library."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(20), unique=True)
    category = db.Column(db.String(50))
    publication_year = db.Column(db.Integer)
    description = db.Column(db.Text)
    available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    loans = db.relationship('Loan', backref='book', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Book {self.title} by {self.author}>'
    
    def is_available(self):
        """Check if the book is available for loan."""
        return self.available
    
    def to_dict(self):
        """Convert book object to dictionary for API responses."""
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'category': self.category,
            'publication_year': self.publication_year,
            'description': self.description,
            'available': self.available,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Member(db.Model):
    """Model representing a library member."""
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    loans = db.relationship('Loan', backref='member', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Member {self.first_name} {self.last_name}>'
    
    def full_name(self):
        """Return the member's full name."""
        return f"{self.first_name} {self.last_name}"
    
    def count_active_loans(self):
        """Count how many books the member currently has on loan."""
        return Loan.query.filter_by(member_id=self.id, returned=False).count()
    
    def has_overdue_loans(self):
        """Check if the member has any overdue loans."""
        today = datetime.utcnow().date()
        return any(loan.due_date.date() < today for loan in self.loans if not loan.returned)
    
    def to_dict(self):
        """Convert member object to dictionary for API responses."""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'registration_date': self.registration_date.isoformat() if self.registration_date else None,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Loan(db.Model):
    """Model representing a book loan transaction."""
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    loan_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime, nullable=True)
    returned = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Loan Book:{self.book_id} Member:{self.member_id}>'
    
    def is_overdue(self):
        """Check if the loan is overdue."""
        if self.returned:
            return False
        return datetime.utcnow() > self.due_date
    
    def days_overdue(self):
        """Calculate how many days the loan is overdue."""
        if not self.is_overdue():
            return 0
        delta = datetime.utcnow() - self.due_date
        return delta.days
    
    def calculate_fine(self, daily_rate=0.50):
        """Calculate the fine amount for an overdue loan."""
        if not self.is_overdue():
            return 0
        return self.days_overdue() * daily_rate
    
    @classmethod
    def create_loan(cls, book_id, member_id, loan_period_days=14):
        """Create a new loan with a calculated due date."""
        loan_date = datetime.utcnow()
        due_date = loan_date + timedelta(days=loan_period_days)
        
        # Check if book is available
        book = Book.query.get(book_id)
        if not book or not book.available:
            return None
        
        # Update book availability
        book.available = False
        
        # Create new loan
        new_loan = cls(
            book_id=book_id,
            member_id=member_id,
            loan_date=loan_date,
            due_date=due_date
        )
        
        db.session.add(new_loan)
        db.session.commit()
        
        return new_loan
    
    def return_book(self):
        """Process a book return."""
        if self.returned:
            return False
        
        self.returned = True
        self.return_date = datetime.utcnow()
        
        # Update book availability
        book = Book.query.get(self.book_id)
        if book:
            book.available = True
        
        db.session.commit()
        return True
    
    def to_dict(self):
        """Convert loan object to dictionary for API responses."""
        return {
            'id': self.id,
            'book_id': self.book_id,
            'member_id': self.member_id,
            'loan_date': self.loan_date.isoformat() if self.loan_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'returned': self.returned,
            'notes': self.notes,
            'is_overdue': self.is_overdue(),
            'days_overdue': self.days_overdue(),
            'fine': self.calculate_fine(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
