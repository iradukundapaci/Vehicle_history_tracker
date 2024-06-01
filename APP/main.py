import logging
import os
import pandas as pd

from datetime import datetime, timedelta
from Data_handling_scripts.DataHandler import DataHandler
from Data_handling_scripts.WebScraper import Scraper
from Data_handling_scripts.MessageHandle import MessageHandler

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
    """
    Cleans the report by renaming and cleaning the file using the DataHandler class.

    Returns:
        bool: True if the report cleaning is successful, False otherwise.
    """
    try:
        handler = DataHandler()
        logging.info("Report cleaning completed.")
        return handler.rename_and_clean_file()
    except Exception as e:
        logging.error(f"An error occurred during report cleaning: {e}")
        return None


def main():
    try:
        user_email = "rutamizabiri@satorrwanda.rw"
        password = "8266"
        plate_number = "RAC 151 S"

        download_success = download_report(user_email, password, plate_number)
        if download_success:
            file_path = clean_report()
            if file_path:
                messanger = MessageHandler(file_path)
                response = messanger.send_whatsapp_message(
                    messanger.get_summary_message()
                )
                if response:
                    logging.info("Message sent successfully.")
                    logging.info("All tasks completed successfully.")
                else:
                    logging.error("Message sending failed.")
            else:
                logging.error("Report cleaning failed.")
        else:
            logging.error("Report download failed.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
