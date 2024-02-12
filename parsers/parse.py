import logging
import time
from selenium import webdriver
from selenium.common import (
    NoSuchElementException,
    TimeoutException,
    ElementNotInteractableException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from config.logging_config import setup_logging


class ParseHelper:
    def __init__(self) -> None:
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)
        setup_logging()

    def wait_and_click(self, locator: tuple) -> None:
        try:
            element = self.wait.until(
                expected_conditions.element_to_be_clickable(locator)
            )
            element.click()
        except TimeoutException as e:
            logging.exception(f"An error occurred: {str(e)}")

    def wait_and_send_keys(self, locator: tuple, keys: str) -> None:
        try:
            element = self.wait.until(
                expected_conditions.visibility_of_element_located(locator)
            )
            self.driver.execute_script("arguments[0].value = '';", element)
            element.send_keys(keys)
        except (
            ElementNotInteractableException,
            NoSuchElementException,
            TimeoutException,
        ) as e:
            logging.exception(f"An error occurred: {str(e)}")

    def wait_and_select_option(self, locator: tuple, value: str) -> None:
        try:
            element = self.wait.until(
                expected_conditions.visibility_of_element_located(locator)
            )
            select_element = Select(element)
            select_element.select_by_visible_text(value)
            time.sleep(1)
        except (TimeoutException, NoSuchElementException) as e:
            logging.exception(f"An error occurred: {str(e)}")

    def get_options_from_checkbox(self) -> list:
        try:
            result = []
            elements = self.driver.find_elements(
                By.CSS_SELECTOR, "#experience_selection > .checkbox"
            )
            for element in elements:
                classes = element.get_attribute("class").split()
                if "disabled" not in classes:
                    result.append(element.find_element(By.TAG_NAME, "span").text)
            return result
        except NoSuchElementException as e:
            logging.exception(f"An error occurred while getting options: {str(e)}")
            return []

    def get_options_from_select_list(self, max_salary: bool = False) -> list:
        max_locator = (By.ID, "salaryto_selection")
        min_locator = (By.ID, "salaryfrom_selection")
        try:
            if max_salary:
                element = self.driver.find_element(*max_locator)
            else:
                element = self.driver.find_element(*min_locator)

            select = Select(element)
            return [option.text for option in select.options]
        except NoSuchElementException as e:
            logging.exception(f"An error occurred while getting options: {str(e)}")
            return []
