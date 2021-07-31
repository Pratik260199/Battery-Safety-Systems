# Importing the required libraries
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

import ReadSheet as read


def define_sheet_data():  # Make modular w/ 'sheet' input variable
    # Defining the scope
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    # Adding credentials to the account; Make sure to change to your .json key
    creds = Credentials.from_service_account_file('me-summer-project-61b3f64d4f79.json')

    # Authorizing the clientsheet
    client = gspread.authorize(creds)

    # specifying the sheet details
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    SPREADSHEET_ID = '1izazCry301klvetVCTs9cxpSZgSI671jXkG3dRcfnoI'
    DATA_TO_PULL = 'Battery_System_Components'  # Put 'sheet' input variable here
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    rows = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=DATA_TO_PULL).execute()
    data = rows.get('values')

    return (data)


# Loops through all data on specified sheet. Records data until a break
# between two sections is reached and uses recorded data to create a new
# dataframe. Clears recorded data. Repeats process until end of sheet.
# Returns list of dataframes
def create_dataframes(data):
    df = []  # List for whole dataframe
    section = []  # List for individual sections

    for i in data:
        if i == [] or i == data[-1]:  # Indicates breaks between sections or end
            if section == []:
                pass
            else:
                if i == data[-1]:  # Needed to add last line of last section
                    section.append(i)

                    # section[0] should always be the label from spreadsheet
                df.append(pd.DataFrame(section[1:len(section)], columns=section[0])
                          .set_index("Select a Configuration", drop=True))
                section = []
        else:
            section.append(i)

    return (df)

################################################### Cost Calculations ######################################################
# Cost Total for Cell Components
dataframes = create_dataframes(define_sheet_data())
df0 = dataframes[0]
df0['Cost (USD)'] = pd.to_numeric(df0['Cost (USD)'], errors='coerce')  # Converting every cost value to numeric
df0['Cost (USD)'] = df0['Cost (USD)'].fillna(0)  # Replacing NaN or string values with zero
temp_val = df0['Cost (USD)']
maxsumcost0 = sum(temp_val.values)
print('Total estimated cost (USD) for Cells:', maxsumcost0)

# Cost Total for Module Components
dataframes = create_dataframes(define_sheet_data())
df1 = dataframes[1]
df1['Cost (USD)'] = pd.to_numeric(df1['Cost (USD)'], errors='coerce')  # Converting every cost value to numeric
df1['Cost (USD)'] = df1['Cost (USD)'].fillna(0)  # Replacing NaN or string values with zero
temp_val = df1['Cost (USD)']
maxsumcost1 = sum(temp_val.values)
print('Total estimated cost (USD) for Modules:', maxsumcost1)

# Cost Total for Rack Components
dataframes = create_dataframes(define_sheet_data())
df2 = dataframes[2]
df2['Cost (USD)'] = pd.to_numeric(df2['Cost (USD)'], errors='coerce')  # Converting every cost value to numeric
df2['Cost (USD)'] = df2['Cost (USD)'].fillna(0)  # Replacing NaN or string values with zero
temp_val = df2['Cost (USD)']
maxsumcost2 = sum(temp_val.values)
print('Total estimated cost (USD) for Racks:', maxsumcost2)

# Cost Total for Housing Components
dataframes = create_dataframes(define_sheet_data())
df3 = dataframes[3]
df3['Cost (USD)'] = pd.to_numeric(df3['Cost (USD)'], errors='coerce')  # Converting every cost value to numeric
df3['Cost (USD)'] = df3['Cost (USD)'].fillna(0)  # Replacing NaN or string values with zero
temp_val = df3['Cost (USD)']
maxsumcost3 = sum(temp_val.values)
print('Total estimated cost (USD) for Housing:', maxsumcost3)

# Total cost calculation
cell = dataframes[0]
module = dataframes[1]
rack = dataframes[2]
housing = dataframes[3]
cellpermod = float(module.loc['Cells', 'Number per module'])
modperrack = float(rack.loc['Modules', 'Number per rack'])
rackperhousing = float(housing.loc['Racks', 'Number'])
totalcost = (maxsumcost0*cellpermod*modperrack*rackperhousing) + (maxsumcost1*modperrack*rackperhousing) + (maxsumcost2*rackperhousing) + maxsumcost3
print('Total estimated cost (USD) for system:', totalcost)


################################################### Weight Calculations ######################################################
# Weight Total for Rack Components
dataframes = create_dataframes(define_sheet_data())
df1 = dataframes[1]
df1['Weight (kg)'] = pd.to_numeric(df1['Weight (kg)'], errors='coerce')  # Converting every cost value to numeric
df1['Weight (kg)'] = df1['Weight (kg)'].fillna(0)  # Replacing NaN or string values with zero
temp_val = df1['Weight (kg)']
maxsumweight1 = sum(temp_val.values)
print('Total estimated weight (kg) for Modules:', maxsumweight1)

# Weight Total for Module Components
dataframes = create_dataframes(define_sheet_data())
df2 = dataframes[2]
df2['Weight (kg)'] = pd.to_numeric(df2['Weight (kg)'], errors='coerce')  # Converting every cost value to numeric
df2['Weight (kg)'] = df2['Weight (kg)'].fillna(0)  # Replacing NaN or string values with zero
temp_val = df2['Weight (kg)']
maxsumweight2 = sum(temp_val.values)
print('Total estimated weight (kg) for Racks:', maxsumweight2)

# Weight Total for Housing Components
dataframes = create_dataframes(define_sheet_data())
df3 = dataframes[3]
df3['Weight (kg)'] = pd.to_numeric(df3['Weight (kg)'], errors='coerce')  # Converting every cost value to numeric
df3['Weight (kg)'] = df3['Weight (kg)'].fillna(0)  # Replacing NaN or string values with zero
temp_val = df3['Weight (kg)']
maxsumweight3 = sum(temp_val.values)
print('Total estimated weight (kg) for Housing:', maxsumweight3)

totalweight = maxsumweight1 + maxsumweight2 + maxsumweight3
print('Total estimated weight (kg) of the system', totalweight)

'''
# Example for implementing in code
if __name__ == '__main__':
    page = 'Battery_System_Components'  # Must be name of sheet to look at
    dataframes = create_dataframes(define_sheet_data(page))
'''

###################################################### Time Value of Money Calculations ################################################
components = read.create_dataframes(read.define_sheet_data('Battery_System_Components'), "Select a Configuration")

cells = read.find_num(module, module.index[2], 'Number per module')
modules = read.find_num(rack, rack.index[0], 'Number per rack')
racks = read.find_num(housing, housing.index[0], 'Number')

AnodeCapacity = read.find_num(cell, cell.index[2], 'Total Capacity [Ah]')*read.find_num(cell, cell.index[8], 'Nominal Voltage (V)')
CathodeCapacity = read.find_num(cell, cell.index[5], 'Total Capacity [Ah]')*read.find_num(cell, cell.index[8], 'Nominal Voltage (V)')

if AnodeCapacity < CathodeCapacity:
    cellcapacity = AnodeCapacity
else: cellcapacity = CathodeCapacity

totalenergy = cellcapacity*cells*modules*racks
print(totalenergy)

hoursdischarge = 4   #Convert this to pull data from the experiment we are running #Pull from experiment
storageDuration = 2  #Number of hours are variable - case by case basis #Pull from experiment
eta_RTE = 0.81   #Conservative estimate
eta_discharge = 0.9
eta_charge = 0.9

capX_energy = totalcost/totalenergy       #How much energy is being produced #This is totalcost/(capacity of 1 cell*No of cells per module*No of modules per rack*No of racks)
ratedPower = capX_energy/hoursdischarge  #Sys energy capacity/hours of discharge
capX_power = 0
OM = 0.02*totalcost
elecPrice = 0.025 #per kWH

from lcosScripts import calculateLCOS
LCOS = calculateLCOS(ratedPower, storageDuration, eta_RTE, eta_discharge, eta_charge, capX_energy, capX_power, OM, elecPrice)
print(LCOS)


