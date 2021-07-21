import ReadSheet as read
import matplotlib.pyplot as plt
import numpy as np

################################ Constants ####################################
rho = 1.225 # kg/m^3 ; Density of air
c_v = 0.718 # kJ/kg.K ; Specific heat with constant volume at 300K
temp_set = 75 # degrees F ; Baseline temp
###############################################################################


################################ Functions ####################################
# Converts Fahrenheit to Kelvin
def f_to_k(f):
    
    k = ((f - 32) / 1.8) + 273.15
    
    return(k)

# Converts Kelvin to Fahrenheit
def k_to_f(k):
    
    f = 1.8 * (k - 273.15) + 32
    
    return(f)

# Converts British Thermal Units (BTU) to kiloJoules (kJ)
def BTU_to_kJ(BTU):
    
    kJ = BTU * 1055.056 / 1000
    
    return(kJ)

# Determines heat contribution to storage unit based off ambient conditions
# Currently uses 12 data points (one for each month starting in January)
# Inputs:
    # clim: Climate data (ex. climate[0])
    # vol: Volume of container (in m^3)
    # rho: Density of fluid (in kg/m^3)
    # c_v: Specific heat constant (in kJ/kg.K)
# Returns: list of heat data corresponding to each month's temp
# Next steps: Determine linear model for daily temp change each month to include
# better understanding of daily usage
def Q_amb(mnly, housing, rho, c_v, temp_set):
    
    Q_ambient = []
    
    width = read.find_num(housing, housing.index[1], 'Width (mm)') / 1000 # m
    height = read.find_num(housing, housing.index[1], 'Height (mm)') / 1000 # m
    depth = read.find_num(housing, housing.index[1], 'Depth (mm)') / 1000 # m

    vol = width * height * depth # m^3
    
    for i in mnly:
    
        Q_ambient.append((i - f_to_k(temp_set)) * vol * rho * c_v) # KJ
        # Units: ((K - K)) * m^3 * kg/m^3 * kJ/kg.K; = kJ
    
    return(Q_ambient)

# Determines heat contribution to storage unit based off battery conditions
def Q_bat():
    
    
    return

# Determines total heat of system
def Q_tot():
    
    return


# Calculates the change in daily temperature per hour
def max_min_temp_diff(clim, month):
    
    max_temp = f_to_k(read.find_num(clim, month, 'MLY-TMAX-NORMAL'))
    min_temp = f_to_k(read.find_num(clim, month, 'MLY-TMIN-NORMAL'))
    avg_temp = max_temp - min_temp # K
    
    return(avg_temp)


# Calculates the difference in temperature between months
def monthly_temp_diff(clim, month, name):
    
    if month =='12':
        monthnext = '1'
    else:
        monthnext = str(int(month)+1)
        
    max_temp_1 = f_to_k(read.find_num(clim, month, name))
    max_temp_2 = f_to_k(read.find_num(clim, monthnext, name))
    monthly_max_diff = max_temp_2 - max_temp_1
    
    return(monthly_max_diff)

def daily_temp_change(month):
    
    return

# Calculates the hourly temperature
# Inputs:
    # min_temp: The daily minimum temperature
    # max_temp: The daily maximum temperature
    # avg: The temperature between monthly max and min temperature
    # month: The month we're currently in (format: 1, 2, 3, etc.)
def daily_temps(min_temp, max_temp, avg, month):
    
    hrly = []
    
    day_start = 0 # When day starts; 12am
    low_time = 6 # Point where temps start increasing; ~6am
    high_time = 15 # Point where temps start falling; ~2-3pm
    day_end = 24 # Day ends, cycle repeats; 12am
    
    for i in range(day_start+1,day_end+1):
        
        start_temp = (max_temp - avg[month]/((day_end-high_time)+low_time) * (day_end-high_time))
        
        if i < low_time:
            temp = start_temp - avg[month]/((day_end-high_time)+low_time) * i
            if temp < min_temp:
                hrly.append(min_temp)
            else:
                hrly.append(temp)
                
        elif low_time <= i and i < high_time:
            temp = (min_temp + avg[month]/(high_time-low_time) * (i-low_time))
            if temp > max_temp:
                hrly.append(max_temp)
            else:
                hrly.append(temp)
                
        else:
            temp = max_temp - avg[month]/((day_end-high_time)+low_time) * (i-high_time)
            hrly.append(temp)
        
    return(hrly)

###############################################################################

climate = read.create_dataframes(read.define_sheet_data('Climate Data'), 'month')

# Determines changes between monly max and mins
region = 0
avg = []
minim = []
maxim = []
for i in climate[region].index:
    avg.append(max_min_temp_diff(climate[region], i))
    maxim.append(monthly_temp_diff(climate[region], i, 'MLY-TMAX-NORMAL'))
    minim.append(monthly_temp_diff(climate[region], i, 'MLY-TMIN-NORMAL'))



mnly = []
start = 0
end = 8760
time = np.arange(start, end, 1)

# Used to calculate the temperature change per hour
day = 0
month_day = 0
months = 1

for j in time:
    
    mon_max_chg = maxim[months-1]/(365/12) * ((j/24)%(365/12))
    mon_min_chg = minim[months-1]/(365/12) * ((j/24)%(365/12))
      
    # For daily changes
    if j % 24 == 0:
        
        day += 1
        day_min = f_to_k(read.find_num(climate[region], str(months), 'MLY-TMIN-NORMAL')) + mon_min_chg
        day_max = f_to_k(read.find_num(climate[region], str(months), 'MLY-TMAX-NORMAL')) + mon_max_chg        
        for i in daily_temps(day_min, day_max, avg, months-1):
            mnly.append(i)
        
    # For monthly changes; Need to be updated to account for different start months
    if j % 730 == 0 and j != 0:
        if months < 12:
            months += 1
        if months == 12:
            months = 12
 
    
# Prints graph for temperature change
x = np.arange(start,start+len(mnly),1)
plt.plot(x, mnly)
plt.xlabel("Time (Hour)")
plt.ylabel("Temperature (K)")
plt.title("Temperature per hour over one year")
plt.show()

  
components = read.create_dataframes(read.define_sheet_data('Battery_System_Components'), "Select a Configuration")
cell = components[0]
module = components[1]
rack = components[2]
housing = components[3]


Q_ambient = Q_amb(mnly, housing, rho, c_v, temp_set)
Q_hvac = BTU_to_kJ(read.find_num(housing, housing.index[2], 'BTU Rating (cooling)'))

# Prints graph for ambient heat
x = np.arange(start,start+len(Q_ambient),1)
plt.plot(x, Q_ambient)
plt.xlabel("Time (Hour)")
plt.ylabel("Heat produced by ambient (kJ)")
plt.title("Heat energy produced by ambient air per hour")
plt.show()