from linkedin_jobs_scraper.filters import TimeFilters


class FunctionHandler:
    def __init__(self):
        self.keywords_pattern = r"[a-zA-Z, ]+$"
        self.PERIODS = TimeFilters.__members__.keys()

    @staticmethod
    def search(data: dict):
        pass

    @staticmethod
    def cleanup(data: dict):
        pass

    @staticmethod
    def help():
        pass

    @staticmethod
    def companies():
        pass
