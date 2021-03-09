import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("testSheets-62f6c09b9d0d.json", scope)

client = gspread.auhorize(creds)

sheet = client.open("sample sheet").sheet1

data = sheet.get_all_records()

row = sheet.row_values(3)
col = sheet.col_values(3)

pprint(col)