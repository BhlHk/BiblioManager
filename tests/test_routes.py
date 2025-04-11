import unittest
from datetime import datetime, timedelta
from app import app, db
from models import Book, Member, Loan
from flask import url_for

class TestBookRoutes(unittest.TestCase):
    def setUp(self):
        """Set up test client and database"""
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        self.client = app.test_client()
        
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create some test data
        self.book1 = Book(
            title="Test Book 1",
            author="Test Author 1",
            isbn="1234567890",
            category="Fiction",
            publication_year=2020,
            description="Test description 1",
            available=True
        )
        
        self.book2 = Book(
            title="Test Book 2",
            author="Test Author 2",
            isbn="0987654321",
            category="Non-Fiction",
            publication_year=2021,
            description="Test description 2",
            available=False
        )
        
        db.session.add_all([self.book1, self.book2])
        db.session.commit()
        
    def tearDown(self):
        """Tear down test database"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_index_route(self):
        """Test book index route"""
        response = self.client.get('/books/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Book 1', response.data)
        self.assertIn(b'Test Book 2', response.data)
    
    def test_show_route(self):
        """Test book show route"""
        response = self.client.get(f'/books/{self.book1.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Book 1', response.data)
        self.assertIn(b'Test Author 1', response.data)
        self.assertIn(b'Fiction', response.data)
    
    def test_create_route_get(self):
        """Test book create route (GET)"""
        response = self.client.get('/books/create')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Add New Book', response.data)
    
    def test_create_route_post(self):
        """Test book create route (POST)"""
        data = {
            'title': 'New Test Book',
            'author': 'New Test Author',
            'isbn': '1122334455',
            'category': 'Mystery',
            'publication_year': 2022,
            'description': 'New test description'
        }
        
        response = self.client.post('/books/create', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Check that the new book exists in the database
        new_book = Book.query.filter_by(title='New Test Book').first()
        self.assertIsNotNone(new_book)
        self.assertEqual(new_book.author, 'New Test Author')
        self.assertEqual(new_book.category, 'Mystery')
    
    def test_edit_route_get(self):
        """Test book edit route (GET)"""
        response = self.client.get(f'/books/{self.book1.id}/edit')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Edit Book', response.data)
        self.assertIn(b'Test Book 1', response.data)
    
    def test_edit_route_post(self):
        """Test book edit route (POST)"""
        data = {
            'title': 'Updated Book Title',
            'author': 'Updated Author',
            'isbn': self.book1.isbn,
            'category': 'Updated Category',
            'publication_year': 2023,
            'description': 'Updated description'
        }
        
        response = self.client.post(f'/books/{self.book1.id}/edit', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Check that the book was updated in the database
        updated_book = Book.query.get(self.book1.id)
        self.assertEqual(updated_book.title, 'Updated Book Title')
        self.assertEqual(updated_book.author, 'Updated Author')
        self.assertEqual(updated_book.category, 'Updated Category')
    
    def test_delete_route(self):
        """Test book delete route"""
        # First, create a book to delete
        book_to_delete = Book(
            title="Delete Me",
            author="Delete Author",
            available=True
        )
        db.session.add(book_to_delete)
        db.session.commit()
        
        book_id = book_to_delete.id
        
        # Delete the book
        response = self.client.post(f'/books/{book_id}/delete', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Check that the book is no longer in the database
        deleted_book = Book.query.get(book_id)
        self.assertIsNone(deleted_book)


class TestMemberRoutes(unittest.TestCase):
    def setUp(self):
        """Set up test client and database"""
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        self.client = app.test_client()
        
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create some test data
        self.member1 = Member(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="123-456-7890",
            address="123 Main St",
            active=True
        )
        
        self.member2 = Member(
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com",
            phone="987-654-3210",
            address="456 Oak Ave",
            active=True
        )
        
        db.session.add_all([self.member1, self.member2])
        db.session.commit()
        
    def tearDown(self):
        """Tear down test database"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_index_route(self):
        """Test member index route"""
        response = self.client.get('/members/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'John Doe', response.data)
        self.assertIn(b'Jane Smith', response.data)
    
    def test_show_route(self):
        """Test member show route"""
        response = self.client.get(f'/members/{self.member1.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'John Doe', response.data)
        self.assertIn(b'john.doe@example.com', response.data)
        self.assertIn(b'123-456-7890', response.data)
    
    def test_create_route_get(self):
        """Test member create route (GET)"""
        response = self.client.get('/members/create')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Add New Member', response.data)
    
    def test_create_route_post(self):
        """Test member create route (POST)"""
        data = {
            'first_name': 'New',
            'last_name': 'Member',
            'email': 'new.member@example.com',
            'phone': '555-123-4567',
            'address': '789 Pine St'
        }
        
        response = self.client.post('/members/create', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Check that the new member exists in the database
        new_member = Member.query.filter_by(email='new.member@example.com').first()
        self.assertIsNotNone(new_member)
        self.assertEqual(new_member.first_name, 'New')
        self.assertEqual(new_member.last_name, 'Member')
        self.assertEqual(new_member.phone, '555-123-4567')
    
    def test_edit_route_get(self):
        """Test member edit route (GET)"""
        response = self.client.get(f'/members/{self.member1.id}/edit')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Edit Member', response.data)
        self.assertIn(b'John', response.data)
        self.assertIn(b'Doe', response.data)
    
    def test_edit_route_post(self):
        """Test member edit route (POST)"""
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated.name@example.com',
            'phone': '999-888-7777',
            'address': 'Updated Address',
            'active': 'on'
        }
        
        response = self.client.post(f'/members/{self.member1.id}/edit', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Check that the member was updated in the database
        updated_member = Member.query.get(self.member1.id)
        self.assertEqual(updated_member.first_name, 'Updated')
        self.assertEqual(updated_member.last_name, 'Name')
        self.assertEqual(updated_member.email, 'updated.name@example.com')
        self.assertEqual(updated_member.phone, '999-888-7777')
        self.assertEqual(updated_member.address, 'Updated Address')
        self.assertTrue(updated_member.active)


class TestLoanRoutes(unittest.TestCase):
    def setUp(self):
        """Set up test client and database"""
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        self.client = app.test_client()
        
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test book and member
        self.book = Book(title="Test Book", author="Test Author", available=True)
        self.member = Member(first_name="Test", last_name="User", email="test@example.com", active=True)
        
        db.session.add_all([self.book, self.member])
        db.session.commit()
        
        # Create a test loan
        loan_date = datetime.utcnow()
        due_date = loan_date + timedelta(days=14)
        
        self.loan = Loan(
            book_id=self.book.id,
            member_id=self.member.id,
            loan_date=loan_date,
            due_date=due_date,
            returned=False
        )
        
        db.session.add(self.loan)
        db.session.commit()
        
    def tearDown(self):
        """Tear down test database"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_index_route(self):
        """Test loan index route"""
        response = self.client.get('/loans/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Book', response.data)
        self.assertIn(b'Test User', response.data)
    
    def test_show_route(self):
        """Test loan show route"""
        response = self.client.get(f'/loans/{self.loan.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Book', response.data)
        self.assertIn(b'Test User', response.data)
        self.assertIn(b'Active Loan', response.data)
    
    def test_create_route_get(self):
        """Test loan create route (GET)"""
        response = self.client.get('/loans/create')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create New Loan', response.data)
        self.assertIn(b'Test Book', response.data)
        self.assertIn(b'Test User', response.data)
    
    def test_create_route_post(self):
        """Test loan create route (POST)"""
        # Create another book for this test
        new_book = Book(title="Another Book", author="Another Author", available=True)
        db.session.add(new_book)
        db.session.commit()
        
        data = {
            'book_id': new_book.id,
            'member_id': self.member.id,
            'loan_days': 7
        }
        
        response = self.client.post('/loans/create', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Check that the new loan exists in the database
        new_loan = Loan.query.filter_by(book_id=new_book.id, member_id=self.member.id).first()
        self.assertIsNotNone(new_loan)
        self.assertFalse(new_loan.returned)
        
        # Check that the book is now unavailable
        updated_book = Book.query.get(new_book.id)
        self.assertFalse(updated_book.available)
    
    def test_return_book_route(self):
        """Test book return route"""
        # Ensure book is marked as unavailable first
        self.book.available = False
        db.session.commit()
        
        response = self.client.post(f'/loans/{self.loan.id}/return', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Check that the loan is marked as returned
        updated_loan = Loan.query.get(self.loan.id)
        self.assertTrue(updated_loan.returned)
        self.assertIsNotNone(updated_loan.return_date)
        
        # Check that the book is now available
        updated_book = Book.query.get(self.book.id)
        self.assertTrue(updated_book.available)


class TestAPIRoutes(unittest.TestCase):
    def setUp(self):
        """Set up test client and database"""
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test data
        self.book = Book(title="API Test Book", author="API Author", available=True)
        self.member = Member(first_name="API", last_name="User", email="api@example.com", active=True)
        
        db.session.add_all([self.book, self.member])
        db.session.commit()
        
        # Create a test loan
        self.loan = Loan(
            book_id=self.book.id,
            member_id=self.member.id,
            loan_date=datetime.utcnow(),
            due_date=datetime.utcnow() + timedelta(days=14),
            returned=False
        )
        
        db.session.add(self.loan)
        db.session.commit()
        
    def tearDown(self):
        """Tear down test database"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_get_books_api(self):
        """Test GET /api/books endpoint"""
        response = self.client.get('/api/books')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['books'][0]['title'], "API Test Book")
    
    def test_get_book_api(self):
        """Test GET /api/books/<id> endpoint"""
        response = self.client.get(f'/api/books/{self.book.id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['book']['title'], "API Test Book")
    
    def test_get_members_api(self):
        """Test GET /api/members endpoint"""
        response = self.client.get('/api/members')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['members'][0]['first_name'], "API")
    
    def test_get_loans_api(self):
        """Test GET /api/loans endpoint"""
        response = self.client.get('/api/loans')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['loans'][0]['book_id'], self.book.id)
    
    def test_statistics_api(self):
        """Test GET /api/statistics endpoint"""
        response = self.client.get('/api/statistics')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['statistics']['books']['total'], 1)
        self.assertEqual(data['statistics']['members']['total'], 1)
        self.assertEqual(data['statistics']['loans']['total'], 1)


if __name__ == '__main__':
    unittest.main()
