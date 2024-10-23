import requests
from datetime import datetime, timedelta
import time
import csv
import os

def search_google_news(query, api_key, cse_id, date_restrict):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': query,
        'key': api_key,
        'cx': cse_id,
        'dateRestrict': date_restrict,
        'num': 10,  # Number of results to return
        'sort': 'date:r:20230101:99999999'  # Sort by date
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        results = response.json().get('items', [])
        return results
    else:
        print(f"Error searching for {query}: {response.status_code}")
        return []

def format_date(date):
    return date.strftime("%Y-%m-%d")

def is_relevant(result, keywords):
    text = (result.get('title', '') + ' ' + result.get('snippet', '')).lower()
    return any(keyword.lower() in text for keyword in keywords)

def search_names(names_file, days_ago, api_key, cse_id, output_file):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_ago)
    date_restrict = f'd{days_ago}'

    with open(names_file, 'r') as file:
        names = [line.strip() for line in file if line.strip()]

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Name', 'Title', 'URL', 'Snippet', 'Search Date Range'])

        for name in names:
            print(f"Searching for Occidental-related articles about {name}...")
            results = search_google_news(f"{name} occidental news", api_key, cse_id, date_restrict)
            
            relevant_results = [r for r in results if is_relevant(r, ['occidental'])]
            
            if relevant_results:
                for result in relevant_results:
                    csvwriter.writerow([
                        name,
                        result['title'],
                        result['link'],
                        result['snippet'],
                        f"{format_date(start_date)} to {format_date(end_date)}"
                    ])
            else:
                csvwriter.writerow([name, "No recent Occidental-related articles found", "", "", f"{format_date(start_date)} to {format_date(end_date)}"])
            
            # Sleep to avoid hitting API rate limits
            time.sleep(1)

    print(f"Search complete. Results saved to {output_file}")

# Google API key and Custom Search Engine ID
API_KEY = 'AIzaSyDMTSIrHXV2UU6dycyuExZuccSrL0HpzmQ'
CSE_ID = 'a118319687a8c4cfe'

# File containing names to search for
NAMES_FILE = 'names.txt'

# Number of days to look back
DAYS_AGO = 60

# Output CSV file name
OUTPUT_FILE = 'occidental_news_results.csv'

# Run the search
search_names(NAMES_FILE, DAYS_AGO, API_KEY, CSE_ID, OUTPUT_FILE)
