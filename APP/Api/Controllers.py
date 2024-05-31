from flask import send_file
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from .Models import db, User, SatorAccount, Vehicle
from Data_handling_scripts.DataHandler import DataHandler

api = Blueprint("api", __name__)


# Signup route
@api.route("/signup", methods=["POST"])
def signup():
    """
    User signup handler
    """
    data = request.json
    firstName = data.get("firstName")
    lastName = data.get("lastName")
    email = data.get("email")
    whatsappNumber = data.get("whatsappNumber")
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
        whatsappNumber=whatsappNumber,
        userName=userName,
        password_hash=generate_password_hash(password),
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201


# Login route to get JWT
@api.route("/login", methods=["POST"])
def login():
    """
    User login handler
    """
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
    """
    Add sator account
    """
    current_user_id = get_jwt_identity()
    data = request.json
    names = data.get("names")
    userName = data.get("userName")
    password = data.get("password")

    sator_account = SatorAccount(
        user_id=current_user_id,
        names=names,
        userName=userName,
        password=password,
    )
    db.session.add(sator_account)
    db.session.commit()

    return jsonify({"message": "Sator account added successfully"}), 201


# Update Sator Account
@api.route("/sator_account/<int:id>", methods=["PUT"])
@jwt_required()
def update_sator_account(id):
    """
    Update Sator account
    """
    current_user_id = get_jwt_identity()
    data = request.json
    new_names = data.get("names")
    new_userName = data.get("userName")
    new_password = data.get("password")

    # Find the Sator account by ID
    sator_account = SatorAccount.query.get(id)
    if not sator_account or sator_account.user_id != current_user_id:
        return jsonify({"message": "Sator account not found"}), 404

    # Update the fields
    sator_account.userName = new_userName if new_userName else sator_account.userName
    sator_account.names = new_names if new_names else sator_account.names
    sator_account.password = new_password if new_password else sator_account.password

    db.session.commit()

    return jsonify({"message": "Sator account updated successfully"}), 200


# View Sator Account Details
@api.route("/sator_account", methods=["GET"])
@jwt_required()
def view_sator_account():
    """
    View Sator account details
    """
    current_user_id = get_jwt_identity()

    # Find the Sator account associated with the current user
    sator_account = SatorAccount.query.filter_by(user_id=current_user_id).first()
    if not sator_account:
        return jsonify({"message": "Sator account not found"}), 404

    # Return the Sator account details
    account_details = {
        "id": sator_account.id,
        "names": sator_account.names,
        "userName": sator_account.userName,
        "password": sator_account.password,
    }

    return jsonify({"sator_account": account_details}), 200


# Add Vehicle
@api.route("/vehicle", methods=["POST"])
@jwt_required()
def add_vehicle():
    """
    Add vehicle
    """
    current_user_id = get_jwt_identity()
    data = request.json
    plate_number = data.get("plate_number")
    vehicle_type = data.get("vehicle_type")

    # Find the Sator account using the current user ID
    sator_account = SatorAccount.query.filter_by(user_id=current_user_id).first()
    if not sator_account:
        return jsonify({"message": "Sator account not found"}), 404

    vehicle = Vehicle(
        sator_account_id=sator_account.id,
        plateNumber=plate_number,
        vehicleType=vehicle_type,
    )
    db.session.add(vehicle)
    db.session.commit()

    return jsonify({"message": "Vehicle added successfully"}), 201


# Delete Vehicle
@api.route("/vehicle/<string:plate_number>", methods=["DELETE"])
@jwt_required()
def delete_vehicle(plate_number):
    """
    Delete vehicle based on the plate number
    """
    current_user_id = get_jwt_identity()

    # Find the vehicle plate using the plate number and ensure it belongs to the current user's Sator account
    vehicle = (
        Vehicle.query.join(SatorAccount)
        .filter(
            Vehicle.plateNumber == plate_number,
            SatorAccount.user_id == current_user_id,
        )
        .first()
    )

    if not vehicle:
        return jsonify({"message": "Vehicle not found"}), 404

    db.session.delete(vehicle)
    db.session.commit()

    return jsonify({"message": "Vehicle deleted successfully"}), 200


# Route to see all vehicles registered under a user
@api.route("/user/vehicles", methods=["GET"])
@jwt_required()
def get_user_vehicles():
    """
    Endpoint to get all vehicles registered under the current user

    Returns:
        JSON containing the list of vehicles
    """
    current_user_id = get_jwt_identity()

    # Retrieve the sator account associated with the current user
    sator_account = SatorAccount.query.filter_by(user_id=current_user_id).first()
    if not sator_account:
        return jsonify({"message": "Sator account not found"}), 404

    # Retrieve all vehicle plates associated with the sator account
    vehicles = Vehicle.query.filter_by(sator_account_id=sator_account.id).all()
    if not vehicles:
        return jsonify({"message": "No vehicles found"}), 404

    # Create a list of vehicle details
    vehicle_list = []
    for vehicle in vehicles:
        vehicle_details = {
            "id": vehicle.id,
            "plate_number": vehicle.plateNumber,
            "vehicle_type": vehicle.vehicleType,  # Assuming vehicleType is a field
        }
        vehicle_list.append(vehicle_details)

    return jsonify({"vehicles": vehicle_list}), 200


# Update Vehicle Plate Number and Vehicle Type
@api.route("/vehicle/<string:plate_number>", methods=["PUT"])
@jwt_required()
def update_vehicle(plate_number):
    """
    Update vehicle plate number and vehicle type based on the plate number
    """
    current_user_id = get_jwt_identity()
    data = request.json
    new_plate_number = data.get("plate_number")
    new_vehicle_type = data.get("vehicle_type")

    # Find the vehicle plate using the plate number and ensure it belongs to the current user's Sator account
    vehicle = (
        Vehicle.query.join(SatorAccount)
        .filter(
            Vehicle.plateNumber == plate_number,
            SatorAccount.user_id == current_user_id,
        )
        .first()
    )

    if not vehicle:
        return jsonify({"message": "Vehicle plate number not found"}), 404

    # Update the fields if provided in the request
    vehicle.plateNumber = new_plate_number if new_plate_number else vehicle.plateNumber
    vehicle.vehicleType = new_vehicle_type if new_vehicle_type else vehicle.vehicleType

    db.session.commit()

    return (
        jsonify(
            {"message": "Vehicle plate number and vehicle type updated successfully"}
        ),
        200,
    )


# Download Report Based on Date
@api.route("/download_report", methods=["GET"])
@jwt_required()
def download_report():
    """
    Endpoint for downloading report based on date

    Returns:
        JSON containing the message and the report file
    """
    # Extract the required parameters from the query string
    vehicle_id = request.args.get("vehicle_id")
    date = request.args.get("date")

    # Ensure all required parameters are provided
    if not vehicle_id or not date:
        return (
            jsonify({"message": f"Missing required parameters {vehicle_id} {date}"}),
            400,
        )

    # Retrieve vehicle and account details from the database
    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        return jsonify({"message": "Vehicle not found"}), 404

    sator_account = SatorAccount.query.get(vehicle.sator_account_id)
    if not sator_account:
        return jsonify({"message": "Sator account not found"}), 404

    vehicle_owner = sator_account.names
    vehicle_type = vehicle.vehicleType
    license_plate = vehicle.plateNumber
    data_handler = DataHandler()

    # Generate the report file based on the provided parameters
    report_file_path = data_handler.generate_report_file(
        vehicle_owner, vehicle_type, license_plate, date
    )

    if not report_file_path:
        return (
            jsonify(
                {
                    "message": f"Report generation failed for {vehicle_owner} {vehicle_type} {license_plate} {date}"
                }
            ),
            500,
        )

    # Load the file and send it for download
    try:
        return send_file(
            report_file_path,
            as_attachment=True,
            mimetype="text/csv",
        )
    except Exception as e:
        return jsonify({"message": f"Failed to send file: {str(e)}"}), 500
