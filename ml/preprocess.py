# ml/preprocess.py - Data Preprocessing Module

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder


def load_and_clean_heart_data(filepath):
    """Load and clean heart disease dataset."""
    df = pd.read_csv(filepath)
    df = df.drop_duplicates()
    return df


def load_and_clean_diabetes_data(filepath):
    """Load and clean diabetes dataset."""
    df = pd.read_csv(filepath)
    df = df.drop_duplicates()

    # Replace zeros with median for invalid columns
    zero_cols = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
    for col in zero_cols:
        median_val = df[col][df[col] != 0].median()
        df[col] = df[col].replace(0, median_val)

    return df


def add_heart_features(df):
    """Add engineered features for heart disease."""
    df = df.copy()
    df['age_group'] = pd.cut(df['age'], bins=[0, 40, 50, 60, 100],
                              labels=[0, 1, 2, 3]).astype(int)
    df['risk_score'] = (
        (df['trestbps'] > 140).astype(int) +
        (df['chol'] > 240).astype(int) +
        (df['thalach'] < 120).astype(int) +
        (df['oldpeak'] > 2).astype(int) +
        df['exang']
    )
    return df


def add_diabetes_features(df):
    """Add engineered features for diabetes."""
    df = df.copy()
    df['BMI_Category'] = pd.cut(df['BMI'], bins=[0, 18.5, 24.9, 29.9, 100],
                                 labels=[0, 1, 2, 3]).astype(int)
    df['Age_Group'] = pd.cut(df['Age'], bins=[0, 30, 45, 60, 100],
                              labels=[0, 1, 2, 3]).astype(int)
    df['Glucose_Level'] = pd.cut(df['Glucose'], bins=[0, 100, 125, 300],
                                  labels=[0, 1, 2]).astype(int)
    return df


def scale_features(X_train, X_test):
    """Scale features using StandardScaler."""
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    return X_train_scaled, X_test_scaled, scaler


def preprocess_user_input(user_data, scaler, feature_names):
    """
    Preprocess user input from the web form for prediction.
    
    Args:
        user_data: dict of user inputs from form
        scaler: fitted StandardScaler
        feature_names: list of feature names in correct order
    
    Returns:
        numpy array ready for model prediction
    """
    df = pd.DataFrame([user_data])

    # Ensure correct column order
    df = df[feature_names]

    # Scale
    scaled = scaler.transform(df.values)
    return scaled
