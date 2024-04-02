import os
from os.path import join, dirname
from datetime import timedelta
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

ACCESS_EXPIRES = timedelta(hours=1)

basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY"),
        JWT_ACCESS_TOKEN_EXPIRES=ACCESS_EXPIRES,
        SECRET_KEY=os.getenv("FLASK_SECRET_KEY"),
        SQLALCHEMY_DATABASE_URI=f'postgresql://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@localhost/documate',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        DEBUG=True
    )
    CORS(app) if os.getenv("FLASK_ENV") == "development" else None
    db.init_app(app)
    jwt.init_app(app)

    from app.auth.routes import auth
    from app.main.routes import main
    app.register_blueprint(auth)
    app.register_blueprint(main)

    # from app.main.errors import page_not_found
    # app.register_error_handler(404, page_not_found)

    return app