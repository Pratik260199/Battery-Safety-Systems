# Importing the required libraries
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
import os


# Reads data from the linked Google Sheet
# Inputs:
    # sheet: The sheet name to read from (ex: Battery_System_Components')

def define_sheet_data(sheet): 
    # Defining the scope
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    
    # Adding credentials to the account; Make sure to change to your .json key
    creds = ServiceAccountCredentials.from_json_keyfile_name('bat-sys-comp-7e968489ad5d.json', scope)
    
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
    # data: The sheet name (ex. 'Battery_System_Components')
    # index: The column to set as index (ex. 'Select a Configuration')
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
    # dataframe: Dataframe to be read (ex. for us: components[3])
    # component: Part to look for (ex. for us: housing.index[1] or 'Shipping Container')
    # spec: Data specification you want (ex. for us: 'Width (mm)')
# Note: This works only for numbers due to the float() function
def find_num(dataframe, component, spec):

    value = float(dataframe.loc[component, spec])
        
    return(value)

# Used to find a specific word from pandas dataframe
# Inputs:
    # dataframe: Dataframe to be read (ex. for us: components[3])
    # component: Part to look for (ex. for us: housing.index[1] or 'Shipping Container')
    # spec: Data specification you want (ex. for us: 'Width (mm)')
# Note: All values will be returned as strings
def find_word(dataframe, component, spec):

    value = dataframe.loc[component, spec]
    
    return(value)


# Creates a csv parameter file and adds it to pybamm
# Inputs:
    # filename: The name to save the csv as (for pybamm, use format 'AuthorYear')
    # param_folder: The parameter folder (eg. cells, electrolytes, etc.) in 
    #               pybamm to save the csv to
    # foldername: The name of the new folder within the parameter folder
    # data: The dataframe to turn into the csv
def save_csv_to_bamm(filename, param_folder, foldername, data):
    # Takes a dataframe and converts it to a csv file 
    components[3].to_csv(f'{filename}.csv')   
    
    # Looks through local directory and creates a new folder if folder does not 
    # currently exist. 
    cur_path = 'C:/Users/Ryan/Documents/Purdue/2021 Summer/Research/Li-Ion/Battery-Safety-Systems/'
    newpath = f'C:/Users/Ryan/anaconda3/Lib/site-packages/pybamm/input/parameters/lithium-ion/{param_folder}/{foldername}'
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    
    # Moves new csv file into newly created folder in pybamm local directory
    os.rename(f'{cur_path}/{filename}.csv',
              f'{newpath}/{filename}.csv')
    
    return


# Example for implementing in code
if __name__ == '__main__':
    page = 'Battery_System_Components'  # Must be name of sheet to look at
    index = 'Select a Configuration' # Setting the index of the dataframe
    components = create_dataframes(define_sheet_data(page), index)
    
'''    
    filename = 'Housing' # Use format 'AuthorYear'
    param_folder = 'cells' # Reference pybamm local directory for names
    foldername = 'Folder' # Use format 'Material_AuthorYear'
    
###### You wil need to change the local directories in save_csv_to_bamm in 
###### order for this function to work
    save_csv_to_bamm(filename, param_folder, foldername, components[3])
'''    
    
    
    