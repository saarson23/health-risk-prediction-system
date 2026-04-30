from flask import Flask
from app.utils.email_alerts import mail
from flask_login import LoginManager
from config import Config
import logging
import os

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # setup logging
    log_dir = os.path.dirname(Config.LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    file_handler = logging.FileHandler(Config.LOG_FILE)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Health Risk Prediction System started')

    from app.models.database import db
    db.init_app(app)
    login_manager.init_app(app)
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
