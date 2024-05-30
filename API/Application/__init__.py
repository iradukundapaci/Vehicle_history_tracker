import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    # Configure the SQLAlchemy part of the app instance
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{os.getenv('DATABASE_USER')}:{os.getenv('DATABASE_PASSWORD')}@{os.getenv('DATABASE_HOST')}/{os.getenv('DATABASE_NAME')}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize the SQLAlchemy extension
    db.init_app(app)

    with app.app_context():
        from .Models import User, SatorAccount, VehiclePlate

        db.create_all()

    return app
