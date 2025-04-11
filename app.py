import os
import logging

from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy with the Base class
db = SQLAlchemy(model_class=Base)

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-library-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///library.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize app with SQLAlchemy
db.init_app(app)

# Import models and create tables
with app.app_context():
    # Import models
    import models

    # Create database tables
    db.create_all()
    
    app.logger.info("Database tables created")

# Register blueprints/routes
from routes.book_routes import book_bp
from routes.member_routes import member_bp
from routes.loan_routes import loan_bp
from routes.api_routes import api_bp
from routes.admin_routes import admin

app.register_blueprint(book_bp)
app.register_blueprint(member_bp)
app.register_blueprint(loan_bp)
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(admin, url_prefix='/admin')

# Home route
@app.route('/')
def home():
    # Get count data for dashboard
    book_count = models.Book.query.count()
    available_books = models.Book.query.filter_by(available=True).count()
    member_count = models.Member.query.count()
    active_members = models.Member.query.filter_by(active=True).count()
    loan_count = models.Loan.query.count()
    active_loans = models.Loan.query.filter_by(returned=False).count()
    overdue_loans = models.Loan.query.filter(
        models.Loan.returned == False,
        models.Loan.due_date < models.Loan.loan_date
    ).count()
    
    # Create stats dictionary
    stats = {
        'total_books': book_count,
        'available_books': available_books,
        'total_members': member_count,
        'active_members': active_members,
        'total_loans': loan_count,
        'active_loans': active_loans,
        'overdue_loans': overdue_loans
    }
    
    # Recent items
    recent_books = models.Book.query.order_by(models.Book.created_at.desc()).limit(5).all()
    recent_members = models.Member.query.order_by(models.Member.created_at.desc()).limit(5).all()
    recent_loans = models.Loan.query.order_by(models.Loan.created_at.desc()).limit(5).all()
    
    return render_template('index.html',
                          stats=stats,
                          recent_books=recent_books,
                          recent_members=recent_members,
                          recent_loans=recent_loans)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
