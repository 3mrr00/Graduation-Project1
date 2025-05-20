from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_babel import Babel
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
jwt = JWTManager()
babel = Babel()
migrate = Migrate()
csrf = CSRFProtect() 