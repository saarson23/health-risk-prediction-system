# app/routes/dashboard.py - Dashboard Routes

from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.models.database import db, Prediction
from collections import Counter

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def home():
    return render_template('home.html')


@dashboard_bp.route('/dashboard')
@login_required
def index():
    # Get user's prediction history
    predictions = Prediction.query.filter_by(user_id=current_user.id)\
        .order_by(Prediction.created_at.desc()).all()

    # Calculate stats
    total_predictions = len(predictions)
    risk_counts = Counter(p.risk_level for p in predictions)
    disease_counts = Counter(p.disease_type for p in predictions)

    # Recent predictions (last 10)
    recent = predictions[:10]

    # Prepare chart data
    chart_data = {
        'risk_labels': list(risk_counts.keys()),
        'risk_values': list(risk_counts.values()),
        'disease_labels': list(disease_counts.keys()),
        'disease_values': list(disease_counts.values()),
        'timeline': [
            {'date': p.created_at.strftime('%Y-%m-%d'),
             'probability': p.probability,
             'disease': p.disease_type}
            for p in predictions[:20]
        ]
    }

    return render_template('dashboard.html',
                           predictions=recent,
                           total=total_predictions,
                           risk_counts=risk_counts,
                           chart_data=chart_data)


@dashboard_bp.route('/api/dashboard-data')
@login_required
def dashboard_data():
    """API endpoint for dashboard chart data."""
    predictions = Prediction.query.filter_by(user_id=current_user.id)\
        .order_by(Prediction.created_at.desc()).all()

    return jsonify({
        'total': len(predictions),
        'predictions': [
            {
                'id': p.id,
                'disease': p.disease_type,
                'result': p.prediction_result,
                'probability': p.probability,
                'risk': p.risk_level,
                'date': p.created_at.strftime('%Y-%m-%d %H:%M')
            }
            for p in predictions
        ]
    })


@dashboard_bp.route('/history')
@login_required
def history():
    """Full prediction history page."""
    predictions = Prediction.query.filter_by(user_id=current_user.id)\
        .order_by(Prediction.created_at.desc()).all()
    return render_template('history.html', predictions=predictions)
