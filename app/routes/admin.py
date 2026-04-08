from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from app.models.database import db, User, Prediction
import pandas as pd
import os

admin_bp = Blueprint('admin', __name__)

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCTORS_CSV = os.path.join(BASE_DIR, 'data', 'raw', 'kathmandu_doctors_with_names.csv')

def load_doctors():
    try:
        return pd.read_csv(DOCTORS_CSV)
    except:
        return pd.DataFrame(columns=['hospital_name','location','phone','hours','type','rating','department','doctor_name','qualification','opd_schedule','diseases_treated','notes'])

def save_doctors(df):
    df.to_csv(DOCTORS_CSV, index=False)

@admin_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('is_admin'):
        return redirect(url_for('admin.admin_dashboard'))
    if request.method == 'POST':
        if request.form.get('username') == ADMIN_USERNAME and request.form.get('password') == ADMIN_PASSWORD:
            session['is_admin'] = True
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Invalid admin credentials.', 'danger')
    return render_template('admin_login.html')

@admin_bp.route('/admin')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('admin.admin_login'))
    users = User.query.all()
    predictions = Prediction.query.order_by(Prediction.created_at.desc()).all()
    doctors_df = load_doctors()
    return render_template('admin.html', users=users, predictions=predictions, doctor_count=len(doctors_df), hospital_count=doctors_df['hospital_name'].nunique() if not doctors_df.empty else 0)

@admin_bp.route('/admin/doctors')
def admin_doctors():
    if not session.get('is_admin'):
        return redirect(url_for('admin.admin_login'))
    doctors = load_doctors().to_dict('records')
    return render_template('admin_doctors.html', doctors=doctors)

@admin_bp.route('/admin/doctors/add', methods=['GET', 'POST'])
def admin_add_doctor():
    if not session.get('is_admin'):
        return redirect(url_for('admin.admin_login'))
    if request.method == 'POST':
        df = load_doctors()
        new = {'hospital_name': request.form.get('hospital_name'), 'location': request.form.get('location'), 'phone': request.form.get('phone'), 'hours': request.form.get('hours'), 'type': request.form.get('type'), 'rating': float(request.form.get('rating', 0)), 'department': request.form.get('department'), 'doctor_name': request.form.get('doctor_name'), 'qualification': request.form.get('qualification'), 'opd_schedule': request.form.get('opd_schedule'), 'diseases_treated': request.form.get('diseases_treated'), 'notes': request.form.get('notes')}
        df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
        save_doctors(df)
        flash('Doctor added!', 'success')
        return redirect(url_for('admin.admin_doctors'))
    return render_template('admin_add_doctor.html')

@admin_bp.route('/admin/doctors/edit/<int:index>', methods=['GET', 'POST'])
def admin_edit_doctor(index):
    if not session.get('is_admin'):
        return redirect(url_for('admin.admin_login'))
    df = load_doctors()
    if index < 0 or index >= len(df):
        flash('Not found.', 'danger')
        return redirect(url_for('admin.admin_doctors'))
    if request.method == 'POST':
        for col in ['hospital_name','location','phone','hours','type','department','doctor_name','qualification','opd_schedule','diseases_treated','notes']:
            df.at[index, col] = request.form.get(col)
        df.at[index, 'rating'] = float(request.form.get('rating', 0))
        save_doctors(df)
        flash('Doctor updated!', 'success')
        return redirect(url_for('admin.admin_doctors'))
    doctor = df.iloc[index].to_dict()
    return render_template('admin_edit_doctor.html', doctor=doctor, index=index)

@admin_bp.route('/admin/doctors/delete/<int:index>')
def admin_delete_doctor(index):
    if not session.get('is_admin'):
        return redirect(url_for('admin.admin_login'))
    df = load_doctors()
    if 0 <= index < len(df):
        name = df.iloc[index]['doctor_name']
        df = df.drop(index).reset_index(drop=True)
        save_doctors(df)
        flash(f'{name} removed!', 'success')
    return redirect(url_for('admin.admin_doctors'))



@admin_bp.route('/admin/users')
def admin_users():
    if not session.get('is_admin'):
        return redirect(url_for('admin.admin_login'))
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@admin_bp.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
def admin_edit_user(user_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin.admin_login'))
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.phone = request.form.get('phone')
        db.session.commit()
        flash(f'{user.username} updated!', 'success')
        return redirect(url_for('admin.admin_users'))
    return render_template('admin_edit_user.html', user=user)

@admin_bp.route('/admin/users/delete/<int:user_id>')
def admin_delete_user(user_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin.admin_login'))
    user = User.query.get_or_404(user_id)
    name = user.username
    Prediction.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    flash(f'{name} deleted!', 'success')
    return redirect(url_for('admin.admin_users'))

@admin_bp.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    flash('Admin logged out.', 'info')
    return redirect(url_for('admin.admin_login'))
