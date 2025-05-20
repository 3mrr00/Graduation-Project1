from app import app, db
from models import User, Appointment, Availability, Role
from datetime import datetime, timedelta, time
import os

def create_dummy_data():
    """Create dummy data for testing purposes"""
    # Clear existing data
    db.drop_all()
    db.create_all()
    
    print("Creating users...")
    # Create admin user
    admin = User(
        username="admin",
        email="admin@eelu.edu.eg",
        password="admin123",
        first_name="System",
        last_name="Administrator",
        role=Role.ADMIN
    )
    
    # Create professors
    prof1 = User(
        username="professor1",
        email="professor1@eelu.edu.eg",
        password="prof123",
        first_name="Ahmed",
        last_name="Mohamed",
        role=Role.PROFESSOR
    )
    
    prof2 = User(
        username="professor2",
        email="professor2@eelu.edu.eg",
        password="prof123",
        first_name="Sara",
        last_name="Ibrahim",
        role=Role.PROFESSOR
    )
    
    prof3 = User(
        username="professor3",
        email="prof3@university.edu",
        password="profpass3",
        first_name="Michael",
        last_name="Thompson",
        role=Role.PROFESSOR
    )
    
    # Create students
    student1 = User(
        username="student1",
        email="student1@eelu.edu.eg",
        password="student123",
        first_name="Omar",
        last_name="Ahmed",
        role=Role.STUDENT
    )
    
    student2 = User(
        username="student2",
        email="student2@eelu.edu.eg",
        password="student123",
        first_name="Nour",
        last_name="Hassan",
        role=Role.STUDENT
    )
    
    student3 = User(
        username="student3",
        email="student3@eelu.edu.eg",
        password="student123",
        first_name="Youssef",
        last_name="Ali",
        role=Role.STUDENT
    )
    
    # Add users to database
    db.session.add_all([admin, prof1, prof2, prof3, student1, student2, student3])
    db.session.commit()
    
    print("Creating professor availabilities...")
    # Create availabilities for professors
    # Professor 1 - Monday and Wednesday mornings
    avail1 = Availability(
        professor_id=prof1.id,
        day_of_week=0,  # Monday
        start_time=time(9, 0),
        end_time=time(12, 0),
        is_recurring=True
    )
    
    avail2 = Availability(
        professor_id=prof1.id,
        day_of_week=2,  # Wednesday
        start_time=time(9, 0),
        end_time=time(12, 0),
        is_recurring=True
    )
    
    # Professor 2 - Tuesday and Thursday afternoons
    avail3 = Availability(
        professor_id=prof2.id,
        day_of_week=1,  # Tuesday
        start_time=time(13, 0),
        end_time=time(16, 0),
        is_recurring=True
    )
    
    avail4 = Availability(
        professor_id=prof2.id,
        day_of_week=3,  # Thursday
        start_time=time(13, 0),
        end_time=time(16, 0),
        is_recurring=True
    )
    
    # Professor 3 - Friday all day
    avail5 = Availability(
        professor_id=prof3.id,
        day_of_week=4,  # Friday
        start_time=time(9, 0),
        end_time=time(17, 0),
        is_recurring=True
    )
    
    # Add availabilities to database
    db.session.add_all([avail1, avail2, avail3, avail4, avail5])
    db.session.commit()
    
    print("Creating appointments...")
    # Create some appointments
    
    # Current date to base appointments on
    now = datetime.now()
    
    # Start with tomorrow's date
    appt_date = now + timedelta(days=1)
    
    # Find the next Monday
    while appt_date.weekday() != 0:
        appt_date += timedelta(days=1)
    
    # Create an appointment for student1 with prof1 on Monday
    monday_appt = Appointment(
        student_id=student1.id,
        professor_id=prof1.id,
        start_time=datetime.combine(appt_date.date(), time(10, 0)),
        end_time=datetime.combine(appt_date.date(), time(10, 30)),
        subject="Project Guidance",
        description="Need help with my final project architecture",
        status="confirmed"
    )
    
    # Create an appointment for student2 with prof2 on Tuesday
    tuesday_appt = Appointment(
        student_id=student2.id,
        professor_id=prof2.id,
        start_time=datetime.combine((appt_date + timedelta(days=1)).date(), time(14, 0)),
        end_time=datetime.combine((appt_date + timedelta(days=1)).date(), time(14, 30)),
        subject="Exam Review",
        description="Would like to review my midterm exam results",
        status="pending"
    )
    
    # Create an appointment for student3 with prof3 on Friday
    friday_appt = Appointment(
        student_id=student3.id,
        professor_id=prof3.id,
        start_time=datetime.combine((appt_date + timedelta(days=4)).date(), time(11, 0)),
        end_time=datetime.combine((appt_date + timedelta(days=4)).date(), time(11, 30)),
        subject="Research Discussion",
        description="Want to discuss potential research opportunities",
        status="confirmed"
    )
    
    # Add appointments to database
    db.session.add_all([monday_appt, tuesday_appt, friday_appt])
    db.session.commit()
    
    print("Database initialized with dummy data!")

if __name__ == "__main__":
    with app.app_context():
        create_dummy_data() 