from flask import Flask
from app.routes.auth import auth_bp
from app.routes.home import home_bp
from app.routes.admin import admin_bp
from app.routes.course import course_bp
from app.routes.about import about_bp
from app.routes.contact import contact_bp
from app.routes.account import account_bp
from app.routes.study import study_bp
from flask_cors import CORS
from app.settings import db, bcrypt
from dotenv import load_dotenv
import os

load_dotenv()

def create_app()->Flask:
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///instance.db"
    app.config['SQLALCHEMY_DATABASE_MODIFICATION'] = False
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
    
    db.init_app(app)
    bcrypt.init_app(app)
    CORS(app=app)
    app.register_blueprint(auth_bp, url_prefix="/")
    app.register_blueprint(home_bp, url_prefix="/")
    app.register_blueprint(course_bp, url_prefix="/course")
    app.register_blueprint(contact_bp, url_prefix="/contact")
    app.register_blueprint(about_bp, url_prefix="/about")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(account_bp, url_prefix="/account")
    app.register_blueprint(study_bp, url_prefix="/study")
    
    return app