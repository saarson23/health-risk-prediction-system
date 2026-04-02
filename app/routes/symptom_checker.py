# ============================================================
# app/routes/symptom_checker.py - Symptom Chatbot Routes
# ============================================================
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.models.database import db, Prediction
import joblib
import numpy as np
import pandas as pd
import json
import os

symptom_bp = Blueprint('symptom', __name__)

# Load models and data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

symptom_model = joblib.load(os.path.join(BASE_DIR, 'models', 'symptom_disease_model.pkl'))
label_encoder = joblib.load(os.path.join(BASE_DIR, 'models', 'label_encoder_disease.pkl'))
severity_dict = joblib.load(os.path.join(BASE_DIR, 'models', 'severity_dict.pkl'))
symptom_list = pd.read_csv(os.path.join(BASE_DIR, 'models', 'symptom_list.csv'))['symptom'].tolist()

# Load descriptions and precautions
description_df = pd.read_csv(os.path.join(BASE_DIR, 'data', 'raw', 'symptom_Description.csv'))
precaution_df = pd.read_csv(os.path.join(BASE_DIR, 'data', 'raw', 'symptom_precaution.csv'))

# Create clean lookup dicts
description_dict = {}
for _, row in description_df.iterrows():
    description_dict[str(row['Disease']).strip()] = str(row['Description'])

precaution_dict = {}
for _, row in precaution_df.iterrows():
    disease = str(row['Disease']).strip()
    precs = []
    for i in range(1, 5):
        col = f'Precaution_{i}'
        if col in row and pd.notna(row[col]) and str(row[col]).strip():
            precs.append(str(row[col]).strip())
    precaution_dict[disease] = precs


def format_symptom_name(symptom):
    """Convert symptom_name to Symptom Name for display."""
    return symptom.replace('_', ' ').strip().title()


def get_symptom_categories():
    """Group symptoms into categories for easier browsing."""
    categories = {
        'General': ['fatigue', 'high_fever', 'mild_fever', 'lethargy', 'malaise',
                     'chills', 'shivering', 'sweating', 'dehydration', 'restlessness',
                     'weight_loss', 'weight_gain', 'obesity'],
        'Head & Neck': ['headache', 'dizziness', 'loss_of_balance', 'lack_of_concentration',
                         'blurred_and_distorted_vision', 'visual_disturbances',
                         'neck_pain', 'stiff_neck', 'puffy_face_and_eyes',
                         'enlarged_thyroid', 'slurred_speech'],
        'Stomach & Digestion': ['stomach_pain', 'acidity', 'vomiting', 'nausea',
                                 'diarrhoea', 'constipation', 'abdominal_pain',
                                 'loss_of_appetite', 'indigestion', 'belly_button_protrusion',
                                 'passage_of_gases', 'internal_itching',
                                 'pain_during_bowel_movements', 'bloody_stool'],
        'Skin': ['itching', 'skin_rash', 'nodal_skin_eruptions', 'pus_filled_pimples',
                  'blackheads', 'skin_peeling', 'blister', 'red_sore_around_nose',
                  'yellow_crust_ooze', 'dischromic _patches', 'bruising',
                  'yellowish_skin', 'red_spots_over_body'],
        'Chest & Breathing': ['breathlessness', 'chest_pain', 'cough',
                               'fast_heart_rate', 'rusty_sputum', 'phlegm',
                               'blood_in_sputum', 'mucoid_sputum'],
        'Muscles & Joints': ['muscle_pain', 'joint_pain', 'back_pain', 'knee_pain',
                              'hip_joint_pain', 'neck_pain', 'muscle_weakness',
                              'muscle_wasting', 'swelling_joints', 'stiff_neck',
                              'movement_stiffness', 'painful_walking', 'cramps'],
        'Urinary': ['burning_micturition', 'spotting_ urination', 'dark_urine',
                     'yellow_urine', 'bladder_discomfort', 'foul_smell_of urine',
                     'continuous_feel_of_urine', 'polyuria'],
        'Mental Health': ['anxiety', 'mood_swings', 'irritability', 'depression',
                           'altered_sensorium', 'coma'],
        'Throat & Mouth': ['throat_irritation', 'patches_in_throat', 'ulcers_on_tongue',
                            'loss_of_smell', 'continuous_sneezing', 'runny_nose',
                            'watering_from_eyes'],
        'Eyes': ['sunken_eyes', 'yellowing_of_eyes', 'blurred_and_distorted_vision',
                  'redness_of_eyes', 'watering_from_eyes'],
        'Other': []
    }

    # Add any symptoms not in categories to 'Other'
    categorized = set()
    for syms in categories.values():
        categorized.update(syms)
    for s in symptom_list:
        if s not in categorized:
            categories['Other'].append(s)

    # Only include categories that have matching symptoms in our dataset
    filtered = {}
    for cat, syms in categories.items():
        valid = [s for s in syms if s in symptom_list]
        if valid:
            filtered[cat] = valid

    return filtered


@symptom_bp.route('/symptom-checker')
@login_required
def symptom_checker():
    categories = get_symptom_categories()
    symptoms_display = {cat: [(s, format_symptom_name(s)) for s in syms]
                        for cat, syms in categories.items()}
    return render_template('symptom_checker.html',
                           categories=symptoms_display,
                           all_symptoms=[(s, format_symptom_name(s)) for s in symptom_list])


@symptom_bp.route('/api/predict-symptoms', methods=['POST'])
@login_required
def predict_symptoms():
    data = request.get_json()
    selected_symptoms = data.get('symptoms', [])

    if len(selected_symptoms) < 2:
        return jsonify({'error': 'Please select at least 2 symptoms'}), 400

    # Create feature vector with severity weights
    feature_vector = np.zeros(len(symptom_list))
    for symptom in selected_symptoms:
        if symptom in symptom_list:
            idx = symptom_list.index(symptom)
            weight = severity_dict.get(symptom, 1)
            feature_vector[idx] = weight

    # Predict
    feature_vector = feature_vector.reshape(1, -1)
    prediction = symptom_model.predict(feature_vector)[0]
    probabilities = symptom_model.predict_proba(feature_vector)[0]

    # Get top 3 diseases
    top3_idx = probabilities.argsort()[-3:][::-1]
    top3_diseases = label_encoder.inverse_transform(top3_idx)
    top3_proba = probabilities[top3_idx]

    # Primary prediction
    primary_disease = top3_diseases[0]
    primary_confidence = float(top3_proba[0])

    # Risk level
    if primary_confidence >= 0.75:
        risk_level = 'Critical'
        risk_color = '#e74c3c'
    elif primary_confidence >= 0.50:
        risk_level = 'High'
        risk_color = '#e67e22'
    elif primary_confidence >= 0.30:
        risk_level = 'Medium'
        risk_color = '#f39c12'
    else:
        risk_level = 'Low'
        risk_color = '#2ecc71'

    # Get description and precautions
    description = description_dict.get(primary_disease, 'No description available.')
    precautions = precaution_dict.get(primary_disease, ['Consult a doctor'])

    # Get related symptoms to ask about
    related = get_related_symptoms(selected_symptoms, primary_disease)

    # Save to database
    try:
        pred = Prediction(
            user_id=current_user.id,
            disease_type=primary_disease,
            prediction_result=1 if primary_confidence > 0.5 else 0,
            probability=primary_confidence,
            risk_level=risk_level,
            input_data=json.dumps(selected_symptoms),
            explanation=json.dumps({
                'top3': [{'disease': d, 'confidence': float(p)} for d, p in zip(top3_diseases, top3_proba)],
                'symptoms': selected_symptoms
            })
        )
        db.session.add(pred)
        db.session.commit()
    except Exception as e:
        print(f"DB save error: {e}")

    result = {
        'primary_disease': primary_disease,
        'confidence': f"{primary_confidence * 100:.1f}",
        'risk_level': risk_level,
        'risk_color': risk_color,
        'description': description,
        'precautions': precautions,
        'top3': [
            {'disease': d, 'confidence': f"{p * 100:.1f}"}
            for d, p in zip(top3_diseases, top3_proba)
        ],
        'symptoms_checked': [format_symptom_name(s) for s in selected_symptoms],
        'related_symptoms': related
    }

    return jsonify(result)


def get_related_symptoms(selected, predicted_disease):
    """Suggest related symptoms the user might also have."""
    # Find common symptoms for this disease from training data
    try:
        symptom_df = pd.read_csv(os.path.join(BASE_DIR, 'data', 'raw', 'dataset.csv'))
        disease_rows = symptom_df[symptom_df['Disease'].str.strip() == predicted_disease]

        common_symptoms = set()
        for _, row in disease_rows.iterrows():
            for col in symptom_df.columns[1:]:
                s = str(row[col]).strip()
                if s and s != 'nan':
                    common_symptoms.add(s)

        # Remove already selected symptoms
        remaining = common_symptoms - set(selected)
        return [(s, format_symptom_name(s)) for s in list(remaining)[:6]]
    except:
        return []


@symptom_bp.route('/api/search-symptoms')
@login_required
def search_symptoms():
    """Search symptoms by keyword for the chatbot autocomplete."""
    query = request.args.get('q', '').lower().strip()
    if len(query) < 2:
        return jsonify([])

    matches = []
    for s in symptom_list:
        display = format_symptom_name(s)
        if query in s.lower() or query in display.lower():
            matches.append({'value': s, 'label': display})
        if len(matches) >= 10:
            break

    return jsonify(matches)
