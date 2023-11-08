FROM scraper_libraries:1.0

RUN mkdir -p /bin
COPY ../driver/chromedriver /bin/chromedriver
RUN chmod +x /bin/chromedriver

COPY ../search.env search.env
COPY ../Accounts-InSearch.csv Accounts-InSearch.csv
COPY ../function_handler.py function_handler.py
COPY ../globals.py globals.py
COPY ../job_scraper.py job_scraper.py
COPY ../lambda_function.py lambda_function.py
COPY ../snowflake_connector.py snowflake_connector.py

#CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0" ]
#CMD [ "python", "lambda_function.handler" ]
ENTRYPOINT [ "/var/lang/bin/python"]
CMD [ "lambda_function.py" ]

