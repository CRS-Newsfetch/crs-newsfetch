# Scraper for CrossRef and Scholarly

This program contains two scripts that scrape publication data from **CrossRef** and **Google Scholar**. You can specify date ranges for the CrossRef scraper, and the results are saved in CSV files.

## Prerequisites

Before running the scrapers, make sure you have:

- **Python 3.x**
- The required Python packages listed in `requirements.txt`

### Step 1: Install Dependencies

To install the required dependencies, run the following command in your terminal:

```
pip install -r requirements.txt
```

## Project Structure

```
project_folder/
│
├── crossref_scraper.py         # Script for scraping CrossRef
├── google_scholar_scraper.py   # Script for scraping Google Scholar
├── names                       # File containing author names (one per line)
├── dates.txt                   # File containing start and end dates
├── requirements.txt            # Python dependencies for the project
└── main.py                     # Main script to run both scrapers
```

## Step 2: Configure Dates and Author Names

### Configure Date Range for CrossRef Scraper

The date range for the CrossRef scraper is defined in the `dates.txt` file.

- **Line 1**: Start date (`YYYY-MM-DD`)
- **Line 2**: End date (`YYYY-MM-DD`)

#### Example `dates.txt`:

```
2023-01-01
2023-01-31
```

### Configure Author Names

The author names are stored in the `names` file. Add each author's name on a new line.

#### Example `names` file:

```
Rebecca Alber
Marvin C. Alkin
Walter Allen
```

## Step 3: Run the Scrapers

### Run both scrapers with the `main.py` script

To scrape publications from both CrossRef and Google Scholar, run the `main.py` file. This will execute both scrapers and save results into separate CSV files.

```
python main.py
```

OR

```
python3 main.py
```

### CrossRef Output

- The CrossRef scraper will store its results in `crossref_publications.csv` by default. The file will contain the following columns: `Author Name`, `Title`, `DOI`, `Publication Date`, and `URL`.

### Google Scholar Output

- The Google Scholar scraper will store its results in `scholar_publications.csv` by default. The file will contain the following columns: `Author Name`, `Title`, `Cited By`, and `URL`.

```

## Notes

- Ensure that the `dates.txt` and `names` files are properly formatted before running the script.
- The Google Scholar scraper may not return a DOI in the results, as Google Scholar does not always provide this information.
