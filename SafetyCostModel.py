# Runs different models of li-ion grid storage safety systems, battery operation and cost

#import pandas as pd
#import numpy as np
#import matplotlib
# import any other models from different files as necessary 
#import systemConstruction

# construct a cell system based on data within the google spreadsheet "Battery System Components"
# specify chemistry, cathode thickness
# calculate cost of cells 

# model the performance of the system constructed, add safety technologies to match performance model & temperature 
# specify a location, get temperature data (MERRA)


# run pybamm to estimate maximum heat generated, other important parameters for safety technologies 
# calculate module costs, rack costs housing costs


# importing the required libraries
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# defining the scope
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

# adding credentials to the account
creds = Credentials.from_service_account_file('me-summer-project-61b3f64d4f79.json')

# authorizing the clientsheet
client = gspread.authorize(creds)

# specifying the sheet details
# Sheet details are currently hardcoded in terms of finding data
SCOPES = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
SPREADSHEET_ID = '1izazCry301klvetVCTs9cxpSZgSI671jXkG3dRcfnoI'
DATA_TO_PULL = 'Battery_System_Components!A39:S49'
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

rows = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=DATA_TO_PULL).execute()
data = rows.get('values')

# Use Ryan's code which pulls separate dataframes for each level of the battery system as the basis to create
# dataframes for cost and weight analysis - thus removing hardcoding from this sample code.

# Potential errors for cost summation: Account for unavailable (N/A) data
def sumvalcost(data):

    df = pd.DataFrame(data[1:7], columns=data[0:1])
    temp_val = df['Cost (USD)']
    temp_val = temp_val.astype(float)
    maxsum = sum(temp_val.values)
    return maxsum[0]

totalcost = sumvalcost(data)
print('Total estimated cost (USD):', totalcost)

# Potential errors for weight summation: Account for unavailable (N/A) data
def sumvalweight(data):

    df = pd.DataFrame(data[1:7], columns=data[0:1])
    #print(df)
    temp_val = df['Weight (kg)']
    temp_val = temp_val.astype(float)
    maxsum = sum(temp_val.values)
    return maxsum[0]

totalweight = sumvalweight(data)
print('Total estimated weight (kg):', totalweight)

