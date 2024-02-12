from parsers.candidates_parser import CandidatesParser
from scraper.candidates_scraper import CandidateScraper


def filter_employees_without_salary(
    position: str | None,
    location: str | None,
    skills: str | None,
):
    employees = CandidatesParser()
    if position:
        employees.get_employees_by_job_position(position)
    if location:
        employees.get_employees_by_location(location)
    if skills:
        employees.get_employees_by_skills_or_keywords(skills)
    return employees


def get_available_candidates_experience(parsed_candidates: CandidatesParser):
    parsed_candidates.driver.get(parsed_candidates.BASE_URL)
    experience = parsed_candidates.get_options_from_checkbox()
    return experience


def filter_candidates_by_experience(parsed_candidates: CandidatesParser, value: str):
    parsed_candidates.get_employees_by_years_of_experience(value)
    return parsed_candidates


def get_available_salary_expectations(
    parsed_candidates: CandidatesParser, max_salary: bool = False
) -> [str]:
    parsed_candidates.driver.get(parsed_candidates.BASE_URL)
    salary_expectations = parsed_candidates.get_options_from_select_list()
    if max_salary:
        salary_expectations = parsed_candidates.get_options_from_select_list(max_salary)
    return salary_expectations


def filter_candidates_by_salary_expectations(
    parsed_candidates: CandidatesParser, value: str, max_salary: bool = False
) -> CandidatesParser:
    parsed_candidates.driver.get(parsed_candidates.BASE_URL)

    if max_salary:
        parsed_candidates.get_employee_by_salary_expectation(value, max_salary)
    else:
        parsed_candidates.get_employee_by_salary_expectation(value)

    return parsed_candidates


async def scrap_all_candidates(
    candidates: CandidatesParser, doc_name: str = "candidates.csv"
):
    """
    Scrapes all candidates' data and writes it to a CSV file.
    Args:
        candidates (CandidatesParser): The parser object to use for scraping.
        doc_name (str, optional): The name of the CSV file to write data to. Defaults to "candidates.csv".
    """

    scraper = CandidateScraper(candidates.BASE_URL)
    result = await scraper.sort_candidates()
    scraper.write_data_to_csv(result, doc_name)
    candidates.close_driver()
