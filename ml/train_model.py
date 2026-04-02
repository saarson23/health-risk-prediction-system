# ============================================================
# ml/train_model.py - Model Training Module
# ============================================================
import pandas as pd
import numpy as np
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import GridSearchCV, cross_val_score
from sklearn.metrics import f1_score


def get_models():
    """Return dictionary of all models to train."""
    return {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Decision Tree': DecisionTreeClassifier(random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'SVM': SVC(kernel='rbf', probability=True, random_state=42),
        'KNN': KNeighborsClassifier(n_neighbors=5),
        'XGBoost': XGBClassifier(n_estimators=100, random_state=42, eval_metric='logloss'),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42)
    }


def train_all_models(X_train, y_train, X_val, y_val):
    """
    Train all models and return results.
    
    Returns:
        dict of trained models and their scores
    """
    models = get_models()
    results = {}

    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_val)
        f1 = f1_score(y_val, y_pred, average='weighted')
        cv = cross_val_score(model, X_train, y_train, cv=5, scoring='f1_weighted')

        results[name] = {
            'model': model,
            'f1_score': f1,
            'cv_mean': cv.mean(),
            'cv_std': cv.std()
        }
        print(f"  {name}: F1={f1:.4f}, CV={cv.mean():.4f} (+/-{cv.std():.4f})")

    return results


def tune_random_forest(X_train, y_train):
    """Tune Random Forest with GridSearchCV."""
    params = {
        'n_estimators': [100, 200, 300],
        'max_depth': [5, 10, 15, None],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }
    grid = GridSearchCV(
        RandomForestClassifier(random_state=42),
        params, cv=5, scoring='f1_weighted', n_jobs=-1
    )
    grid.fit(X_train, y_train)
    print(f"  Best params: {grid.best_params_}")
    print(f"  Best score: {grid.best_score_:.4f}")
    return grid.best_estimator_


def tune_xgboost(X_train, y_train):
    """Tune XGBoost with GridSearchCV."""
    params = {
        'n_estimators': [100, 200, 300],
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.1, 0.2],
        'subsample': [0.8, 1.0]
    }
    grid = GridSearchCV(
        XGBClassifier(random_state=42, eval_metric='logloss'),
        params, cv=5, scoring='f1_weighted', n_jobs=-1
    )
    grid.fit(X_train, y_train)
    print(f"  Best params: {grid.best_params_}")
    print(f"  Best score: {grid.best_score_:.4f}")
    return grid.best_estimator_


def save_model(model, filepath):
    """Save trained model to file."""
    joblib.dump(model, filepath)
    print(f"  Model saved to {filepath}")


if __name__ == '__main__':
    print("Run this from notebooks/03_model_training.ipynb")
