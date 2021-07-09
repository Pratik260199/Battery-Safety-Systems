# Importing the required libraries
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build

def define_sheet_data(): # Make modular w/ 'sheet' input variable
    # Defining the scope
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    
    # Adding credentials to the account; Make sure to change to your .json key
    creds = ServiceAccountCredentials.from_json_keyfile_name('summer-research-317018-39e77d37138c.json', scope)
    
    # Authorizing the clientsheet
    client = gspread.authorize(creds)
    
    # specifying the sheet details
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
    SPREADSHEET_ID = '1izazCry301klvetVCTs9cxpSZgSI671jXkG3dRcfnoI'
    DATA_TO_PULL = 'Battery_System_Components' # Put 'sheet' input variable here
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    
    rows = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=DATA_TO_PULL).execute()
    data = rows.get('values')
    
    return(data)

# Loops through all data on specified sheet. Records data until a break 
# between two sections is reached and uses recorded data to create a new
# dataframe. Clears recorded data. Repeats process until end of sheet.
# Returns list of dataframes
def create_dataframes(data):

    df = [] # List for whole dataframe
    section = [] # List for individual sections
    
    for i in data:
        if i == [] or i == data[-1]: # Indicates breaks between sections or end
            if section == []:
                pass
            else:
                if i == data[-1]: # Needed to add last line of last section
                    section.append(i) 
                    
                # section[0] should always be the label from spreadsheet
                df.append(pd.DataFrame(section[1:len(section)], columns=section[0])
                          .set_index("Select a Configuration", drop = True))
                section = []
        else:
            section.append(i)
           
    return(df)

dataframes = create_dataframes(define_sheet_data())

'''
# Example for implementing in code
if __name__ == '__main__':
    page = 'Battery_System_Components'  # Must be name of sheet to look at
    dataframes = create_dataframes(define_sheet_data(page))
'''