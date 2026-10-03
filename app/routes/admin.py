import os
import uuid

from flask import (
    Blueprint,
    render_template,
    session,
    redirect,
    url_for,
    request,
    flash,
)

from app.settings import db, is_login, is_admin, bcrypt
from app.models.course_db import User, Course, Enrollment, Video, Contact


# =========================================================
# ADMIN BLUEPRINT
# =========================================================

admin_bp = Blueprint(
    "admin",
    __name__,
    static_folder="static",
    template_folder="templates"
)


# =========================================================
# VIDEO CONFIGURATION
# =========================================================

ALLOWED_VIDEO_EXTENSIONS = {
    "mp4",
    "webm",
    "ogg",
    "mov",
    "avi",
    "mkv",
}


def allowed_video(filename):
    """
    Check whether the uploaded file has an allowed
    video extension.
    """

    if not filename:
        return False

    if "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()

    return extension in ALLOWED_VIDEO_EXTENSIONS



def get_video_directory():
    """
    Return the existing app/static/videos directory.
    """

    app_directory = os.path.dirname(
        os.path.dirname(__file__)
    )

    return os.path.join(
        app_directory,
        "static",
        "videos"
    )


def save_video_file(video_file):
    """
    Save the uploaded video to:

        static/videos/

    Store the complete URL in the database.

    Example:

        http://127.0.0.1:5000/static/videos/abc123.mp4
    """

    if not video_file:
        return None

    if not video_file.filename:
        return None

    if not allowed_video(video_file.filename):
        return None

    # -----------------------------------------------------
    # Get static/videos directory
    # -----------------------------------------------------

    video_directory = get_video_directory()

    os.makedirs(
        video_directory,
        exist_ok=True
    )

    # -----------------------------------------------------
    # Get file extension
    # -----------------------------------------------------

    extension = video_file.filename.rsplit(
        ".",
        1
    )[1].lower()

    # -----------------------------------------------------
    # Generate unique filename
    # -----------------------------------------------------

    filename = f"{uuid.uuid4().hex}.{extension}"

    # -----------------------------------------------------
    # Physical file path
    # -----------------------------------------------------

    file_path = os.path.join(
        video_directory,
        filename
    )

    # -----------------------------------------------------
    # Save actual video
    # -----------------------------------------------------

    video_file.save(file_path)

    # -----------------------------------------------------
    # Create absolute URL
    # -----------------------------------------------------

    video_url = (
        request.host_url.rstrip("/")
        + "/static/videos/"
        + filename
    )

    return video_url


def delete_video_file(video_url):
    """
    Delete the physical video file from static/videos/.

    Example:

        /static/videos/abc123.mp4
    """

    if not video_url:
        return

    # Get only filename.
    filename = os.path.basename(video_url)

    if not filename:
        return

    video_directory = get_video_directory()

    file_path = os.path.join(
        video_directory,
        filename
    )

    if os.path.isfile(file_path):
        try:
            os.remove(file_path)
        except OSError:
            pass


# =========================================================
# DASHBOARD
# =========================================================

@admin_bp.route("/")
@is_admin
@is_login
def admin_page():

    user = session.get("user_id", "")
    is_admin_ = session.get("is_admin", "")

    user_count = User.query.count()
    course_count = Course.query.count()
    enrollment_count = Enrollment.query.count()
    video_count = Video.query.count()
    contact_count = Contact.query.count()

    return render_template(
        "admin.html",

        user=user,
        is_admin=is_admin_,

        user_count=user_count,
        course_count=course_count,
        enrollment_count=enrollment_count,
        video_count=video_count,
        contact_count=contact_count,
    )


# =========================================================
# USERS
# =========================================================

@admin_bp.route("/users")
@is_admin
@is_login
def users():
    user = session.get("user_id", "")
    is_admin_ = session.get("is_admin", "")
    users = User.query.order_by(
        User.id.desc()
    ).all()

    return render_template(
        "admin_users.html",
        users=users,
        user=user,
        is_admin=is_admin_
    )


# ---------------------------------------------------------
# CREATE USER
# ---------------------------------------------------------

@admin_bp.route("/users/create", methods=["GET", "POST"])
@is_admin
@is_login
def create_user():
    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        mobile = request.form.get(
            "mobile",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        is_admin_value = (
            request.form.get("is_admin") == "1"
        )

        # -----------------------------
        # Validation
        # -----------------------------

        if not username:
            flash(
                "Username is required.",
                "error"
            )

            return render_template(
                "admin_user_form.html",
                user_record=None,
                form_action=url_for(
                    "admin.create_user"
                ),
            )

        if not email:
            flash(
                "Email is required.",
                "error"
            )

            return render_template(
                "admin_user_form.html",
                user_record=None,
                form_action=url_for(
                    "admin.create_user"
                ),
            )

        if not mobile:
            flash(
                "Mobile number is required.",
                "error"
            )

            return render_template(
                "admin_user_form.html",
                user_record=None,
                form_action=url_for(
                    "admin.create_user"
                ),
            )

        if not password:
            flash(
                "Password is required.",
                "error"
            )

            return render_template(
                "admin_user_form.html",
                user_record=None,
                form_action=url_for(
                    "admin.create_user"
                ),
            )

        # -----------------------------
        # Duplicate checks
        # -----------------------------

        existing_email = User.query.filter_by(
            email=email
        ).first()

        if existing_email:
            flash(
                "Email already exists.",
                "error"
            )

            return render_template(
                "admin_user_form.html",
                user_record=None,
                form_action=url_for(
                    "admin.create_user"
                ),
            )

        existing_mobile = User.query.filter_by(
            mobile=mobile
        ).first()

        if existing_mobile:
            flash(
                "Mobile number already exists.",
                "error"
            )

            return render_template(
                "admin_user_form.html",
                user_record=None,
                form_action=url_for(
                    "admin.create_user"
                ),
            )

        # -----------------------------
        # Create user
        # -----------------------------

        new_user = User(
            username=username,
            email=email,
            mobile=mobile,
            password=bcrypt.generate_password_hash(password),
            is_admin=is_admin_value,
        )

        db.session.add(new_user)
        db.session.commit()

        flash(
            "User created successfully.",
            "success"
        )

        return redirect(
            url_for("admin.users")
        )

    return render_template(
        "admin_user_form.html",
        user_record=None,
        form_action=url_for(
            "admin.create_user"
        ),
    )


# ---------------------------------------------------------
# EDIT USER
# ---------------------------------------------------------

@admin_bp.route(
    "/users/<int:user_id>/edit",
    methods=["GET", "POST"]
)
@is_admin
@is_login
def edit_user(user_id):
    
    user_record = db.session.get(
        User,
        user_id
    )

    if not user_record:
        flash(
            "User not found.",
            "error"
        )

        return redirect(
            url_for("admin.users")
        )

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        mobile = request.form.get(
            "mobile",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        # -----------------------------
        # Validation
        # -----------------------------

        if not username:
            flash(
                "Username is required.",
                "error"
            )

            return render_template(
                "admin_user_form.html",
                user_record=user_record,
                form_action=url_for(
                    "admin.edit_user",
                    user_id=user_record.id
                ),
            )

        if not email:
            flash(
                "Email is required.",
                "error"
            )

            return render_template(
                "admin_user_form.html",
                user_record=user_record,
                form_action=url_for(
                    "admin.edit_user",
                    user_id=user_record.id
                ),
            )

        if not mobile:
            flash(
                "Mobile number is required.",
                "error"
            )

            return render_template(
                "admin_user_form.html",
                user_record=user_record,
                form_action=url_for(
                    "admin.edit_user",
                    user_id=user_record.id
                ),
            )

        # -----------------------------
        # Duplicate email check
        # -----------------------------

        existing_email = User.query.filter(
            User.email == email,
            User.id != user_record.id
        ).first()

        if existing_email:
            flash(
                "Email already exists.",
                "error"
            )

            return render_template(
                "admin_user_form.html",
                user_record=user_record,
                form_action=url_for(
                    "admin.edit_user",
                    user_id=user_record.id
                ),
            )

        # -----------------------------
        # Duplicate mobile check
        # -----------------------------

        existing_mobile = User.query.filter(
            User.mobile == mobile,
            User.id != user_record.id
        ).first()

        if existing_mobile:
            flash(
                "Mobile number already exists.",
                "error"
            )

            return render_template(
                "admin_user_form.html",
                user_record=user_record,
                form_action=url_for(
                    "admin.edit_user",
                    user_id=user_record.id
                ),
            )

        # -----------------------------
        # Update user
        # -----------------------------

        user_record.username = username
        user_record.email = email
        user_record.mobile = mobile

        # Only change password when
        # a new password was entered.
        if password:
            user_record.password = password

        db.session.commit()

        flash(
            "User updated successfully.",
            "success"
        )

        return redirect(
            url_for("admin.users")
        )

    return render_template(
        "admin_user_form.html",
        user_record=user_record,
        form_action=url_for(
            "admin.edit_user",
            user_id=user_record.id
        ),
    )


# ---------------------------------------------------------
# TOGGLE ADMIN
# ---------------------------------------------------------

@admin_bp.route(
    "/users/<int:user_id>/toggle-admin",
    methods=["POST"]
)
@is_admin
@is_login
def toggle_admin(user_id):

    user_record = db.session.get(
        User,
        user_id
    )

    if not user_record:
        flash(
            "User not found.",
            "error"
        )

        return redirect(
            url_for("admin.users")
        )

    current_user_id = session.get(
        "user_id"
    )

    # Prevent current admin from removing
    # their own admin permission.
    if str(current_user_id) == str(user_record.id):
        flash(
            "You cannot remove your own admin permission.",
            "error"
        )

        return redirect(
            url_for("admin.users")
        )

    user_record.is_admin = not user_record.is_admin

    db.session.commit()

    flash(
        "Admin status updated.",
        "success"
    )

    return redirect(
        url_for("admin.users")
    )


# ---------------------------------------------------------
# DELETE USER
# ---------------------------------------------------------

@admin_bp.route(
    "/users/<int:user_id>/delete",
    methods=["POST"]
)
@is_admin
@is_login
def delete_user(user_id):

    user_record = db.session.get(
        User,
        user_id
    )

    if not user_record:
        flash(
            "User not found.",
            "error"
        )

        return redirect(
            url_for("admin.users")
        )

    current_user_id = session.get(
        "user_id"
    )

    # Prevent deleting yourself.
    if str(current_user_id) == str(user_record.id):
        flash(
            "You cannot delete your own account.",
            "error"
        )

        return redirect(
            url_for("admin.users")
        )

    # Delete user's enrollments first.
    enrollments = Enrollment.query.filter_by(
        user_id=user_record.id
    ).all()

    for enrollment in enrollments:
        db.session.delete(enrollment)

    # Courses authored by this user have
    # nullable user_id, so detach them.
    courses = Course.query.filter_by(
        user_id=user_record.id
    ).all()

    for course in courses:
        course.user_id = None

    db.session.delete(user_record)

    db.session.commit()

    flash(
        "User deleted successfully.",
        "success"
    )

    return redirect(
        url_for("admin.users")
    )


# =========================================================
# COURSES
# =========================================================

@admin_bp.route("/courses")
@is_admin
@is_login
def courses():

    courses = Course.query.order_by(
        Course.id.desc()
    ).all()

    return render_template(
        "admin_courses.html",
        courses=courses,
    )


# ---------------------------------------------------------
# CREATE COURSE
# ---------------------------------------------------------

@admin_bp.route(
    "/courses/create",
    methods=["GET", "POST"]
)
@is_admin
@is_login
def create_course():

    users = User.query.order_by(
        User.username
    ).all()

    if request.method == "POST":

        course_name = request.form.get(
            "course_name",
            ""
        ).strip()

        course_details = request.form.get(
            "course_details",
            ""
        ).strip()

        price = request.form.get(
            "price",
            type=int
        )

        thumbnail = request.form.get(
            "thumbnail",
            ""
        ).strip()

        course_type = request.form.get(
            "course_type",
            ""
        ).strip()

        course_duration = request.form.get(
            "course_duration",
            type=int
        )

        user_id = request.form.get(
            "user_id",
            type=int
        )

        # -----------------------------
        # Validation
        # -----------------------------

        if not course_name:
            flash(
                "Course name is required.",
                "error"
            )

            return render_template(
                "admin_course_form.html",
                course=None,
                users=users,
                form_action=url_for(
                    "admin.create_course"
                ),
            )

        if not course_type:
            flash(
                "Course type is required.",
                "error"
            )

            return render_template(
                "admin_course_form.html",
                course=None,
                users=users,
                form_action=url_for(
                    "admin.create_course"
                ),
            )

        if course_duration is None:
            flash(
                "Course duration is required.",
                "error"
            )

            return render_template(
                "admin_course_form.html",
                course=None,
                users=users,
                form_action=url_for(
                    "admin.create_course"
                ),
            )

        if course_duration < 0:
            flash(
                "Course duration cannot be negative.",
                "error"
            )

            return render_template(
                "admin_course_form.html",
                course=None,
                users=users,
                form_action=url_for(
                    "admin.create_course"
                ),
            )

        if price is None:
            price = 0

        if price < 0:
            flash(
                "Price cannot be negative.",
                "error"
            )

            return render_template(
                "admin_course_form.html",
                course=None,
                users=users,
                form_action=url_for(
                    "admin.create_course"
                ),
            )

        # -----------------------------
        # Validate author
        # -----------------------------

        if user_id:

            author = db.session.get(
                User,
                user_id
            )

            if not author:
                flash(
                    "Selected author does not exist.",
                    "error"
                )

                return render_template(
                    "admin_course_form.html",
                    course=None,
                    users=users,
                    form_action=url_for(
                        "admin.create_course"
                    ),
                )

        # -----------------------------
        # Create course
        # -----------------------------

        course = Course(
            course_name=course_name,
            course_details=course_details or None,
            user_id=user_id or None,
            price=price,
            thumbnail=thumbnail or None,
            course_type=course_type,
            course_duration=course_duration,
        )

        db.session.add(course)
        db.session.commit()

        flash(
            "Course created successfully.",
            "success"
        )

        return redirect(
            url_for("admin.courses")
        )

    return render_template(
        "admin_course_form.html",
        course=None,
        users=users,
        form_action=url_for(
            "admin.create_course"
        ),
    )


# ---------------------------------------------------------
# EDIT COURSE
# ---------------------------------------------------------

@admin_bp.route(
    "/courses/<int:course_id>/edit",
    methods=["GET", "POST"]
)
@is_admin
@is_login
def edit_course(course_id):

    course = db.session.get(
        Course,
        course_id
    )

    if not course:
        flash(
            "Course not found.",
            "error"
        )

        return redirect(
            url_for("admin.courses")
        )

    users = User.query.order_by(
        User.username
    ).all()

    if request.method == "POST":

        course_name = request.form.get(
            "course_name",
            ""
        ).strip()

        course_details = request.form.get(
            "course_details",
            ""
        ).strip()

        price = request.form.get(
            "price",
            type=int
        )

        thumbnail = request.form.get(
            "thumbnail",
            ""
        ).strip()

        course_type = request.form.get(
            "course_type",
            ""
        ).strip()

        course_duration = request.form.get(
            "course_duration",
            type=int
        )

        user_id = request.form.get(
            "user_id",
            type=int
        )

        if not course_name:
            flash(
                "Course name is required.",
                "error"
            )

            return render_template(
                "admin_course_form.html",
                course=course,
                users=users,
                form_action=url_for(
                    "admin.edit_course",
                    course_id=course.id
                ),
            )

        if not course_type:
            flash(
                "Course type is required.",
                "error"
            )

            return render_template(
                "admin_course_form.html",
                course=course,
                users=users,
                form_action=url_for(
                    "admin.edit_course",
                    course_id=course.id
                ),
            )

        if course_duration is None:
            flash(
                "Course duration is required.",
                "error"
            )

            return render_template(
                "admin_course_form.html",
                course=course,
                users=users,
                form_action=url_for(
                    "admin.edit_course",
                    course_id=course.id
                ),
            )

        if course_duration < 0:
            flash(
                "Course duration cannot be negative.",
                "error"
            )

            return render_template(
                "admin_course_form.html",
                course=course,
                users=users,
                form_action=url_for(
                    "admin.edit_course",
                    course_id=course.id
                ),
            )

        if price is None:
            price = 0

        if price < 0:
            flash(
                "Price cannot be negative.",
                "error"
            )

            return render_template(
                "admin_course_form.html",
                course=course,
                users=users,
                form_action=url_for(
                    "admin.edit_course",
                    course_id=course.id
                ),
            )

        if user_id:

            author = db.session.get(
                User,
                user_id
            )

            if not author:
                flash(
                    "Selected author does not exist.",
                    "error"
                )

                return render_template(
                    "admin_course_form.html",
                    course=course,
                    users=users,
                    form_action=url_for(
                        "admin.edit_course",
                        course_id=course.id
                    ),
                )

        course.course_name = course_name
        course.course_details = (
            course_details or None
        )
        course.user_id = user_id or None
        course.price = price
        course.thumbnail = thumbnail or None
        course.course_type = course_type
        course.course_duration = course_duration

        db.session.commit()

        flash(
            "Course updated successfully.",
            "success"
        )

        return redirect(
            url_for("admin.courses")
        )

    return render_template(
        "admin_course_form.html",
        course=course,
        users=users,
        form_action=url_for(
            "admin.edit_course",
            course_id=course.id
        ),
    )


# ---------------------------------------------------------
# DELETE COURSE
# ---------------------------------------------------------

@admin_bp.route(
    "/courses/<int:course_id>/delete",
    methods=["POST"]
)
@is_admin
@is_login
def delete_course(course_id):

    course = db.session.get(
        Course,
        course_id
    )

    if not course:
        flash(
            "Course not found.",
            "error"
        )

        return redirect(
            url_for("admin.courses")
        )

    # --------------------------------
    # Delete videos belonging to course
    # --------------------------------

    videos = Video.query.filter_by(
        course_id=course.id
    ).all()

    for video in videos:

        delete_video_file(
            video.url
        )

        db.session.delete(video)

    # --------------------------------
    # Delete enrollments
    # --------------------------------

    enrollments = Enrollment.query.filter_by(
        course_id=course.id
    ).all()

    for enrollment in enrollments:
        db.session.delete(enrollment)

    # --------------------------------
    # Delete course
    # --------------------------------

    db.session.delete(course)

    db.session.commit()

    flash(
        "Course and its related data deleted successfully.",
        "success"
    )

    return redirect(
        url_for("admin.courses")
    )


# =========================================================
# ENROLLMENTS
# =========================================================

@admin_bp.route("/enrollments")
@is_admin
@is_login
def enrollments():

    enrollments = Enrollment.query.order_by(
        Enrollment.id.desc()
    ).all()

    users = User.query.all()
    courses = Course.query.all()

    user_map = {
        user.id: user
        for user in users
    }

    course_map = {
        course.id: course
        for course in courses
    }

    return render_template(
        "admin_enrollments.html",
        enrollments=enrollments,
        user_map=user_map,
        course_map=course_map,
    )


# ---------------------------------------------------------
# UPDATE ENROLLMENT
# ---------------------------------------------------------

@admin_bp.route(
    "/enrollments/<int:enrollment_id>/update",
    methods=["POST"]
)
@is_admin
@is_login
def update_enrollment(enrollment_id):

    enrollment = db.session.get(
        Enrollment,
        enrollment_id
    )

    if not enrollment:
        flash(
            "Enrollment not found.",
            "error"
        )

        return redirect(
            url_for("admin.enrollments")
        )

    enrollment.is_purchased = (
        request.form.get("is_purchased") == "on"
    )

    enrollment.is_accessed = (
        request.form.get("is_accessed") == "on"
    )

    db.session.commit()

    flash(
        "Enrollment updated successfully.",
        "success"
    )

    return redirect(
        url_for("admin.enrollments")
    )


# ---------------------------------------------------------
# DELETE ENROLLMENT
# ---------------------------------------------------------

@admin_bp.route(
    "/enrollments/<int:enrollment_id>/delete",
    methods=["POST"]
)
@is_admin
@is_login
def delete_enrollment(enrollment_id):

    enrollment = db.session.get(
        Enrollment,
        enrollment_id
    )

    if not enrollment:
        flash(
            "Enrollment not found.",
            "error"
        )

        return redirect(
            url_for("admin.enrollments")
        )

    db.session.delete(enrollment)
    db.session.commit()

    flash(
        "Enrollment deleted successfully.",
        "success"
    )

    return redirect(
        url_for("admin.enrollments")
    )


# =========================================================
# VIDEOS
# =========================================================

@admin_bp.route("/videos")
@is_admin
@is_login
def videos():

    videos = Video.query.order_by(
        Video.id.desc()
    ).all()

    courses = Course.query.all()

    # Video has course_id but no course relationship.
    # Therefore create a lookup dictionary.
    course_map = {
        course.id: course
        for course in courses
    }

    return render_template(
        "admin_videos.html",
        videos=videos,
        course_map=course_map,
    )


# ---------------------------------------------------------
# CREATE / UPLOAD VIDEO
# ---------------------------------------------------------

@admin_bp.route(
    "/videos/create",
    methods=["GET", "POST"]
)
@is_admin
@is_login
def create_video():

    courses = Course.query.order_by(
        Course.course_name
    ).all()

    if request.method == "POST":

        course_id = request.form.get(
            "course_id",
            type=int
        )

        title = request.form.get(
            "title",
            ""
        ).strip()

        desc = request.form.get(
            "desc",
            ""
        ).strip()

        video_file = request.files.get(
            "video"
        )

        # -----------------------------
        # Course validation
        # -----------------------------

        if not course_id:

            flash(
                "Please select a course.",
                "error"
            )

            return render_template(
                "admin_video_form.html",
                video=None,
                courses=courses,
                form_action=url_for(
                    "admin.create_video"
                ),
            )

        course = db.session.get(
            Course,
            course_id
        )

        if not course:

            flash(
                "Selected course does not exist.",
                "error"
            )

            return render_template(
                "admin_video_form.html",
                video=None,
                courses=courses,
                form_action=url_for(
                    "admin.create_video"
                ),
            )

        # -----------------------------
        # File validation
        # -----------------------------

        if not video_file or not video_file.filename:

            flash(
                "Please select a video file.",
                "error"
            )

            return render_template(
                "admin_video_form.html",
                video=None,
                courses=courses,
                form_action=url_for(
                    "admin.create_video"
                ),
            )

        if not allowed_video(
            video_file.filename
        ):

            flash(
                "Invalid video format. "
                "Allowed: MP4, WebM, OGG, MOV, AVI, MKV.",
                "error"
            )

            return render_template(
                "admin_video_form.html",
                video=None,
                courses=courses,
                form_action=url_for(
                    "admin.create_video"
                ),
            )

        # -----------------------------
        # Save physical video
        # -----------------------------

        video_url = save_video_file(
            video_file
        )

        if not video_url:

            flash(
                "Video upload failed.",
                "error"
            )

            return render_template(
                "admin_video_form.html",
                video=None,
                courses=courses,
                form_action=url_for(
                    "admin.create_video"
                ),
            )

        # -----------------------------
        # Create database record
        # -----------------------------

        video = Video(
            course_id=course_id,
            url=video_url,
            title=title or None,
            desc=desc or None,
        )

        db.session.add(video)

        db.session.commit()

        flash(
            "Video uploaded successfully.",
            "success"
        )

        return redirect(
            url_for("admin.videos")
        )

    return render_template(
        "admin_video_form.html",
        video=None,
        courses=courses,
        form_action=url_for(
            "admin.create_video"
        ),
    )


# ---------------------------------------------------------
# EDIT / REPLACE VIDEO
# ---------------------------------------------------------

@admin_bp.route(
    "/videos/<int:video_id>/edit",
    methods=["GET", "POST"]
)
@is_admin
@is_login
def edit_video(video_id):

    video = db.session.get(
        Video,
        video_id
    )

    if not video:

        flash(
            "Video not found.",
            "error"
        )

        return redirect(
            url_for("admin.videos")
        )

    courses = Course.query.order_by(
        Course.course_name
    ).all()

    if request.method == "POST":

        course_id = request.form.get(
            "course_id",
            type=int
        )

        title = request.form.get(
            "title",
            ""
        ).strip()

        desc = request.form.get(
            "desc",
            ""
        ).strip()

        # -----------------------------
        # Course validation
        # -----------------------------

        if not course_id:

            flash(
                "Please select a course.",
                "error"
            )

            return render_template(
                "admin_video_form.html",
                video=video,
                courses=courses,
                form_action=url_for(
                    "admin.edit_video",
                    video_id=video.id
                ),
            )

        course = db.session.get(
            Course,
            course_id
        )

        if not course:

            flash(
                "Selected course does not exist.",
                "error"
            )

            return render_template(
                "admin_video_form.html",
                video=video,
                courses=courses,
                form_action=url_for(
                    "admin.edit_video",
                    video_id=video.id
                ),
            )

        # -----------------------------
        # Update basic information
        # -----------------------------

        video.course_id = course_id
        video.title = title or None
        video.desc = desc or None

        # -----------------------------
        # Optional replacement video
        # -----------------------------

        new_video_file = request.files.get(
            "video"
        )

        if (
            new_video_file
            and new_video_file.filename
        ):

            if not allowed_video(
                new_video_file.filename
            ):

                flash(
                    "Invalid video format. "
                    "Allowed: MP4, WebM, OGG, MOV, AVI, MKV.",
                    "error"
                )

                return render_template(
                    "admin_video_form.html",
                    video=video,
                    courses=courses,
                    form_action=url_for(
                        "admin.edit_video",
                        video_id=video.id
                    ),
                )

            # Save new file first.
            new_video_url = save_video_file(
                new_video_file
            )

            if not new_video_url:

                flash(
                    "Replacement video upload failed.",
                    "error"
                )

                return render_template(
                    "admin_video_form.html",
                    video=video,
                    courses=courses,
                    form_action=url_for(
                        "admin.edit_video",
                        video_id=video.id
                    ),
                )

            # Remember old URL.
            old_video_url = video.url

            # Update DB with new URL.
            video.url = new_video_url

            # Delete old physical file.
            delete_video_file(
                old_video_url
            )

        db.session.commit()

        flash(
            "Video updated successfully.",
            "success"
        )

        return redirect(
            url_for("admin.videos")
        )

    return render_template(
        "admin_video_form.html",
        video=video,
        courses=courses,
        form_action=url_for(
            "admin.edit_video",
            video_id=video.id
        ),
    )


# ---------------------------------------------------------
# DELETE VIDEO
# ---------------------------------------------------------

@admin_bp.route(
    "/videos/<int:video_id>/delete",
    methods=["POST"]
)
@is_admin
@is_login
def delete_video(video_id):

    video = db.session.get(
        Video,
        video_id
    )

    if not video:

        flash(
            "Video not found.",
            "error"
        )

        return redirect(
            url_for("admin.videos")
        )

    # Delete physical video.
    delete_video_file(
        video.url
    )

    # Delete database record.
    db.session.delete(video)

    db.session.commit()

    flash(
        "Video deleted successfully.",
        "success"
    )

    return redirect(
        url_for("admin.videos")
    )


# =========================================================
# CONTACTS
# =========================================================

@admin_bp.route("/contacts")
@is_admin
@is_login
def contacts():

    contacts = Contact.query.order_by(
        Contact.id.desc()
    ).all()

    return render_template(
        "admin_contacts.html",
        contacts=contacts,
    )


# ---------------------------------------------------------
# DELETE CONTACT
# ---------------------------------------------------------

@admin_bp.route(
    "/contacts/<int:contact_id>/delete",
    methods=["POST"]
)
@is_admin
@is_login
def delete_contact(contact_id):

    contact = db.session.get(
        Contact,
        contact_id
    )

    if not contact:

        flash(
            "Contact message not found.",
            "error"
        )

        return redirect(
            url_for("admin.contacts")
        )

    db.session.delete(contact)

    db.session.commit()

    flash(
        "Contact message deleted successfully.",
        "success"
    )

    return redirect(
        url_for("admin.contacts")
    )