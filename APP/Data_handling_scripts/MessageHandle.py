import pandas as pd
import os
import logging
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

# Configure logging to write to a file
logging.basicConfig(
    filename="message_handler.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="w",
)


class MessageHandler:
    """
    A class to handle the processing of vehicle movement data and sending summarized messages via WhatsApp.

    Attributes:
        df (pd.DataFrame): The input dataframe containing vehicle movement data.
        report_date (str): The date of the report based on the first entry in the dataframe.
        summary (pd.DataFrame): The summarized dataframe grouped by District and Sector with start and end times.
    """

    def __init__(self, file_path: str):
        """
        Initializes the MessageHandler with a file path and processes the data.

        Args:
            file_path (str): The file path to the CSV containing vehicle movement data.
        """
        logging.info(f"Initializing MessageHandler with file: {file_path}")
        self.df = self.load_and_prepare_data(file_path)
        self.report_date = self.get_report_date()
        self.summary = self.summarize_by_location()

    def load_and_prepare_data(self, file_path: str) -> pd.DataFrame:
        """
        Loads the dataframe from a CSV file and converts the 'Date Recorded' column to datetime.

        Args:
            file_path (str): The file path to the CSV containing vehicle movement data.

        Returns:
            pd.DataFrame: The dataframe with 'Date Recorded' column converted to datetime.
        """
        logging.info(f"Loading data from file: {file_path}")
        df = pd.read_csv(file_path)
        df["Date Recorded"] = pd.to_datetime(df["Date Recorded"])
        logging.info("Data loaded and 'Date Recorded' column converted to datetime")
        return df

    def get_report_date(self) -> str:
        """
        Extracts the report date from the dataframe.

        Returns:
            str: The report date in 'YYYY-MM-DD' format.
        """
        report_date = self.df["Date Recorded"].dt.date.iloc[0].strftime("%Y-%m-%d")
        logging.info(f"Report date determined: {report_date}")
        return report_date

    def summarize_by_location(self) -> pd.DataFrame:
        """
        Summarizes the dataframe by grouping by District and Sector, and calculating start and end times.

        Returns:
            pd.DataFrame: The summarized dataframe.
        """
        logging.info("Summarizing data by location")
        summary = (
            self.df.groupby(["District", "Sector"])
            .agg({"Date Recorded": ["min", "max"]})
            .reset_index()
        )
        summary.columns = ["District", "Sector", "Start Time", "End Time"]
        return summary

    def get_summary_message(self) -> str:
        """
        Formats the summary of vehicle movements as a string message.

        Returns:
            str: The formatted summary message.
        """
        logging.info("Generating summary message")
        self.summary.sort_values(by="Start Time", inplace=True)

        summary_message = (
            f"Summary of Vehicle Movements by Location on {self.report_date}:\n"
        )
        first_row = self.summary.iloc[0]
        last_row = self.summary.iloc[-1]
        middle_rows = self.summary.iloc[1:-1].head(8)

        summary_message += self.format_row(first_row)
        for _, row in middle_rows.iterrows():
            summary_message += self.format_row(row)
        summary_message += self.format_row(last_row)

        logging.info("Summary message generated")
        return summary_message

    def format_row(self, row: pd.Series) -> str:
        """
        Formats a single row of the summary dataframe as a string.

        Args:
            row (pd.Series): A row of the summary dataframe.

        Returns:
            str: The formatted string of the row.
        """
        location = f"{row['District']}, {row['Sector']}"
        start_time = row["Start Time"].strftime("%H:%M")
        end_time = row["End Time"].strftime("%H:%M")
        return f"{location}: {start_time} -- {end_time}\n"

    def send_whatsapp_message(
        self, message: str, receiver_number: str = "+250782669679"
    ) -> bool:
        """
        Sends a WhatsApp message using Twilio's API.

        Args:
            message (str): The message to send.
            receiver_number (str, optional): The receiver's WhatsApp number. Defaults to "+250782669679".

        Returns: True if message is sent
        """
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        client = Client(account_sid, auth_token)
        try:
            logging.info("Sending WhatsApp message")
            message = client.messages.create(
                from_="whatsapp:+14155238886",
                body=message,
                to=f"whatsapp:{receiver_number}",
            )
            logging.info("WhatsApp message sent successfully")
            return True
        except Exception as e:
            logging.error(f"Failed to send WhatsApp message: {e}")
            return False
