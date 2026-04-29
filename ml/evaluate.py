# ml/evaluate.py - Model Evaluation Module
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                              f1_score, confusion_matrix, classification_report,
                              roc_curve, roc_auc_score)


def evaluate_model(model, X_test, y_test, model_name="Model"):
    """
    Complete evaluation of a model on test data.
    
    Returns:
        dict with all evaluation metrics
    """
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    metrics = {
        'model_name': model_name,
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, average='weighted'),
        'recall': recall_score(y_test, y_pred, average='weighted'),
        'f1_score': f1_score(y_test, y_pred, average='weighted'),
        'roc_auc': roc_auc_score(y_test, y_proba)
    }

    return metrics


def plot_confusion_matrix(y_test, y_pred, labels, title="Confusion Matrix"):
    """Plot a confusion matrix heatmap."""
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=labels, yticklabels=labels)
    plt.title(title, fontsize=14, fontweight='bold')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.tight_layout()
    plt.show()


def plot_roc_curve(y_test, y_proba, title="ROC Curve"):
    """Plot ROC curve."""
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    auc_score = roc_auc_score(y_test, y_proba)

    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='#2ecc71', linewidth=2,
             label=f'ROC Curve (AUC = {auc_score:.4f})')
    plt.plot([0, 1], [0, 1], 'k--', linewidth=1)
    plt.fill_between(fpr, tpr, alpha=0.1, color='#2ecc71')
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.show()


def compare_models(results_dict):
    """
    Compare multiple models visually.
    
    Args:
        results_dict: dict of {model_name: metrics_dict}
    """
    import pandas as pd
    df = pd.DataFrame(results_dict).T
    df = df.sort_values('f1_score', ascending=False)

    fig, ax = plt.subplots(figsize=(12, 6))
    df[['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc']].plot(
        kind='bar', ax=ax, colormap='Set2', edgecolor='black'
    )
    plt.title('Model Comparison', fontsize=16, fontweight='bold')
    plt.ylabel('Score')
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, 1.05)
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.show()

    return df
