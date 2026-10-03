from app.settings import db
from app.models.course_db import User, Course, Enrollment
from main import app1

with app1.app_context():
    db.create_all()

print("All DataBase are Created....")