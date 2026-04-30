import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'h3alth_pr3dict_s3cret_k3y_2024'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///health_prediction.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # model paths
    HEART_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'heart_disease_model.pkl')
    DIABETES_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'diabetes_model.pkl')

    # admin credentials (password hashed with werkzeug for security)
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD_HASH = 'scrypt:32768:8:1$xuXsoz4mw1p2grxU$b0b1244246ab4294ff1e84a3381319afa76ad335b8652c9f3a303f21031e687d9c793c9fc7c450e2469c57faec36ee2bfa3c2ff8f4b18a606fdb9f00ee151d69'

    # email
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'aarsonsubba67@gmail.com'
    MAIL_PASSWORD = 'ayfoxvhkixaxayhs'
    MAIL_DEFAULT_SENDER = 'aarsonsubba67@gmail.com'

    # logging
    LOG_FILE = os.path.join(BASE_DIR, 'logs', 'app.log')
