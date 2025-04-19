from flask_sqlalchemy import SQLAlchemy
from datetime import date,datetime,timezone

db=SQLAlchemy()
class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    admno = db.Column(db.String(50), unique=True, nullable=False)
    study_year = db.Column(db.String(10), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    hostel_name = db.Column(db.String(50), nullable=False)
    hostel_room = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="student")
    parent_id=db.Column(db.Integer,db.ForeignKey("parents.id"),nullable=True)


class Parent(db.Model):
    __tablename__ = "parents"
    id = db.Column(db.Integer, primary_key=True)
    par_name = db.Column(db.String(100), nullable=False)
    addressp = db.Column(db.String(200), nullable=False)
    par_role = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="parent")


class Warden(db.Model):
    __tablename__ = "wardens"
    id = db.Column(db.Integer, primary_key=True)
    war_name = db.Column(db.String(100), nullable=False)
    war_address = db.Column(db.String(200), nullable=False)
    hos_name_war = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="warden")


class GatePassRequest(db.Model):
    __tablename__ = "gatepass_requests"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.admno"), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("parents.id"), nullable=False)
    request_date = db.Column(db.Date, nullable=False)
    request_time = db.Column(db.String(10), nullable=False)
    pass_type = db.Column(db.String(50), nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    place = db.Column(db.String(100), nullable=False)
    going_date = db.Column(db.Date, nullable=False)
    going_time = db.Column(db.String(10), nullable=False)
    return_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(30), default="pending")
