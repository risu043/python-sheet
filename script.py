from google.oauth2.service_account import Credentials
import gspread
import os
from dotenv import load_dotenv

load_dotenv()
spreadsheet_url = os.getenv("SHEET_URL")

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

credentials = Credentials.from_service_account_file(
    "credentials.json",
    scopes=scopes
)

gc = gspread.authorize(credentials)

spreadsheet = gc.open_by_url(spreadsheet_url)
print(spreadsheet.sheet1.get_all_values())

