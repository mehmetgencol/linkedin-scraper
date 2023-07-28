import csv
import re

from flask import Flask, jsonify, request
from linkedin_jobs_scraper.filters import TimeFilters

from job_scraper import JobScraper

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

    job_scraper.run_search(COMPANY_ENUM[company], TimeFilters[search_period], keywords.split(","))


if __name__ == '__main__':
    app.run()
