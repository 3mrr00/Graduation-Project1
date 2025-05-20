from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required # type: ignore
from extensions import db
from models import User, Appointment, Availability, Role
from forms import AppointmentForm
from datetime import datetime, timedelta, time
from functools import wraps
from ai.appointment_recommender import recommend_appointment

student = Blueprint('student', __name__)

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_student():
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@student.route('/dashboard')
@login_required
@student_required
def dashboard():
    # Get upcoming appointments for the student
    upcoming_appointments = Appointment.query.filter(
        Appointment.student_id == current_user.id,
        Appointment.status.in_(['confirmed', 'pending']),
        Appointment.start_time > datetime.now()
    ).order_by(Appointment.start_time).limit(5).all()
    # Get professors
    professors = User.query.filter_by(role=Role.PROFESSOR).all()
    
    # Get AI recommended times (placeholder for now)
    ai_recommendations = generate_ai_recommendations(current_user.id)
    
    return render_template('student/dashboard.html', 
                          title='Student Dashboard',
                          upcoming_appointments=upcoming_appointments,
                          professors=professors,
                          ai_recommendations=ai_recommendations)

# Function to generate AI recommendations (placeholder)
def generate_ai_recommendations(student_id):
    """
    Generate AI-powered appointment recommendations for a student.
    This function gathers all available slots for all professors,
    computes the required features for the AI model, and returns
    the top 3 recommended slots and optimal days.
    """
    student = User.query.get(student_id)
    professors = User.query.filter_by(role=Role.PROFESSOR).all()
    recommendations = []

    preferred_days = getattr(student, 'preferred_days', [])  # e.g., ['Monday', 'Wednesday']
    preferred_times = getattr(student, 'preferred_times', [])  # e.g., ['09:00', '10:30']

    for professor in professors:
        available_slots = Availability.query.filter_by(professor_id=professor.id).all()
        for slot in available_slots:
            slot_day = getattr(slot, 'day', None)
            slot_time = getattr(slot, 'time', None)

            day_overlap = 1 if slot_day in preferred_days else 0
            slot_match = 1 if slot_time in preferred_times else 0
            student_count = Appointment.query.filter_by(
                professor_id=professor.id,
                start_time=slot_time
            ).count()
            post_lec_count = 0  # Placeholder, adjust as needed

            features = {
                "day_overlap": day_overlap,
                "slot_match": slot_match,
                "student_count": student_count,
                "post_lec_count": post_lec_count
            }

            try:
                score = recommend_appointment(features)
            except Exception:
                score = 0

            recommendations.append({
                "professor": professor.get_full_name() if hasattr(professor, 'get_full_name') else professor.username,
                "slot_day": slot_day,
                "slot_time": slot_time,
                "score": score
            })

    best = sorted(recommendations, key=lambda x: x['score'], reverse=True)[:3]
    optimal_days = list({rec['slot_day'] for rec in best if rec['slot_day']})
    optimal_times = list({rec['slot_time'] for rec in best if rec['slot_time']})

    return {
        "recommendations": best,
        "optimal_days": optimal_days,
        "optimal_times": optimal_times
    }
        
@student.route('/appointments')
@login_required
@student_required
def appointments():
    appointments = Appointment.query.filter_by(student_id=current_user.id).order_by(Appointment.start_time.desc()).all()
    return render_template('student/appointments.html', 
                          title='My Appointments',
                          appointments=appointments,
                          now=datetime.now())

@student.route('/book_appointment', methods=['GET', 'POST'])
@login_required
@student_required
def book_appointment():
    form = AppointmentForm()
    
    # Populate the professor dropdown
    professors = User.query.filter_by(role=Role.PROFESSOR).all()
    form.professor.choices = [(p.id, p.get_full_name()) for p in professors]
    
    # Generate a list of fixed time slots directly in the route
    available_time_slots = []
    for hour in range(9, 17):  # 9 AM to 5 PM
        for minute in [0, 30]:  # Every 30 minutes
            time_str = f"{hour:02d}:{minute:02d}"
            time_display = datetime.strptime(time_str, "%H:%M").strftime('%I:%M %p')
            available_time_slots.append((time_str, time_display))
    
    # Set the time slot choices directly
    form.time_slot.choices = [("", "Select Time")] + available_time_slots
    
    if request.method == 'GET':
        # Pre-select a professor if provided in URL
        professor_id = request.args.get('professor_id')
        if professor_id and professor_id.isdigit():
            form.professor.data = int(professor_id)
    
    if form.validate_on_submit():
        try:
            # Get the date from the form
            appointment_date = form.date.data
            
            # Get the time from the time_slot field (format: HH:MM)
            time_parts = form.time_slot.data.split(':')
            hour = int(time_parts[0])
            minute = int(time_parts[1])
            
            # Create datetime objects for start and end time
            start_time = datetime.combine(appointment_date, time(hour, minute))
            end_time = start_time + timedelta(minutes=30)  # 30-minute appointments
            
            # Check if this time slot is already booked
            existing_appointment = Appointment.query.filter(
                Appointment.professor_id == form.professor.data,
                Appointment.start_time == start_time,
                Appointment.status != 'cancelled'
            ).first()
            
            if existing_appointment:
                flash('This time slot is already booked. Please select another time.', 'danger')
                return render_template('student/book_appointment.html', 
                                      title='Book Appointment',
                                      form=form,
                                      available_time_slots=available_time_slots)
            
            # Create appointment
            appointment = Appointment(
                student_id=current_user.id,
                professor_id=form.professor.data,
                start_time=start_time,
                end_time=end_time,
                subject=form.subject.data,
                description=form.description.data,
                status='pending'
            )
            db.session.add(appointment)
            db.session.commit()
            
            flash('Your appointment has been requested! You will receive confirmation soon.', 'success')
            return redirect(url_for('student.appointments'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error booking appointment: {str(e)}', 'danger')
            print(f"Error booking appointment: {str(e)}")
        
    return render_template('student/book_appointment.html', 
                          title='Book Appointment',
                          form=form,
                          available_time_slots=available_time_slots)

@student.route('/cancel_appointment/<int:appointment_id>', methods=['POST'])
@login_required
@student_required
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Check if this appointment belongs to the current user
    if appointment.student_id != current_user.id:
        flash('You do not have permission to cancel this appointment.', 'danger')
        return redirect(url_for('student.appointments'))
    
    # Check if the appointment can be cancelled (e.g., not too close to start time)
    appointment.status = 'cancelled'
    db.session.commit()
    
    flash('Your appointment has been cancelled.', 'success')
    return redirect(url_for('student.appointments'))

@student.route('/get_available_slots/<int:professor_id>/<string:date>')
@login_required
@student_required
def get_available_slots(professor_id, date):
    # Parse the date string
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    
    # Get the day of week (0 = Monday, 6 = Sunday)
    day_of_week = date_obj.weekday()
    
    # Log the request details
    print(f"Fetching slots for professor {professor_id} on date {date} (day of week: {day_of_week})")
    
    # Get the professor's availabilities for this day
    availabilities = Availability.query.filter_by(
        professor_id=professor_id,
        day_of_week=day_of_week,
        is_recurring=True
    ).all()
    
    # Add any specific date availabilities
    specific_availabilities = Availability.query.filter_by(
        professor_id=professor_id,
        specific_date=date_obj,
        is_recurring=False
    ).all()
    
    availabilities.extend(specific_availabilities)
    
    # Log the availabilities found
    print(f"Found {len(availabilities)} availability records for professor {professor_id} on {date}")
    for avail in availabilities:
        print(f"  - {avail.day_of_week} from {avail.start_time} to {avail.end_time}")
    
    # Create fixed time slots (fallback) - always provide some slots regardless of DB
    fixed_slots = []
    start_hour = 9  # 9 AM
    end_hour = 17   # 5 PM
    
    for hour in range(start_hour, end_hour):
        for minute in [0, 30]:
            slot_time = time(hour, minute)
            fixed_slots.append({
                'value': f"{hour:02d}:{minute:02d}",
                'text': datetime.strptime(f"{hour:02d}:{minute:02d}", "%H:%M").strftime('%I:%M %p')
            })
    
    # If no availabilities found in the database, return the fixed slots
    if not availabilities:
        print(f"No availabilities found in DB for professor {professor_id} on {date}, returning fixed slots")
        return jsonify(fixed_slots)
    
    # Get existing appointments for this professor and date
    existing_appointments = Appointment.query.filter(
        Appointment.professor_id == professor_id,
        Appointment.start_time >= datetime.combine(date_obj, datetime.min.time()),
        Appointment.start_time < datetime.combine(date_obj + timedelta(days=1), datetime.min.time()),
        Appointment.status != 'cancelled'
    ).all()
    
    # Calculate available time slots from the database
    available_slots = []
    
    # Calculate actual available slots based on availabilities and existing appointments
    for availability in availabilities:
        start_time = availability.start_time
        end_time = availability.end_time
        
        # Create 30-minute slots
        current_time = start_time
        while current_time < end_time:
            slot_end = (datetime.combine(date_obj, current_time) + timedelta(minutes=30)).time()
            if slot_end <= end_time:
                # Check if this slot is already booked
                is_booked = False
                for appointment in existing_appointments:
                    if appointment.start_time.time() <= current_time < appointment.end_time.time():
                        is_booked = True
                        break
                
                if not is_booked:
                    available_slots.append({
                        'value': current_time.strftime('%H:%M'),
                        'text': current_time.strftime('%I:%M %p')
                    })
                
            current_time = slot_end
    
    # If no available slots found from the database availability records, return fixed slots
    if not available_slots:
        print(f"No available slots calculated for professor {professor_id} on {date}, returning fixed slots")
        return jsonify(fixed_slots)
    
    print(f"Returning {len(available_slots)} available slots from database")
    return jsonify(available_slots)

@student.route('/ai/recommendations', methods=['GET'])
@login_required
@student_required
def get_ai_recommendations():
    """API endpoint to get personalized AI recommendations for appointments"""
    recommendations = generate_ai_recommendations(current_user.id)
    return jsonify(recommendations)

@student.route('/ai/auto-rebook/<int:appointment_id>', methods=['POST'])
@login_required
@student_required
def auto_rebook_appointment(appointment_id):
    """
    When an appointment is canceled, this endpoint finds the nearest available
    slot with the same professor and automatically books it
    """
    # Get the canceled appointment
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Verify that this appointment belongs to the current user
    if appointment.student_id != current_user.id:
        flash('You do not have permission to rebook this appointment.', 'danger')
        return redirect(url_for('student.appointments'))
    
    # Find the nearest available slot with the same professor
    # In a real implementation, this would use more sophisticated algorithms
    professor_id = appointment.professor_id
    
    # Get all availabilities for this professor that are in the future
    availabilities = Availability.query.filter_by(
        professor_id=professor_id
    ).filter(
        Availability.start_time > datetime.utcnow()
    ).order_by(Availability.start_time).all()
    
    # Find slots that aren't already booked
    available_slot = None
    for availability in availabilities:
        # Check if this slot is already booked
        existing_appointment = Appointment.query.filter_by(
            professor_id=professor_id,
            start_time=availability.start_time
        ).first()
        
        if not existing_appointment:
            available_slot = availability
            break
    
    if available_slot:
        # Create a new appointment
        new_appointment = Appointment(
            student_id=current_user.id,
            professor_id=professor_id,
            start_time=available_slot.start_time,
            end_time=available_slot.end_time,
            subject=appointment.subject,
            description=f"Auto-rebooked after cancellation of appointment #{appointment_id}",
            status='pending'
        )
        
        try:
            db.session.add(new_appointment)
            db.session.commit()
            flash('Your appointment was automatically rebooked for the next available slot.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error rebooking appointment: {str(e)}', 'danger')
    else:
        flash('No available slots found with this professor. Please book manually.', 'warning')
    
    return redirect(url_for('student.appointments'))

@student.route('/ai/toggle-assistance', methods=['POST'])
@login_required
@student_required
def toggle_ai_assistance():
    """Toggle AI assistance features on/off"""
    # In a real implementation, this would update a user preference in the database
    enabled = request.form.get('enabled', 'false') == 'true'
    
    # Placeholder for updating user preferences
    # current_user.ai_assistance_enabled = enabled
    # db.session.commit()
    
    return jsonify({"success": True, "ai_enabled": enabled})

@student.route('/ai-assistant')
@login_required
@student_required
def ai_assistant():
    """Dedicated page for AI appointment assistant"""
    # Get professors
    professors = User.query.filter_by(role=Role.PROFESSOR).all()
    
    # Get upcoming appointments for context
    upcoming_appointments = Appointment.query.filter_by(
        student_id=current_user.id,
        status='confirmed'
    ).filter(
        Appointment.start_time > datetime.utcnow()
    ).order_by(Appointment.start_time).all()
    
    # Get AI recommendations
    ai_recommendations = generate_ai_recommendations(current_user.id)
    
    # Get previous appointment patterns
    previous_appointments = Appointment.query.filter_by(
        student_id=current_user.id
    ).filter(
        Appointment.start_time < datetime.utcnow()
    ).order_by(Appointment.start_time.desc()).all()
    
    # Extract pattern data
    appointment_days = {}
    appointment_times = {}
    
    for appointment in previous_appointments:
        # Count days of week
        day_name = appointment.start_time.strftime('%A')
        appointment_days[day_name] = appointment_days.get(day_name, 0) + 1
        
        # Count hour ranges
        hour = appointment.start_time.hour
        hour_range = f"{hour}:00 - {hour+1}:00"
        appointment_times[hour_range] = appointment_times.get(hour_range, 0) + 1
    
    # Sort by frequency
    appointment_days = dict(sorted(appointment_days.items(), key=lambda x: x[1], reverse=True))
    appointment_times = dict(sorted(appointment_times.items(), key=lambda x: x[1], reverse=True))
    
    return render_template('student/ai_assistant.html',
                          title='AI Appointment Assistant',
                          professors=professors,
                          upcoming_appointments=upcoming_appointments,
                          previous_appointments=previous_appointments,
                          ai_recommendations=ai_recommendations,
                          appointment_days=appointment_days,
                          appointment_times=appointment_times) 

@student.route('/appointment/<int:appointment_id>')
@login_required
@student_required
def appointment_detail(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    return render_template('student/appointment_detail.html', appointment=appointment)