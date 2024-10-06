import csv
import os
from scholarly import scholarly


class GoogleScholar_Scraper:
    def __init__(self, output_file='scholar_publications.csv'):
        self.names = self._read_files()
        self.output_file = output_file
        self.scrape()

    def _read_files(self):
        with open('names.txt') as ct:
            names = [line.strip() for line in ct.readlines()]
        return names

    def scrape(self):
        # Check if CSV file exists. If not, create one with headers
        if not os.path.exists(self.output_file):
            with open(self.output_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Author Name', 'Title', 'Cited By', 'Publication Year'])

        for name in self.names:
            self.search_publications_by_author(name)

    def search_publications_by_author(self, author_name):
        try:
            # Search for the author on Google Scholar
            search_query = scholarly.search_author(author_name)
            author = next(search_query)  # Get the first result
            scholarly.fill(author)  # Fill in the author’s details
            # Append scraped data to the CSV file
            with open(self.output_file, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                for pub in author['publications']:
                    title = pub.get('bib', {}).get('title', 'No title')
                    cited_by = pub.get('num_citations', 'No citation')
                    pub_year = pub.get('bib', {}).get('pub_year', 'Unknown')
                    print(f"Scraped: {title} by {author_name}")
                    # Write the row in the CSV file
                    writer.writerow([author_name, title, cited_by, pub_year])
        except StopIteration:
            print(f"No author found for {author_name}")
        except Exception as e:
            print(f"An error occurred: {e}")


# Example usage
# gs = GoogleScholar_Scraper()