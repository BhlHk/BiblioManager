import unittest
from unittest.mock import patch, MagicMock
import logging
from datetime import datetime, timedelta
from app import app, db
from models import Book, Member, Loan
from utils.notifications import send_notification, send_overdue_notification, send_upcoming_due_reminder, send_return_confirmation

class TestNotifications(unittest.TestCase):
    def setUp(self):
        """Set up test database and logging"""
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test data
        self.book = Book(
            title="Test Book",
            author="Test Author",
            isbn="1234567890",
            category="Fiction",
            available=True
        )
        
        self.member = Member(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            phone="123-456-7890",
            active=True
        )
        
        db.session.add_all([self.book, self.member])
        db.session.commit()
        
        # Create a test loan
        self.active_loan = Loan(
            book_id=self.book.id,
            member_id=self.member.id,
            loan_date=datetime.utcnow() - timedelta(days=7),
            due_date=datetime.utcnow() + timedelta(days=7),
            returned=False
        )
        
        self.overdue_loan = Loan(
            book_id=self.book.id,
            member_id=self.member.id,
            loan_date=datetime.utcnow() - timedelta(days=21),
            due_date=datetime.utcnow() - timedelta(days=7),
            returned=False
        )
        
        self.returned_loan = Loan(
            book_id=self.book.id,
            member_id=self.member.id,
            loan_date=datetime.utcnow() - timedelta(days=14),
            due_date=datetime.utcnow() - timedelta(days=7),
            returned=True,
            return_date=datetime.utcnow()
        )
        
        db.session.add_all([self.active_loan, self.overdue_loan, self.returned_loan])
        db.session.commit()
        
    def tearDown(self):
        """Tear down test database"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    @patch('logging.info')
    def test_send_notification(self, mock_log):
        """Test send_notification function"""
        recipient = "test@example.com"
        subject = "Test Subject"
        message = "Test Message"
        
        result = send_notification(recipient, subject, message)
        
        self.assertTrue(result)
        mock_log.assert_any_call(f"To: {recipient}")
        mock_log.assert_any_call(f"Subject: {subject}")
        mock_log.assert_any_call(f"Message: {message}")
    
    @patch('utils.notifications.send_notification')
    def test_send_overdue_notification(self, mock_send):
        """Test send_overdue_notification function"""
        mock_send.return_value = True
        
        result = send_overdue_notification(self.overdue_loan)
        
        self.assertTrue(result)
        mock_send.assert_called_once()
        
        # Check that the correct arguments were passed
        args = mock_send.call_args[0]
        self.assertEqual(args[0], self.member.email)
        self.assertIn("OVERDUE", args[1])
        self.assertIn(self.book.title, args[2])
        self.assertIn(str(self.overdue_loan.days_overdue()), args[2])
        self.assertIn(str(self.overdue_loan.calculate_fine()), args[2])
    
    @patch('utils.notifications.send_notification')
    def test_send_upcoming_due_reminder(self, mock_send):
        """Test send_upcoming_due_reminder function"""
        mock_send.return_value = True
        
        result = send_upcoming_due_reminder(self.active_loan)
        
        self.assertTrue(result)
        mock_send.assert_called_once()
        
        # Check that the correct arguments were passed
        args = mock_send.call_args[0]
        self.assertEqual(args[0], self.member.email)
        self.assertIn("Reminder", args[1])
        self.assertIn(self.book.title, args[2])
        self.assertIn(self.active_loan.due_date.strftime('%Y-%m-%d'), args[2])
    
    @patch('utils.notifications.send_notification')
    def test_send_return_confirmation(self, mock_send):
        """Test send_return_confirmation function"""
        mock_send.return_value = True
        
        result = send_return_confirmation(self.returned_loan)
        
        self.assertTrue(result)
        mock_send.assert_called_once()
        
        # Check that the correct arguments were passed
        args = mock_send.call_args[0]
        self.assertEqual(args[0], self.member.email)
        self.assertIn("Return Confirmation", args[1])
        self.assertIn(self.book.title, args[2])
        self.assertIn(self.returned_loan.return_date.strftime('%Y-%m-%d'), args[2])


if __name__ == '__main__':
    unittest.main()
