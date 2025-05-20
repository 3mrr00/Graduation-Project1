import os
from flask import Flask, render_template, request, session, g
from dotenv import load_dotenv
import click
from flask.cli import with_appcontext
from extensions import db, login_manager, jwt, babel, migrate, csrf
from flask_babel import _
from flask_wtf.csrf import generate_csrf, CSRFProtect

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///appointments.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-dev-key')
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_CHECK_DEFAULT'] = False  # Don't check CSRF for all requests, we'll handle it manually

# Initialize extensions
db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)
jwt.init_app(app)
csrf.init_app(app)

# CSRF Protection
@app.after_request
def add_csrf_cookie(response):
    response.set_cookie('csrf_token', generate_csrf())
    return response

# Flask-Babel configuration
def get_locale():
    # Try to get the language from the session
    if 'lang_code' in session:
        return session['lang_code']
    # Or default to the user's browser settings or default language
    return request.accept_languages.best_match(['en', 'ar']) or 'en'

# Initialize Babel with the locale selector
babel.init_app(app, locale_selector=get_locale)

# Make _ available in templates
app.jinja_env.globals['_'] = _
# Make csrf_token available in templates
app.jinja_env.globals['csrf_token'] = generate_csrf

# Add custom Jinja2 filters
@app.template_filter('argmax')
def argmax_filter(values):
    """Find the index of the maximum value in a list."""
    if not values:
        return 0
    return values.index(max(values))

# Set up g with language info for templates
@app.before_request
def before_request():
    g.lang_code = get_locale()

login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# Import models after db is initialized
from models import User, Appointment, Availability

# Register blueprints
from routes.auth import auth as auth_blueprint
from routes.main import main as main_blueprint
from routes.student import student as student_blueprint
from routes.professor import professor as professor_blueprint
from routes.admin import admin as admin_blueprint

app.register_blueprint(auth_blueprint)
app.register_blueprint(main_blueprint)
app.register_blueprint(student_blueprint, url_prefix='/student')
app.register_blueprint(professor_blueprint, url_prefix='/professor')
app.register_blueprint(admin_blueprint, url_prefix='/admin')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/test')
def test():
    return render_template('test.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True) 