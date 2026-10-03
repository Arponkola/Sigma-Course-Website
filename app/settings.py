from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from functools import wraps
from flask import abort, session

bcrypt = Bcrypt()
db = SQLAlchemy()

def is_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" in session:
            return func(*args, **kwargs)
        return abort(404, "Unauthorized access")
    return wrapper

def is_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        from app.models.course_db import User
        admin = User.query.get(session.get("user_id"))
        if not admin:
            return abort(404, "user not found")
        if admin.is_admin==1:
            return func(*args, **kwargs)
        return abort(406, "Unauthorized access")
    return wrapper