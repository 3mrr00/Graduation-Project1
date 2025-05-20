# University Appointment System

A web-based system for managing appointments between students and professors at universities.

## Multilanguage Support

The system supports multiple languages using Flask-Babel. Currently, it includes:

- English (default)
- Arabic (with RTL support)

### How Language Selection Works

- The system detects the user's browser language preference and uses that if available
- Users can manually switch languages using the language dropdown in the navigation bar
- The selected language is stored in the session for consistency between pages
- Arabic pages are automatically displayed with RTL (right-to-left) text direction

### Managing Translations

To work with translations, you need the Flask-Babel package which is included in requirements.txt.

#### Create Translation Templates

To extract all translatable strings from the application and create/update `.pot` files:

```
flask translate update
```

#### Initialize a New Language

To add support for a new language (e.g., French):

```
flask translate init fr
```

This creates a new directory structure in the `translations` folder for the language.

#### Edit Translations

After initializing or updating translations, edit the `.po` files in the respective language folders:

```
translations/<language_code>/LC_MESSAGES/messages.po
```

#### Compile Translations

After editing the `.po` files, compile them to `.mo` files for the application to use:

```
flask translate compile
```

### Translation Workflow

1. Mark strings for translation in templates using the `{{ _("text") }}` syntax
2. In Python files, import and use gettext: `from flask_babel import gettext as _` and then `_("text")`
3. Run `flask translate update` to extract all strings
4. Edit translations in the `.po` files
5. Run `flask translate compile` to compile the translations
6. Restart the application to see changes

### RTL Support

Arabic and other RTL languages are automatically displayed with the correct text direction using:

- Bootstrap RTL CSS version for RTL pages
- Custom CSS adjustments for RTL in `static/css/style.css`
- Conditional `dir="rtl"` attribute on the HTML tag

## Installation

1. Clone the repository
2. Install the requirements:
```
pip install -r requirements.txt
```
3. Set up environment variables or a `.env` file with:
```
SECRET_KEY=your-secret-key
DATABASE_URI=your-database-uri
JWT_SECRET_KEY=your-jwt-secret-key
```
4. Initialize the database:
```
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```
5. Run the application:
```
flask run
```

## Development

To work on translations:

1. Extract messages:
```
flask translate update
```
2. Edit the `.po` files
3. Compile translations:
```
flask translate compile
```

## Features

- Secure user authentication for students, professors, and administrators
- Interactive calendar for booking appointments
- Real-time notifications and email confirmations
- Prevention of double-booking
- Responsive design for all devices
- Comprehensive admin dashboard with analytics

## Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap
- **Backend**: Python (Flask), SQLite
- **Authentication**: JWT with bcrypt password encryption

## User Roles

- **Student**: Book, modify, and cancel appointments
- **Professor**: Set availability, manage appointments, send notifications
- **Admin**: Manage users, generate reports, monitor system performance 