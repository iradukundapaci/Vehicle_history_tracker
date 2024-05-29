#!/usr/bin/python3
"""
Module to rename, clean and move downloaded GPS data files
"""

import os
import pandas as pd
import logging
import requests
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    filename="data_handler.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class DataHandler:
    """
    Class to handle downloaded data
    """

    BASE_FILE_NAME = "m_tracking"
    DOWNLOAD_FOLDER_PATH = os.getenv("DOWNLOAD_DIR")
    CLEANED_DATA_FOLDER = os.getenv("CLEAN_DATA_DIR")
    PROCESSED_DATA_FOLDER = os.getenv("PROCESSED_DATA_DIR")
    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
    TILESET_ID = os.getenv("TILESET_ID")

    def rename_and_clean_file(self) -> bool:
        """
        Search for yesterday downloaded files for renaming and cleaning

        return: True if files have been renamed and cleaned
        """
        if not os.path.exists(self.DOWNLOAD_FOLDER_PATH):
            logging.error("Download folder not found")
            return False

        file_names = [
            file
            for file in os.listdir(self.DOWNLOAD_FOLDER_PATH)
            if os.path.isfile(os.path.join(self.DOWNLOAD_FOLDER_PATH, file))
            and file.startswith(self.BASE_FILE_NAME)
        ]

        success = True

        for file_name in file_names:
            try:
                file_path = os.path.join(self.DOWNLOAD_FOLDER_PATH, file_name)
                dataframe = pd.read_csv(file_path, skiprows=2)

                new_file_path = self.construct_new_file_path(dataframe)
                dataframe = self.drop_columns(dataframe)
                self.save_file(new_file_path, dataframe)
                self.process_daily_data(dataframe, new_file_path)
                self.delete_file(file_path, new_file_path)

                logging.info(f"File {new_file_path} renamed and cleaned successfully")
            except Exception as e:
                logging.error(f"Error processing file {file_name}: {e}")
                success = False

        return success

    def construct_new_file_path(self, dataframe: pd.DataFrame) -> str:
        """
        Construct new file path from dataframe

        return: new file path
        """
        try:
            vehicle_owner = dataframe["Owner"][0]
            license_plate = dataframe["Name"][0]
            data_date = dataframe["Date Recorded"][0].split()[0]
            year, month = data_date.split("-")[0], data_date.split("-")[1]
            vehicle_type = dataframe["Type"][0][:-1]
            new_file_name = f"{vehicle_owner}/{vehicle_type}/{license_plate}/{year}/{month}/{data_date}.csv"
            new_file_path = os.path.join(self.CLEANED_DATA_FOLDER, new_file_name)
            return new_file_path
        except KeyError as e:
            logging.error(f"Missing expected column in the dataframe: {e}")
            raise

    def save_file(self, file_path: str, dataframe: pd.DataFrame) -> None:
        """
        Save cleaned dataframe to the specified path
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            dataframe.to_csv(file_path, index=False)
            logging.info(f"Saved file {file_path}")
        except Exception as e:
            logging.error(f"Error saving file {file_path}: {e}")
            raise

    def drop_columns(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Drop unecessary columns and replace the Position column data

        args:
            data: dataframe of csv

        return: cleaned data frame
        """
        try:
            # Drop unnecessary columns
            data.drop(
                ["Name", "Serial Number", "Type", "Speed", "Owner"],
                axis=1,
                inplace=True,
            )

            # Replace Position values
            data["Position"] = data["Position"].replace({1: "Moving", 0: "Stopped"})

            logging.info(f"Dropped unnecesary columns")
            return data
        except Exception as e:
            logging.error(f"Error droping columns: {e}")
            raise

    def delete_file(self, file_path: str, name_of_file: str) -> None:
        """
        Delete the specified file
        """
        try:
            os.remove(file_path)
            logging.info(f"Deleted file {name_of_file}")
        except Exception as e:
            logging.error(f"Error deleting file {file_path}: {e}")
            raise

    def process_daily_data(self, data: pd.DataFrame, file_path: str) -> bool:
        """
        Process yesterday downloaded GPS data for all users
        """
        processed_data = []
        new_file_path = file_path.replace("CleanData", "ProcessedData")
        logging.info(f"Processing the cleaned data for {file_path}")
        data = data.drop_duplicates(subset=["Latitude", "Longitude"])

        for _, row in data.iterrows():
            try:
                longitude = row["Longitude"]
                latitude = row["Latitude"]
                position = row["Position"]
                date_recorded = row["Date Recorded"]

                response = self.get_location(longitude, latitude)
                if response:
                    location = self.extract_locations(response)
                    processed_data.append(
                        {
                            **location,
                            "Position": position,
                            "Date Recorded": date_recorded,
                        }
                    )
            except KeyError as e:
                logging.error(f"Missing expected column in the row: {e}")
            except Exception as e:
                logging.error(f"Error processing row: {e}")

        processed_df = pd.DataFrame(processed_data)

        try:
            self.save_file(new_file_path, processed_df)
        except Exception as e:
            logging.error(f"Error saving processed file {new_file_path}: {e}")
            return False

        return True

    def get_location(self, longitude: float, latitude: float) -> List[Dict[str, Any]]:
        """
        Turn coordinates into a human-readable address
        return: address as a JSON response
        """
        try:
            # Construct the URL
            url = f"https://api.mapbox.com/v4/{self.TILESET_ID}/tilequery/{longitude},{latitude}.json"

            # Define the parameters
            params = {
                "radius": 25,
                "limit": 5,
                "dedupe": True,
                "access_token": self.ACCESS_TOKEN,
            }

            # Send the GET request
            response = requests.get(url, params=params)

            # Check if the request was successful
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching location data: {e}")
            return None

    def extract_locations(self, response: Dict[str, Any]) -> Dict[str, str]:
        """
        Parse the retrieved json response and get the locations

        args:
            response: json response from map box

        return: dictionary of location
        """
        try:
            adm_levels = {}

            for feature in response["features"]:
                level = feature["properties"].get("Level")
                shape_name = feature["properties"].get("shapeName")
                if level and shape_name:
                    adm_levels[level] = shape_name

            return adm_levels
        except KeyError as e:
            logging.error(f"Missing expected key in the response: {e}")
            return {}
