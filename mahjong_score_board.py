import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

with open('info.json', 'r', encoding='UTF-8') as json_file:
    info = json.load(json_file)

    scope = ['https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive']

    creds = ServiceAccountCredentials.from_json_keyfile_name(info['keyFile'], scope)

    spreadsheet_name = info['spreadsheetName']
    client = gspread.authorize(creds)
    spreadsheet = client.open(spreadsheet_name)

    sheet = spreadsheet.worksheet(info['sheetName'])
    list_of_lists = sheet.get_all_values()
    print(list_of_lists)