import pandas as pd
import os
from dotenv import load_dotenv
from twilio.rest import Client

from Data_handling_scripts.DataHandler import DataHandler

# Load environment variables from .env file
load_dotenv()


# Load the CSV file
df = pd.read_csv(
    "/home/paci/tracer/Vehicle_history_tracker/ProcessedData/RUTAMIZABIRI JEAN DAMASCENE/Lorry Truck/RAC 151 S/2024/05/2024-05-28.csv"
)

handler = DataHandler()
file_path = handler.generate_report_file(
    "RUTAMIZABIRI JEAN DAMASCENE", "Lorry Truck", "RAC 151 S", "2024-05-28"
)
print(file_path)
