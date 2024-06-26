from datetime import timedelta
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from .Models import db
from dotenv import load_dotenv

load_dotenv()

jwt = JWTManager()


def create_app():
    app = Flask(__name__)

    # Verify environment variables
    database_user = os.getenv("DATABASE_USER")
    database_password = os.getenv("DATABASE_PASSWORD")
    database_host = os.getenv("DATABASE_HOST")
    database_name = os.getenv("DATABASE_NAME")
    jwt_secret_key = os.getenv("JWT_SECRET_KEY")

    if not all(
        [database_user, database_password, database_host, database_name, jwt_secret_key]
    ):
        raise ValueError("One or more environment variables are missing")

    # Configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{database_user}:{database_password}@{database_host}/{database_name}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = jwt_secret_key
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)

    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        # Create tables
        db.create_all()

        from .Controllers import api

        app.register_blueprint(api, url_prefix="/api")

    return app
