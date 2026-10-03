from app import create_app
from flask import session

app1 = create_app()

@app1.context_processor
def inject_user_data():
    return {
        "user": session.get("user_id"),
        "is_admin": session.get("is_admin", False)
    }

if __name__ == "__main__":
    app1.run()