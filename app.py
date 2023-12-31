import csv
import logging
import re
from datetime import datetime
from multiprocessing import Process

from dotenv import dotenv_values
from flask import Flask, jsonify, request, Response
from linkedin_jobs_scraper.filters import TimeFilters
from apscheduler.schedulers.background import BackgroundScheduler

from job_scraper import JobScraper

import pandas as pd

app = Flask(__name__)

keywords_pattern = r"[a-zA-Z, ]+$"

# Define the enum values for the search period
PERIODS = TimeFilters.__members__.keys()
job_scraper = JobScraper()

# Read the company enum values from a CSV file
def read_company_enum(file_path):
    company_enum = {}
    with open(file_path, 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter=";")
        for row in reader:
            if len(row) > 1:
                company_enum[row[0]] = row[1]
    return company_enum

COMPANY_ENUM = read_company_enum('Accounts-InSearch.csv')

def searchJobsForToday():
    search_configs = dotenv_values('search.env')
    keywords = search_configs["RELATED_KEYWORDS"].split(",")
    search_period = TimeFilters[search_configs["SEARCH_PERIOD"]]
    company_df = pd.read_csv(search_configs["COMPANY_DETAIL_FILE"], delimiter=';', header=None)
    company_df = company_df.dropna()

    search_process = Process(
        target=run_search,
        args=(company_df, search_period, keywords),
        daemon=True
    )
    search_process.start()


sched = BackgroundScheduler(daemon=True)

# run the job every day
sched.add_job(searchJobsForToday,'interval',minutes=1440, next_run_time=datetime.now())
sched.start()


def run_search(company_df, period, keywords):
    job_scraper.run_search(company_df, period, keywords)


def cleanup_jobs():
    job_scraper.cleanup_outdated()


@app.route('/companies', methods=['GET'])
def companies_endpoint():
    company_values = list(COMPANY_ENUM.keys())
    return jsonify(company_values)


@app.route('/help', methods=['GET'])
def help_endpoint():
    company_values = list(COMPANY_ENUM.keys())
    period_values = list(PERIODS)
    return f'''This is the help endpoint. Use /search for the main functionality.

- Available company values: {company_values}
-Search keywords should be a string, and if you provide multiple keywords, separate it with comma. 
Example: software engineer, product manager
- Available search period values: {period_values}

'''


@app.route('/cleanup', methods=['PATCH'])
def cleanup_endpoint():
    cleanup_process = Process(
        target=cleanup_jobs,
        args=(),
        daemon=True
    )
    cleanup_process.start()

    return Response(mimetype='application/json', status=200)


@app.route('/search', methods=['POST'])
async def search_endpoint():
    data = request.get_json()

    # Retrieve the values of the three arguments
    company = data.get('company')
    keywords = data.get('keywords')
    search_period = data.get('search_period')

    # Validate the values of the arguments
    if company not in COMPANY_ENUM:
        return jsonify({'error': f'Invalid company value. Possible values: {list(COMPANY_ENUM.keys())}'}), 400

    if not keywords or not re.match(keywords_pattern, keywords):
        return jsonify({'error': 'Search keywords cannot be empty'}), 400

    if search_period not in PERIODS:
        return jsonify({'error': f'Invalid search period value. Possible values: {list(PERIODS)}'}), 400

    company_ids_combined = COMPANY_ENUM[company]
    period = TimeFilters[search_period]
    split_keywords = keywords.split(",")

    search_process = Process(
        target=run_search,
        args=(company_ids_combined.split(","), period, split_keywords,),
        daemon=True
    )
    search_process.start()

    return Response(mimetype='application/json', status=200)


if __name__ == '__main__':
    app.run()
