import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'h3alth_pr3dict_s3cret_k3y_2024'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///health_prediction.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # model paths
    HEART_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'heart_disease_model.pkl')
    DIABETES_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'diabetes_model.pkl')

    # email
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'aarsonsubba67@gmail.com'
    MAIL_PASSWORD = 'ayfoxvhkixaxayhs'
    MAIL_DEFAULT_SENDER = 'aarsonsubba67@gmail.com'