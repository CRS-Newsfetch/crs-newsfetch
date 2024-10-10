# Google News Search Script

Documentation created using Claude.ai

This Python script searches for recent news articles related to specific names and "Occidental" using the Google Custom Search API. The results are saved in a CSV file for easy analysis.

## Prerequisites

Before running the script, make sure you have:

- Python 3.x

## Step 1: Install Dependencies

To install the required dependencies, run the following command in your terminal:

```
pip install -r requirements.txt
```

## Project Structure

```
project_folder/
│
├── news_search.py     # Main script for searching Google News
├── names.txt          # File containing names to search for (one per line)
└── occidental_news_results.csv  # Output file (will be created when script runs)
```

## Step 2: Configure API Credentials and Search Parameters

1. Set up a Google Cloud project and enable the Custom Search API.
2. Create a Programmable Search Engine and note down the Search Engine ID.
3. Generate an API key for your Google Cloud project.
4. Update the `API_KEY` and `CSE_ID` variables in the `news_search.py` script with your credentials.

## Step 3: Configure Names to Search

The names to search for are stored in the `names.txt` file. Add each name on a new line.

Example `names.txt` file:

```
John Doe
Jane Smith
Robert Johnson
```

## Step 4: Run the Script

To search for recent news articles, run the `news_search.py` file:

```
python news_search.py
```

OR

```
python3 news_search.py
```

## Output

The script will store its results in `occidental_news_results.csv` by default. The file will contain the following columns:

- Name
- Title
- URL
- Snippet
- Search Date Range

## Customization

You can modify the following parameters in the `news_search.py` file:

- `DAYS_AGO`: Number of days to look back for articles (default is 7)
- `OUTPUT_FILE`: Name of the output CSV file
- Keywords in the `is_relevant` function to filter results (currently set to ['Occidental College'])

## Notes

- Ensure that the `names.txt` file is properly formatted before running the script.
- The script includes a delay between searches to avoid hitting API rate limits.
- Make sure you're aware of your Google Custom Search API usage and any associated costs.
