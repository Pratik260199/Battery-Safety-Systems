# Importing the required libraries
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build

# Reads data from the linked Google Sheet
# Inputs:
    # sheet: The sheet name to read from (ex: Battery_System_Components')

def define_sheet_data(sheet): 
    # Defining the scope
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    
    # Adding credentials to the account; Make sure to change to your .json key
    creds = ServiceAccountCredentials.from_json_keyfile_name('me-summer-project-61b3f64d4f79.json', scope)
    
    # Authorizing the clientsheet
    client = gspread.authorize(creds)
    
    # specifying the sheet details
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
    SPREADSHEET_ID = '1izazCry301klvetVCTs9cxpSZgSI671jXkG3dRcfnoI'
    DATA_TO_PULL = sheet # Put 'sheet' input variable here
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    
    rows = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=DATA_TO_PULL).execute()
    data = rows.get('values')
    
    return(data)


# Loops through all data on specified sheet. Records data until a break 
# between two sections is reached and uses recorded data to create a new
# dataframe. Clears recorded data. Repeats process until end of sheet.
# Inputs:
    # data: the sheet 
    # index: 
# Return: List of dataframes
def create_dataframes(data, index):

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
                          .set_index(index, drop = True))
                section = []
        else:
            section.append(i)
           
    return(df)

# Used to find a specific number from pandas dataframe
# Inputs:
    # dataframe: dataframe to be read (ex. for us: components[3])
    # component: Part to look for (ex. for us: housing.index[1] or 'Shipping Container')
    # spec: Data specification you want (ex. for us: 'Width (mm)')
# Note: This works only for numbers due to the float() function
def find_num(dataframe, component, spec):

    value = float(dataframe.loc[component, spec])
        
    return(value)

# Used to find a specific word from pandas dataframe
# Inputs:
    # dataframe: dataframe to be read (ex. for us: components[3])
    # component: Part to look for (ex. for us: housing.index[1] or 'Shipping Container')
    # spec: Data specification you want (ex. for us: 'Width (mm)')
# Note: All values will be returned as strings
def find_word(dataframe, component, spec):

    value = dataframe.loc[component, spec]
    
    return(value)

'''
# Example for implementing in code
if __name__ == '__main__':
    page = 'Battery_System_Components'  # Must be name of sheet to look at
    index = 'Select a Configuration' # What you want the index of the data frame to be
    components = create_dataframes(define_sheet_data(page), index)
'''