from flask import Flask
from app.utils.email_alerts import mail
from flask_login import LoginManager
import os

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health_prediction.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    from app.models.database import db
    db.init_app(app)
    login_manager.init_app(app)
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'aarsonsubba67@gmail.com'
    app.config['MAIL_PASSWORD'] = 'ayfoxvhkixaxayhs'
    app.config['MAIL_DEFAULT_SENDER'] = 'aarsonsubba67@gmail.com'
    mail.init_app(app)

    login_manager.login_view = 'auth.login'

    from app.routes.auth import auth_bp
    from app.routes.predict import predict_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.admin import admin_bp
    from app.routes.symptom_checker import symptom_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(predict_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(symptom_bp)

    with app.app_context():
        db.create_all()

    return app
