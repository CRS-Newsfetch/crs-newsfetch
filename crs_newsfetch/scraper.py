import re
import time
from PySide6 import QtCore, QtWidgets
from datetime import date
import requests
from scholarly import scholarly

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

    NAMES_FILE = "crs_newsfetch/names.txt"
    NUM_FROM_SOURCES = 10

    def __init__(self, startDate, endDate, gui_instance=None):
        super().__init__()

        self.signals = Scraper.Signals()
        self._startDate = startDate
        self._endDate = endDate
        self._gui_instance = gui_instance  # Store the gui_instance
      

    @QtCore.Slot()
    def run(self):
        self._database = DatabaseManager()

        # Validate the names before proceeding with the search
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
    def _validate_names_file(self, names_file_path: str) -> bool:
        """Checks if all names in names.txt are valid (only letters)."""
        try:
            with open(names_file_path, "r") as file:
                names = file.readlines()

            invalid_names = []
            # Check each name for validity and keep track of the line number
            for line_number, name in enumerate(names, start=1):
                name = name.strip()
                if not re.match("^[A-Za-z ]+$", name):  # Only letters and spaces allowed
                    invalid_names.append((line_number, name))

            if invalid_names:
                # Prepare the error message and emit the signal
                error_message = "The following names contain invalid characters (only letters allowed):\n"
                for line_number, invalid_name in invalid_names:
                    error_message += f"Line {line_number}: {invalid_name}\n"
                print(error_message) #prints error message in console/terminal
      
                return False

            return True

        except FileNotFoundError:
            error_message = f"The file {names_file_path} was not found."
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
                                    pub_date = year  # Only year
                            
                            # TODO: record full publication date

                            url = result.get('URL')
                            self._handle_result(ScholarResult(
                                author,
                                title,
                                int(year),
                                url
                            ))

        # Now get papers from Scholarly

        self.signals.source_scraping.emit("Google Scholar")

        try:
            first_author_result = next(scholarly.search_author(author))
            author_details = scholarly.fill(first_author_result)

            for result in author_details.get("publications", []):
                bib = result.get("bib", {})

                self._handle_result(ScholarResult(
                    author,
                    bib.get("title"),
                    int(bib.get("pub_year", "0")),
                    result.get("pub_url")
                ))
        except StopIteration:
            pass

        # Finally get articles from Google News

        self.signals.source_scraping.emit("Google News")

        start_formatted = startDate.strftime("%Y%m%d")
        end_formatted = endDate.strftime("%Y%m%d")

        google_response = requests.get(
                "https://googleapis.com/customsearch/v1",
                {
                    "q": f"{author} occidental news",
                    "key": Scraper.GOOGLE_API_KEY,
                    "cx": Scraper.GOOGLE_CSE_ID,
                    "dateRestrict": f"d{(date.today() - startDate).days}",
                    "num": Scraper.NUM_FROM_SOURCES,
                    "sort": f"date:r:{start_formatted}:{end_formatted}"
                }
        )
        if google_response == 200:
            for item in google_response.json().get("items", []):
                self._handle_result(ScholarResult(
                    author,
                    item.get("title"),
                    endDate.year,
                    item.get("link")
                ))

    def _handle_result(self, result: ScholarResult):
        self.signals.result_scraped.emit()

        if self._startDate.year <= result.publication_year <= self._endDate.year:
            author_id = self._database.insert_author(result.author)
            self._database.insert_publication(
                    author_id,
                    result.title,
                    result.publication_year,
                    result.url
            )
            self.signals.result.emit(result)
