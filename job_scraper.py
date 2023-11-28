from __future__ import print_function

import datetime
import logging
import os.path

import pandas as pd
from dotenv import dotenv_values
from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, EventData
from linkedin_jobs_scraper.filters import RelevanceFilters, TimeFilters, TypeFilters
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.utils.chrome_driver import get_default_driver_options

from globals import *
from snowflake_connector import SnowflakeConnector

# Change root logger level (default is WARN)
logging.basicConfig(level=logging.INFO)


class JobScraper:
    search_results = []

    def __init__(self):
        self.search_configs = dotenv_values('search.env')
        self.snowflake_connector = None
        self.scraper = self.get_scraper()
        self.company_df = None
        self.keywords = []
        self.output_file = ""
        self.time_filters = None
        self.stored_jobs = []

    def get_snowflake_connector(self):
        if not self.snowflake_connector:
            user = self.search_configs["SNOWFLAKE_USER"]
            password = self.search_configs["SNOWFLAKE_PASSWORD"]
            account = self.search_configs["SNOWFLAKE_ACCOUNT"]
            db = self.search_configs["SNOWFLAKE_DB"]
            schema = self.search_configs["SNOWFLAKE_SCHEMA"]
            table = self.search_configs["SNOWFLAKE_TABLE"]
            warehouse = self.search_configs["SNOWFLAKE_WAREHOUSE"]
            self.snowflake_connector = SnowflakeConnector(user, password, account, db, schema, table, warehouse)
        return self.snowflake_connector

    def set_local_search(self):
        self.company_df = pd.read_csv(self.search_configs["COMPANY_DETAIL_FILE"], delimiter=';', header=None)
        self.company_df = self.company_df.dropna()
        self.keywords = self.search_configs["RELATED_KEYWORDS"].split(",")
        self.output_file = self.search_configs["OUTPUT_FILE"]
        self.time_filters = TimeFilters[self.search_configs["SEARCH_PERIOD"]]

        # Check if the input file exists and is not empty
        if os.path.isfile(self.output_file) and os.path.getsize(self.output_file) > 0:
            # Read the CSV file into a pandas DataFrame
            self.stored_jobs = pd.read_csv(self.output_file, encoding="utf-8")
        else:
            # Create an empty DataFrame if the file does not exist or is empty
            self.stored_jobs = pd.DataFrame(columns=OUTPUT_KEYS)

        earliest_date = datetime.datetime.now() - datetime.timedelta(days=30)
        self.stored_jobs[POSTED_AT] = pd.to_datetime(self.stored_jobs[POSTED_AT], format=DATE_FORMAT)
        self.stored_jobs = self.stored_jobs[self.stored_jobs[POSTED_AT] >= earliest_date]

    def get_scraper(self):

        chrome_options = get_default_driver_options()
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--hide-scrollbars")
        chrome_options.add_argument("--enable-logging")
        chrome_options.add_argument("--log-level=0")
        chrome_options.add_argument("--v=99")
        chrome_options.add_argument("--single-process")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument('--disable-dev-tools')
        chrome_options.add_argument('--user-data-dir=/tmp/chrome-user-data')
        chrome_options.add_argument("--no-zygote")

        return LinkedinScraper(
            chrome_executable_path=self.search_configs["CHROME_EXE"],
            # Custom Chrome executable path (e.g. /foo/bar/bin/chromedriver)
            chrome_options=chrome_options,  # Custom Chrome options here
            headless=True,  # Overrides headless mode only if chrome_options is None
            max_workers=1,
            # How many threads will be spawned to run queries concurrently (one Chrome driver for each thread)
            slow_mo=5  # Slow down the scraper to avoid 'Too many requests 429' errors (in seconds)
        )

    @staticmethod
    def prepare_query(company_ids, search_period, keywords):
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
                        time=search_period,
                        type=[TypeFilters.FULL_TIME, TypeFilters.CONTRACT, TypeFilters.TEMPORARY]
                    )
                )
            )
            for keyword in keywords
        ]
        return company_queries

    @staticmethod
    def on_data(data: EventData, search_results=[]):
        new_data = pd.DataFrame({
            COMPANY_NAME: [data.company],
            TITLE_HEADER: [data.title],
            JOB_ID: [int(data.job_id)],
            POSTED_AT: data.date,
            LINK: [data.link],
        })
        search_results.append(new_data)
        print('[ON_DATA]', data.title, data.company, data.company_link, data.date, data.link, data.insights,
              len(data.description))

    @staticmethod
    def on_error(error):
        print('[ON_ERROR]', error)

    def run_local_search(self):
        queries = []

        for index, row in self.company_df.iterrows():
            companies = [value.strip() for value in str(row[1]).split(',') if value.strip()]
            company_queries = JobScraper.prepare_query(companies, self.time_filters, self.keywords)
            queries.extend(company_queries)

        search_results = []
        self.scraper.on(Events.DATA, lambda x: JobScraper.on_data(x, search_results))
        self.scraper.on(Events.ERROR, JobScraper.on_error)
        self.scraper.run(queries)

        if search_results:
            self.stored_jobs = pd.concat([self.stored_jobs, pd.concat(search_results)])

        self.stored_jobs = self.stored_jobs.drop_duplicates(subset=[JOB_ID])
        self.stored_jobs = self.stored_jobs.sort_values(by=[COMPANY_NAME, POSTED_AT])
        self.stored_jobs.to_csv(self.output_file, index=False)

    def run_search(self, companies, time_period, keywords):
        for company in companies:
            company_queries = JobScraper.prepare_query(list(company), time_period, keywords)
            search_results = []
            self.scraper.on(Events.DATA, lambda x: JobScraper.on_data(x, search_results))
            self.scraper.on(Events.ERROR, JobScraper.on_error)

            self.scraper.run(company_queries)

            if len(search_results) > 0:
                df_results = pd.concat(search_results, ignore_index=True)
                df_results = df_results.drop_duplicates(subset=[JOB_ID])
                self.get_snowflake_connector().write_pandas(df_results)

    def cleanup_outdated(self):
        self.get_snowflake_connector().clear_depends_on()


if __name__ == '__main__':
    scraper = JobScraper()
    scraper.set_local_search()
    scraper.run_local_search()
