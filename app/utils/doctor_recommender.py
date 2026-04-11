import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCTORS_CSV = os.path.join(BASE_DIR, 'data', 'raw', 'kathmandu_doctors_with_names.csv')

DISEASE_DEPARTMENT_MAP = {
    'Heart attack': ['Cardiology', 'Cardiac Surgery', 'Emergency'],
    'Hypertension': ['Cardiology', 'Internal Medicine'],
    'Diabetes': ['Internal Medicine', 'General Medicine', 'Nephrology'],
    'Diabetes ': ['Internal Medicine', 'General Medicine', 'Nephrology'],
    'Hypoglycemia': ['Internal Medicine'],
    'Hyperthyroidism': ['Internal Medicine'],
    'Hypothyroidism': ['Internal Medicine'],
    'Hepatitis A': ['Gastroenterology', 'Hepatology', 'Internal Medicine'],
    'Hepatitis B': ['Gastroenterology', 'Hepatology', 'Internal Medicine'],
    'Hepatitis C': ['Gastroenterology', 'Hepatology', 'Internal Medicine'],
    'Hepatitis D': ['Gastroenterology', 'Hepatology', 'Internal Medicine'],
    'Hepatitis E': ['Gastroenterology', 'Hepatology', 'Internal Medicine'],
    'Alcoholic hepatitis': ['Gastroenterology', 'Hepatology'],
    'Chronic cholestasis': ['Gastroenterology', 'Hepatology'],
    'Jaundice': ['Gastroenterology', 'Internal Medicine'],
    'GERD': ['Gastroenterology', 'Internal Medicine'],
    'Peptic ulcer diseae': ['Gastroenterology', 'Internal Medicine'],
    'Gastroenteritis': ['Gastroenterology', 'Internal Medicine'],
    'Bronchial Asthma': ['Chest & Respiratory', 'Internal Medicine', 'Pediatrics'],
    'Pneumonia': ['Chest & Respiratory', 'Internal Medicine', 'Emergency'],
    'Tuberculosis': ['Chest & Respiratory', 'Internal Medicine'],
    'Common Cold': ['Internal Medicine', 'General Medicine'],
    'Malaria': ['Internal Medicine', 'Emergency'],
    'Dengue': ['Internal Medicine', 'Emergency'],
    'Typhoid': ['Internal Medicine', 'General Medicine'],
    'Chicken pox': ['Internal Medicine', 'Dermatology', 'Pediatrics'],
    'AIDS': ['Internal Medicine'],
    'Fungal infection': ['Dermatology', 'General Medicine'],
    'Allergy': ['Dermatology', 'Internal Medicine'],
    'Drug Reaction': ['Dermatology', 'Internal Medicine', 'Emergency'],
    'Acne': ['Dermatology'],
    'Psoriasis': ['Dermatology'],
    'Impetigo': ['Dermatology', 'Pediatrics'],
    'Arthritis': ['Orthopedics', 'Internal Medicine'],
    'Cervical spondylosis': ['Orthopedics', 'Orthopedics & Spine', 'Neurology'],
    'Osteoarthristis': ['Orthopedics', 'Physiotherapy'],
    'Migraine': ['Neurology', 'Internal Medicine'],
    'Paralysis (brain hemorrhage)': ['Neurology', 'Neurosurgery', 'Emergency'],
    'Urinary tract infection': ['Urology', 'Nephrology', 'Internal Medicine'],
    'Dimorphic hemmorhoids(piles)': ['General Surgery', 'Gastroenterology'],
    'Varicose veins': ['Cardiovascular & Thoracic Surgery', 'General Surgery'],
    'Depression': ['Psychiatry', 'Psychiatry & Psychology'],
    'default': ['Internal Medicine', 'General Medicine', 'Emergency']
}

def load_doctors():
    try:
        return pd.read_csv(DOCTORS_CSV)
    except:
        return pd.DataFrame()

def recommend_doctors(disease_name, max_results=5):
    doctors_df = load_doctors()
    if doctors_df.empty:
        return []
    departments = DISEASE_DEPARTMENT_MAP.get(disease_name.strip(), DISEASE_DEPARTMENT_MAP['default'])
    recommended = []
    for dept in departments:
        matches = doctors_df[doctors_df['department'].str.contains(dept, case=False, na=False)]
        for _, doc in matches.iterrows():
            if not any(r['doctor_name'] == doc['doctor_name'] and r['hospital'] == doc['hospital_name'] for r in recommended):
                recommended.append({
                    'doctor_name': doc['doctor_name'],
                    'department': doc['department'],
                    'hospital': doc['hospital_name'],
                    'location': doc['location'],
                    'phone': str(doc['phone']),
                    'qualification': doc['qualification'],
                    'opd_schedule': doc['opd_schedule'],
                    'diseases_treated': doc['diseases_treated'],
                    'rating': 0.0 if (str(doc['rating']) == 'nan' or doc['rating'] != doc['rating']) else float(doc['rating']),
                    'notes': str(doc.get('notes', ''))
                })
    disease_lower = disease_name.lower().strip()
    text_matches = doctors_df[doctors_df['diseases_treated'].str.contains(disease_lower.split()[0], case=False, na=False)]
    for _, doc in text_matches.iterrows():
        if not any(r['doctor_name'] == doc['doctor_name'] and r['hospital'] == doc['hospital_name'] for r in recommended):
            recommended.append({
                'doctor_name': doc['doctor_name'],
                'department': doc['department'],
                'hospital': doc['hospital_name'],
                'location': doc['location'],
                'phone': str(doc['phone']),
                'qualification': doc['qualification'],
                'opd_schedule': doc['opd_schedule'],
                'diseases_treated': doc['diseases_treated'],
                'rating': 0.0 if (str(doc['rating']) == 'nan' or doc['rating'] != doc['rating']) else float(doc['rating']),
                'notes': str(doc.get('notes', ''))
            })
    recommended.sort(key=lambda x: -x['rating'])
    return recommended[:max_results]
