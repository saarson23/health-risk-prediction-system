# ============================================================
# app/routes/predict.py - Prediction Routes
# ============================================================
from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from app.models.database import db, Prediction
import joblib
import numpy as np
import json
import os

predict_bp = Blueprint('predict', __name__)

# Load models (do this once when app starts)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
heart_model = joblib.load(os.path.join(BASE_DIR, 'models', 'heart_disease_model.pkl'))
diabetes_model = joblib.load(os.path.join(BASE_DIR, 'models', 'diabetes_model.pkl'))


def get_risk_level(probability):
    """Determine risk level from probability."""
    if probability >= 0.75:
        return 'Critical', '#e74c3c'
    elif probability >= 0.50:
        return 'High', '#e67e22'
    elif probability >= 0.30:
        return 'Medium', '#f39c12'
    else:
        return 'Low', '#2ecc71'


@predict_bp.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    if request.method == 'POST':
        disease_type = request.form.get('disease_type')

        try:
            if disease_type == 'heart':
                result = predict_heart(request.form)
            elif disease_type == 'diabetes':
                result = predict_diabetes(request.form)
            else:
                flash('Invalid disease type selected.', 'danger')
                return render_template('predict.html')

            # Save prediction to database
            prediction = Prediction(
                user_id=current_user.id,
                disease_type=disease_type,
                prediction_result=result['prediction'],
                probability=result['probability'],
                risk_level=result['risk_level'],
                input_data=json.dumps(result['input_data']),
                explanation=json.dumps(result.get('explanation', []))
            )
            db.session.add(prediction)
            db.session.commit()

            return render_template('results.html', result=result)

        except Exception as e:
            flash(f'Prediction error: {str(e)}', 'danger')
            return render_template('predict.html')

    return render_template('predict.html')


def predict_heart(form_data):
    """Process heart disease prediction from form data."""
    features = {
        'age': float(form_data.get('age', 0)),
        'sex': int(form_data.get('sex', 0)),
        'cp': int(form_data.get('cp', 0)),
        'trestbps': float(form_data.get('trestbps', 0)),
        'chol': float(form_data.get('chol', 0)),
        'fbs': int(form_data.get('fbs', 0)),
        'restecg': int(form_data.get('restecg', 0)),
        'thalach': float(form_data.get('thalach', 0)),
        'exang': int(form_data.get('exang', 0)),
        'oldpeak': float(form_data.get('oldpeak', 0)),
        'slope': int(form_data.get('slope', 0)),
        'ca': int(form_data.get('ca', 0)),
        'thal': int(form_data.get('thal', 0)),
    }

    # Add engineered features
    features['age_group'] = 0 if features['age'] <= 40 else 1 if features['age'] <= 50 else 2 if features['age'] <= 60 else 3
    features['risk_score'] = (
        (1 if features['trestbps'] > 140 else 0) +
        (1 if features['chol'] > 240 else 0) +
        (1 if features['thalach'] < 120 else 0) +
        (1 if features['oldpeak'] > 2 else 0) +
        features['exang']
    )

    # Create feature array in correct order
    feature_array = np.array(list(features.values())).reshape(1, -1)

    # Predict
    prediction = heart_model.predict(feature_array)[0]
    probability = heart_model.predict_proba(feature_array)[0][1]
    risk_level, risk_color = get_risk_level(probability)

    return {
        'disease_type': 'Heart Disease',
        'prediction': int(prediction),
        'prediction_label': 'Positive (At Risk)' if prediction == 1 else 'Negative (Low Risk)',
        'probability': float(probability),
        'probability_percent': f"{probability * 100:.1f}%",
        'risk_level': risk_level,
        'risk_color': risk_color,
        'input_data': features,
        'recommendations': get_heart_recommendations(risk_level)
    }


def predict_diabetes(form_data):
    """Process diabetes prediction from form data."""
    features = {
        'Pregnancies': int(form_data.get('pregnancies', 0)),
        'Glucose': float(form_data.get('glucose', 0)),
        'BloodPressure': float(form_data.get('blood_pressure', 0)),
        'SkinThickness': float(form_data.get('skin_thickness', 0)),
        'Insulin': float(form_data.get('insulin', 0)),
        'BMI': float(form_data.get('bmi', 0)),
        'DiabetesPedigreeFunction': float(form_data.get('dpf', 0)),
        'Age': int(form_data.get('age', 0)),
    }

    # Add engineered features
    bmi = features['BMI']
    features['BMI_Category'] = 0 if bmi <= 18.5 else 1 if bmi <= 24.9 else 2 if bmi <= 29.9 else 3

    age = features['Age']
    features['Age_Group'] = 0 if age <= 30 else 1 if age <= 45 else 2 if age <= 60 else 3

    glucose = features['Glucose']
    features['Glucose_Level'] = 0 if glucose <= 100 else 1 if glucose <= 125 else 2

    feature_array = np.array(list(features.values())).reshape(1, -1)

    prediction = diabetes_model.predict(feature_array)[0]
    probability = diabetes_model.predict_proba(feature_array)[0][1]
    risk_level, risk_color = get_risk_level(probability)

    return {
        'disease_type': 'Diabetes',
        'prediction': int(prediction),
        'prediction_label': 'Positive (At Risk)' if prediction == 1 else 'Negative (Low Risk)',
        'probability': float(probability),
        'probability_percent': f"{probability * 100:.1f}%",
        'risk_level': risk_level,
        'risk_color': risk_color,
        'input_data': features,
        'recommendations': get_diabetes_recommendations(risk_level)
    }


def get_heart_recommendations(risk_level):
    """Get doctor recommendations based on heart disease risk."""
    base = [
        {'specialist': 'Cardiologist', 'reason': 'Heart health specialist for detailed cardiac assessment'},
        {'specialist': 'General Physician', 'reason': 'Regular health check-up and monitoring'},
    ]
    if risk_level in ['High', 'Critical']:
        base.insert(0, {'specialist': 'Emergency Cardiologist', 'reason': 'Immediate cardiac evaluation recommended'})
        base.append({'specialist': 'Nutritionist', 'reason': 'Heart-healthy diet plan'})
    return base


def get_diabetes_recommendations(risk_level):
    """Get doctor recommendations based on diabetes risk."""
    base = [
        {'specialist': 'Endocrinologist', 'reason': 'Diabetes specialist for blood sugar management'},
        {'specialist': 'General Physician', 'reason': 'Regular health monitoring'},
    ]
    if risk_level in ['High', 'Critical']:
        base.insert(0, {'specialist': 'Diabetologist', 'reason': 'Immediate blood sugar assessment needed'})
        base.append({'specialist': 'Dietitian', 'reason': 'Diabetes-friendly nutrition plan'})
    return base
