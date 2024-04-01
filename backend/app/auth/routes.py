from flask import Blueprint, jsonify, request
from app import db, jwt, ACCESS_EXPIRES
from app.models import User
from flask_jwt_extended import create_access_token, jwt_required, current_user, get_jwt
# import redis

auth = Blueprint("auth", __name__)


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.email

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(email=identity).one_or_none()

@auth.route("/api/register", methods=["POST"])
def register():
    try:
        if current_user:
            return jsonify({'message': f'{current_user.email} already logged in'}), 401
        data = request.get_json()
        email = data.get('email', '')
        password = data.get('password', '')
        user = User(email, password)
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'registered successfully'})
    except Exception as e:
        return jsonify({'message': 'Server Error'}), 500


@auth.route("/api/login", methods=["POST"])
def login():
    if current_user:
        return jsonify({'message': f'{current_user.email} already logged in'}), 401
    data = request.get_json()
    email = data.get('email', '')
    password = data.get('password', '')
    user = User.query.filter_by(email=email).one_or_none()
    if not user or not user.check_password(password):
        return jsonify({'message': 'Bad credentials'}), 401
    access_token = create_access_token(identity=user)
    return jsonify({'email': user.email, 'access_token': access_token, 'message': 'Logged in successfully'})


@auth.route("/api/logout")
@jwt_required()
def logout():
    if current_user:
        return jsonify({'message': f'{current_user.email} Logged out successfully'})
    # return jsonify({'message': 'User not logged in'}), 401

# jwt_redis_blocklist = redis.StrictRedis(
#     host="localhost", port=6379, db=0, decode_responses=True
# )

# @jwt.token_in_blocklist_loader
# def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
#     jti = jwt_payload["jti"]
#     token_in_redis = jwt_redis_blocklist.get(jti)
#     return token_in_redis is not None

# @app.route("/logout", methods=["DELETE"])
# @jwt_required()
# def logout():
#     jti = get_jwt()["jti"]
#     jwt_redis_blocklist.set(jti, "", ex=ACCESS_EXPIRES)
#     return jsonify(msg="Access token revoked")


# @auth.app_context_processor
# def inject_current_user():
#     return dict(current_user=get_current_user())

