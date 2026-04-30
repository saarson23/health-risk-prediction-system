# app/utils/email_alerts.py
import logging
from flask_mail import Mail, Message
from flask import current_app

logger = logging.getLogger(__name__)
mail = Mail()

def init_mail(app):
    mail.init_app(app)

def send_health_alert(user_email, username, disease, risk_level, probability, precautions, doctors):
    try:
        risk_colors = {'Critical': '#e74c3c', 'High': '#e67e22', 'Medium': '#f39c12', 'Low': '#2ecc71'}
        color = risk_colors.get(risk_level, '#2ecc71')

        prec_html = ''
        for p in precautions:
            prec_html += f'<li style="padding:4px 0">{p}</li>'

        doc_html = ''
        for d in doctors[:3]:
            doc_html += f'<div style="padding:8px 12px;background:#f8f9fa;border-radius:8px;margin-bottom:6px;border-left:3px solid #00c9a7"><strong>{d["doctor_name"]}</strong><br><span style="font-size:0.85rem;color:#666">{d["department"]} | {d["hospital"]}</span><br><span style="font-size:0.85rem;color:#666">{d["phone"]}</span></div>'

        html_body = f'''
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#ffffff;border-radius:12px;overflow:hidden;border:1px solid #eee">
            <div style="background:#0b1120;padding:20px 30px;text-align:center">
                <h2 style="color:#00c9a7;margin:0">HealthPredict AI</h2>
                <p style="color:#7b8ca3;margin:5px 0 0;font-size:0.9rem">Health Risk Alert</p>
            </div>
            <div style="padding:30px">
                <p>Hi <strong>{username}</strong>,</p>
                <p>Our AI system has detected a potential health risk based on your recent symptom check:</p>
                <div style="background:#f8f9fa;border-radius:10px;padding:20px;text-align:center;margin:20px 0;border-left:4px solid {color}">
                    <h3 style="margin:0;color:#333">{disease}</h3>
                    <div style="margin-top:10px">
                        <span style="background:{color};color:white;padding:5px 15px;border-radius:20px;font-weight:600">{risk_level} Risk</span>
                        <span style="margin-left:10px;font-size:1.1rem;font-weight:600;color:{color}">{probability}%</span>
                    </div>
                </div>
                <h4 style="color:#333;margin-top:25px">Recommended Precautions:</h4>
                <ul style="color:#555;line-height:1.8">{prec_html}</ul>
                <h4 style="color:#333;margin-top:25px">Recommended Doctors:</h4>
                {doc_html}
                <div style="background:#fff3cd;border-radius:8px;padding:12px 16px;margin-top:25px;font-size:0.85rem;color:#856404">
                    <strong>Disclaimer:</strong> This is an AI-generated prediction for educational purposes only. Please consult a healthcare professional for proper diagnosis and treatment.
                </div>
            </div>
            <div style="background:#f8f9fa;padding:15px;text-align:center;font-size:0.8rem;color:#999">
                HealthPredict AI - BSc Computing Project by Aarson Subba
            </div>
        </div>'''

        msg = Message(
            subject=f'Health Alert: {disease} - {risk_level} Risk Detected',
            sender=current_app.config.get('MAIL_USERNAME'),
            recipients=[user_email],
            html=html_body
        )
        mail.send(msg)
        logger.info(f'Health alert email sent to {user_email} for {disease}')
        return True
    except Exception as e:
        logger.error(f'Failed to send email to {user_email}: {e}')
        return False
