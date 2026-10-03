from flask import Blueprint, render_template, request, url_for, redirect, session
from app.models.course_db import User
from app.settings import bcrypt, db
from sqlalchemy import or_

auth_bp = Blueprint(
    "auth", __name__,
    template_folder='templates',
    static_folder='static'
)

@auth_bp.route("/login", methods=['GET', 'POST'])
def login():
    if "user_id" in session.keys():
        return redirect(url_for('home.index'))
    if request.method == "POST":
        data = request.form
        pid = data.get("id")
        password = data.get("password")
        user = User.query.filter(
            or_(
                User.mobile==pid,
                User.email==pid
            )
        ).first()
        
        if not user:
            return render_template("login.html", error="User Not Present")
        if not bcrypt.check_password_hash(user.password, password):
            return render_template("login.html", error="Password Is Invalid")
        else:
            session["user_id"] = user.id
            session["is_admin"] = user.is_admin
            return redirect(url_for('home.index'))
    return render_template("login.html")

@auth_bp.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        data = request.form
        name = data.get("name", '').strip()
        email = data.get("email", '').strip()
        mobile = data.get("mobile", '').strip()
        password = data.get("password", '').strip()
        
        if not name or not email or not mobile or not password:
            return render_template("register.html", error="Name, Email, Mobile or Password is not valid")
        
        u = User.query.filter(
                or_(User.email == email, User.mobile==mobile)
            ).first()
        if u:
            return render_template("register.html", error="User with this email or mobile already present")
        
        try:
            user = User(
                username = name, email=email,
                mobile=mobile, password=bcrypt.generate_password_hash(password).decode('utf-8')
            )
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            print(e)
            return render_template("register.html", error="Some DataBase Error...")
    return render_template("register.html")

@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():
    if "user_id" in session:
        session.clear()
    return redirect(url_for('auth.login'))