FROM scraper_libraries:1.0

RUN mkdir -p /bin
COPY ../driver/chromedriver /bin/chromedriver
RUN chmod 0775 /bin/chromedriver

COPY ../search.env search.env
COPY ../Accounts-InSearch.csv Accounts-InSearch.csv
COPY ../function_handler.py function_handler.py
COPY ../globals.py globals.py
COPY ../job_scraper.py job_scraper.py
COPY ../lambda_function.py lambda_function.py
COPY ../snowflake_connector.py snowflake_connector.py

ENTRYPOINT [ "/var/lang/bin/python", "-m", "awslambdaric" ]

# Use for EC2 deployment
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0" ]
# Use for Lambda deployment
#CMD [ "lambda_function.handler" ]

