from flask import Blueprint, session, g, jsonify, request
from app import db
from app.models import User
from werkzeug.local import LocalProxy

auth = Blueprint("auth", __name__)

current_user = LocalProxy(lambda: get_current_user())

@auth.route("/register", methods=["POST"])
def register():
    if current_user.is_authenticated():
        return jsonify({'message': 'User already logged in'}), 401
    data = request.get_json()
    email = data.get('email', '')
    password = data.get('password', '')
    user = User(email, password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'registered successfully'})


@auth.route("/login", methods=["POST"])
def login():
    if current_user.is_authenticated():
        return jsonify({'message': 'User already logged in'}), 401
    data = request.get_json()
    email = data.get('email', '')
    password = data.get('password', '')
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'message': 'Bad credentials'}), 400
    login_user(user)
    return jsonify({'message': 'Logged in successfully'})


@auth.route("/logout")
def logout():
    if current_user.is_authenticated():
        logout_user()
        return jsonify({'message': 'Logged out successfully'})
    return jsonify({'message': 'User not logged in'}), 401

def login_user(user):
    session["email"] = user.email

def logout_user():
    session.pop("email")

# @auth.app_context_processor
# def inject_current_user():
#     return dict(current_user=get_current_user())

def get_current_user():
    _current_user = getattr(g, "_current_user", None)
    if _current_user is None and session.get("email"):
        user = User.query.filter_by(email=session.get("email")).first()
        if user:
            _current_user = g._current_user = user

    if _current_user is None:
        _current_user = User()
    return _current_user
