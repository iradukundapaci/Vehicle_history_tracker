from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from .Models import db, User, SatorAccount, VehiclePlate

api = Blueprint("api", __name__)


# Signup route
@api.route("/signup", methods=["POST"])
def signup():
    data = request.json
    firstName = data.get("firstName")
    lastName = data.get("lastName")
    email = data.get("email")
    userName = data.get("userName")
    password = data.get("password")

    if (
        User.query.filter_by(email=email).first()
        or User.query.filter_by(userName=userName).first()
    ):
        return jsonify({"message": "User already exists"}), 400

    new_user = User(
        firstName=firstName,
        lastName=lastName,
        email=email,
        userName=userName,
        password_hash=generate_password_hash(password),
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201


# Login route to get JWT
@api.route("/login", methods=["POST"])
def login():
    data = request.json
    userName = data.get("userName")
    password = data.get("password")

    user = User.query.filter_by(userName=userName).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200


# Add Sator Account
@api.route("/sator_account", methods=["POST"])
@jwt_required()
def add_sator_account():
    current_user_id = get_jwt_identity()
    data = request.json
    userName = data.get("userName")
    password = data.get("password")

    sator_account = SatorAccount(
        user_id=current_user_id, userName=userName, password=password
    )
    db.session.add(sator_account)
    db.session.commit()

    return jsonify({"message": "Sator account added successfully"}), 201


# Add Vehicle Plate Number
@api.route("/vehicle_plate", methods=["POST"])
@jwt_required()
def add_vehicle_plate():
    current_user_id = get_jwt_identity()
    data = request.json
    sator_account_id = data.get("sator_account_id")
    plate_number = data.get("plate_number")

    sator_account = SatorAccount.query.get(sator_account_id)
    if not sator_account or sator_account.user_id != current_user_id:
        return jsonify({"message": "Sator account not found"}), 404

    vehicle_plate = VehiclePlate(
        sator_account_id=sator_account_id, plateNumber=plate_number
    )
    db.session.add(vehicle_plate)
    db.session.commit()

    return jsonify({"message": "Vehicle plate number added successfully"}), 201


# Delete Vehicle Plate Number
@api.route("/vehicle_plate/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_vehicle_plate(id):
    current_user_id = get_jwt_identity()
    vehicle_plate = VehiclePlate.query.get(id)
    if not vehicle_plate or vehicle_plate.sator_account.user_id != current_user_id:
        return jsonify({"message": "Vehicle plate number not found"}), 404

    db.session.delete(vehicle_plate)
    db.session.commit()

    return jsonify({"message": "Vehicle plate number deleted successfully"}), 200


# Update Vehicle Plate Number
@api.route("/vehicle_plate/<int:id>", methods=["PUT"])
@jwt_required()
def update_vehicle_plate(id):
    current_user_id = get_jwt_identity()
    data = request.json
    new_plate_number = data.get("plate_number")

    vehicle_plate = VehiclePlate.query.get(id)
    if not vehicle_plate or vehicle_plate.sator_account.user_id != current_user_id:
        return jsonify({"message": "Vehicle plate number not found"}), 404

    vehicle_plate.plateNumber = new_plate_number
    db.session.commit()

    return jsonify({"message": "Vehicle plate number updated successfully"}), 200


# See Report Based on Given Dates and Time
@api.route("/report", methods=["GET"])
@jwt_required()
def see_report():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    # Assume we have a function to generate the report
    report = generate_report(start_date, end_date)

    return jsonify(report), 200


# Download Report Based on Dates and Time
@api.route("/download_report", methods=["GET"])
@jwt_required()
def download_report():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    # Assume we have a function to generate and return the report file
    report_file = generate_report_file(start_date, end_date)

    return (
        jsonify({"message": "Report file generated successfully", "file": report_file}),
        200,
    )


def generate_report(start_date, end_date):
    # Mock implementation, replace with actual report generation logic
    return {"start_date": start_date, "end_date": end_date, "data": []}


def generate_report_file(start_date, end_date):
    # Mock implementation, replace with actual report file generation logic
    return "/path/to/report/file.csv"
