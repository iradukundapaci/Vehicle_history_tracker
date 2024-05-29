import logging
import os
from data_handler import DataHandler  # Ensure this imports the correct class
from send_whatsapp_message import (
    send_whatsapp_message,
)  # Ensure this imports the correct function

# Configure logging
logging.basicConfig(
    filename="main.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def download_report():
    logging.info("Starting report download...")
    handler = DataHandler()
    result = handler.rename_and_clean_file()
    if result:
        logging.info("Report download completed successfully.")
    else:
        logging.error("Report download failed.")


def clean_report():
    logging.info("Starting report cleaning...")
    handler = DataHandler()
    file_path = os.path.join(
        handler.CLEANED_DATA_FOLDER, "example.csv"
    )  # Update with the correct file path
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        handler.process_daily_data(df, file_path)
        logging.info("Report cleaning completed.")
    else:
        logging.error(f"File {file_path} does not exist.")


def main():
    try:
        download_report()
        clean_report()
        send_whatsapp_message()
        logging.info("All tasks completed successfully.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
