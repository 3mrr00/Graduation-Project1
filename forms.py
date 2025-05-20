from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, DateTimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models import User, Role

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    role = SelectField('Role', choices=[('student', 'Student'), ('instructor', 'Instructor')], validators=[DataRequired()])
    accept_terms = BooleanField('Accept Terms', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class AdminUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    role = SelectField('Role', choices=[(Role.ADMIN, 'Admin'), (Role.PROFESSOR, 'Professor'), (Role.STUDENT, 'Student')], validators=[DataRequired()])
    is_active = BooleanField('Active')
    submit = SubmitField('Add User')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    role = SelectField('Role', choices=[(Role.ADMIN, 'Admin'), (Role.PROFESSOR, 'Professor'), (Role.STUDENT, 'Student')], validators=[DataRequired()])
    is_active = BooleanField('Active')
    submit = SubmitField('Update User')

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class AppointmentForm(FlaskForm):
    professor = SelectField('Professor', coerce=int, validators=[DataRequired()])
    date = DateTimeField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    time_slot = SelectField('Time Slot', validators=[DataRequired()])
    subject = StringField('Subject', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    submit = SubmitField('Book Appointment')

class AvailabilityForm(FlaskForm):
    day_of_week = SelectField('Day of Week', choices=[(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), 
                                                     (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), 
                                                     (6, 'Sunday')], coerce=int, validators=[DataRequired()])
    start_time = StringField('Start Time (HH:MM)', validators=[DataRequired()])
    end_time = StringField('End Time (HH:MM)', validators=[DataRequired()])
    is_recurring = BooleanField('Recurring Weekly')
    specific_date = DateTimeField('Specific Date', format='%Y-%m-%d', validators=[])
    submit = SubmitField('Set Availability') 