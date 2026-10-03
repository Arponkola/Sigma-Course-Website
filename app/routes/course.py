from flask import Blueprint, render_template, session, jsonify, request
from app.settings import is_login, db
from app.models.course_db import  User, Course, Enrollment
from typing import List
from sqlalchemy import func, or_, and_, not_

course_bp = Blueprint(
    "course", __name__,
    static_folder='static',
    template_folder='templates'
)

def get_all_courses() -> List[Course]:
    user_id = session.get("user_id")
    
    if not user_id:
        return db.session.query(Course).all()
        
    # FIX: Remove .subquery() from the end here
    enrolled_query = (
        db.session.query(Enrollment.course_id)
        .filter(Enrollment.user_id == user_id)
    )
    
    # SQLAlchemy will cleanly convert enrolled_query into a valid IN() statement
    available_courses = (
        db.session.query(Course)
        .filter(not_(Course.id.in_(enrolled_query)))
        .all()
    )
    return available_courses

def find_specific_type_course(course_type:str)->List:
    courses = Course.query.filter(
        Course.course_type == course_type
    ).all()
    courses1 = []
    for course in courses:
        en = Enrollment.query.filter(Enrollment.course_id == course.id).first()
        if not en:
            courses1.append(course.to_dict())
    return courses1

def get_all_enroll_course(user_id:int):
    enrollments = Enrollment.query.filter(Enrollment.user_id == user_id).all()
    en = []
    for enrollment in enrollments:
        en.append(Course.query.get(enrollment.course_id))
    courses = []
    for course in en:
        courses.append(course.to_dict())
    return courses

@course_bp.route("/", methods=['GET', 'POST'])
def course_page():
    user = session.get("user_id", "")
    is_admin = session.get("is_admin", "")
    return render_template('courses.html', user=user, is_admin=is_admin, courses = get_all_courses())

@course_bp.route("/<course_type>", methods=['GET', 'POST'])
def course_type_found(course_type:str):
    if not course_type:
        return jsonify({
            "message": "faliure"
        }), 400
    if course_type == "all":
        courses = []
        for course in get_all_courses():
            courses.append(course.to_dict())
            
        return jsonify({
            "message": "success",
            "courses": courses
        }), 200
    courses = find_specific_type_course(course_type)
    if not courses:
        return jsonify({
            "message" : "faliure"
        }), 400
    return jsonify({
        "message": "success",
        "courses" : courses
    }), 200

@course_bp.route("/enroll", methods=['GET', 'POST'])
@is_login
def enroll():
    if request.method == "POST":
        username = request.get_json()["username"]
        course_id = request.get_json()["course_id"]
        
        enrollment = Enrollment(
            user_id=session.get("user_id"),
            course_id=course_id,
            is_purchased=True,
            is_accessed=True
        )
        
        try:
            db.session.add(enrollment)
            db.session.commit()
            return jsonify({
                "message": "success"
            }), 200
        except Exception as e:
            db.session.rollback()
        
    return jsonify({
        "message": "faliure"
    }), 400

@course_bp.route("/search/<string:query>", methods=['GET', 'POST'])
def search(query:str):
    all_course = get_all_courses()
    courses = []
    for course in all_course:
        if query.lower() in course.course_name.lower():
            courses.append(course.to_dict())
    if not courses:
        return {
            "message" : "faliure"
        }, 404
    
    return {
        "message" : "success",
        "courses": courses
    }, 200

@course_bp.route("/own", methods=['GET', 'POST'])
@is_login
def own_page():
    user = session.get("user_id", "")
    is_admin = session.get("is_admin", "")
    courses = get_all_enroll_course(user)
    return render_template('account_courses.html', user=user, is_admin=is_admin, courses=courses)

@course_bp.route("/own/search/<string:query>", methods=['GET', 'POST'])
@is_login
def own_page_search(query:str):
    query = query.strip()
    if not query:
        return jsonify({
            "message": "faliure"
        }), 400
    user = session.get("user_id", "")
    is_admin = session.get("is_admin", "")
    enroll_courses = get_all_enroll_course(user)
    courses = []
    for course in enroll_courses:
        if query.lower() in course.get("course_name", "").lower():
            courses.append(course)
    if not courses:
        return jsonify({
            "message": "faliure"
        }), 404
    
    return jsonify({
        "message": "success",
        "courses": courses
    }), 200