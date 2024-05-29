#!/usr/bin/python3
"""
Webscraper to retrieve the GPS data from
sator website
"""

import logging
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    WebDriverException,
    TimeoutException,
)
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta

logging.basicConfig(
    filename="scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class Scraper:
    """
    Web scraper class to handle data retrieval
    """

    URL = "https://track.satorrwanda.rw:8443/login/admin"
    USER_EMAIL_BY_NAME = "username"
    PASSWORD_BY_NAME = "password"
    LOGIN_BUTTON_BY_SELECTOR = "[type=submit]"
    REPORT_BY_SELECTOR = "[href=reportsu]"
    PLATE_NUMBER_FIELD_BY_NAME = "_plateNo"
    START_DATE_TIME_BY_NAME = "startdate"
    END_DATE_TIME_BY_NAME = "enddate"
    DOWNLOAD_BUTTON_BY_NAME = "export_custom"
    START_DATE = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d 00:00")
    END_DATE = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d 23:55")

    def __init__(self, user_email: str, password: str, plate_number: str) -> None:
        """
        Initialize scraper object
        args:
            user_email: sator account userEmail
            password: sator account password
            plate_number: vehicle plate number
        """
        self.user_email = user_email
        self.password = password
        self.plate_number = plate_number
        self.driver = None

    def __enter__(self):
        self.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install())
        )
        self.driver.get(self.URL)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.driver:
            self.driver.quit()
            logging.info("Browser closed successfully")

    def login(self) -> bool:
        """
        Handles user login
        return: True for success and False for failure
        """
        logging.info(f"Logging in for username: {self.user_email}")
        try:
            user_email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, self.USER_EMAIL_BY_NAME))
            )
            password_field = self.driver.find_element(By.NAME, self.PASSWORD_BY_NAME)
            login_button = self.driver.find_element(
                By.CSS_SELECTOR, self.LOGIN_BUTTON_BY_SELECTOR
            )

            user_email_field.clear()
            user_email_field.send_keys(self.user_email)
            password_field.clear()
            password_field.send_keys(self.password)
            login_button.click()

            report_link = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.REPORT_BY_SELECTOR)
                )
            )
            report_link.click()

            return True
        except (NoSuchElementException, TimeoutException) as e:
            logging.error(
                f"Element not found during login for username {self.user_email}: {e}"
            )
            return False
        except WebDriverException as e:
            logging.error(
                f"WebDriver error during login for username {self.user_email}: {e}"
            )
            return False

    def fill_fields_and_download(
        self, start_date: str = None, end_date: str = None
    ) -> bool:
        """
        Filling custom report form and downloading report.
        Args:
            start_date: The start date/time for the report (format: 'YYYY-MM-DD HH:MM').
            end_date: The end date/time for the report (format: 'YYYY-MM-DD HH:MM').
        return: True if form is downloaded
        """
        start_date = start_date or self.START_DATE
        end_date = end_date or self.END_DATE

        logging.info(
            f"Filling fields and downloading report for plate number: {self.plate_number} from {start_date} to {end_date}"
        )
        try:
            plate_number_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.NAME, self.PLATE_NUMBER_FIELD_BY_NAME)
                )
            )
            plate_number_select = Select(plate_number_field)
            start_date_field = self.driver.find_element(
                By.NAME, self.START_DATE_TIME_BY_NAME
            )
            end_date_field = self.driver.find_element(
                By.NAME, self.END_DATE_TIME_BY_NAME
            )
            download_button = self.driver.find_element(
                By.NAME, self.DOWNLOAD_BUTTON_BY_NAME
            )

            plate_number_select.select_by_visible_text(self.plate_number)

            start_date_field.clear()
            start_date_field.send_keys(start_date)

            end_date_field.clear()
            end_date_field.send_keys(end_date)

            download_button.click()
            sleep(5)
            logging.info(
                f"Downloaded report for plate number: {self.plate_number} from {start_date} to {end_date}"
            )
            return True
        except (NoSuchElementException, TimeoutException) as e:
            logging.error(
                f"Element not found during field filling for plate number {self.plate_number}: {e}"
            )
            return False
        except WebDriverException as e:
            logging.error(
                f"WebDriver error during field filling for plate number {self.plate_number}: {e}"
            )
            return False
