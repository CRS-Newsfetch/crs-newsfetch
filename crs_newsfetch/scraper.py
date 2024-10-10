from datetime import date
import requests
from scholarly import scholarly
import time

from scholar_result import ScholarResult

class Scraper:
    GOOGLE_API_KEY = "AIzaSyDMTSIrHXV2UU6dycyuExZuccSrL0HpzmQ"
    GOOGLE_CSE_ID = "a118319687a8c4cfe"

    NAMES_FILE = "names.txt"
    NUM_FROM_SOURCES = 10

    def __init__(self):
        self._author_names_cached = None

    def scrape(self, start_date: date, end_date: date) -> list[ScholarResult]:
        collected_results= []

        for name in self._author_names():
            collected_results += Scraper._author_scrape(name, start_date, end_date)
            time.sleep(1) # Avoid being blocked from APIs for spam

        return collected_results

    def _author_names(self):
        if self._author_names_cached == None:
            with open(Scraper.NAMES_FILE) as names_file:
                self._author_names_cached = list(map(lambda l: l.strip(),
                                                     names_file.readlines()))
            
        return self._author_names_cached

    def _author_scrape(
            author: str,
            start_date: date,
            end_date: date
    ) -> list[ScholarResult]:
        collected_results = []

        # First get papers from CrossRef

        crossref_response = requests.get(
                "https://api.crossref.org/works",
                {
                    "query.author": author,
                    "filter": f"from-pub-date:{start_date},until-pub-date:{end_date}",
                    "rows": Scraper.NUM_FROM_SOURCES
                }
        )
        if crossref_response.status_code == 200:
            items = crossref_response.json().get("message", {}).get("items", [])
            for result in items:
                if author.lower() in map(
                        lambda a:
                            f"{a.get("given", "")} {a.get("family", "")}".strip().lower(),
                        result.get("author", [])
                ):
                    publication_date = result.get("date-parts")
                    if publication_date != None:
                        publication_date = datetime.date(*(map(int, publication_date[0])))

                    collected_results.append(ScholarResult(
                        author,
                        result.get("title", [None])[0],
                        publication_date,
                        result.get("URL")
                    ))

        # Now get papers from Scholarly

        try:
            first_author_result = next(scholarly.search_author(author))
            author_details = scholarly.fill(first_author_result)

            for result in author_details.get("publications", []):
                bib = result.get("bib", {})

                publication_date = bib.get("pub_year")
                if publication_date != None:
                    publication_date = date(int(publication_date), 1, 1)

                collected_results.append(ScholarResult(
                    author,
                    bib.get("title"),
                    publication_date,
                    result.get("pub_url")
                ))
        except StopIteration:
            pass

        # Finally get articles from Google News

        google_response = requests.get(
                "https://googleapis.com/customsearch/v1",
                {
                    "q": f"{author} occidental news",
                    "key": Scraper.GOOGLE_API_KEY,
                    "cx": Scraper.GOOGLE_CSE_ID,
                    "dateRestrict": f"d{(date.today() - start_date).days}",
                    "num": Scraper.NUM_FROM_SOURCES,
                    "sort": "date"
                }
        )
        if google_response == 200:
            collected_results.append(map(
                lambda r: ScholarResult(author, r.get("title"), None, r.get("link")),
                google_response.json().get("items", [])
            ))

        return collected_results
