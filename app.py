import csv

from flask import Flask, jsonify, request
from linkedin_jobs_scraper.filters import TimeFilters

from job_scraper import JobScraper

app = Flask(__name__)

# Define the enum values for the search period
PERIOD_ENUM = TimeFilters.__members__.keys()
job_scraper = JobScraper()


# Read the company enum values from a CSV file
def read_company_enum(file_path):
    company_enum = {}
    with open(file_path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            if len(row) > 1:
                company_enum[row[0]] = row[1]
    return company_enum


COMPANY_ENUM = read_company_enum('Accounts-InSearch.csv')


@app.route('/help', methods=['GET'])
def help_endpoint():
    company_values = list(COMPANY_ENUM.keys())
    period_values = list(PERIOD_ENUM)
    return f'''This is the help endpoint. Use /search for the main functionality.

Available company values: {company_values}
Available search period values: {period_values}
'''


@app.route('/search', methods=['POST'])
def search_endpoint():
    data = request.get_json()

    # Retrieve the values of the three arguments
    company = data.get('company')
    search_keywords = data.get('search_keywords')
    search_period = data.get('search_period')

    # Validate the values of the arguments
    if company not in COMPANY_ENUM:
        return jsonify({'error': f'Invalid company value. Possible values: {list(COMPANY_ENUM.keys())}'}), 400

    if not search_keywords:
        return jsonify({'error': 'Search keywords cannot be empty'}), 400

    if search_period not in PERIOD_ENUM:
        return jsonify({'error': f'Invalid search period value. Possible values: {list(PERIOD_ENUM)}'}), 400

    results = job_scraper.run_search(COMPANY_ENUM[company], TimeFilters[search_period], search_keywords)

    return jsonify(results), 200


if __name__ == '__main__':
    app.run()
