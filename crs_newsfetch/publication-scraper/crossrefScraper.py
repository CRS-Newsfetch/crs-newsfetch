import requests
import csv
import os

class CrossRef_Scraper:
    def __init__(self, startdate, enddate, output_file='publications.csv'):
        self.names = self._read_files()
        self.startdate = startdate
        self.enddate = enddate
        self.output_file = output_file
        self.scrape()

    def _read_files(self):
        with open('names.txt') as ct:  # Ensure your file has the correct extension if not '.txt'
            names = [line.strip() for line in ct.readlines()]
        return names

    def scrape(self):
        # Check if CSV file exists. If not, create one with headers
        if not os.path.exists(self.output_file):
            with open(self.output_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Author Name', 'Title', 'DOI', 'Publication Date', 'URL'])

        for name in self.names:
            self.search_publications_by_author(name, self.startdate, self.enddate)

    def search_publications_by_author(self, author_name, start_date, end_date):
        url = "https://api.crossref.org/works"
        params = {
            "query.author": author_name,
            "filter": f"from-pub-date:{start_date},until-pub-date:{end_date}",
            "rows": 1000
        }
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            items = data.get("message", {}).get("items", [])

            # Append scraped data to the CSV file only for exact matches
            with open(self.output_file, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                for item in items:
                    for author in item.get('author', []):  # Check each author in the item
                        full_name = f"{author.get('given', '')} {author.get('family', '')}".strip()
                        if full_name.lower() == author_name.lower():  # Exact match check
                            title = item.get("title", ["No title"])[0]
                            publication_date = item.get("published", {}).get("date-parts", [["Unknown"]])[0]
                            doi = item.get("DOI", "No DOI")
                            url = item.get('URL', 'No URL')
                            writer.writerow([full_name, title, doi, '-'.join(map(str, publication_date)), url])
                            break  # Stop checking once a match is found to avoid duplicate entries for the same item
        else:
            print(f"Error: {response.status_code}")

# Example usage
# cf = CrossRef_Scraper("2023-01-01", "2023-01-31")
