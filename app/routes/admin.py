# app/routes/admin.py
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import current_user, logout_user
from werkzeug.security import check_password_hash
from app.models.database import db, User, Prediction
from config import Config
import pandas as pd
import os

logger = logging.getLogger(__name__)
admin_bp = Blueprint('admin', __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCTORS_CSV = os.path.join(BASE_DIR, 'data', 'raw', 'kathmandu_doctors_with_names.csv')

def load_doctors():
    try:
        return pd.read_csv(DOCTORS_CSV)
    except Exception as e:
        logger.error(f'Failed to load doctors CSV: {e}')
        return pd.DataFrame(columns=['hospital_name','location','phone','hours','type','rating','department','doctor_name','qualification','opd_schedule','diseases_treated','notes'])

def save_doctors(df):
    try:
        df.to_csv(DOCTORS_CSV, index=False)
    except Exception as e:
        logger.error(f'Failed to save doctors CSV: {e}')


def admin_required(f):
    """Decorator to check admin session."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Please login as admin.', 'danger')
            return redirect(url_for('admin.admin_login'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('is_admin'):
        return redirect(url_for('admin.admin_dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please enter both username and password.', 'danger')
            return render_template('admin_login.html')

        if username == Config.ADMIN_USERNAME and check_password_hash(Config.ADMIN_PASSWORD_HASH, password):
            logout_user()  # clear any regular user session
            session['is_admin'] = True
            logger.info('Admin logged in')
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin.admin_dashboard'))
        else:
            logger.warning(f'Failed admin login attempt: {username}')
            flash('Invalid admin credentials.', 'danger')
    return render_template('admin_login.html')


@admin_bp.route('/admin')
@admin_required
def admin_dashboard():
    users = User.query.all()
    predictions = Prediction.query.order_by(Prediction.created_at.desc()).all()
    doctors_df = load_doctors()
    return render_template('admin.html', users=users, predictions=predictions,
                           doctor_count=len(doctors_df),
                           hospital_count=doctors_df['hospital_name'].nunique() if not doctors_df.empty else 0)


@admin_bp.route('/admin/doctors')
@admin_required
def admin_doctors():
    doctors = load_doctors().to_dict('records')
    return render_template('admin_doctors.html', doctors=doctors)


@admin_bp.route('/admin/doctors/add', methods=['GET', 'POST'])
@admin_required
def admin_add_doctor():
    if request.method == 'POST':
        doctor_name = request.form.get('doctor_name', '').strip()
        hospital_name = request.form.get('hospital_name', '').strip()
        department = request.form.get('department', '').strip()

        if not doctor_name or not hospital_name or not department:
            flash('Doctor name, hospital, and department are required.', 'danger')
            return render_template('admin_add_doctor.html')

        try:
            rating = float(request.form.get('rating', 0))
            if rating < 0 or rating > 5:
                rating = 0
        except ValueError:
            rating = 0

        df = load_doctors()
        new = {
            'hospital_name': hospital_name,
            'location': request.form.get('location', '').strip(),
            'phone': request.form.get('phone', '').strip(),
            'hours': request.form.get('hours', '').strip(),
            'type': request.form.get('type', '').strip(),
            'rating': rating,
            'department': department,
            'doctor_name': doctor_name,
            'qualification': request.form.get('qualification', '').strip(),
            'opd_schedule': request.form.get('opd_schedule', '').strip(),
            'diseases_treated': request.form.get('diseases_treated', '').strip(),
            'notes': request.form.get('notes', '').strip()
        }
        df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
        save_doctors(df)
        logger.info(f'Doctor added: {doctor_name} at {hospital_name}')
        flash('Doctor added!', 'success')
        return redirect(url_for('admin.admin_doctors'))
    return render_template('admin_add_doctor.html')


@admin_bp.route('/admin/doctors/edit/<int:index>', methods=['GET', 'POST'])
@admin_required
def admin_edit_doctor(index):
    df = load_doctors()
    if index < 0 or index >= len(df):
        flash('Doctor not found.', 'danger')
        return redirect(url_for('admin.admin_doctors'))
    if request.method == 'POST':
        doctor_name = request.form.get('doctor_name', '').strip()
        hospital_name = request.form.get('hospital_name', '').strip()
        department = request.form.get('department', '').strip()

        if not doctor_name or not hospital_name or not department:
            flash('Doctor name, hospital, and department are required.', 'danger')
            doctor = df.iloc[index].to_dict()
            return render_template('admin_edit_doctor.html', doctor=doctor, index=index)

        for col in ['hospital_name','location','phone','hours','type','department','doctor_name','qualification','opd_schedule','diseases_treated','notes']:
            df.at[index, col] = request.form.get(col, '').strip()

        try:
            rating = float(request.form.get('rating', 0))
            df.at[index, 'rating'] = max(0, min(5, rating))
        except ValueError:
            df.at[index, 'rating'] = 0

        save_doctors(df)
        logger.info(f'Doctor updated: {doctor_name}')
        flash('Doctor updated!', 'success')
        return redirect(url_for('admin.admin_doctors'))
    doctor = df.iloc[index].to_dict()
    return render_template('admin_edit_doctor.html', doctor=doctor, index=index)


@admin_bp.route('/admin/doctors/delete/<int:index>')
@admin_required
def admin_delete_doctor(index):
    df = load_doctors()
    if 0 <= index < len(df):
        name = df.iloc[index]['doctor_name']
        df = df.drop(index).reset_index(drop=True)
        save_doctors(df)
        logger.info(f'Doctor deleted: {name}')
        flash(f'{name} removed!', 'success')
    else:
        flash('Doctor not found.', 'danger')
    return redirect(url_for('admin.admin_doctors'))


@admin_bp.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin_users.html', users=users)


@admin_bp.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()

        if not username or len(username) < 3:
            flash('Username must be at least 3 characters.', 'danger')
            return render_template('admin_edit_user.html', user=user)

        if not email:
            flash('Email is required.', 'danger')
            return render_template('admin_edit_user.html', user=user)

        # check for duplicate username/email (excluding current user)
        existing = User.query.filter(User.username == username, User.id != user_id).first()
        if existing:
            flash('Username already taken by another user.', 'danger')
            return render_template('admin_edit_user.html', user=user)

        existing = User.query.filter(User.email == email, User.id != user_id).first()
        if existing:
            flash('Email already used by another user.', 'danger')
            return render_template('admin_edit_user.html', user=user)

        user.username = username
        user.email = email
        user.phone = phone
        db.session.commit()
        logger.info(f'Admin updated user: {username}')
        flash(f'{username} updated!', 'success')
        return redirect(url_for('admin.admin_users'))
    return render_template('admin_edit_user.html', user=user)


@admin_bp.route('/admin/users/delete/<int:user_id>')
@admin_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    name = user.username
    Prediction.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    logger.info(f'Admin deleted user: {name}')
    flash(f'{name} deleted!', 'success')
    return redirect(url_for('admin.admin_users'))


@admin_bp.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    logger.info('Admin logged out')
    flash('Admin logged out.', 'info')
    return redirect(url_for('admin.admin_login'))
