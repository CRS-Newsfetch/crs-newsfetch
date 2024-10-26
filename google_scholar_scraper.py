#modified version of aly's code to populate the database

# google_scholar_scraper.py

from scholarly import scholarly
from database import DatabaseManager

class GoogleScholarScraper:
    def __init__(self):
        self.names = self._read_names()
        self.db_manager = DatabaseManager()
        self.scrape() 
        self.db_manager.close_connection()

    def _read_names(self):
        # Read author names from names.txt
        with open('names.txt', 'r', encoding='utf-8') as ct:
            names = [line.strip() for line in ct.readlines()]
        return names

    def scrape(self):
        # Scrape publications for each author
        for name in self.names:
            self.search_publications_by_author(name)

    def search_publications_by_author(self, author_name):
        try:
            # Insert the author into the authors table (if not already present)
            author_id = self.db_manager.insert_author(author_name)
            if not author_id:
                print(f"Failed to retrieve author_id for {author_name}")
                return

            # Search for the author on Google Scholar
            search_query = scholarly.search_author(author_name)
            author = next(search_query)  # Get the first result
            scholarly.fill(author)  # Fill in the author's details
            for pub in author['publications']:
                title = pub.get('bib', {}).get('title', 'No title')
                cited_by = pub.get('num_citations', 'No citation')
                pub_year = pub.get('bib', {}).get('pub_year', 'Unknown')
                print(f"Scraped: {title} by {author_name}")
                # Insert the publication into the publications table
                self.db_manager.insert_publication(author_id, title, cited_by, pub_year)
        except StopIteration:
            print(f"No author found for {author_name}")
        except Exception as e:
            print(f"An error occurred while processing {author_name}: {e}")

# Example usage
if __name__ == '__main__':
    gs = GoogleScholarScraper() 