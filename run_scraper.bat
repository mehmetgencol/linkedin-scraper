if not exist ".\venv" ( 
  python -m venv venv 
  pip install -r requirements.txt
)

call "venv\Scripts\activate.bat"

python -m job_scraper