import logging
from selenium.webdriver.common.by import By

from .parse import ParseHelper


class CandidatesParser(ParseHelper):
    """A class for parsing candidates data from a website."""

    def __init__(self) -> None:
        super().__init__()
        self.BASE_URL = "https://www.work.ua/employer/"

    def get_employees_by_job_position(self, position: str) -> None:
        """Get employees by job position.
        Args:
            position (str): The job position to search for.
        """

        self.driver.get(self.BASE_URL)
        self.wait_and_send_keys((By.NAME, "search"), position)
        self.wait_and_click((By.ID, "sm-but"))
        self.BASE_URL = self.driver.current_url

    def get_employees_by_years_of_experience(self, years: str) -> None:
        """Get employees by years of experience.
        Args:
            years (str): The years of experience to filter by.
        """

        options = self.get_options_from_checkbox()
        years = years.capitalize()
        if years in options:
            self.wait_and_click((By.XPATH, f"//span[text()='{years}']"))
            self.BASE_URL = self.driver.current_url
        else:
            logging.exception(f"Option '{years}' not found in checkbox.")
            raise ValueError(f"Option '{years}' not found in checkbox.")

    def get_employees_by_skills_or_keywords(self, skills: str) -> None:
        """Get employees by skills or keywords.
        Args:
            skills (str): The skills or keywords to search for.
        """

        self.driver.get(self.BASE_URL)
        self.driver.find_elements(By.CSS_SELECTOR, ".checkbox")[-3].click()
        self.wait_and_click((By.ID, "search"))
        self.wait_and_send_keys((By.ID, "search"), skills)
        self.wait_and_click((By.ID, "sm-but"))
        self.BASE_URL = self.driver.current_url

    def get_employees_by_location(self, location: str) -> None:
        """Get employees by location.
        Args:
            location (str): The location to search for.
        """

        self.driver.get(self.BASE_URL)
        self.wait_and_send_keys((By.ID, "city"), location)
        self.wait_and_click((By.ID, "sm-but"))
        self.BASE_URL = self.driver.current_url

    def get_employee_by_salary_expectation(
        self, value: str, max_salary: bool = False
    ) -> None:
        """Get employees by salary expectation.
        Args:
            value (str): The value of the salary expectation.
            max_salary (bool, optional): Indicates if it's a maximum salary. Defaults to False.
        """

        self.driver.get(self.BASE_URL)

        max_locator = (By.ID, "salaryto_selection")
        min_locator = (By.ID, "salaryfrom_selection")

        if max_salary:
            self.wait_and_select_option(max_locator, value)
        else:
            self.wait_and_select_option(min_locator, value)

        self.BASE_URL = self.driver.current_url

    def close_driver(self) -> None:
        """Close the WebDriver."""

        self.driver.quit()
