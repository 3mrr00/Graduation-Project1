# University Appointment System - Setup Guide

This document provides instructions for setting up and running the University Appointment System.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd university-appointment-system
```

### 2. Create a Virtual Environment (Recommended)

#### On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

#### On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables Setup

Create a `.env` file in the root directory and add the following variables:

```
SECRET_KEY=your_super_secret_key_change_this_in_production
JWT_SECRET_KEY=another_secret_key_for_jwt_change_this_in_production
DATABASE_URI=sqlite:///appointments.db
FLASK_APP=app.py
FLASK_ENV=development

# Email Settings (Optional, for email notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### 5. Initialize the Database

```bash
python init_db.py
```

This will create the database with dummy data for testing purposes.

### 6. Run the Application

```bash
flask run
```

The application will be available at `http://localhost:5000`.

## Default Users

The initialization script creates the following test users:

### Admin
- Username: admin
- Email: admin@university.edu
- Password: adminpass

### Professors
1. **Professor Sarah Johnson**
   - Username: professor1
   - Email: prof1@university.edu
   - Password: profpass1

2. **Professor David Wilson**
   - Username: professor2
   - Email: prof2@university.edu
   - Password: profpass2

3. **Professor Michael Thompson**
   - Username: professor3
   - Email: prof3@university.edu
   - Password: profpass3

### Students
1. **Emma Davis**
   - Username: student1
   - Email: student1@university.edu
   - Password: studpass1

2. **James Miller**
   - Username: student2
   - Email: student2@university.edu
   - Password: studpass2

3. **Sophia Brown**
   - Username: student3
   - Email: student3@university.edu
   - Password: studpass3

## Project Structure

- `app.py`: Main application file
- `models.py`: Database models
- `forms.py`: Form definitions
- `routes/`: Route blueprints
  - `main.py`: Main routes
  - `auth.py`: Authentication routes
  - `student.py`: Student-specific routes
  - `professor.py`: Professor-specific routes
  - `admin.py`: Admin-specific routes
- `static/`: Static assets (CSS, JS, images)
- `templates/`: HTML templates
- `init_db.py`: Database initialization script 