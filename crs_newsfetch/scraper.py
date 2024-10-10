from datetime import date
import requests
from scholarly import scholarly

from scholar_result import ScholarResult

class Scraper:
    def __init__(self):
        self._author_names_cached = None

    def papers(self, start_date: date, end_date: date) -> list[ScholarResult]:
        collected_results = []

        for line in self._author_names():
            collected_results += Scraper._author_papers(line, start_date, end_date)

        return collected_results

    def _author_names(self):
        if self._author_names_cached == None:
            with open("names.txt") as names_file:
                self._author_names_cached = list(map(lambda l: l.strip(),
                                                     names_file.readlines()))
            
        return self._author_names_cached

    def _author_papers(
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
                    "rows": 1000
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
                        result.get("DOI"),
                        result.get("URL")
                    ))

        # Now get papers from Scholarly

        try:
            first_author_result = next(scholarly.search_author(author))
            author_details = scholarly.fill(first_author_result)

            for result in author_details["publications"]:
                bib = result.get("bib", {})

                publication_date = bib.get("pub_year")
                if publication_date != None:
                    publication_date = date(int(publication_date), 1, 1)

                collected_results.append(ScholarResult(
                    author,
                    bib.get("title"),
                    publication_date,
                    None, # As far as I know, there is no way to get a DOI from Scholarly
                    result.get("pub_url")
                ))
        except StopIteration:
            pass

        return collected_results
