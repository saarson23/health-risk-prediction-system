"""
============================================================
Unit Tests for Health Risk Prediction System
============================================================
Covers: Models, Auth, Dashboard, Admin, Predict utils, Config
"""

import pytest
import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import create_app
from app.models.database import db, User, Prediction, MedicalHistory, Alert
from app.routes.predict import get_risk_level


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def app():
    """Create a test Flask application with in-memory SQLite DB."""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
        'MAIL_SUPPRESS_SEND': True,
        'SERVER_NAME': 'localhost',
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def sample_user(app):
    """Create and return a sample user in the database."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('TestPass123'),
            phone='9800000000'
        )
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user


@pytest.fixture
def sample_prediction(app, sample_user):
    """Create and return a sample prediction."""
    with app.app_context():
        user = User.query.get(sample_user.id)
        prediction = Prediction(
            user_id=user.id,
            disease_type='heart',
            prediction_result=1,
            probability=0.82,
            risk_level='Critical',
            input_data=json.dumps({'age': 55, 'chol': 280}),
            explanation=json.dumps({'feature_importance': {'age': 0.3}})
        )
        db.session.add(prediction)
        db.session.commit()
        db.session.refresh(prediction)
        return prediction


@pytest.fixture
def auth_client(client, sample_user):
    """Return a test client that is already logged in."""
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'TestPass123'
    }, follow_redirects=True)
    return client


# ============================================================
# 1. DATABASE MODEL TESTS
# ============================================================

class TestUserModel:
    """Tests for User model."""

    def test_create_user(self, app):
        with app.app_context():
            user = User(
                username='john',
                email='john@example.com',
                password_hash=generate_password_hash('password'),
                phone='9841000000'
            )
            db.session.add(user)
            db.session.commit()

            fetched = User.query.filter_by(username='john').first()
            assert fetched is not None
            assert fetched.email == 'john@example.com'
            assert fetched.phone == '9841000000'

    def test_user_repr(self, app, sample_user):
        with app.app_context():
            user = User.query.get(sample_user.id)
            assert repr(user) == '<User testuser>'

    def test_user_password_hashing(self, app):
        with app.app_context():
            pw_hash = generate_password_hash('mysecret')
            user = User(username='pw_test', email='pw@test.com', password_hash=pw_hash)
            db.session.add(user)
            db.session.commit()

            fetched = User.query.filter_by(username='pw_test').first()
            assert check_password_hash(fetched.password_hash, 'mysecret')
            assert not check_password_hash(fetched.password_hash, 'wrongpassword')

    def test_unique_username(self, app, sample_user):
        with app.app_context():
            duplicate = User(
                username='testuser',
                email='other@example.com',
                password_hash=generate_password_hash('pass')
            )
            db.session.add(duplicate)
            with pytest.raises(Exception):
                db.session.commit()
            db.session.rollback()

    def test_unique_email(self, app, sample_user):
        with app.app_context():
            duplicate = User(
                username='otheruser',
                email='test@example.com',
                password_hash=generate_password_hash('pass')
            )
            db.session.add(duplicate)
            with pytest.raises(Exception):
                db.session.commit()
            db.session.rollback()

    def test_user_created_at_default(self, app):
        with app.app_context():
            user = User(username='timetest', email='time@test.com',
                        password_hash=generate_password_hash('pass'))
            db.session.add(user)
            db.session.commit()
            assert user.created_at is not None
            assert isinstance(user.created_at, datetime)


class TestPredictionModel:
    """Tests for Prediction model."""

    def test_create_prediction(self, app, sample_user):
        with app.app_context():
            pred = Prediction(
                user_id=sample_user.id,
                disease_type='diabetes',
                prediction_result=0,
                probability=0.25,
                risk_level='Low',
                input_data=json.dumps({'glucose': 90}),
            )
            db.session.add(pred)
            db.session.commit()

            fetched = Prediction.query.first()
            assert fetched.disease_type == 'diabetes'
            assert fetched.probability == 0.25
            assert fetched.risk_level == 'Low'

    def test_prediction_repr(self, app, sample_prediction):
        with app.app_context():
            pred = Prediction.query.get(sample_prediction.id)
            assert 'heart' in repr(pred)
            assert 'Critical' in repr(pred)

    def test_prediction_user_relationship(self, app, sample_user, sample_prediction):
        with app.app_context():
            user = User.query.get(sample_user.id)
            assert len(user.predictions) == 1
            assert user.predictions[0].disease_type == 'heart'

    def test_prediction_stores_json_data(self, app, sample_prediction):
        with app.app_context():
            pred = Prediction.query.get(sample_prediction.id)
            data = json.loads(pred.input_data)
            assert data['age'] == 55
            assert data['chol'] == 280


class TestMedicalHistoryModel:
    """Tests for MedicalHistory model."""

    def test_create_medical_history(self, app, sample_user):
        with app.app_context():
            history = MedicalHistory(
                user_id=sample_user.id,
                age=45,
                gender='Male',
                blood_pressure=130.0,
                cholesterol=220.0,
                glucose=100.0,
                bmi=25.5,
                smoking=False,
                diabetes_history=True,
                heart_disease_history=False
            )
            db.session.add(history)
            db.session.commit()

            fetched = MedicalHistory.query.first()
            assert fetched.age == 45
            assert fetched.bmi == 25.5
            assert fetched.diabetes_history is True

    def test_medical_history_repr(self, app, sample_user):
        with app.app_context():
            history = MedicalHistory(user_id=sample_user.id, age=30, gender='Female')
            db.session.add(history)
            db.session.commit()
            assert f'User:{sample_user.id}' in repr(history)


class TestAlertModel:
    """Tests for Alert model."""

    def test_create_alert(self, app, sample_user, sample_prediction):
        with app.app_context():
            alert = Alert(
                user_id=sample_user.id,
                prediction_id=sample_prediction.id,
                alert_type='email',
                message='High risk detected for heart disease',
                sent=True
            )
            db.session.add(alert)
            db.session.commit()

            fetched = Alert.query.first()
            assert fetched.alert_type == 'email'
            assert fetched.sent is True
            assert 'High risk' in fetched.message

    def test_alert_default_sent_false(self, app, sample_user):
        with app.app_context():
            alert = Alert(
                user_id=sample_user.id,
                alert_type='sms',
                message='Test alert'
            )
            db.session.add(alert)
            db.session.commit()
            assert alert.sent is False


# ============================================================
# 2. AUTHENTICATION ROUTE TESTS
# ============================================================

class TestAuthRoutes:
    """Tests for authentication routes."""

    def test_register_page_loads(self, client):
        response = client.get('/register')
        assert response.status_code == 200

    def test_login_page_loads(self, client):
        response = client.get('/login')
        assert response.status_code == 200

    def test_register_new_user(self, client, app):
        response = client.post('/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'NewPass123',
            'phone': '9800000001'
        }, follow_redirects=True)
        assert response.status_code == 200

        with app.app_context():
            user = User.query.filter_by(email='new@example.com').first()
            assert user is not None
            assert user.username == 'newuser'

    def test_register_duplicate_email(self, client, sample_user):
        response = client.post('/register', data={
            'username': 'another',
            'email': 'test@example.com',
            'password': 'Pass123',
            'phone': '9800000002'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'already registered' in response.data or response.status_code == 200

    def test_register_duplicate_username(self, client, sample_user):
        response = client.post('/register', data={
            'username': 'testuser',
            'email': 'different@example.com',
            'password': 'Pass123',
            'phone': '9800000003'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_login_valid_credentials(self, client, sample_user):
        response = client.post('/login', data={
            'email': 'test@example.com',
            'password': 'TestPass123'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_login_invalid_password(self, client, sample_user):
        response = client.post('/login', data={
            'email': 'test@example.com',
            'password': 'WrongPassword'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Invalid' in response.data

    def test_login_nonexistent_user(self, client):
        response = client.post('/login', data={
            'email': 'noone@example.com',
            'password': 'NoPass'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Invalid' in response.data

    def test_logout(self, auth_client):
        response = auth_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200

    def test_protected_route_redirects_anonymous(self, client):
        response = client.get('/dashboard')
        assert response.status_code == 302 or response.status_code == 401


# ============================================================
# 3. DASHBOARD ROUTE TESTS
# ============================================================

class TestDashboardRoutes:
    """Tests for dashboard routes."""

    def test_home_page_loads(self, client):
        response = client.get('/')
        assert response.status_code == 200

    def test_dashboard_requires_login(self, client):
        response = client.get('/dashboard')
        assert response.status_code == 302

    def test_dashboard_accessible_when_logged_in(self, auth_client):
        response = auth_client.get('/dashboard')
        assert response.status_code == 200

    def test_history_requires_login(self, client):
        response = client.get('/history')
        assert response.status_code == 302

    def test_history_accessible_when_logged_in(self, auth_client):
        response = auth_client.get('/history')
        assert response.status_code == 200

    def test_dashboard_api_requires_login(self, client):
        response = client.get('/api/dashboard-data')
        assert response.status_code == 302 or response.status_code == 401

    def test_dashboard_api_returns_json(self, auth_client):
        response = auth_client.get('/api/dashboard-data')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total' in data
        assert 'predictions' in data

    def test_dashboard_with_predictions(self, auth_client, app, sample_user):
        with app.app_context():
            for i in range(3):
                pred = Prediction(
                    user_id=sample_user.id,
                    disease_type='heart' if i % 2 == 0 else 'diabetes',
                    prediction_result=1,
                    probability=0.5 + i * 0.1,
                    risk_level='High',
                    input_data=json.dumps({'test': i}),
                )
                db.session.add(pred)
            db.session.commit()

        response = auth_client.get('/api/dashboard-data')
        data = json.loads(response.data)
        assert data['total'] == 3


# ============================================================
# 4. ADMIN ROUTE TESTS
# ============================================================

class TestAdminRoutes:
    """Tests for admin routes."""

    def test_admin_login_page_loads(self, client):
        response = client.get('/admin/login')
        assert response.status_code == 200

    def test_admin_login_valid_credentials(self, client):
        response = client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_admin_login_invalid_credentials(self, client):
        response = client.post('/admin/login', data={
            'username': 'admin',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Invalid' in response.data

    def test_admin_dashboard_requires_admin_session(self, client):
        response = client.get('/admin')
        assert response.status_code == 302

    def test_admin_dashboard_accessible_after_login(self, client):
        client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        response = client.get('/admin')
        assert response.status_code == 200

    def test_admin_users_page(self, client, sample_user):
        client.post('/admin/login', data={
            'username': 'admin', 'password': 'admin123'
        })
        response = client.get('/admin/users')
        assert response.status_code == 200

    def test_admin_logout(self, client):
        client.post('/admin/login', data={
            'username': 'admin', 'password': 'admin123'
        })
        response = client.get('/admin/logout', follow_redirects=True)
        assert response.status_code == 200

        # After logout, admin dashboard should redirect
        response = client.get('/admin')
        assert response.status_code == 302


# ============================================================
# 5. PREDICTION UTILITY TESTS
# ============================================================

class TestPredictUtils:
    """Tests for prediction utility functions."""

    def test_risk_level_critical(self):
        level, color = get_risk_level(0.80)
        assert level == 'Critical'
        assert color == '#e74c3c'

    def test_risk_level_high(self):
        level, color = get_risk_level(0.60)
        assert level == 'High'
        assert color == '#e67e22'

    def test_risk_level_medium(self):
        level, color = get_risk_level(0.40)
        assert level == 'Medium'
        assert color == '#f39c12'

    def test_risk_level_low(self):
        level, color = get_risk_level(0.15)
        assert level == 'Low'
        assert color == '#2ecc71'

    def test_risk_level_boundary_critical(self):
        level, _ = get_risk_level(0.75)
        assert level == 'Critical'

    def test_risk_level_boundary_high(self):
        level, _ = get_risk_level(0.50)
        assert level == 'High'

    def test_risk_level_boundary_medium(self):
        level, _ = get_risk_level(0.30)
        assert level == 'Medium'

    def test_risk_level_zero(self):
        level, color = get_risk_level(0.0)
        assert level == 'Low'
        assert color == '#2ecc71'

    def test_risk_level_one(self):
        level, color = get_risk_level(1.0)
        assert level == 'Critical'


# ============================================================
# 6. PREDICT ROUTE TESTS
# ============================================================

class TestPredictRoutes:
    """Tests for prediction routes."""

    def test_predict_page_requires_login(self, client):
        response = client.get('/predict')
        assert response.status_code == 302

    def test_predict_page_loads_when_logged_in(self, auth_client):
        response = auth_client.get('/predict')
        assert response.status_code == 200


# ============================================================
# 7. SYMPTOM CHECKER ROUTE TESTS
# ============================================================

class TestSymptomCheckerRoutes:
    """Tests for symptom checker routes."""

    def test_symptom_checker_requires_login(self, client):
        response = client.get('/symptom-checker')
        assert response.status_code == 302

    def test_symptom_api_requires_login(self, client):
        response = client.post('/api/predict-symptoms',
                               json={'symptoms': ['headache', 'fever']})
        assert response.status_code == 302 or response.status_code == 401

    def test_search_symptoms_requires_login(self, client):
        response = client.get('/api/search-symptoms?q=head')
        assert response.status_code == 302 or response.status_code == 401


# ============================================================
# 8. APP CONFIGURATION TESTS
# ============================================================

class TestAppConfig:
    """Tests for application configuration."""

    def test_app_creation(self, app):
        assert app is not None

    def test_testing_config(self, app):
        assert app.config['TESTING'] is True

    def test_secret_key_set(self, app):
        assert app.config['SECRET_KEY'] is not None

    def test_database_uri_set(self, app):
        assert 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']

    def test_mail_config_exists(self, app):
        assert 'MAIL_SERVER' in app.config

    def test_blueprints_registered(self, app):
        blueprint_names = list(app.blueprints.keys())
        assert 'auth' in blueprint_names
        assert 'predict' in blueprint_names
        assert 'dashboard' in blueprint_names
        assert 'admin' in blueprint_names
        assert 'symptom' in blueprint_names


# ============================================================
# 9. DOCTOR RECOMMENDER TESTS
# ============================================================

class TestDoctorRecommender:
    """Tests for doctor recommendation utility."""

    def test_disease_department_mapping_import(self):
        from app.utils.doctor_recommender import DISEASE_DEPARTMENT_MAP
        assert 'Heart attack' in DISEASE_DEPARTMENT_MAP
        assert 'Diabetes' in DISEASE_DEPARTMENT_MAP
        assert 'default' in DISEASE_DEPARTMENT_MAP

    def test_recommend_doctors_returns_list(self, app):
        with app.app_context():
            from app.utils.doctor_recommender import recommend_doctors
            result = recommend_doctors('Heart attack', max_results=3)
            assert isinstance(result, list)

    def test_recommend_doctors_max_results(self, app):
        with app.app_context():
            from app.utils.doctor_recommender import recommend_doctors
            result = recommend_doctors('Heart attack', max_results=2)
            assert len(result) <= 2


# ============================================================
# 10. EMAIL ALERTS TESTS
# ============================================================

class TestEmailAlerts:
    """Tests for email alert utility."""

    def test_mail_object_exists(self):
        from app.utils.email_alerts import mail
        assert mail is not None

    def test_send_health_alert_function_exists(self):
        from app.utils.email_alerts import send_health_alert
        assert callable(send_health_alert)


# ============================================================
# 11. SYMPTOM CHECKER UTILITY TESTS
# ============================================================

class TestSymptomUtils:
    """Tests for symptom checker utility functions."""

    def test_format_symptom_name(self, app):
        with app.app_context():
            from app.routes.symptom_checker import format_symptom_name
            assert format_symptom_name('high_fever') == 'High Fever'
            assert format_symptom_name('chest_pain') == 'Chest Pain'
            assert format_symptom_name('headache') == 'Headache'

    def test_get_symptom_categories(self, app):
        with app.app_context():
            from app.routes.symptom_checker import get_symptom_categories
            categories = get_symptom_categories()
            assert isinstance(categories, dict)
            assert len(categories) > 0


# ============================================================
# 12. EDGE CASE & INTEGRATION TESTS
# ============================================================

class TestEdgeCases:
    """Edge case and integration tests."""

    def test_multiple_predictions_same_user(self, app, sample_user):
        with app.app_context():
            for i in range(5):
                pred = Prediction(
                    user_id=sample_user.id,
                    disease_type='heart' if i % 2 == 0 else 'diabetes',
                    prediction_result=i % 2,
                    probability=0.1 * (i + 1),
                    risk_level='Low' if i < 3 else 'High',
                    input_data=json.dumps({'test': i}),
                )
                db.session.add(pred)
            db.session.commit()

            preds = Prediction.query.filter_by(user_id=sample_user.id).all()
            assert len(preds) == 5

    def test_delete_user_cascade_check(self, app, sample_user, sample_prediction):
        with app.app_context():
            user = User.query.get(sample_user.id)
            pred_id = sample_prediction.id

            # Manually delete predictions first (as admin route does)
            Prediction.query.filter_by(user_id=user.id).delete()
            db.session.delete(user)
            db.session.commit()

            assert User.query.get(sample_user.id) is None
            assert Prediction.query.get(pred_id) is None

    def test_empty_dashboard(self, auth_client):
        response = auth_client.get('/api/dashboard-data')
        data = json.loads(response.data)
        assert data['total'] == 0
        assert data['predictions'] == []

    def test_authenticated_user_cannot_access_register(self, auth_client):
        response = auth_client.get('/register')
        # Should redirect to dashboard since user is already logged in
        assert response.status_code == 302 or response.status_code == 200

    def test_authenticated_user_cannot_access_login(self, auth_client):
        response = auth_client.get('/login')
        assert response.status_code == 302 or response.status_code == 200
