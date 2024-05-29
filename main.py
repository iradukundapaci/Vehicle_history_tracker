import logging
import os
import pandas as pd

from datetime import datetime, timedelta
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


# def clean_report(file_path):
#     logging.info("Starting report cleaning...")
#     try:
#         handler = DataHandler()
#         if os.path.exists(file_path):
#             df = pd.read_csv(file_path)
#             handler.process_daily_data(df, file_path)
#             logging.info("Report cleaning completed.")
#         else:
#             logging.error(f"File {file_path} does not exist.")
#             return False
#     except Exception as e:
#         logging.error(f"An error occurred during report cleaning: {e}")
#         return False
#     return True


def main():
    try:
        user_email = "rutamizabiri@satorrwanda.rw"  # Replace with actual user email
        password = "8266"  # Replace with actual password
        plate_number = "RAC 151 S"  # Replace with actual plate number

        download_success = download_report(user_email, password, plate_number)
        # if download_success:
        #     handler = DataHandler()
        #     file_path = os.path.join(
        #         handler.CLEANED_DATA_FOLDER, "example.csv"
        #     )  # Update with the correct file path
        #     clean_success = clean_report(file_path)
        #     if clean_success:
        #         send_whatsapp_message()
        #         logging.info("All tasks completed successfully.")
        #     else:
        #         logging.error("Report cleaning failed.")
        # else:
        #     logging.error("Report download failed.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
