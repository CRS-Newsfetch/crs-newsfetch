import re
import time
from PySide6 import QtCore, QtWidgets
from datetime import date
import requests
from bs4 import BeautifulSoup

from database import DatabaseManager
from scholar_result import ScholarResult

class Scraper(QtCore.QRunnable):
    class Signals(QtCore.QObject):
        # Signals the Scraper can raise
        author_amount = QtCore.Signal(int)
        author_scraping = QtCore.Signal(str)
        source_scraping = QtCore.Signal(str)
        result_scraped = QtCore.Signal()
        result = QtCore.Signal(ScholarResult)
        finished = QtCore.Signal()

    GOOGLE_API_KEY = "AIzaSyDMTSIrHXV2UU6dycyuExZuccSrL0HpzmQ"
    GOOGLE_CSE_ID = "a118319687a8c4cfe"

    NAMES_FILE = "names.txt"
    NUM_FROM_SOURCES = 10

    def __init__(self, startDate, endDate, keywords, gui_instance=None):
        super().__init__()

        self.signals = Scraper.Signals()
        self._startDate = startDate
        self._endDate = endDate
        self._keywords = keywords
        self._gui_instance = gui_instance  # Store the gui_instance

    @QtCore.Slot()
    def run(self):
        self._database = DatabaseManager()

        if not self._validate_names_file(Scraper.NAMES_FILE):
            return  # Stop execution if names are invalid

        with open(Scraper.NAMES_FILE) as names_file:
            author_names = list(map(lambda l: l.strip(), names_file.readlines()))
        self.signals.author_amount.emit(len(author_names))

        for name in author_names:
            self.signals.author_scraping.emit(name)
            self._author_scrape(name, self._startDate, self._endDate)
            time.sleep(1)  # Avoid being blocked from APIs for spam

        self.signals.finished.emit()

   #NEW CODE THAT CHECKS NAMES.TXT FILE FOR ONLY NAMES BEFORE RUNNING SCRAPER
    # NOTE: this doesn't work because many faculty have characters not allowed here in their names.
    #       not using for now
    def _validate_names_file(self, names_file_path: str) -> bool:
        """Checks if all entries in the file are valid (only letters and spaces are allowed, no numbers)."""
        try:
            with open(names_file_path, "r") as file:
                names = file.readlines()

            invalid_entries = []
            # Check each entry for numbers and keep track of the line number
            for line_number, entry in enumerate(names, start=1):
                entry = entry.strip()
                if re.search(r"\d", entry):  # Check for any digit in the entry
                    invalid_entries.append((line_number, entry))

            if invalid_entries:
                # Prepare the error message
                error_message = "The following entries contain invalid characters (numbers are not allowed):\n"
                for line_number, invalid_entry in invalid_entries:
                    error_message += f"Line {line_number}: {invalid_entry}\n"
                print(error_message)  # Prints error message in console/terminal

                return False

            return True

        except FileNotFoundError:
            error_message = f"The file {names_file_path} was not found."
            print(error_message)  # Prints file not found message in console/terminal
            return False

    def _author_scrape(self, author: str, startDate: date, endDate: date):
        # First get papers from CrossRef

        self.signals.source_scraping.emit("CrossRef")

        crossref_response = requests.get(
                "https://api.crossref.org/works",
                {
                    "query.author": author,
                    "filter": f"from-pub-date:{startDate},until-pub-date:{endDate}",
                    "rows": Scraper.NUM_FROM_SOURCES
                }
        )

        if crossref_response.status_code == 200:
            items = crossref_response.json().get("message", {}).get("items", [])
            for result in items:
                for authors in result.get('author', []):
                        full_name = f"{authors.get('given', '')} {authors.get('family', '')}".strip()
                        if full_name.lower() == author.lower():
                            title = result.get("title")[0]
                            date_parts = result.get("published").get("date-parts", [])
                            if date_parts:
                                year = date_parts[0][0]
                                month = date_parts[0][1] if len(date_parts[0]) > 1 else ''
                                day = date_parts[0][2] if len(date_parts[0]) > 2 else ''
                    
                                if month and day:
                                    pub_date = f"{month:02d}-{day:02d}-{year}"
                                elif month:
                                    pub_date = f"{month:02d}-{year}"
                                else:
                                    pub_date = year

                            url = result.get('URL')
                            full_content = self._fetch_full_content(url)
                            self._handle_result(ScholarResult(
                                author,
                                title,
                                pub_date,
                                url,
                                full_content
                            ))

        # Now get articles from Google News

        self.signals.source_scraping.emit("Google News")

        start_formatted = startDate.strftime("%Y%m%d")
        end_formatted = endDate.strftime("%Y%m%d")

        google_response = requests.get(
                "https://www.googleapis.com/customsearch/v1",
                {
                    "q": f'"{author}"',
                    "key": Scraper.GOOGLE_API_KEY,
                    "cx": Scraper.GOOGLE_CSE_ID,
                    "dateRestrict": f"d{(endDate - startDate).days}",
                    "num": Scraper.NUM_FROM_SOURCES,
                    "sort": f"date:r:{start_formatted}:{end_formatted}"
                }
        )
        if google_response.status_code == 200:
            for item in google_response.json().get("items", []):
                full_content = self._fetch_full_content(item.get("link"))
                self._handle_result(ScholarResult(
                    author,
                    item.get("title"),
                    item.get("snippet")[:12],
                    item.get("link"),
                    full_content
                ))

    # Fetch Full Content Using Beautiful Soup If Possible

    def _fetch_full_content(self, url):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            content = soup.get_text()
            return content
        except Exception as e:
            print(f"Error fetching content from {url}: {e}")
            return ""  # Return empty string if content can't be fetched

    def _handle_result(self, result: ScholarResult):
        if result.url != None:
            if self._perform_keyword_search(result):
                 full_content = self._fetch_full_content(result.url)
                 self._database.insert_publication(
                        result.author,
                        result.title,
                        result.publication_year,
                        result.url,
                        full_content
                    )
                 self.signals.result_scraped.emit()
                 self.signals.result.emit(result)

    # Perform a case-insensitive search for keywords in full body

    def _perform_keyword_search(self, result: ScholarResult):
        content = result.full_content
        for keyword in self._keywords:
            if keyword.lower() in result.title.lower() or keyword.lower() in content.lower():
                return True  # Return True if any keyword is found in either title or content
        return False  # Return False if no keyword is found
