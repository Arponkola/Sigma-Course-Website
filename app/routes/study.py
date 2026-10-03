from flask import Blueprint, request, render_template, session, abort
from app.settings import is_login
from app.models.course_db import User, Course, Enrollment, Video

study_bp = Blueprint(
    "study", __name__,
    template_folder="templates",
    static_folder="static"
)

def get_enroll_course(user_id:int, course_id:int):
    enrollment = Enrollment.query.filter(Enrollment.user_id == user_id, Enrollment.course_id == course_id).first()
    if not enrollment:
        return None
    return enrollment

@study_bp.route("/", methods=['GET', 'POST'])
@is_login
def index():
    course_id = request.args.get("course_id", "")
    if not course_id:
        return abort(404, "Course Not Found!")
    user_id = session.get("user_id", "")
    is_admin = session.get("is_admin")
    course = get_enroll_course(user_id, course_id)
    if not course:
        return "Course Not Enrolled"
    videos = Video.query.filter(Video.course_id == course.id).all()
    v = []
    for video in videos:
        v.append(video.to_dict())
    if len(videos)>=2:
        first = v[0]
        v = v[1:]
    else:
        if not videos:
            first = []
            v = []
            return "Course Videos Not Available"
        else:
            first = videos
            v = []
    return render_template("study_course.html", user=user_id, is_admin=is_admin, videos=v, firstVideo=first)