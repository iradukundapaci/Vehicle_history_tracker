from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    whatsappNmber = db.Column(db.String(15), unique=True, nullable=False)
    userName = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(250), nullable=False)
    sator_account = db.relationship(
        "SatorAccount", back_populates="user", uselist=False
    )

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.userName}>"


class SatorAccount(db.Model):
    __tablename__ = "sator_accounts"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    userName = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    user = db.relationship("User", back_populates="sator_account")
    vehicle_plates = db.relationship(
        "VehiclePlate", back_populates="sator_account", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<SatorAccount {self.userName}>"


class VehiclePlate(db.Model):
    __tablename__ = "vehicle_plates"
    id = db.Column(db.Integer, primary_key=True)
    plateNumber = db.Column(db.String(20), unique=True, nullable=False)
    sator_account_id = db.Column(
        db.Integer, db.ForeignKey("sator_accounts.id"), nullable=False
    )
    sator_account = db.relationship("SatorAccount", back_populates="vehicle_plates")

    def __repr__(self):
        return f"<VehiclePlate {self.plateNumber}>"
