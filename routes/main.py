from flask import Blueprint, render_template, redirect, url_for, flash, request, g, session, current_app
from flask_login import current_user, login_required
from extensions import db
from models import User
import os
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import uuid

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_student():
            return redirect(url_for('student.dashboard'))
        elif current_user.is_professor():
            return redirect(url_for('professor.dashboard'))
        elif current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
    return render_template('index.html', title='Welcome')

@main.route('/home')
def home():
    # This route always shows the home page, even for authenticated users
    return render_template('index.html', title='Home')

@main.route('/about')
def about():
    return render_template('about.html', title='About')

@main.route('/contact')
def contact():
    return render_template('contact.html', title='Contact')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title='Profile')

@main.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    try:
        # Get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        
        # Validate required fields
        if not first_name or not last_name or not email:
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('main.profile'))
        
        # Check if email is taken by another user
        email_exists = db.session.query(db.exists().where(
            (User.email == email) & (User.id != current_user.id)
        )).scalar()
        
        if email_exists:
            flash('Email is already taken.', 'danger')
            return redirect(url_for('main.profile'))
        
        # Update user information
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.email = email
        
        # Update role-specific information
        if current_user.is_professor():
            current_user.faculty_id = request.form.get('faculty_id')
            current_user.office = request.form.get('office')
        
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename:
                # Generate a unique filename
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                
                # Create profile pictures directory if it doesn't exist
                profile_pics_dir = os.path.join(current_app.static_folder, 'profile_pictures')
                os.makedirs(profile_pics_dir, exist_ok=True)
                
                # Save the file
                file_path = os.path.join(profile_pics_dir, unique_filename)
                file.save(file_path)
                
                # Delete old profile picture if it exists
                if current_user.profile_picture:
                    old_pic_path = os.path.join(current_app.static_folder, current_user.profile_picture)
                    if os.path.exists(old_pic_path) and os.path.isfile(old_pic_path):
                        try:
                            os.remove(old_pic_path)
                        except:
                            pass  # Ignore if file couldn't be deleted
                
                current_user.profile_picture = unique_filename
        
        # Handle password change if provided
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if current_password and new_password and confirm_password:
            if not current_user.check_password(current_password):
                flash('Current password is incorrect.', 'danger')
                return redirect(url_for('main.profile'))
            
            if new_password != confirm_password:
                flash('New passwords do not match.', 'danger')
                return redirect(url_for('main.profile'))
            
            current_user.set_password(new_password)
        
        # Save changes
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    
    return redirect(url_for('main.profile'))

def allowed_file(filename):
    """Check if the file has an allowed extension"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/update-profile-picture', methods=['POST'])
@login_required
def update_profile_picture():
    # Check if the post request has the file part
    if 'profile_picture' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('main.profile'))
    
    file = request.files['profile_picture']
    
    # If user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('main.profile'))
    
    if file and allowed_file(file.filename):
        # Generate a unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        # Create profile pictures directory if it doesn't exist
        profile_pics_dir = os.path.join(current_app.static_folder, 'uploads', 'profile_pics')
        os.makedirs(profile_pics_dir, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(profile_pics_dir, unique_filename)
        file.save(file_path)
        
        # Update user's profile picture field - Use forward slashes for URL paths
        # Convert Windows backslashes to forward slashes for web URLs
        relative_path = '/'.join(['uploads', 'profile_pics', unique_filename])
        
        # Delete old profile picture if it exists
        if current_user.profile_picture:
            old_pic_path = os.path.join(current_app.static_folder, current_user.profile_picture.replace('/', os.path.sep))
            if os.path.exists(old_pic_path) and os.path.isfile(old_pic_path):
                try:
                    os.remove(old_pic_path)
                except:
                    pass  # Ignore if file couldn't be deleted
        
        current_user.profile_picture = relative_path
        
        try:
            db.session.commit()
            flash('Profile picture updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    else:
        flash('Invalid file format. Please upload a JPG, PNG, or GIF image.', 'danger')
    
    return redirect(url_for('main.profile'))

@main.route('/change-password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # Validate input
    if not current_password or not new_password or not confirm_password:
        flash('Please fill in all password fields.', 'danger')
        return redirect(url_for('main.profile'))
    
    if new_password != confirm_password:
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('main.profile'))
    
    # Check if current password is correct
    if not current_user.check_password(current_password):
        flash('Current password is incorrect.', 'danger')
        return redirect(url_for('main.profile'))
    
    # Update password
    current_user.set_password(new_password)
    
    try:
        db.session.commit()
        flash('Password changed successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    
    return redirect(url_for('main.profile'))

@main.route('/language/<language>')
def set_language(language):
    # Validate that the language is supported
    if language not in ['en', 'ar']:
        flash('Language not supported.', 'warning')
        return redirect(request.referrer or url_for('main.index'))
    
    # Set the language in the session
    session['lang_code'] = language
    
    # Redirect back to the referring page or home
    return redirect(request.referrer or url_for('main.index'))

@main.route('/faq')
def faq():
    return render_template('faq.html', title='FAQ') 