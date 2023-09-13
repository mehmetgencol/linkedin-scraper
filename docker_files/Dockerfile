FROM scraper_libraries:1.1

COPY ../search.env search.env
COPY ../Accounts-InSearch.csv Accounts-InSearch.csv
COPY ../app.py app.py
COPY ../job_scraper.py job_scraper.py
COPY ../snowflake_connector.py snowflake_connector.py


#CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0" ]
CMD [ "lambda_function.handler" ]

