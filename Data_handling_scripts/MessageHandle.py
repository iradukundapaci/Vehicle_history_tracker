import pandas as pd
import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()


class MessageHandler:
    """
    A class to handle the processing of vehicle movement data and sending summarized messages via WhatsApp.

    Attributes:
        df (pd.DataFrame): The input dataframe containing vehicle movement data.
        report_date (str): The date of the report based on the first entry in the dataframe.
        summary (pd.DataFrame): The summarized dataframe grouped by ADM2 and ADM3 with start and end times.
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initializes the MessageHandler with a dataframe and processes the data.

        Args:
            df (pd.DataFrame): The input dataframe containing vehicle movement data.
        """
        self.df = self.load_and_prepare_data(df)
        self.report_date = self.get_report_date()
        self.summary = self.summarize_by_location()

    def load_and_prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Converts the 'Date Recorded' column to datetime in the dataframe.

        Args:
            df (pd.DataFrame): The input dataframe containing vehicle movement data.

        Returns:
            pd.DataFrame: The dataframe with 'Date Recorded' column converted to datetime.
        """
        # Convert 'Date Recorded' to datetime
        df["Date Recorded"] = pd.to_datetime(df["Date Recorded"])
        return df

    def get_report_date(self) -> str:
        """
        Extracts the report date from the dataframe.

        Returns:
            str: The report date in 'YYYY-MM-DD' format.
        """
        # Get the report date (assuming the date of the first entry)
        report_date = self.df["Date Recorded"].dt.date.iloc[0].strftime("%Y-%m-%d")
        return report_date

    def summarize_by_location(self) -> pd.DataFrame:
        """
        Summarizes the dataframe by grouping by ADM2 and ADM3, and calculating start and end times.

        Returns:
            pd.DataFrame: The summarized dataframe.
        """
        # Group by location and summarize the times
        summary = (
            self.df.groupby(["ADM2", "ADM3"])
            .agg({"Date Recorded": ["min", "max"]})
            .reset_index()
        )
        # Rename the columns for clarity
        summary.columns = ["ADM2", "ADM3", "Start Time", "End Time"]
        return summary

    def format_summary_message(self) -> str:
        """
        Formats the summary of vehicle movements as a string message.

        Returns:
            str: The formatted summary message.
        """
        # Sort the summary by 'Start Time'
        self.summary.sort_values(by="Start Time", inplace=True)

        # Format the summary as a string, limiting to 10 lines
        summary_message = (
            f"Summary of Vehicle Movements by Location on {self.report_date}:\n"
        )

        # Ensure the first and last lines are included and extract the middle 8 lines
        first_row = self.summary.iloc[0]
        last_row = self.summary.iloc[-1]
        middle_rows = self.summary.iloc[1:-1].head(8)

        # Format the first line
        summary_message += self.format_row(first_row)

        # Format the middle 8 lines
        for _, row in middle_rows.iterrows():
            summary_message += self.format_row(row)

        # Format the last line
        summary_message += self.format_row(last_row)

        return summary_message

    def format_row(self, row: pd.Series) -> str:
        """
        Formats a single row of the summary dataframe as a string.

        Args:
            row (pd.Series): A row of the summary dataframe.

        Returns:
            str: The formatted string of the row.
        """
        location = f"{row['ADM2']}, {row['ADM3']}"
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
        message = client.messages.create(
            from_="whatsapp:+14155238886",
            body=message,
            to=f"whatsapp:{receiver_number}",
        )
        if message:
            return True
        else:
            return False
