import unittest
from datetime import datetime, timedelta
from app import app, db
from models import Book, Member, Loan

class TestBookModel(unittest.TestCase):
    def setUp(self):
        """Set up test database"""
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        
    def tearDown(self):
        """Tear down test database"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_book_creation(self):
        """Test creating a new book"""
        book = Book(
            title="Test Book",
            author="Test Author",
            isbn="1234567890",
            category="Test Category",
            publication_year=2023,
            description="Test description",
            available=True
        )
        db.session.add(book)
        db.session.commit()
        
        retrieved_book = Book.query.filter_by(title="Test Book").first()
        self.assertIsNotNone(retrieved_book)
        self.assertEqual(retrieved_book.author, "Test Author")
        self.assertEqual(retrieved_book.isbn, "1234567890")
        self.assertEqual(retrieved_book.category, "Test Category")
        self.assertEqual(retrieved_book.publication_year, 2023)
        self.assertEqual(retrieved_book.description, "Test description")
        self.assertTrue(retrieved_book.available)
    
    def test_book_is_available(self):
        """Test book availability method"""
        # Create an available book
        available_book = Book(title="Available Book", author="Author", available=True)
        # Create an unavailable book
        unavailable_book = Book(title="Unavailable Book", author="Author", available=False)
        
        db.session.add(available_book)
        db.session.add(unavailable_book)
        db.session.commit()
        
        self.assertTrue(available_book.is_available())
        self.assertFalse(unavailable_book.is_available())
    
    def test_book_to_dict(self):
        """Test book to_dict method"""
        book = Book(
            title="Dictionary Test",
            author="Dict Author",
            isbn="0987654321",
            category="Test",
            publication_year=2020,
            description="Test description",
            available=True
        )
        db.session.add(book)
        db.session.commit()
        
        book_dict = book.to_dict()
        self.assertEqual(book_dict['title'], "Dictionary Test")
        self.assertEqual(book_dict['author'], "Dict Author")
        self.assertEqual(book_dict['isbn'], "0987654321")
        self.assertEqual(book_dict['category'], "Test")
        self.assertEqual(book_dict['publication_year'], 2020)
        self.assertEqual(book_dict['description'], "Test description")
        self.assertTrue(book_dict['available'])


class TestMemberModel(unittest.TestCase):
    def setUp(self):
        """Set up test database"""
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        
    def tearDown(self):
        """Tear down test database"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_member_creation(self):
        """Test creating a new member"""
        member = Member(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="123-456-7890",
            address="123 Main St",
            active=True
        )
        db.session.add(member)
        db.session.commit()
        
        retrieved_member = Member.query.filter_by(email="john.doe@example.com").first()
        self.assertIsNotNone(retrieved_member)
        self.assertEqual(retrieved_member.first_name, "John")
        self.assertEqual(retrieved_member.last_name, "Doe")
        self.assertEqual(retrieved_member.phone, "123-456-7890")
        self.assertEqual(retrieved_member.address, "123 Main St")
        self.assertTrue(retrieved_member.active)
    
    def test_member_full_name(self):
        """Test member full_name method"""
        member = Member(first_name="Jane", last_name="Smith")
        self.assertEqual(member.full_name(), "Jane Smith")
    
    def test_count_active_loans(self):
        """Test counting active loans for a member"""
        # Create a member
        member = Member(first_name="Test", last_name="User", email="test@example.com")
        db.session.add(member)
        
        # Create some books
        book1 = Book(title="Book 1", author="Author 1")
        book2 = Book(title="Book 2", author="Author 2")
        book3 = Book(title="Book 3", author="Author 3")
        db.session.add_all([book1, book2, book3])
        db.session.commit()
        
        # Create loans
        loan1 = Loan(book_id=book1.id, member_id=member.id, loan_date=datetime.utcnow(),
                    due_date=datetime.utcnow() + timedelta(days=14), returned=False)
        loan2 = Loan(book_id=book2.id, member_id=member.id, loan_date=datetime.utcnow(),
                    due_date=datetime.utcnow() + timedelta(days=14), returned=True)
        loan3 = Loan(book_id=book3.id, member_id=member.id, loan_date=datetime.utcnow(),
                    due_date=datetime.utcnow() + timedelta(days=14), returned=False)
        
        db.session.add_all([loan1, loan2, loan3])
        db.session.commit()
        
        self.assertEqual(member.count_active_loans(), 2)
    
    def test_member_to_dict(self):
        """Test member to_dict method"""
        member = Member(
            first_name="Dict",
            last_name="Test",
            email="dict.test@example.com",
            phone="987-654-3210",
            address="456 Test St",
            active=True
        )
        db.session.add(member)
        db.session.commit()
        
        member_dict = member.to_dict()
        self.assertEqual(member_dict['first_name'], "Dict")
        self.assertEqual(member_dict['last_name'], "Test")
        self.assertEqual(member_dict['email'], "dict.test@example.com")
        self.assertEqual(member_dict['phone'], "987-654-3210")
        self.assertEqual(member_dict['address'], "456 Test St")
        self.assertTrue(member_dict['active'])


class TestLoanModel(unittest.TestCase):
    def setUp(self):
        """Set up test database"""
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test book and member
        self.book = Book(title="Test Book", author="Test Author", available=True)
        self.member = Member(first_name="Test", last_name="User", email="test@example.com")
        db.session.add_all([self.book, self.member])
        db.session.commit()
        
    def tearDown(self):
        """Tear down test database"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_loan_creation(self):
        """Test creating a new loan"""
        loan_date = datetime.utcnow()
        due_date = loan_date + timedelta(days=14)
        
        loan = Loan(
            book_id=self.book.id,
            member_id=self.member.id,
            loan_date=loan_date,
            due_date=due_date,
            returned=False
        )
        db.session.add(loan)
        db.session.commit()
        
        retrieved_loan = Loan.query.filter_by(book_id=self.book.id, member_id=self.member.id).first()
        self.assertIsNotNone(retrieved_loan)
        self.assertEqual(retrieved_loan.book_id, self.book.id)
        self.assertEqual(retrieved_loan.member_id, self.member.id)
        self.assertFalse(retrieved_loan.returned)
    
    def test_is_overdue(self):
        """Test loan is_overdue method"""
        # Create a loan that is not overdue
        future_due_date = datetime.utcnow() + timedelta(days=7)
        active_loan = Loan(
            book_id=self.book.id,
            member_id=self.member.id,
            loan_date=datetime.utcnow(),
            due_date=future_due_date,
            returned=False
        )
        
        # Create a loan that is overdue
        past_due_date = datetime.utcnow() - timedelta(days=7)
        overdue_loan = Loan(
            book_id=self.book.id,
            member_id=self.member.id,
            loan_date=datetime.utcnow() - timedelta(days=14),
            due_date=past_due_date,
            returned=False
        )
        
        # Create a returned loan that was overdue
        returned_overdue_loan = Loan(
            book_id=self.book.id,
            member_id=self.member.id,
            loan_date=datetime.utcnow() - timedelta(days=14),
            due_date=past_due_date,
            returned=True,
            return_date=datetime.utcnow()
        )
        
        db.session.add_all([active_loan, overdue_loan, returned_overdue_loan])
        db.session.commit()
        
        self.assertFalse(active_loan.is_overdue())
        self.assertTrue(overdue_loan.is_overdue())
        self.assertFalse(returned_overdue_loan.is_overdue())  # Not overdue because it's returned
    
    def test_calculate_fine(self):
        """Test fine calculation"""
        # Create an overdue loan (7 days overdue)
        past_due_date = datetime.utcnow() - timedelta(days=7)
        overdue_loan = Loan(
            book_id=self.book.id,
            member_id=self.member.id,
            loan_date=datetime.utcnow() - timedelta(days=14),
            due_date=past_due_date,
            returned=False
        )
        db.session.add(overdue_loan)
        db.session.commit()
        
        # Fine should be 7 days * $0.50 = $3.50
        self.assertEqual(overdue_loan.calculate_fine(), 3.50)
        
        # Create a non-overdue loan
        future_due_date = datetime.utcnow() + timedelta(days=7)
        active_loan = Loan(
            book_id=self.book.id,
            member_id=self.member.id,
            loan_date=datetime.utcnow(),
            due_date=future_due_date,
            returned=False
        )
        db.session.add(active_loan)
        db.session.commit()
        
        # Fine should be $0.00
        self.assertEqual(active_loan.calculate_fine(), 0.00)
    
    def test_return_book(self):
        """Test book return functionality"""
        # Create an active loan
        loan = Loan(
            book_id=self.book.id,
            member_id=self.member.id,
            loan_date=datetime.utcnow(),
            due_date=datetime.utcnow() + timedelta(days=14),
            returned=False
        )
        db.session.add(loan)
        db.session.commit()
        
        # Update book availability to match a real loan
        self.book.available = False
        db.session.commit()
        
        # Return the book
        result = loan.return_book()
        
        # Check that the return was successful
        self.assertTrue(result)
        self.assertTrue(loan.returned)
        self.assertIsNotNone(loan.return_date)
        
        # Check that the book is now available
        retrieved_book = Book.query.get(self.book.id)
        self.assertTrue(retrieved_book.available)
        
        # Try to return again (should fail)
        result = loan.return_book()
        self.assertFalse(result)  # Already returned


if __name__ == '__main__':
    unittest.main()
