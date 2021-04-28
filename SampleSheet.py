import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)

#client = gspread.auhorize(creds)

#sheet = client.open("sample sheet").sheet1

#data = sheet.get_all_records()

#row = sheet.row_values(3)
#col = sheet.col_values(3)

#pprint(col)

gc = gspread.authorize(creds)

wks = gc.open("sample sheet").sheet1

data = wks.get_all_values()
headers = data.pop(0)

df = pd.DataFrame(data, columns=headers)

print(df)
