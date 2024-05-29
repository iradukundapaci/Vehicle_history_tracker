import logging
import os
import pandas as pd

from datetime import datetime, timedelta
from Data_handling_scripts.DataHandler import DataHandler
from Data_handling_scripts.WebScraper import Scraper

# from .DataHandler import DataHandler

# Configure logging
logging.basicConfig(
    filename="main.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def download_report(user_email, password, plate_number):
    logging.info("Starting report download...")
    try:
        with Scraper(user_email, password, plate_number) as scraper:
            login_success = scraper.login()
            if login_success:
                scraper.fill_fields_and_download()
                logging.info("Report download completed successfully.")
            else:
                logging.error("Report download failed.")
                return False
    except Exception as e:
        logging.error(f"An error occurred during report download: {e}")
        return False
    return True


def clean_report():
    logging.info("Starting report cleaning...")
    try:
        handler = DataHandler()
        if handler.rename_and_clean_file():
            logging.info("Report cleaning completed.")
        else:
            logging.error("Report cleaning failed")
            return False
    except Exception as e:
        logging.error(f"An error occurred during report cleaning: {e}")
        return False
    return True


def main():
    try:
        user_email = "rutamizabiri@satorrwanda.rw"  # Replace with actual user email
        password = "8266"  # Replace with actual password
        plate_number = "RAC 151 S"  # Replace with actual plate number

        download_success = download_report(user_email, password, plate_number)
        if download_success:
            if clean_report():
                logging.info("All tasks completed successfully.")
            else:
                logging.error("Report cleaning failed.")
        else:
            logging.error("Report download failed.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
