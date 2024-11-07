from PySide6 import QtCore
from datetime import date
import requests
from scholarly import scholarly
import time

from database import DatabaseManager
from scholar_result import ScholarResult

class Scraper(QtCore.QRunnable):
    class Signals(QtCore.QObject):
        # Signals the Scraper can raise
        result = QtCore.Signal(ScholarResult)
        finished = QtCore.Signal()

    GOOGLE_API_KEY = "AIzaSyDMTSIrHXV2UU6dycyuExZuccSrL0HpzmQ"
    GOOGLE_CSE_ID = "a118319687a8c4cfe"

    NAMES_FILE = "crs_newsfetch/names.txt"
    NUM_FROM_SOURCES = 10

    def __init__(self, startDate, endDate):
        super().__init__()

        self.signals = Scraper.Signals()
        self._startDate = startDate
        self._endDate = endDate
        self._database = DatabaseManager()
        self._author_names_cached = None

    @QtCore.Slot()
    def run(self):
        for name in self._author_names():
            self._author_scrape(name, self._startDate, self._endDate)
            time.sleep(1) # Avoid being blocked from APIs for spam

        self.signals.finished.emit()

    def _author_names(self):
        if self._author_names_cached == None:
            with open(Scraper.NAMES_FILE) as names_file:
                self._author_names_cached = list(map(lambda l: l.strip(),
                                                     names_file.readlines()))
            
        return self._author_names_cached

    def _author_scrape(self, author: str, startDate: date, endDate: date):
        # First get papers from CrossRef

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
                            
                            # TODO: record full publication year

                            url = result.get('URL')
                            self._handle_result(ScholarResult(
                                author,
                                title,
                                int(year),
                                url
                            ))
                            
        # Now get papers from Scholarly

        try:
            first_author_result = next(scholarly.search_author(author))
            author_details = scholarly.fill(first_author_result)

            for result in author_details.get("publications", []):
                bib = result.get("bib", {})

                pub_year = int(bib.get("pub_year", "0"))
                if startDate.year <= pub_year <= endDate.year:
                    self._handle_result(ScholarResult(
                        author,
                        bib.get("title"),
                        pub_year,
                        result.get("pub_url")
                    ))
        except StopIteration:
            pass

        # Finally get articles from Google News

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
        author_id = self._database.insert_author(result.author)
        self._database.insert_publication(
                author_id,
                result.title,
                result.publication_year,
                result.url
        )
        self.signals.result.emit(result)
