from flask import Blueprint, render_template, session
from app.settings import is_login

about_bp = Blueprint(
    "about", __name__,
    static_folder='static',
    template_folder='templates'
)

@about_bp.route('/', methods=['GET', 'POST'])
def about_page():
    user = session.get("user_id", "")
    is_admin = session.get("is_admin")
    return render_template('aboutus.html', user=user, is_admin=is_admin)