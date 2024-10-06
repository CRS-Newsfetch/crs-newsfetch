# main.py

from crossrefScraper import CrossRef_Scraper
from googlescholarScraper import GoogleScholar_Scraper


def read_dates():
    """Reads start and end dates from the 'dates.txt' file."""
    with open('dates.txt') as f:
        lines = f.readlines()
        start_date = lines[0].strip()
        end_date = lines[1].strip()
    return start_date, end_date


def main():
    # Read dates from the 'dates.txt' file
    start_date, end_date = read_dates()

    # Specify the output file names
    crossref_output_file = 'crossref_publications.csv'
    scholar_output_file = 'scholar_publications.csv'

    # Run CrossRef Scraper
    print("Running CrossRef Scraper...")
    crossref_scraper = CrossRef_Scraper(startdate=start_date,
                                        enddate=end_date,
                                        output_file=crossref_output_file)

    # Run Google Scholar Scraper
    print("Running Google Scholar Scraper...")
    google_scholar_scraper = GoogleScholar_Scraper(output_file=scholar_output_file)

    print("Scraping completed for both sources!")


if __name__ == "__main__":
    main()
