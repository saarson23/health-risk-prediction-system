# ============================================================
# ml/predict.py - Prediction Module
# ============================================================
import joblib
import numpy as np
import shap


def load_model(model_path):
    """Load a saved model from .pkl file."""
    return joblib.load(model_path)


def predict_disease(model, features):
    """
    Make a prediction using the trained model.
    
    Args:
        model: trained sklearn model
        features: preprocessed numpy array (1 sample)
    
    Returns:
        dict with prediction, probability, and risk level
    """
    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0]

    # Determine risk level based on probability
    disease_prob = probability[1]
    if disease_prob >= 0.75:
        risk_level = 'Critical'
        risk_color = '#e74c3c'
    elif disease_prob >= 0.50:
        risk_level = 'High'
        risk_color = '#e67e22'
    elif disease_prob >= 0.30:
        risk_level = 'Medium'
        risk_color = '#f39c12'
    else:
        risk_level = 'Low'
        risk_color = '#2ecc71'

    return {
        'prediction': int(prediction),
        'prediction_label': 'Positive' if prediction == 1 else 'Negative',
        'probability': float(disease_prob),
        'probability_percent': f"{disease_prob * 100:.1f}%",
        'risk_level': risk_level,
        'risk_color': risk_color,
        'confidence': f"{max(probability) * 100:.1f}%"
    }


def get_risk_score(heart_result=None, diabetes_result=None):
    """
    Calculate overall health risk score from multiple predictions.
    
    Returns:
        dict with overall risk assessment
    """
    scores = []
    conditions = []

    if heart_result:
        scores.append(heart_result['probability'])
        if heart_result['prediction'] == 1:
            conditions.append('Heart Disease')

    if diabetes_result:
        scores.append(diabetes_result['probability'])
        if diabetes_result['prediction'] == 1:
            conditions.append('Diabetes')

    if not scores:
        return {'overall_risk': 0, 'risk_level': 'Unknown', 'conditions': []}

    overall = np.mean(scores)

    if overall >= 0.75:
        level = 'Critical'
    elif overall >= 0.50:
        level = 'High'
    elif overall >= 0.30:
        level = 'Medium'
    else:
        level = 'Low'

    return {
        'overall_risk': float(overall),
        'overall_percent': f"{overall * 100:.1f}%",
        'risk_level': level,
        'conditions_detected': conditions,
        'needs_alert': level in ['High', 'Critical']
    }


def explain_prediction(model, features, feature_names):
    """
    Generate SHAP-based explanation for a prediction.
    
    Args:
        model: trained model
        features: numpy array (1 sample)
        feature_names: list of feature names
    
    Returns:
        list of dicts explaining top contributing features
    """
    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(features)

        if isinstance(shap_values, list):
            sv = shap_values[1][0]
        else:
            sv = shap_values[0]

        # Create feature contribution list
        contributions = []
        for name, value in zip(feature_names, sv):
            contributions.append({
                'feature': name,
                'impact': float(value),
                'direction': 'increases' if value > 0 else 'decreases',
                'importance': float(abs(value))
            })

        # Sort by absolute importance
        contributions.sort(key=lambda x: x['importance'], reverse=True)

        return contributions[:5]  # Return top 5

    except Exception as e:
        print(f"SHAP explanation error: {e}")
        return []
