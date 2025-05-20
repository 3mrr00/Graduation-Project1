from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from extensions import db
from models import User, Appointment, Role
from datetime import datetime, timedelta
from functools import wraps
from sqlalchemy import func, and_
from forms import AdminUserForm, EditUserForm

admin = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Get total users
    total_users = User.query.count()
    
    # Get total professors
    total_professors = User.query.filter_by(role=Role.PROFESSOR).count()
    
    # Get active appointments (pending or confirmed)
    active_appointments = Appointment.query.filter(
        Appointment.status.in_(['pending', 'confirmed'])
    ).count()
    
    # Get all users for the users table
    users = User.query.order_by(User.created_at.desc()).all()
    
    # Get recent appointments
    recent_appointments = Appointment.query.order_by(
        Appointment.created_at.desc()
    ).limit(5).all()
    
    return render_template('admin/dashboard.html',
                          total_users=total_users,
                          total_professors=total_professors,
                          active_appointments=active_appointments,
                          users=users,
                          recent_appointments=recent_appointments)

@admin.route('/users')
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('admin/users.html', 
                          title='User Management',
                          users=users)

@admin.route('/add_user', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    form = AdminUserForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role=form.role.data,
            is_active=form.is_active.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'User {user.username} has been created successfully.', 'success')
        return redirect(url_for('admin.users'))
    return render_template('admin/add_user.html', 
                          title='Add New User',
                          form=form)

@admin.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = EditUserForm(original_username=user.username, original_email=user.email)
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.role = form.role.data
        user.is_active = form.is_active.data
        db.session.commit()
        flash(f'User {user.username} has been updated successfully.', 'success')
        return redirect(url_for('admin.user_detail', user_id=user.id))
    
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.role.data = user.role
        form.is_active.data = user.is_active
    
    return render_template('admin/edit_user.html', 
                          title=f'Edit User: {user.username}',
                          form=form,
                          user=user)

@admin.route('/appointments')
@login_required
@admin_required
def appointments():
    appointments = Appointment.query.order_by(Appointment.start_time.desc()).all()
    # Get list of students and professors for the appointment form
    students = User.query.filter_by(role='student', is_active=True).all()
    professors = User.query.filter_by(role='professor', is_active=True).all()
    
    return render_template('admin/appointments.html', 
                          title='All Appointments',
                          appointments=appointments,
                          students=students,
                          professors=professors)

@admin.route('/user/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_student():
        appointments = Appointment.query.filter_by(student_id=user_id).all()
    elif user.is_professor():
        appointments = Appointment.query.filter_by(professor_id=user_id).all()
    else:
        appointments = []
    
    return render_template('admin/user_detail.html', 
                          title=f'User: {user.username}',
                          user=user,
                          appointments=appointments)

@admin.route('/toggle_user_status/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent deactivating your own admin account
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'danger')
        return redirect(url_for('admin.users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} has been {status}.', 'success')
    return redirect(url_for('admin.users'))

@admin.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting your own admin account
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.users'))
    
    # Store username for flash message
    username = user.username
    
    # Delete associated appointments
    if user.is_student():
        appointments = Appointment.query.filter_by(student_id=user_id).all()
        for appointment in appointments:
            db.session.delete(appointment)
    elif user.is_professor():
        appointments = Appointment.query.filter_by(professor_id=user_id).all()
        for appointment in appointments:
            db.session.delete(appointment)
    
    # Delete the user
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {username} has been deleted successfully.', 'success')
    return redirect(url_for('admin.users'))

@admin.route('/approve_appointment/<int:appointment_id>', methods=['POST'])
@login_required
@admin_required
def approve_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = 'confirmed'
    db.session.commit()
    
    flash(f'Appointment has been approved.', 'success')
    return redirect(url_for('admin.appointments'))

@admin.route('/reject_appointment/<int:appointment_id>', methods=['POST'])
@login_required
@admin_required
def reject_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = 'cancelled'
    db.session.commit()
    
    flash(f'Appointment has been rejected.', 'danger')
    return redirect(url_for('admin.appointments'))

@admin.route('/update_appointment_status/<int:appointment_id>', methods=['POST'])
@login_required
@admin_required
def update_appointment_status(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    new_status = request.form.get('status')
    
    if new_status in ['approved', 'rejected', 'completed', 'scheduled']:
        appointment.status = new_status
        db.session.commit()
        
        status_messages = {
            'approved': 'Appointment has been approved.',
            'rejected': 'Appointment has been rejected.',
            'completed': 'Appointment has been marked as completed.',
            'scheduled': 'Appointment has been scheduled.'
        }
        
        status_categories = {
            'approved': 'success',
            'rejected': 'danger',
            'completed': 'info',
            'scheduled': 'success'
        }
        
        flash(status_messages.get(new_status), status_categories.get(new_status))
    else:
        flash('Invalid status value.', 'danger')
        
    return redirect(url_for('admin.appointments'))

@admin.route('/api/approve_appointment', methods=['POST'])
@login_required
@admin_required
def api_approve_appointment():
    data = request.get_json()
    appointment_id = data.get('appointment_id')
    
    if not appointment_id:
        return jsonify({'success': False, 'message': 'Missing appointment ID'}), 400
        
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = 'confirmed'
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Appointment approved successfully'})

@admin.route('/api/reject_appointment', methods=['POST'])
@login_required
@admin_required
def api_reject_appointment():
    data = request.get_json()
    appointment_id = data.get('appointment_id')
    
    if not appointment_id:
        return jsonify({'success': False, 'message': 'Missing appointment ID'}), 400
        
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = 'cancelled'
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Appointment rejected successfully'})

@admin.route('/api/appointment/<int:appointment_id>', methods=['GET'])
@login_required
@admin_required
def api_appointment_details(appointment_id):
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        
        # Format appointment data
        appointment_data = {
            'id': appointment.id,
            'subject': appointment.subject,
            'date': appointment.start_time.strftime('%B %d, %Y'),
            'time': f"{appointment.start_time.strftime('%I:%M %p')} - {appointment.end_time.strftime('%I:%M %p')}",
            'status': appointment.status,
            'student': {
                'id': appointment.student.id,
                'name': appointment.student.get_full_name(),
                'email': appointment.student.email
            },
            'professor': {
                'id': appointment.professor.id,
                'name': appointment.professor.get_full_name(),
                'email': appointment.professor.email
            }
        }
        
        return jsonify({
            'success': True,
            'appointment': appointment_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@admin.route('/add_appointment', methods=['POST'])
@login_required
@admin_required
def add_appointment():
    # Get form data
    student_id = request.form.get('student_id')
    professor_id = request.form.get('professor_id')
    subject = request.form.get('subject')
    date_str = request.form.get('date')
    start_time_str = request.form.get('start_time')
    end_time_str = request.form.get('end_time')
    
    # Validate inputs
    if not all([student_id, professor_id, subject, date_str, start_time_str, end_time_str]):
        flash('All required fields must be filled', 'danger')
        return redirect(url_for('admin.appointments'))
    
    try:
        # Parse date and times
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        start_time_obj = datetime.strptime(start_time_str, '%H:%M').time()
        end_time_obj = datetime.strptime(end_time_str, '%H:%M').time()
        
        # Create datetime objects for start and end times
        start_datetime = datetime.combine(date_obj, start_time_obj)
        end_datetime = datetime.combine(date_obj, end_time_obj)
        
        # Validate time range
        if end_datetime <= start_datetime:
            flash('End time must be after start time', 'danger')
            return redirect(url_for('admin.appointments'))
        
        # Create appointment
        appointment = Appointment(
            student_id=student_id,
            professor_id=professor_id,
            subject=subject,
            start_time=start_datetime,
            end_time=end_datetime,
            status='scheduled'  # Default status
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        flash('Appointment added successfully', 'success')
    except Exception as e:
        flash(f'Error creating appointment: {str(e)}', 'danger')
    
    return redirect(url_for('admin.appointments'))

@admin.route('/reports')
@login_required
@admin_required
def reports():
    # Usage statistics for the past month
    one_month_ago = datetime.utcnow() - timedelta(days=30)
    
    # Get total appointments
    total_appointments = Appointment.query.count()
    
    # Get completed appointments
    completed_appointments = Appointment.query.filter_by(status='completed').count()
    
    # Get active users
    active_users = User.query.filter_by(is_active=True).count()
    
    # Calculate success rate (completed appointments / total appointments)
    success_rate = round((completed_appointments / total_appointments * 100) if total_appointments > 0 else 0, 1)
    
    # Get appointment status counts
    status_counts = {
        'pending': Appointment.query.filter_by(status='pending').count(),
        'approved': Appointment.query.filter_by(status='approved').count(),
        'completed': completed_appointments,
        'cancelled': Appointment.query.filter_by(status='cancelled').count()
    }
    
    # Get trend data for the last 30 days
    trend_data = []
    trend_labels = []
    for i in range(30, -1, -1):
        date = datetime.utcnow() - timedelta(days=i)
        count = Appointment.query.filter(
            func.date(Appointment.created_at) == date.date()
        ).count()
        trend_data.append(count)
        trend_labels.append(date.strftime('%Y-%m-%d'))
    
    # Get top professors by appointment count
    top_professors = db.session.query(
        User,
        func.count(Appointment.id).label('appointment_count')
    ).join(
        Appointment, User.id == Appointment.professor_id
    ).filter(
        User.role == Role.PROFESSOR
    ).group_by(
        User.id
    ).order_by(
        func.count(Appointment.id).desc()
    ).limit(5).all()

    # Format professor data for template
    top_professors_data = [{
        'name': prof[0].get_full_name(),
        'department': 'Faculty',  # You can add department field to User model if needed
        'appointments': prof[1],
        'rating': 'N/A'  # Since we don't have ratings yet
    } for prof in top_professors]
    
    # Get recent activities
    recent_activities = []
    
    # Add recent appointments
    recent_appts = Appointment.query.order_by(Appointment.created_at.desc()).limit(5).all()
    for appt in recent_appts:
        activity_type = {
            'pending': 'warning',
            'approved': 'info',
            'completed': 'success',
            'cancelled': 'danger'
        }.get(appt.status, 'secondary')
        
        recent_activities.append({
            'type': activity_type,
            'icon': 'calendar-check',
            'title': f'New Appointment',
            'description': f'{appt.student.get_full_name()} with {appt.professor.get_full_name()}',
            'time': appt.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    # Add recent user registrations
    recent_users = User.query.order_by(User.created_at.desc()).limit(3).all()
    for user in recent_users:
        recent_activities.append({
            'type': 'primary',
            'icon': 'user-plus',
            'title': 'New User Registration',
            'description': f'{user.get_full_name()} joined as {user.role}',
            'time': user.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    # Sort activities by time
    recent_activities.sort(key=lambda x: datetime.strptime(x['time'], '%Y-%m-%d %H:%M'), reverse=True)
    recent_activities = recent_activities[:5]  # Keep only the 5 most recent
    
    return render_template('admin/reports.html',
                          title='System Reports',
                          total_appointments=total_appointments,
                          completed_appointments=completed_appointments,
                          active_users=active_users,
                          success_rate=success_rate,
                          status_counts=status_counts,
                          trend_labels=trend_labels,
                          trend_data=trend_data,
                          top_professors=top_professors_data,
                          recent_activities=recent_activities) 