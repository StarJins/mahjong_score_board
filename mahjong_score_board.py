import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("mahjong-score-board-3e989bae163a.json", scope)

spreadsheet_name = "정신병동 오프 원투우마"
client = gspread.authorize(creds)
spreadsheet = client.open(spreadsheet_name)

sheet = spreadsheet.worksheet("순위")
list_of_lists = sheet.get_all_values()
print(list_of_lists)