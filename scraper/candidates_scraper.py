import csv
import ssl
import logging

import aiohttp
import asyncio

from dataclasses import fields, astuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from models import Candidate
from config.logging_config import setup_logging


class CandidateScraper:
    """A class for scraping candidate data from a website."""

    def __init__(self, filtered_candidates: str) -> None:
        """Initialize the CandidateScraper.
        Args: filtered_candidates (str): The URL of the filtered candidates page."""

        self.candidates = filtered_candidates
        self.BASE_URL = "https://www.work.ua/"
        setup_logging()

    @staticmethod
    def get_ssl_connector():
        """Create an SSL connector for aiohttp."""

        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        return aiohttp.TCPConnector(ssl=ssl_context)

    async def scrap_one_candidate(
        self, session, soup: BeautifulSoup
    ) -> Candidate | dict:
        """Scrape data for a single candidate.
        Args:
            session: The aiohttp ClientSession object.
            soup (BeautifulSoup): The BeautifulSoup object representing the candidate's page.
        Returns:
            Candidate | dict: The scraped candidate data."""

        url_name = soup.select_one("a")["href"]
        url = urljoin(self.BASE_URL, url_name)
        async with session.get(url, ssl=False) as response:
            page_content = await response.text()
            new_soup = BeautifulSoup(page_content, "html.parser")

            high_education = new_soup.find(
                lambda tag: tag.name == "h2" and "Освіта" in tag.text
            )
            additional_education = new_soup.find(
                lambda tag: tag.name == "h2"
                and "Додаткова освіта та сертифікати" in tag.text
            )
            english = new_soup.find(
                lambda tag: tag.name == "p"
                and "Англійська — вище середнього" in tag.text
            )
            return Candidate(
                name=new_soup.select_one(".add-top > h1.cut-top").text.strip(),
                position=new_soup.select_one(".add-top > h2").text.split(",")[0],
                ready_to_work=new_soup.select("dl.dl-horizontal > dd")[-1].text,
                education=True if high_education else False,
                additional_education=True if additional_education else False,
                skills=len(new_soup.select(".label > .ellipsis")),
                english=True if english else False,
                url=urljoin(self.BASE_URL, url),
            )

    @staticmethod
    def get_num_pages(soup: BeautifulSoup) -> int:
        """Get the total number of pages of candidates.
        Args:
            soup (BeautifulSoup): The BeautifulSoup object representing the page.
        Returns:
            int: The total number of pages."""

        pagination = soup.select_one("nav > ul.pagination")

        if pagination is None:
            return 1
        return int(pagination.select("li > a")[-2].text)

    async def get_candidates_from_one_page(
        self, session, soup: BeautifulSoup
    ) -> list[Candidate]:
        """Get candidates from one page.
        Args:
            session: The aiohttp ClientSession object.
            soup (BeautifulSoup): The BeautifulSoup object representing the page.
        Returns:
            [Candidate]: A list of Candidate objects.
        """

        candidates_cvs = soup.select(".resume-link")
        tasks = [
            self.scrap_one_candidate(session, one_soup) for one_soup in candidates_cvs
        ]

        return await asyncio.gather(*tasks)

    async def get_all_candidates(self) -> list[Candidate]:
        """Get all candidates from all pages.
        Returns:
            [Candidate]: A list of Candidate objects.
        """

        async with aiohttp.ClientSession(connector=self.get_ssl_connector()) as session:
            logging.info(f"Start parsing Candidates")
            page = await session.get(self.candidates)
            first_page_soup = BeautifulSoup(await page.text(), "html.parser")

            num_pages = self.get_num_pages(first_page_soup)
            all_candidates = await self.get_candidates_from_one_page(
                session, first_page_soup
            )
            for page in range(2, num_pages + 1):
                logging.info(f"Start parsing page #{page}")
                page = await session.get(self.candidates, params={"page": page})
                soup = BeautifulSoup(await page.text(), "html.parser")
                all_candidates.extend(
                    await self.get_candidates_from_one_page(session, soup)
                )

        return all_candidates

    async def sort_candidates(self) -> list[Candidate]:
        """Sort candidates based on their ratings.
        Returns:
            [Candidate]: A list of Candidate objects sorted by ratings.
        """

        candidate_list = await self.get_all_candidates()
        ratings = {candidate: 0 for candidate in candidate_list}

        for candidate in candidate_list:
            ratings[candidate] = sum(
                [
                    5 if candidate.education else 0,
                    4 if candidate.additional_education else 0,
                    candidate.skills // 6,
                    4 if candidate.english else 0,
                ]
            )
        return sorted(ratings, key=ratings.get, reverse=True)

    @staticmethod
    def write_data_to_csv(data: list[Candidate], doc_name: str) -> None:
        """Write candidate data to a CSV file.
        Args:
            data ([Candidate]): A list of Candidate objects.
            doc_name (str): The name of the CSV file to write.
        """

        try:
            with open(doc_name, "w") as file:
                writer = csv.writer(file)
                writer.writerow(field.name for field in fields(Candidate))
                writer.writerows([astuple(item) for item in data])
            logging.info("Data written to CSV successfully.")
        except Exception as e:
            logging.error(f"Error writing data to CSV: {e}")
