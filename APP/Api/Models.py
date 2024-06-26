from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    """
    User model for tables mapping
    """

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    whatsappNumber = db.Column(db.String(15), unique=True, nullable=False)
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
    """
    Sator Account model for tables mapping
    """

    __tablename__ = "sator_accounts"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    names = db.Column(db.String(200), nullable=False)
    userName = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    user = db.relationship("User", back_populates="sator_account")
    vehicles = db.relationship(
        "Vehicle", back_populates="sator_account", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<SatorAccount {self.userName}>"


class Vehicle(db.Model):
    """
    Vehicle model for tables mapping
    """

    __tablename__ = "vehicle"
    id = db.Column(db.Integer, primary_key=True)
    vehicleType = db.Column(db.String(20), nullable=False)
    plateNumber = db.Column(db.String(20), unique=True, nullable=False)
    sator_account_id = db.Column(
        db.Integer, db.ForeignKey("sator_accounts.id"), nullable=False
    )
    sator_account = db.relationship("SatorAccount", back_populates="vehicles")

    def __repr__(self):
        return f"<VehiclePlate {self.plateNumber}>"
