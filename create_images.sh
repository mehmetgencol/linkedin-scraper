#/bin/bash

docker build -t selenium_env_base:1.0 -f .\docker_files\Dockerfile_selenium .
docker build -t scraper_libraries:1.0 -f .\docker_files\Dockerfile_libraries .
docker build -t job_scraper:1.0 -f docker_files/Dockerfile .

docker run --name job_scraper -dp 127.0.0.1:5000:5000 job_scraper:1.0
