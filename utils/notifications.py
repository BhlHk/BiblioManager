import logging
from datetime import datetime

def send_notification(recipient_email, subject, message):
    """
    Simulate sending a notification to a library member.
    
    In a production environment, this would use an email service or SMS gateway.
    For this implementation, we'll log the notifications to the console.
    
    Args:
        recipient_email (str): The email address of the recipient
        subject (str): The subject of the notification
        message (str): The body of the notification
    
    Returns:
        bool: True if notification was sent successfully, False otherwise
    """
    # Get the current timestamp
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    
    # Log the notification to the console
    logging.info(f"[NOTIFICATION - {timestamp}]")
    logging.info(f"To: {recipient_email}")
    logging.info(f"Subject: {subject}")
    logging.info(f"Message: {message}")
    logging.info("-" * 50)
    
    # In a real implementation, you would send the email here
    # For example, using smtplib or an email service API
    
    return True

def send_overdue_notification(loan):
    """
    Send a notification for an overdue book.
    
    Args:
        loan (Loan): The loan object containing member and book information
        
    Returns:
        bool: True if notification was sent successfully, False otherwise
    """
    from models import Book, Member
    
    book = Book.query.get(loan.book_id)
    member = Member.query.get(loan.member_id)
    
    days_overdue = loan.days_overdue()
    fine = loan.calculate_fine()
    
    subject = f"OVERDUE: Your library book is {days_overdue} days late"
    
    message = (
        f"Dear {member.full_name()},\n\n"
        f"Our records show that you have not returned the following item:\n\n"
        f"Title: {book.title}\n"
        f"Author: {book.author}\n"
        f"Due Date: {loan.due_date.strftime('%Y-%m-%d')}\n"
        f"Days Overdue: {days_overdue}\n"
        f"Current Fine: ${fine:.2f}\n\n"
        f"Please return this item as soon as possible to avoid additional fines.\n\n"
        f"Thank you,\n"
        f"Library Management System"
    )
    
    return send_notification(member.email, subject, message)

def send_upcoming_due_reminder(loan):
    """
    Send a reminder for a book that will be due soon.
    
    Args:
        loan (Loan): The loan object containing member and book information
        
    Returns:
        bool: True if notification was sent successfully, False otherwise
    """
    from models import Book, Member
    from datetime import datetime
    
    book = Book.query.get(loan.book_id)
    member = Member.query.get(loan.member_id)
    
    days_remaining = (loan.due_date - datetime.utcnow()).days
    
    subject = f"Reminder: Your library book is due in {days_remaining} days"
    
    message = (
        f"Dear {member.full_name()},\n\n"
        f"This is a friendly reminder that the following item is due soon:\n\n"
        f"Title: {book.title}\n"
        f"Author: {book.author}\n"
        f"Due Date: {loan.due_date.strftime('%Y-%m-%d')}\n\n"
        f"Please return this item on or before the due date to avoid late fees.\n\n"
        f"Thank you,\n"
        f"Library Management System"
    )
    
    return send_notification(member.email, subject, message)

def send_return_confirmation(loan):
    """
    Send a confirmation when a book is returned.
    
    Args:
        loan (Loan): The loan object containing member and book information
        
    Returns:
        bool: True if notification was sent successfully, False otherwise
    """
    from models import Book, Member
    
    book = Book.query.get(loan.book_id)
    member = Member.query.get(loan.member_id)
    
    subject = "Book Return Confirmation"
    
    fine = 0
    fine_message = ""
    if loan.is_overdue():
        fine = loan.calculate_fine()
        fine_message = f"\nThis return was {loan.days_overdue()} days late, resulting in a fine of ${fine:.2f}."
    
    message = (
        f"Dear {member.full_name()},\n\n"
        f"We confirm that you have returned the following item:\n\n"
        f"Title: {book.title}\n"
        f"Author: {book.author}\n"
        f"Return Date: {loan.return_date.strftime('%Y-%m-%d')}"
        f"{fine_message}\n\n"
        f"Thank you for using our library services.\n\n"
        f"Regards,\n"
        f"Library Management System"
    )
    
    return send_notification(member.email, subject, message)
