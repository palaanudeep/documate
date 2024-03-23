import os
from os.path import join, dirname
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("FLASK_SECRET_KEY"),
        SQLALCHEMY_DATABASE_URI=f'postgresql://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@localhost/documate',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        DEBUG=True
    )
    CORS(app)
    db.init_app(app)

    from app.auth.routes import auth
    from app.main.routes import main
    app.register_blueprint(auth)
    app.register_blueprint(main)

    # from app.main.errors import page_not_found
    # app.register_error_handler(404, page_not_found)

    return app