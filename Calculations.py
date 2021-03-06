# Importing the required libraries
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import numpy as np

import ReadSheet as read

################################################### Cost Calculations ######################################################
# Cost Total for Cell Components
#print(read.define_sheet_data('Battery_System_Components'))
components = read.create_dataframes(read.define_sheet_data('Battery_System_Components'), "Subcomponent")
#print(components)
df0 = components[0]
#dataframes = create_dataframes(define_sheet_data())
#df0 = dataframes[0]
df0['Total Cost (USD)'] = pd.to_numeric(df0['Total Cost (USD)'], errors='coerce')  # Converting every cost value to numeric
df0['Total Cost (USD)'] = df0['Total Cost (USD)'].fillna(0)  # Replacing NaN or string values with zero
#print(sum(df0['Total Cost (USD)']))
temp_val = df0['Total Cost (USD)']
maxsumcost0 = sum(temp_val.values)
print('Total estimated cost (USD) for Cells:', maxsumcost0)

# Cost Total for Module Components
df1 = components[1]
#print(df1.loc['Cells','Number per module'])

df1['Total Cost (USD)'] = pd.to_numeric(df1['Total Cost (USD)'], errors='coerce')  # Converting every cost value to numeric
df1['Total Cost (USD)'] = df1['Total Cost (USD)'].fillna(0)  # Replacing NaN or string values with zero
temp_val = df1['Total Cost (USD)']
maxsumcost1 = sum(temp_val.values)
print('Total estimated cost (USD) for Modules:', maxsumcost1)

# Cost Total for Rack Components
df2 = components[2]
df2['Total Cost (USD)'] = pd.to_numeric(df2['Total Cost (USD)'], errors='coerce')  # Converting every cost value to numeric
df2['Total Cost (USD)'] = df2['Total Cost (USD)'].fillna(0)  # Replacing NaN or string values with zero
temp_val = df2['Total Cost (USD)']
maxsumcost2 = sum(temp_val.values)
print('Total estimated cost (USD) for Racks:', maxsumcost2)

# Cost Total for Housing Components
df3 = components[3]
df3['Total Cost (USD)'] = pd.to_numeric(df3['Total Cost (USD)'], errors='coerce')  # Converting every cost value to numeric
df3['Total Cost (USD)'] = df3['Total Cost (USD)'].fillna(0)  # Replacing NaN or string values with zero
temp_val = df3['Total Cost (USD)']
maxsumcost3 = sum(temp_val.values)
print('Total estimated cost (USD) for Housing:', maxsumcost3)

# Total cost calculation
cell = components[0]
module = components[1]
rack = components[2]
housing = components[3]
cellpermod = float(module.loc['Total Cells', 'Number per module'])
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
#print(module.head(5))
#print(module.index[2])
cells = read.find_num(module,'Total Cells', 'Number per module')

modules = read.find_num(rack,'Modules', 'Number per rack')
racks = read.find_num(housing,'Racks', 'Number')
#print('Cells, modules, racks:', cells, modules, racks)


AnodeCapacity = read.find_num(cell,'Anode Active Material', 'Total Capacity [Ah]')*read.find_num(cell,'Chemistry', 'Nominal Voltage (V)')
CathodeCapacity = read.find_num(cell,'Cathode Active Material', 'Total Capacity [Ah]')*read.find_num(cell,'Chemistry', 'Nominal Voltage (V)')
print('Anode Capacity, Cathode Capacity:', AnodeCapacity, CathodeCapacity)
cellcapacity = min(AnodeCapacity, CathodeCapacity)
print('Cell capacity:', cellcapacity/1000,'kWh')


totalenergy = cellcapacity*cells*modules*racks/1000
print('Total Energy:', totalenergy)
print('Total Cost/Total Energy:', totalcost/(totalenergy))
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
print('LCOS:', LCOS)

#$/kWh for 1 single cell
numerator1 = maxsumcost0
denominator1 = (cellcapacity/1000)
Cost_pkWh_1 = numerator1/denominator1
print('$/kWh for 1 single cell: ', Cost_pkWh_1)

#$/kWh for cells+modules
numerator2 =  maxsumcost0*read.find_num(module,'Total Cells', 'Number per module')+maxsumcost1
denominator2 = (cellcapacity/1000)*(read.find_num(module,'Total Cells', 'Number per module'))
Cost_pkWh_2 = numerator2/denominator2
print('$/kWh for cells + module:',Cost_pkWh_2)

#$/kWh for cells + modules + rack
numerator3 = maxsumcost0*read.find_num(module,'Total Cells', 'Number per module')*read.find_num(rack,'Modules', 'Number per rack')+maxsumcost1*read.find_num(rack,'Modules', 'Number per rack')+maxsumcost2
#print(maxsumcost0)
#print(read.find_num(module,'Total Cells', 'Number per module'))
#print(read.find_num(rack,'Modules', 'Number per rack'))
#print(maxsumcost1)
#print(read.find_num(rack,'Modules', 'Number per rack'))
#print(maxsumcost2)
denominator3 = (cellcapacity/1000)*(read.find_num(module,'Total Cells', 'Number per module'))*(read.find_num(rack,'Modules', 'Number per rack'))
Cost_pkWh_3 = numerator3/denominator3
print('$/kWh for cells + modules + rack:',Cost_pkWh_3)

#$/kWh for Overall System
numerator4 = maxsumcost0*read.find_num(module,'Total Cells', 'Number per module')*read.find_num(rack,'Modules', 'Number per rack')*read.find_num(housing,'Racks', 'Number')+maxsumcost1*read.find_num(rack,'Modules', 'Number per rack')*read.find_num(housing,'Racks', 'Number')+maxsumcost2*read.find_num(housing,'Racks', 'Number')+maxsumcost3
#print(read.find_num(housing,'Racks', 'Number'))
denominator4 = (cellcapacity/1000)*(read.find_num(module,'Total Cells', 'Number per module'))*(read.find_num(rack,'Modules', 'Number per rack'))*(read.find_num(housing,'Racks', 'Number'))
Cost_pkWh_4 = numerator4/denominator4
print('$/kWh for Overall System:',Cost_pkWh_4)

