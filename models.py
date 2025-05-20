from datetime import datetime
from extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Role:
    STUDENT = 'student'
    PROFESSOR = 'professor'
    ADMIN = 'admin'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Profile fields
    profile_picture = db.Column(db.String(255))  # Path to profile picture
    phone = db.Column(db.String(20))
    department = db.Column(db.String(100))
    
    # Student fields
    student_id = db.Column(db.String(20))
    year = db.Column(db.String(10))
    
    # Professor fields
    faculty_id = db.Column(db.String(20))
    office = db.Column(db.String(100))
    
    # Relationships
    appointments_as_student = db.relationship('Appointment', foreign_keys='Appointment.student_id', backref='student', lazy=True)
    appointments_as_professor = db.relationship('Appointment', foreign_keys='Appointment.professor_id', backref='professor', lazy=True)
    availabilities = db.relationship('Availability', backref='professor', lazy=True)

    def __init__(self, username, email, password, first_name, last_name, role):
        self.username = username
        self.email = email
        self.set_password(password)
        self.first_name = first_name
        self.last_name = last_name
        self.role = role

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def is_student(self):
        return self.role == Role.STUDENT
        
    def is_professor(self):
        return self.role == Role.PROFESSOR
        
    def is_admin(self):
        return self.role == Role.ADMIN
        
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
        
    @property
    def appointments(self):
        """Property to get appointments for students"""
        if self.is_student():
            return self.appointments_as_student
        return []
        
    @property
    def professor_appointments(self):
        """Property to get appointments for professors"""
        if self.is_professor():
            return self.appointments_as_professor
        return []

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"Appointment('{self.subject}', '{self.start_time}', '{self.status}')"

class Availability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    professor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_recurring = db.Column(db.Boolean, default=True)
    specific_date = db.Column(db.Date)  # For non-recurring availabilities
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        day = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][self.day_of_week]
        return f"Availability('{day}', '{self.start_time}' - '{self.end_time}')" 