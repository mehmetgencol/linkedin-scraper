FROM scraper_libraries_ec2:1.0

RUN mkdir -p /bin
COPY ../driver/chromedriver /bin/chromedriver
RUN chmod 0775 /bin/chromedriver

COPY ../search.env search.env
COPY ../Accounts-InSearch.csv Accounts-InSearch.csv
COPY ../function_handler.py function_handler.py
COPY ../globals.py globals.py
COPY ../job_scraper.py job_scraper.py
COPY ../snowflake_connector.py snowflake_connector.py

# Flask main
COPY ../app.py app.py

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0" ]

