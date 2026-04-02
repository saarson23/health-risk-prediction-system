# ============================================================
# config.py - Application Configuration
# ============================================================
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'health_prediction.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Model paths
    HEART_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'heart_disease_model.pkl')
    DIABETES_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'diabetes_model.pkl')

    # Email settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
