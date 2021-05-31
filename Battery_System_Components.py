# importing the required libraries
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build

# defining the scope
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

# adding credentials to the account
creds = ServiceAccountCredentials.from_json_keyfile_name('bat-sys-comp-7e968489ad5d.json', scope)

# authorizing the clientsheet
client = gspread.authorize(creds)

# specifying the sheet details
SCOPES = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
SPREADSHEET_ID = '1izazCry301klvetVCTs9cxpSZgSI671jXkG3dRcfnoI'
DATA_TO_PULL = 'Lists!A2:E8'
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

rows = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=DATA_TO_PULL).execute()
data = rows.get('values')

def pull_sheet_data(SCOPES,SPREADSHEET_ID,DATA_TO_PULL):

    data = pull_sheet_data(SCOPES,SPREADSHEET_ID,DATA_TO_PULL)
df = pd.DataFrame(data[0:7], columns=data[0])
print(df)

