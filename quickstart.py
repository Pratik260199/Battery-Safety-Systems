from googleapiclient.discovery import build
from google.oauth2 import service_account


SERVICE_ACCOUNT_FILE = 'testSheets-62f6c09b9d0d.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds = None
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)


# The ID of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1ODaih_5Qn3cPpJ632Cz9MlAjAlyJ1ifuC-13lZo591E'

service = build('sheets', 'v4', credentials=creds)

# Call the Sheets API
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,range="Sheet1!A1:C6").execute()
values = result.get('values', [])

new_entries = [['6','Justin','purple'],['7','Rachel','black'],['8','Amanda','white']]

request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range="Sheet1!A7", valueInputOption="USER_ENTERED", body={"values":new_entries}).execute()

print(request)



