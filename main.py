from __future__ import print_function

import datetime
import logging
import os.path

import pandas as pd
from dotenv import dotenv_values
from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, EventData, EventMetrics
from linkedin_jobs_scraper.filters import RelevanceFilters, TimeFilters, TypeFilters
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters

# Change root logger level (default is WARN)
logging.basicConfig(level=logging.INFO)

BASE_URL = "https://www.linkedin.com/jobs/search/?f_C="
AND_CHAR = "%2C"

COMPANY_NAME = "CompanyName"
TITLE_HEADER = "Title"
JOB_ID = "JobId"
POSTED_AT = "PostedAt"
LINK = "Link"

OUTPUT_KEYS = [COMPANY_NAME, TITLE_HEADER, JOB_ID, POSTED_AT, LINK]

DATETIME_FORMAT = "%Y-%m-%d"

search_configs = dotenv_values('search.env')

df = pd.read_csv(search_configs["COMPANY_DETAIL_FILE"], delimiter=';', header=None)
df = df.dropna()

keywords = search_configs["RELATED_KEYWORDS"].split(",")
output_file = search_configs["OUTPUT_FILE"]

# Check if the input file exists and is not empty
if os.path.isfile(output_file) and os.path.getsize(output_file) > 0:
    # Read the CSV file into a pandas DataFrame
    stored_jobs = pd.read_csv(output_file, encoding="utf-8")
else:
    # Create an empty DataFrame if the file does not exist or is empty
    stored_jobs = pd.DataFrame(columns=OUTPUT_KEYS)

earliest_date = datetime.datetime.now() - datetime.timedelta(days=30)
stored_jobs[POSTED_AT] = pd.to_datetime(stored_jobs[POSTED_AT], format=DATETIME_FORMAT)
stored_jobs = stored_jobs[stored_jobs[POSTED_AT] >= earliest_date]

search_results = []


# Fired once for each successfully processed job
def on_data(data: EventData):
    new_data = pd.DataFrame({
        COMPANY_NAME: [data.company],
        TITLE_HEADER: [data.title],
        JOB_ID: [int(data.job_id)],
        POSTED_AT: [data.date],
        LINK: [data.link],
    })
    search_results.append(new_data)
    print('[ON_DATA]', data.title, data.company, data.company_link, data.date, data.link, data.insights,
          len(data.description))


# Fired once for each page (25 jobs)
def on_metrics(metrics: EventMetrics):
    print('[ON_METRICS]', str(metrics))


def on_error(error):
    print('[ON_ERROR]', error)


def on_end():
    print('[ON_END]')


scraper = LinkedinScraper(
    chrome_executable_path=search_configs["CHROME_EXE"],
    # Custom Chrome executable path (e.g. /foo/bar/bin/chromedriver)
    chrome_options=None,  # Custom Chrome options here
    headless=True,  # Overrides headless mode only if chrome_options is None
    max_workers=1,  # How many threads will be spawned to run queries concurrently (one Chrome driver for each thread)
    slow_mo=5  # Slow down the scraper to avoid 'Too many requests 429' errors (in seconds)
)

# Add event listeners
scraper.on(Events.DATA, on_data)
scraper.on(Events.ERROR, on_error)
scraper.on(Events.END, on_end)

queries = []

for index, row in df.iterrows():
    company_ids = values = [value.strip() for value in str(row[1]).split(',') if value.strip()]
    search_url = BASE_URL + AND_CHAR.join(company_ids)
    company_queries = [
        Query(
            query=keyword.strip(),
            options=QueryOptions(
                locations=['United States'],
                filters=QueryFilters(
                    company_jobs_url=search_url,
                    # Filter by companies.
                    relevance=RelevanceFilters.RECENT,
                    time=TimeFilters.DAY,
                    type=[TypeFilters.FULL_TIME, TypeFilters.CONTRACT, TypeFilters.TEMPORARY]
                )
            )
        )
        for keyword in keywords
    ]
    queries.extend(company_queries)

scraper.run(queries)

stored_jobs = pd.concat([stored_jobs, pd.concat(search_results)])

stored_jobs = stored_jobs.drop_duplicates(subset=[JOB_ID])
stored_jobs = stored_jobs.sort_values(by=[COMPANY_NAME, POSTED_AT])
stored_jobs.to_csv(output_file, index=False)
