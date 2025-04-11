from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse
from datetime import datetime

from app import db
from models import User, Member
from forms import LoginForm, RegistrationForm

# Créer le blueprint pour l'authentification
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Gérer la connexion des utilisateurs."""
    # Si l'utilisateur est déjà connecté, rediriger vers la page d'accueil
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Trouver l'utilisateur par son nom d'utilisateur
        user = User.query.filter_by(username=form.username.data).first()
        
        # Vérifier si l'utilisateur existe et si le mot de passe est correct
        if user is None or not user.check_password(form.password.data):
            flash('Nom d\'utilisateur ou mot de passe incorrect', 'danger')
            return redirect(url_for('auth.login'))
        
        # Connecter l'utilisateur
        login_user(user, remember=form.remember_me.data)
        
        # Mettre à jour la date de dernière connexion
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Rediriger vers la page demandée ou la page d'accueil
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            if user.is_admin():
                next_page = url_for('admin.dashboard')
            elif user.is_librarian():
                next_page = url_for('admin.dashboard')
            else:
                next_page = url_for('members.dashboard')
        
        flash(f'Bienvenue, {user.username}!', 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Connexion', form=form)

@auth_bp.route('/logout')
def logout():
    """Gérer la déconnexion des utilisateurs."""
    logout_user()
    flash('Vous avez été déconnecté avec succès.', 'info')
    return redirect(url_for('home'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Gérer l'inscription des nouveaux utilisateurs."""
    # Si l'utilisateur est déjà connecté, rediriger vers la page d'accueil
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegistrationForm()
    
    # Administrateurs uniquement peuvent choisir un rôle
    # Par défaut, les nouveaux utilisateurs sont des membres
    form.role.choices = [('member', 'Membre')]
    if current_user.is_authenticated and current_user.is_admin():
        form.role.choices = [('member', 'Membre'), ('librarian', 'Bibliothécaire'), ('admin', 'Administrateur')]
    
    if form.validate_on_submit():
        # Créer un nouvel utilisateur
        user = User(
            username=form.username.data,
            email=form.email.data,
            role='member'  # Par défaut, tous les nouveaux utilisateurs sont des membres
        )
        
        # Si un administrateur crée le compte, utiliser le rôle sélectionné
        if current_user.is_authenticated and current_user.is_admin():
            user.role = form.role.data
        
        # Définir le mot de passe
        user.set_password(form.password.data)
        
        # Ajouter l'utilisateur à la base de données
        db.session.add(user)
        db.session.commit()
        
        flash('Félicitations, vous êtes maintenant inscrit!', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Inscription', form=form)

@auth_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    """Afficher le profil de l'utilisateur."""
    # Si l'utilisateur est un membre, afficher son profil de membre
    if current_user.is_member() and current_user.member_id:
        return redirect(url_for('members.show', id=current_user.member_id))
    
    return render_template('auth/profile.html', title='Mon Profil', user=current_user)