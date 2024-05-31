import requests
import cmd


class VehicleTrackerCLI(cmd.Cmd):
    intro = "Welcome to Vehicle Tracker CLI. Type help or ? to list commands.\n"
    prompt = "> "

    def __init__(self):
        super().__init__()
        self.jwt_token = None

    def do_login(self, arg):
        """Login to the system"""
        username = input("Enter username: ")
        password = input("Enter password: ")
        response = requests.post(
            "http://localhost:5000/api/login",
            json={"userName": username, "password": password},
        )
        if response.status_code == 200:
            self.jwt_token = response.json()["access_token"]
            print("Login successful")
        else:
            print("Login failed")

    def do_signup(self, arg):
        """Sign up for a new account"""
        # Similar logic to login for signup

    def do_logout(self, arg):
        """Logout from the system"""
        self.jwt_token = None
        print("Logged out")

    def do_add_account(self, arg):
        """Add account username and password"""
        # Similar logic to login for add_account

    def do_add_vehicle(self, arg):
        """Add vehicle Plate Number"""
        plate_number = input("Enter plate number: ")
        response = requests.post(
            "http://localhost:5000/vehicle_plate",
            json={"sator_account_id": 1, "plate_number": plate_number},
            headers={"Authorization": f"Bearer {self.jwt_token}"},
        )
        if response.status_code == 201:
            print("Vehicle plate number added successfully")
        else:
            print("Failed to add vehicle plate number")

    # Implement other methods similarly for other functionalities

    def do_exit(self, arg):
        """Exit the program"""
        print("Exiting Vehicle Tracker CLI")
        return True


if __name__ == "__main__":
    VehicleTrackerCLI().cmdloop()
