from flask import Blueprint, render_template, redirect, url_for, flash
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from app import db
from models import Book, Member, Loan

# Créer le blueprint pour les routes d'administration
admin = Blueprint('admin', __name__)

@admin.route('/dashboard')
def dashboard():
    """Affiche le tableau de bord d'administration avec les statistiques globales."""
    # Récupérer les statistiques de base
    total_books = Book.query.count()
    available_books = Book.query.filter_by(available=True).count()
    total_members = Member.query.count()
    active_members = Member.query.filter_by(active=True).count()
    
    # Récupérer les statistiques des emprunts
    total_loans = Loan.query.count()
    total_active_loans = Loan.query.filter_by(returned=False).count()
    total_overdue_loans = Loan.query.filter(
        Loan.returned == False,
        Loan.due_date < datetime.utcnow()
    ).count()
    
    # Calculer les taux
    usage_rate = round((total_active_loans / total_books * 100)) if total_books > 0 else 0
    overdue_rate = round((total_overdue_loans / total_active_loans * 100)) if total_active_loans > 0 else 0
    
    # Récupérer les emprunts récents (15 derniers)
    recent_loans = Loan.query.order_by(desc(Loan.loan_date)).limit(15).all()
    
    # Récupérer les catégories populaires
    category_stats = db.session.query(
        Book.category,
        func.count(Book.id).label('book_count'),
        func.count(Loan.id).label('loan_count')
    ).outerjoin(Loan).group_by(Book.category).order_by(desc('loan_count')).limit(5).all()
    
    popular_categories = [
        (category or "Non catégorisé", book_count, loan_count)
        for category, book_count, loan_count in category_stats
    ]
    
    return render_template(
        'admin/dashboard.html',
        total_books=total_books,
        available_books=available_books,
        total_members=total_members,
        active_members=active_members,
        inactive_members=total_members - active_members,
        total_loans=total_loans,
        total_active_loans=total_active_loans,
        total_overdue_loans=total_overdue_loans,
        usage_rate=usage_rate,
        overdue_rate=overdue_rate,
        recent_loans=recent_loans,
        popular_categories=popular_categories
    )

@admin.route('/system-status')
def system_status():
    """Affiche les informations sur l'état du système."""
    # Obtenir le nombre d'entrées dans chaque table
    book_count = Book.query.count()
    member_count = Member.query.count()
    loan_count = Loan.query.count()
    
    # Heure actuelle pour afficher les informations de timing
    current_time = datetime.utcnow()
    
    return render_template(
        'admin/system_status.html',
        book_count=book_count,
        member_count=member_count,
        loan_count=loan_count,
        current_time=current_time,
        timedelta=timedelta  # Passer timedelta pour les calculs de temps dans le template
    )