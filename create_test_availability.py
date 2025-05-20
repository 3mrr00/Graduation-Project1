from app import app
from extensions import db
from models import User, Availability, Role
from datetime import datetime, time

def create_test_availabilities():
    # Find all professors
    professors = User.query.filter_by(role=Role.PROFESSOR).all()
    
    if not professors:
        print("No professors found in the database")
        return
    
    print(f"Found {len(professors)} professors")
    
    # For each professor, create availability for each day of the week
    for professor in professors:
        print(f"Processing professor: {professor.first_name} {professor.last_name} (ID: {professor.id})")
        
        # Check existing availabilities
        existing = Availability.query.filter_by(professor_id=professor.id).count()
        print(f"  Current availability count: {existing}")
        
        if existing > 0:
            print("  Professor already has availabilities - skipping")
            continue
        
        # Create availabilities for each weekday
        for day in range(5):  # Monday to Friday (0-4)
            avail = Availability(
                professor_id=professor.id,
                day_of_week=day,
                start_time=time(9, 0),  # 9:00 AM
                end_time=time(17, 0),   # 5:00 PM
                is_recurring=True
            )
            db.session.add(avail)
            print(f"  Added availability for day {day} (9:00 AM - 5:00 PM)")
    
    # Commit changes
    db.session.commit()
    print("All availabilities created successfully")

if __name__ == "__main__":
    with app.app_context():
        create_test_availabilities() 