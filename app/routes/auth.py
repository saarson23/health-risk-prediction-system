# app/routes/auth.py
import re
import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.database import db, User
from app import login_manager

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone):
    # nepali phone: 10 digits starting with 97 or 98
    pattern = r'^(97|98)\d{8}$'
    return re.match(pattern, phone) is not None


def validate_password(password):
    if len(password) < 6:
        return False, 'Password must be at least 6 characters.'
    if not re.search(r'[A-Za-z]', password):
        return False, 'Password must contain at least one letter.'
    if not re.search(r'[0-9]', password):
        return False, 'Password must contain at least one number.'
    return True, ''


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        phone = request.form.get('phone', '').strip()

        # validate inputs
        if not username or len(username) < 3:
            flash('Username must be at least 3 characters.', 'danger')
            return redirect(url_for('auth.register'))

        if not validate_email(email):
            flash('Please enter a valid email address.', 'danger')
            return redirect(url_for('auth.register'))

        valid_pw, pw_msg = validate_password(password)
        if not valid_pw:
            flash(pw_msg, 'danger')
            return redirect(url_for('auth.register'))

        if phone and not validate_phone(phone):
            flash('Please enter a valid 10-digit Nepali phone number.', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return redirect(url_for('auth.register'))

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            phone=phone
        )
        db.session.add(user)
        db.session.commit()
        logger.info(f'New user registered: {username} ({email})')

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return render_template('login.html')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            session.pop('is_admin', None)  # clear admin session on user login
            logger.info(f'User logged in: {user.username}')
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            logger.warning(f'Failed login attempt for email: {email}')
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logger.info(f'User logged out: {current_user.username}')
    logout_user()
    session.pop('is_admin', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
