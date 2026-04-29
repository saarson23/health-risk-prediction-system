# app/models/database.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta

db = SQLAlchemy()

def nepal_now():
    return datetime.utcnow() + timedelta(hours=5, minutes=45)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=nepal_now)

    predictions = db.relationship('Prediction', backref='user', lazy=True)
    medical_history = db.relationship('MedicalHistory', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'


class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    disease_type = db.Column(db.String(50), nullable=False)
    prediction_result = db.Column(db.Integer, nullable=False)
    probability = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)
    input_data = db.Column(db.Text)
    explanation = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=nepal_now)

    def __repr__(self):
        return f'<Prediction {self.disease_type}: {self.risk_level}>'


class MedicalHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    blood_pressure = db.Column(db.Float)
    cholesterol = db.Column(db.Float)
    glucose = db.Column(db.Float)
    bmi = db.Column(db.Float)
    smoking = db.Column(db.Boolean, default=False)
    diabetes_history = db.Column(db.Boolean, default=False)
    heart_disease_history = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=nepal_now)

    def __repr__(self):
        return f'<MedicalHistory User:{self.user_id}>'


class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    prediction_id = db.Column(db.Integer, db.ForeignKey('prediction.id'))
    alert_type = db.Column(db.String(20))
    message = db.Column(db.Text)
    sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=nepal_now)

    def __repr__(self):
        return f'<Alert {self.alert_type}: {self.sent}>'