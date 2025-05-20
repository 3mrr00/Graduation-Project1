from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from extensions import db
from models import Appointment, Availability
from forms import AvailabilityForm
from datetime import datetime, time, timedelta
from functools import wraps

professor = Blueprint('professor', __name__)

def professor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_professor():
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@professor.route('/dashboard')
@login_required
@professor_required
def dashboard():
    # Get pending appointments for approval
    pending_appointments = Appointment.query.filter_by(
        professor_id=current_user.id,
        status='pending'
    ).order_by(Appointment.start_time).all()
    
    # Get today's appointments
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    todays_appointments = Appointment.query.filter(
        Appointment.professor_id == current_user.id,
        Appointment.start_time >= today_start,
        Appointment.start_time < today_end
    ).order_by(Appointment.start_time).all()
    
    # Get upcoming confirmed appointments
    upcoming_appointments = Appointment.query.filter_by(
        professor_id=current_user.id,
        status='confirmed'
    ).filter(
        Appointment.start_time > datetime.utcnow()
    ).order_by(Appointment.start_time).limit(5).all()
    
    # Get all appointments for stats
    all_appointments = Appointment.query.filter_by(professor_id=current_user.id).all()
    
    # Get completed appointments today
    completed_today = Appointment.query.filter(
        Appointment.professor_id == current_user.id,
        Appointment.status == 'completed',
        Appointment.start_time >= today_start,
        Appointment.start_time < today_end
    ).count()
    
    # Get total unique students
    total_students = db.session.query(Appointment.student_id).filter(
        Appointment.professor_id == current_user.id
    ).distinct().count()
    
    # Get cancelled appointments
    cancelled_appointments = Appointment.query.filter_by(
        professor_id=current_user.id,
        status='cancelled'
    ).count()
    
    # Get completed appointments
    completed_appointments = Appointment.query.filter_by(
        professor_id=current_user.id,
        status='completed'
    ).count()
    
    return render_template('professor/dashboard.html', 
                          title='Professor Dashboard',
                          datetime=datetime,
                          pending_appointments=pending_appointments,
                          upcoming_appointments=upcoming_appointments,
                          appointments=all_appointments,
                          completed_today=completed_today,
                          total_students=total_students,
                          cancelled_appointments=cancelled_appointments,
                          completed_appointments=completed_appointments,
                          todays_appointments=todays_appointments)

@professor.route('/appointments')
@login_required
@professor_required
def appointments():
    # Get pending appointments for badge
    pending_appointments = Appointment.query.filter_by(
        professor_id=current_user.id,
        status='pending'
    ).order_by(Appointment.start_time).all()
    
    # Get all appointments
    appointments = Appointment.query.filter_by(professor_id=current_user.id).order_by(Appointment.start_time.desc()).all()
    
    # Define status colors
    status_colors = {
        'pending': 'warning',
        'confirmed': 'info',
        'completed': 'success',
        'cancelled': 'danger',
        'scheduled': 'dark'
    }
    
    # Pass all necessary variables to template
    return render_template('professor/appointments.html', 
                          title='My Appointments',
                          datetime=datetime,
                          appointments=appointments,
                          pending_appointments=pending_appointments,
                          status_colors=status_colors)

@professor.route('/availabilities')
@login_required
@professor_required
def availabilities():
    availabilities = Availability.query.filter_by(professor_id=current_user.id).all()
    return render_template('professor/availabilities.html', 
                          title='My Availabilities',
                          availabilities=availabilities)

@professor.route('/add_availability', methods=['GET', 'POST'])
@login_required
@professor_required
def add_availability():
    form = AvailabilityForm()
    
    if form.validate_on_submit():
        # Parse time strings
        try:
            start_time_parts = form.start_time.data.split(':')
            end_time_parts = form.end_time.data.split(':')
            start_time_obj = time(int(start_time_parts[0]), int(start_time_parts[1]))
            end_time_obj = time(int(end_time_parts[0]), int(end_time_parts[1]))
        except (ValueError, IndexError):
            flash('Invalid time format. Please use HH:MM format.', 'danger')
            return render_template('professor/add_availability.html', title='Add Availability', form=form)
        
        # Create availability
        availability = Availability(
            professor_id=current_user.id,
            day_of_week=form.day_of_week.data,
            start_time=start_time_obj,
            end_time=end_time_obj,
            is_recurring=form.is_recurring.data,
            specific_date=form.specific_date.data if not form.is_recurring.data else None
        )
        db.session.add(availability)
        db.session.commit()
        
        flash('Availability added successfully!', 'success')
        return redirect(url_for('professor.availabilities'))
        
    return render_template('professor/add_availability.html', 
                          title='Add Availability',
                          form=form)

@professor.route('/delete_availability/<int:availability_id>', methods=['POST'])
@login_required
@professor_required
def delete_availability(availability_id):
    availability = Availability.query.get_or_404(availability_id)
    
    # Check if this availability belongs to the current user
    if availability.professor_id != current_user.id:
        flash('You do not have permission to delete this availability.', 'danger')
        return redirect(url_for('professor.availabilities'))
    
    db.session.delete(availability)
    db.session.commit()
    
    flash('Availability deleted successfully.', 'success')
    return redirect(url_for('professor.availabilities'))

@professor.route('/update_appointment_status/<int:appointment_id>', methods=['POST'])
@login_required
@professor_required
def update_appointment_status(appointment_id):
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        status = request.form.get('status')
        
        # Debug logging
        print(f"Updating appointment {appointment_id}: Status requested = {status}")
        print(f"Form data: {request.form}")
        print(f"Request data: {request.data}")
        
        # Check if this appointment belongs to the current user
        if appointment.professor_id != current_user.id:
            return jsonify({
                'success': False,
                'message': 'You do not have permission to update this appointment.'
            }), 403
        
        # Validate status
        if not status:
            return jsonify({
                'success': False,
                'message': 'No status provided.'
            }), 400
            
        if status not in ['confirmed', 'cancelled', 'completed', 'pending']:
            return jsonify({
                'success': False,
                'message': f'Invalid status: {status}. Must be one of: confirmed, cancelled, completed, pending'
            }), 400
        
        # Update the appointment status
        old_status = appointment.status
        appointment.status = status
        db.session.commit()
        
        print(f"Appointment {appointment_id} status updated: {old_status} -> {status}")
        
        return jsonify({
            'success': True,
            'message': f'Appointment status changed to {status}.'
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error updating appointment {appointment_id}: {str(e)}")
        
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@professor.route('/test_appointment_status/<int:appointment_id>/<status>')
@login_required
@professor_required
def test_appointment_status(appointment_id, status):
    """Test route to quickly change appointment status"""
    try:
        if status not in ['pending', 'confirmed', 'cancelled', 'completed']:
            flash(f'Invalid status: {status}', 'danger')
            return redirect(url_for('professor.appointments'))
            
        appointment = Appointment.query.get_or_404(appointment_id)
        
        # Check if this appointment belongs to the current user
        if appointment.professor_id != current_user.id:
            flash('You do not have permission to update this appointment.', 'danger')
            return redirect(url_for('professor.appointments'))
        
        # Update status
        old_status = appointment.status
        appointment.status = status
        db.session.commit()
        
        flash(f'Appointment status changed from {old_status} to {status} for testing', 'info')
        return redirect(url_for('professor.appointments'))
        
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('professor.appointments'))

@professor.route('/ai_assistant')
@login_required
@professor_required
def ai_assistant():
    try:
        # Check if current_user is properly authenticated
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('auth.login'))
            
        if not current_user.is_professor():
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
            
        # Get appointment data for analysis
        try:
            all_appointments = Appointment.query.filter_by(professor_id=current_user.id).all()
            print(f"Found {len(all_appointments)} appointments for professor {current_user.id}")
        except Exception as e:
            print(f"Error fetching appointments: {str(e)}")
            all_appointments = []
        
        # Get appointment days breakdown
        appointment_days = {}
        try:
            for day in range(7):  # 0=Monday, 6=Sunday
                count = Appointment.query.filter(
                    Appointment.professor_id == current_user.id,
                    Appointment.start_time.is_not(None)
                ).filter(
                    db.func.strftime('%w', Appointment.start_time) == str(day)
                ).count()
                appointment_days[day] = count
            print(f"Appointment days breakdown: {appointment_days}")
        except Exception as e:
            print(f"Error calculating appointment days: {str(e)}")
            appointment_days = {i: 0 for i in range(7)}
        
        # Get appointment time breakdown
        appointment_times = {}
        try:
            for hour in range(9, 18):  # 9 AM to 6 PM
                count = Appointment.query.filter(
                    Appointment.professor_id == current_user.id,
                    Appointment.start_time.is_not(None)
                ).filter(
                    db.func.strftime('%H', Appointment.start_time) == str(hour).zfill(2)
                ).count()
                appointment_times[hour] = count
            print(f"Appointment times breakdown: {appointment_times}")
        except Exception as e:
            print(f"Error calculating appointment times: {str(e)}")
            appointment_times = {i: 0 for i in range(9, 18)}
        
        # Generate AI insights
        try:
            ai_insights = generate_ai_insights_for_professor(current_user.id)
            print(f"Generated AI insights: {ai_insights}")
        except Exception as e:
            print(f"Error generating AI insights: {str(e)}")
            ai_insights = {
                "popular_days": ["Tuesday", "Thursday"],
                "popular_times": ["10:00 AM - 12:00 PM", "2:00 PM - 4:00 PM"],
                "avg_appointment_duration": 30,
                "common_subjects": ["Project Discussion", "Exam Preparation", "Career Advice"],
                "student_satisfaction": 95
            }
        
        # Recommended availability
        recommended_availability = [
            {"day": "Tuesday", "start_time": "10:00 AM", "end_time": "12:00 PM", "reason": "High student demand"},
            {"day": "Thursday", "start_time": "2:00 PM", "end_time": "4:00 PM", "reason": "Compatible with student schedules"}
        ]
        
        return render_template('professor/ai_assistant.html',
                            title='AI Appointment Assistant',
                            appointment_days=appointment_days,
                            appointment_times=appointment_times,
                            ai_insights=ai_insights,
                            recommended_availability=recommended_availability,
                            all_appointments=all_appointments)
    except Exception as e:
        print(f"Critical error in ai_assistant route: {str(e)}")
        flash('An error occurred while loading the AI assistant. Please try again later.', 'danger')
        return redirect(url_for('professor.dashboard'))

# Function to generate AI insights for professors (placeholder)
def generate_ai_insights_for_professor(professor_id):
    # In a real implementation, this would analyze:
    # 1. Patterns in appointment requests
    # 2. Student preferences
    # 3. Optimal scheduling for professor productivity
    # 4. Potential conflicts or scheduling issues
    
    # For now, return placeholder insights
    return {
        "popular_days": ["Tuesday", "Thursday"],
        "popular_times": ["10:00 AM - 12:00 PM", "2:00 PM - 4:00 PM"],
        "avg_appointment_duration": 30,
        "common_subjects": ["Project Discussion", "Exam Preparation", "Career Advice"],
        "student_satisfaction": 95
    }

@professor.route('/update_ai_preference', methods=['POST'])
@login_required
@professor_required
def update_ai_preference():
    try:
        data = request.json
        enabled = data.get('enabled', False)
        
        # In a real application, this would update the professor's preferences in database
        
        return jsonify({"success": True, "message": "AI preference updated successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}) 