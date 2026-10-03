from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify
from app.settings import is_login, db
from app.models.course_db import Contact

contact_bp = Blueprint(
    "contact", __name__,
    static_folder='static',
    template_folder='templates'
)

@contact_bp.route('/', methods=['GET', 'POST'])
def contact_page():
    user = session.get("user_id", "")
    is_admin = session.get("is_admin", "")
    return render_template('contactus.html', user=user, is_admin=is_admin)

@contact_bp.route("/submit", methods=["GET", "POST"])
def contact_submit():
    if request.method == "POST":
        form = request.form
        name = form.get("name", "")
        email = form.get("email", "")
        message = form.get("message", "")
        
        if not name or not email or not message:
            return jsonify({
                "status": "faliure"
            }), 404
        con = Contact(name=name, email=email, message=message)
        try:
            db.session.add(con)
            db.session.commit()
            return jsonify({
                "status": "success"
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status" : "faliure"
            }), 404
        
    return jsonify({
        "status": "faliure"
    })