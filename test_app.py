import pytest
from app import app, db, mail
from models.models import Student, Parent, GatePassRequest
from datetime import datetime
import json
from unittest.mock import patch

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with app.app_context():
            db.create_all()

            # Create parent
            parent = Parent(
                id=1,
                par_name="Test Parent",
                addressp="123 Main St",
                par_role="Father",
                email="parent@example.com",
                phone="9876543210",
                password_hash="pass123",
                role="parent"
            )

            # Create student
            student = Student(
                admno=45673,
                full_name="Test Student",
                study_year="2",
                department="CS",
                address="456 Hostel Lane",
                hostel_name="UG girls",
                hostel_room="101",
                phone_number="9999999999",
                email="student@example.com",
                password="pass123",
                parent_id=1,
                role="student"
            )

            db.session.add_all([parent, student])
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()

# --------------------------- CONTROLLERS --------------------------- #

def test_register_student(client):
    response = client.post("/regstud", data={
        "fname": "Another Student",
        "admno": "99999",
        "year": "1",
        "department": "ECE",
        "address": "New Hostel Lane",
        "hostel_name": "UG boys",
        "hostel_room": "202",
        "email": "another@student.com",
        "ph": "1231231231",
        "pwd": "123456"
    }, follow_redirects=True)
    assert response.status_code == 200

def test_login_student(client):
    response = client.post("/", data={
        "email": "student@example.com",
        "pwd": "pass123"
    }, follow_redirects=True)
    assert response.status_code == 200 or b"studentportal" in response.data

def test_logout(client):
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200

@patch("app.mail.send")
def test_gatepass_submission_email(mock_send, client):
    response = client.post('/gpassreq/45673', data={
        'pass_type': 'Homegoing',
        'reason': 'Test Email Trigger',
        'place': 'Chennai',
        'gdate': "2025-04-20",
        'going_time': '08:00',
        'rdate': "2025-04-22",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert mock_send.called
    assert mock_send.call_count == 1

# --------------------------- REST API RESOURCES --------------------------- #

def test_api_student_login(client):
    response = client.post('/api/login', data=json.dumps({
        "email": "student@example.com",
        "password": "pass123"
    }), content_type='application/json')
    assert response.status_code == 200
    assert response.json["message"] == "Login successful"

def test_api_invalid_login(client):
    response = client.post('/api/login', data=json.dumps({
        "email": "wrong@example.com",
        "password": "nope"
    }), content_type='application/json')
    assert response.status_code == 401
    assert response.json["message"] == "Invalid credentials"

def test_api_download_gatepass_pdf(client):
    with app.app_context():
        gpr = GatePassRequest(
            student_id=45673,
            parent_id=1,
            request_date=datetime.now(),
            request_time="10:00 AM",
            pass_type="Day Pass",
            reason="Test Reason",
            place="Test Place",
            going_date=datetime.now().date(),
            going_time="11:00 AM",
            return_date=datetime.now().date(),
            status="approved"
        )
        db.session.add(gpr)
        db.session.commit()

    response = client.get('/api/download-gatepass/45673')
    assert response.status_code == 200
    assert response.mimetype == "application/pdf"

# --------------------------- WARDEN ACTIONS --------------------------- #

def test_warden_approves_request(client):
    with app.app_context():
        gpr = GatePassRequest(
            student_id=45673,
            parent_id=1,
            request_date=datetime.now(),
            request_time="11:00 AM",
            pass_type="Day Pass",
            reason="Approve this",
            place="Home",
            going_date=datetime.now().date(),
            going_time="11:00 AM",
            return_date=datetime.now().date(),
            status="parent_approved"
        )
        db.session.add(gpr)
        db.session.commit()
        req_id = gpr.id

    response = client.post(f"/wardensanction/{req_id}", data={"approve": "Approve"}, follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        updated = db.session.get(GatePassRequest, req_id)
        assert updated.status == "approved"

def test_warden_rejects_request(client):
    with app.app_context():
        gpr = GatePassRequest(
            student_id=45673,
            parent_id=1,
            request_date=datetime.now(),
            request_time="12:00 PM",
            pass_type="Movement",
            reason="Reject this",
            place="Campus",
            going_date=datetime.now().date(),
            going_time="12:00 PM",
            return_date=datetime.now().date(),
            status="parent_approved"
        )
        db.session.add(gpr)
        db.session.commit()
        req_id = gpr.id

    response = client.post(f"/wardensanction/{req_id}", data={"reject": "Reject"}, follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        updated = db.session.get(GatePassRequest, req_id)
        assert updated.status == "rejected"



def test_student_gatepass_download(client):
    with app.app_context():
        gpr = GatePassRequest(
            student_id=45673,
            parent_id=1,
            request_date=datetime.now(),
            request_time="10:30 AM",
            pass_type="Day Pass",
            reason="Family Event",
            place="Thrissur",
            going_date=datetime.now().date(),
            going_time="11:00 AM",
            return_date=datetime.now().date(),
            status="approved"
        )
        db.session.add(gpr)
        db.session.commit()
        req_id = gpr.id

    response = client.get(f"/dwnloadgp/{req_id}", follow_redirects=True)
    assert response.status_code == 200
    assert b"Gate Pass" in response.data or b"Student Name" in response.data or b"Download" in response.data















