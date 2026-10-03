from flask import Blueprint, render_template, session
from app.settings import db, is_login
from app.models.course_db import User

account_bp = Blueprint(
    "account", __name__,
    static_folder='static',
    template_folder='templates'
)

@account_bp.route('/', methods=['GET', 'POST'])
@is_login
def account_page():
    user = session.get("user_id", "")
    is_admin = session.get("is_admin")
    user_record = User.query.get(user)    
    return render_template('account.html', user=user, user_record=user_record, is_admin=is_admin)