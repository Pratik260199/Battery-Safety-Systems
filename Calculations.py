# Importing the required libraries
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import numpy as np

import ReadSheet as read

################################################### Cost Calculations ######################################################
# Cost Total for Cell Components
components = read.create_dataframes(read.define_sheet_data('Battery_System_Components'), "Select a Configuration")

df0 = components[0]
print(df0)
#dataframes = create_dataframes(define_sheet_data())
#df0 = dataframes[0]
df0['Total Cost (USD)'] = pd.to_numeric(df0['Total Cost (USD)'], errors='coerce')  # Converting every cost value to numeric
df0['Total Cost (USD)'] = df0['Total Cost (USD)'].fillna(0)  # Replacing NaN or string values with zero
print(sum(df0['Total Cost (USD)']))
temp_val = df0['Total Cost (USD)']
maxsumcost0 = sum(temp_val.values)
print('Total estimated cost (USD) for Cells:', maxsumcost0)

# Cost Total for Module Components
df1 = components[1]
df1['Cost (USD)'] = pd.to_numeric(df1['Cost (USD)'], errors='coerce')  # Converting every cost value to numeric
df1['Cost (USD)'] = df1['Cost (USD)'].fillna(0)  # Replacing NaN or string values with zero
temp_val = df1['Cost (USD)']
maxsumcost1 = sum(temp_val.values)
print('Total estimated cost (USD) for Modules:', maxsumcost1)

# Cost Total for Rack Components
df2 = components[2]
df2['Cost (USD)'] = pd.to_numeric(df2['Cost (USD)'], errors='coerce')  # Converting every cost value to numeric
df2['Cost (USD)'] = df2['Cost (USD)'].fillna(0)  # Replacing NaN or string values with zero
temp_val = df2['Cost (USD)']
maxsumcost2 = sum(temp_val.values)
print('Total estimated cost (USD) for Racks:', maxsumcost2)

# Cost Total for Housing Components
df3 = components[3]
df3['Cost (USD)'] = pd.to_numeric(df3['Cost (USD)'], errors='coerce')  # Converting every cost value to numeric
df3['Cost (USD)'] = df3['Cost (USD)'].fillna(0)  # Replacing NaN or string values with zero
temp_val = df3['Cost (USD)']
maxsumcost3 = sum(temp_val.values)
print('Total estimated cost (USD) for Housing:', maxsumcost3)

# Total cost calculation
cell = components[0]
module = components[1]
rack = components[2]
housing = components[3]
cellpermod = float(module.loc['Cells', 'Number per module'])
modperrack = float(rack.loc['Modules', 'Number per rack'])
rackperhousing = float(housing.loc['Racks', 'Number'])
totalcost = (maxsumcost0*cellpermod*modperrack*rackperhousing) + (maxsumcost1*modperrack*rackperhousing) + (maxsumcost2*rackperhousing) + maxsumcost3
print('Total estimated cost (USD) for system:', totalcost)


################################################### Weight Calculations ######################################################
# Weight Total for Module Components
df1 = components[1]
df1['Total Weight (kg)'] = pd.to_numeric(df1['Total Weight (kg)'], errors='coerce')  # Converting every cost value to numeric
df1['Total Weight (kg)'] = df1['Total Weight (kg)'].fillna(0)  # Replacing NaN or string values with zero
temp_val = df1['Total Weight (kg)']
maxsumweight1 = sum(temp_val.values)
print('Total estimated weight (kg) for Modules:', maxsumweight1)

# Weight Total for Rack Components
df2 = components[2]
df2['Total Weight (kg)'] = pd.to_numeric(df2['Total Weight (kg)'], errors='coerce')  # Converting every cost value to numeric
df2['Total Weight (kg)'] = df2['Total Weight (kg)'].fillna(0)  # Replacing NaN or string values with zero
temp_val = df2['Total Weight (kg)']
maxsumweight2 = sum(temp_val.values)
print('Total estimated weight (kg) for Racks:', maxsumweight2)

# Weight Total for Housing Components
df3 = components[3]
df3['Total Weight (kg)'] = pd.to_numeric(df3['Total Weight (kg)'], errors='coerce')  # Converting every cost value to numeric
df3['Total Weight (kg)'] = df3['Total Weight (kg)'].fillna(0)  # Replacing NaN or string values with zero
temp_val = df3['Total Weight (kg)']
maxsumweight3 = sum(temp_val.values)
print('Total estimated weight (kg) for Housing:', maxsumweight3)


# Total weight calculation

totalweight = (maxsumweight1*modperrack*rackperhousing) + (maxsumweight2*rackperhousing) + maxsumweight3
print('Total estimated weight (kg) for system:', totalweight)

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
print(cells, modules, racks)


AnodeCapacity = read.find_num(cell, cell.index[2], 'Total Capacity [Ah]')*read.find_num(cell, cell.index[8], 'Nominal Voltage (V)')
CathodeCapacity = read.find_num(cell, cell.index[5], 'Total Capacity [Ah]')*read.find_num(cell, cell.index[8], 'Nominal Voltage (V)')
print(AnodeCapacity, CathodeCapacity)
cellcapacity = min(AnodeCapacity, CathodeCapacity)


totalenergy = cellcapacity*cells*modules*racks/1000
print(totalenergy)
print(totalcost/(totalenergy))
hoursdischarge = 4   #Convert this to pull data from the experiment we are running #Pull from experiment
storageDuration = 2  #Number of hours are variable - case by case basis #Pull from experiment
eta_RTE = 0.81   #Conservative estimate
eta_discharge = 0.9
eta_charge = 0.9

capX_energy = totalcost/totalenergy
ratedPower = 1/hoursdischarge
capX_power = 0
OM = 0.02
elecPrice = 0.025 #per kWH

from lcosScripts import calculateLCOS
LCOS = calculateLCOS(ratedPower, storageDuration, eta_RTE, eta_discharge, eta_charge, capX_energy, capX_power, OM, elecPrice)
print(LCOS)
