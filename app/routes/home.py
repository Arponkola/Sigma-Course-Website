from flask import Blueprint, request, render_template, session
from app.models.course_db import Course, Enrollment
from typing import List
from app.settings import db
from sqlalchemy import func

home_bp = Blueprint(
    "home", __name__,
    template_folder="templates",
    static_folder="static"
)

# Image-url: https://www.w3schools.com/html/pic_trulli.jpg

def get_popular_courses(limit:int=10, min_:int=1)->List:
    # Selects the course model AND the total user count for that course
    popular_courses = (
        db.session.query(Course)
        .join(Enrollment, Course.id == Enrollment.course_id)
        .group_by(Course.id)
        .having(func.count(Enrollment.user_id) >= min_)
        .order_by(func.count(Enrollment.user_id).desc())
        .limit(limit)
        .all()
    )
    return popular_courses

@home_bp.route("/", methods=['GET', 'POST'])
def index():
    user = session.get("user_id", "")
    is_admin = session.get("is_admin", "")
    courses = get_popular_courses(min_=5) # if 10 user enroll for the course
    return render_template("home.html", courses=courses, user=user, is_admin=is_admin)