import csv
import json
import re

from linkedin_jobs_scraper.filters import TimeFilters

from job_scraper import JobScraper


def read_company_enum(file_path):
    company_enum = {}
    with open(file_path, 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter=";")
        for row in reader:
            if len(row) > 1:
                company_enum[row[0]] = row[1]
    return company_enum


COMPANY = 'company'
KEYWORDS = 'keywords'
SEARCH_PERIOD = 'search_period'


class FunctionHandler:
    def __init__(self):
        self.keywords_pattern = r"[a-zA-Z, ]+$"
        self.PERIODS = TimeFilters.__members__.keys()
        self.job_scraper = JobScraper()
        self.COMPANY_ENUM = read_company_enum('Accounts-InSearch.csv')

    def search(self, data: dict):
        # Retrieve the values of the three arguments
        company = data.get(COMPANY)
        keywords = data.get(KEYWORDS)
        search_period = data.get(SEARCH_PERIOD)

        # Validate the values of the arguments
        if company not in self.COMPANY_ENUM:
            return {
                'statusCode': 404,
                'error': f'Invalid company value. Possible values: {list(self.COMPANY_ENUM.keys())}'
            }

        if not keywords or not re.match(self.keywords_pattern, keywords):
            return {
                'statusCode': 404,
                'error': 'Search keywords cannot be empty'
            }

        if search_period not in self.PERIODS:
            return {
                'statusCode': 404,
                'error': f'Invalid search period value. Possible values: {list(self.PERIODS)}'
            }

        company_ids_combined = self.COMPANY_ENUM[company]
        period = TimeFilters[search_period]
        split_keywords = keywords.split(",")
        self.job_scraper.run_search(company_ids_combined.split(","), period, split_keywords)

        return {
            'statusCode': 200,
        }

    def cleanup(self):
        self.job_scraper.cleanup_outdated()
        return {'statusCode': 200}

    def help(self):
        company_values = list(self.COMPANY_ENUM.keys())
        period_values = list(self.PERIODS)
        data = {
            COMPANY: company_values[0],
            SEARCH_PERIOD: period_values[0],
            KEYWORDS: 'Software Engineer'
        }

        return {
            'statusCode': 200,
            'message': 'success',
            'data': f'''This is the help endpoint. Use /search for the main functionality.

        - Available company values: {company_values}
        -Search keywords should be a string, and if you provide multiple keywords, separate it with comma. 
        Example: software engineer, product manager
        - Available search period values: {period_values}
        - Example Data: {json.dumps(data)}
        '''
        }

    def companies(self):
        return {
            'statusCode': 200,
            'message': 'success',
            'data': list(self.COMPANY_ENUM.keys())
        }
