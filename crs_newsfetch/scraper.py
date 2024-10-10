from datetime import date
import requests
from scholarly import scholarly

from scholar_result import ScholarResult

def scrape_papers(start_date: date, end_date: date) -> list[ScholarResult]:
    collected_results = []

    with open("names.txt") as names_file:
        for line in names_file.readlines():
            collected_results += _scrape_author_papers(line.strip(), start_date, end_date)

    return collected_results

def _scrape_author_papers(
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

    if response.status_code == 200:
        items = response.json().get("message", {}).get("items", [])
        for result in items:
            if author_name.lower() in map(
                    lambda a:
                        f"{a.get("given", "")} {a.get("family", "")}".strip().lower(),
                    result.get("author", [])
            ):
                publication_date = result.get("date-parts")
                if publication_date != None:
                    publication_date = datetime.date(*(map(int, publication_date[0])))

                collected_results.append(ScholarResult(
                    author_name,
                    result.get("title", [None])[0],
                    publication_date,
                    result.get("DOI"),
                    result.get("URL")
                ))

    # Now get papers from Scholarly

    try:
        first_author_result = next(scholarly.search_author(author_name))
        author = scholarly.fill(first_author_result)

        for result in author["publications"]:
            bib = result.get("bib", {})

            publication_date = bib.get("pub_year")
            if publication_date != None:
                publication_date = datetime.date(int(publication_date))

            collected_results.append(ScholarResult(
                author_name,
                bib.get("title"),
                publication_date,
                None, # As far as I know, there is no way to get a DOI from Scholarly
                result.get(pub_url)
            ))
    except StopIteration:
        pass

    return collected_results
