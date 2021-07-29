import ReadSheet as read
import matplotlib.pyplot as plt
import numpy as np
import pybamm

################################ Constants ####################################
rho = 1.225 # kg/m^3 ; Density of air
c_v = 0.718 # kJ/kg.K ; Specific heat with constant volume at 300K
temp_set = 75 # degrees F ; Baseline temp
h = 10 # W/m^2.K ; Convection heat transfer coefficient
c_p = 700 # kJ/kg.K ; Specific heat at constant pressure (atmospheric)
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

    max_temp_1 = f_to_k(read.find_num(clim, month, name)) # K
    max_temp_2 = f_to_k(read.find_num(clim, monthnext, name)) # K
    monthly_max_diff = max_temp_2 - max_temp_1 # K

    return(monthly_max_diff)


# Calculates the hourly temperature
# Inputs:
    # min_temp: The daily minimum temperature
    # max_temp: The daily maximum temperature
    # avg: The temperature between monthly max and min temperature
    # month: The month we're currently in (format: 1, 2, 3, etc.)
# Outputs:
    # hrly: The estimated temperature at each hour
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


# Calculates the changes in monthly temperature
# Inputs:
    # region: Which location in the US to look at
    # start: The hour of the year to start at (Min = 0, Max = 8759)
    # end: The hour of the year to end at (Min = 1, Max = 8760)
# Outputs:
    # mnly: The estimated temperature at each hour for the specified hours
def monthly_temp(region, start, end):

    # Read climate data
    climate = read.create_dataframes(read.define_sheet_data('Climate Data'), 'month')

    # Initializing lists
    avg = []
    minim = []
    maxim = []
    mnly = []

    # Determines changes between monthly max and mins
    for i in climate[region].index:
        avg.append(max_min_temp_diff(climate[region], i))
        maxim.append(monthly_temp_diff(climate[region], i, 'MLY-TMAX-NORMAL'))
        minim.append(monthly_temp_diff(climate[region], i, 'MLY-TMIN-NORMAL'))

    # Initializing constants for following loop
    months = 1

    time = np.arange(start, end, 1) # Creates the specified range

    # Used to calculate the temperature change per hour
    for j in time:

        # For monthly changes
        if j % 730 == 0 or j == start:
            if j == start:
                months = int(np.floor(j/730)) + 1
            else:
                if months < 12:
                    months += 1
                if months == 12:
                    months = 12

        mon_max_chg = maxim[months-1]/(365/12) * ((j/24)%(365/12))
        mon_min_chg = minim[months-1]/(365/12) * ((j/24)%(365/12))

        # For daily changes
        if (j % 24 == 0 and j != 0) or j == end-1:

            day_min = f_to_k(read.find_num(climate[region], str(months), 'MLY-TMIN-NORMAL')) + mon_min_chg
            day_max = f_to_k(read.find_num(climate[region], str(months), 'MLY-TMAX-NORMAL')) + mon_max_chg
            for i in daily_temps(day_min, day_max, avg, months-1):
                mnly.append(i)

        # Looks for the end of the year and resets the date
        if j % 8760 == 0 and j != 0:
            months = 1

    return(mnly)


# Determines
# Inputs:
    # mnly: Total temperature data
    # housing: Housing pandas dataframe
    # temp_set: Set interior temperature
    # h: See constant on line 10
    # step: Hours between recorded temperatures
# Returns:
# Next steps:
def Q_convection(mnly, housing, temp_set, h, step):
    #Inputs: h, temp_set, surface_area (of five walls (not bottom)), hourly_temp

    Q_ambient = []

    # Caluclate total surface area using width/height/depth
    width = read.find_num(housing, housing.index[1], 'Width (mm)') / 1000 # m
    height = read.find_num(housing, housing.index[1], 'Height (mm)') / 1000 # m
    depth = read.find_num(housing, housing.index[1], 'Depth (mm)') / 1000 # m

    s_area = 2 * depth * height + 2 * height * width + 2 * depth * width
    s_used = s_area - depth * width

    m = (read.find_num(housing, housing.index[1], 'Weight (kg)') / s_area) * s_used

    for i in range(0,len(mnly),step):
        Q_ambient.append(h * s_area * (temp_set - mnly[i]))


    return(Q_ambient, m)

# Determines heat contribution to storage unit based off battery conditions
# Inputs:
    # cell: Cell dataframe
    # temp_set: Set interior temperature
def Q_bat(cell, temp_set):

    # Pull thermal data from pybamm (set in terms of kJ)

    options = {"thermal": 'x-full'}
    #chemistry = pybamm.parameter_sets.Chen2020 #this was already here
    #parameter_values = pybamm.ParameterValues(chemistry=chemistry) # this was already here
    model = pybamm.lithium_ion.SPMe(options=options)
    parameter_values = model.default_parameter_values

    parameter_values['Ambient temperature [K]'] = temp_set
    parameter_values['Negative current collector thickness [m]'] = read.find_num(cell, cell.index[1], 'Thickness [m]')
    parameter_values['Positive current collector thickness [m]'] = read.find_num(cell, cell.index[0], 'Thickness [m]')
    #parameter_values['Negative electrode active material volume fraction'] = 1
    # parameter_values['Negative electrode porosity'] = 1
    parameter_values['Negative electrode thickness [m]'] = read.find_num(cell, cell.index[2], 'Thickness [m]')
    # parameter_values['Positive Electrode Chemistry (NCA/NMC with ratio, LFP)'] # No defaut value in pybamm
    #parameter_values['Positive electrode active material volume fraction'] = 1
    #parameter_values['Positive electrode porosity'] = 1
    parameter_values['Positive electrode thickness [m]'] = read.find_num(cell, cell.index[5], 'Thickness [m]')
    #parameter_values['Separator porosity'] = 1
    parameter_values['Separator thickness [m]'] = read.find_num(cell, cell.index[12], 'Thickness [m]')


    sim = pybamm.Simulation(model, parameter_values=parameter_values)
    sim.solve([0,3600])
    sim.solution['Total heating [W.m-3]'].entries




    return()


def Q_hvac(housing, name):

    Q_HVAC = BTU_to_kJ(read.find_num(housing, housing.index[2], name)) # kJ

    return(Q_HVAC)


# Calculates the total temperature inside housing
# Inputs:
    # data: The estimated temperature data
    # h: See constant on line 10
    # step: Hours between temperatures
    # temp_set: Set interior temperature
def total_thermal(data, h, step, temp_set):

    # Final equation: (Q_convection + Q_bat - Q_HVAC) / (m*c_p) + T_start = T_final
    # Update such that T_final becomes T_start after first iteration
    # T_start should be the ambient temperature at the starting time for first

    components = read.create_dataframes(read.define_sheet_data('Battery_System_Components'), "Select a Configuration")
    cell = components[0]
    housing = components[3]

    T_final = []
    T_start = data[0]

    Q_HVAC = Q_hvac(housing, 'BTU Rating (cooling)')
    Q_CON = Q_convection(data, housing, temp_set, h, step)[0]
    Q_BAT = Q_bat(cell, temp_set) # Still working to convert heat to kJ
    Q_BAT = 36000 # Remove when function works

    m = Q_convection(data, housing, temp_set, h, step)[1]

    for i in range(0,len(Q_CON)):
        print(T_final, i)
        T_final.append(T_start)
        if T_start > temp_set:
            T_start = ((Q_CON[i] +Q_BAT - Q_HVAC) / (m * c_p)) + T_start
            # K = ((kJ + kJ - kJ) / (kg * kJ/kg.K)) + K
        elif T_start < 70:
            T_start = ((Q_CON[i] +Q_BAT + Q_HVAC) / (m * c_p)) + T_start
        else:
            T_start = ((Q_CON[i] +Q_BAT) / (m * c_p)) + T_start


    return(T_final)


###############################################################################
# Rebecca - Thermal optimization
#def thermalOptimization(data, h, step, temp_set):
components = read.create_dataframes(read.define_sheet_data('Battery_System_Components'), "Select a Configuration")
cell = components[0]
housing = components[3]

#T_final = []
end = 24*7 # starting with one week
temp_data = monthly_temp(0, 0, end)
T_start = temp_data[0]
step = 1


Q_HVAC = Q_hvac(housing, 'BTU Rating (cooling)') # does this unit match the others?
Q_CON = Q_convection(temp_data, housing, temp_set, h, step)[0]
#Q_BAT = Q_bat(cell, temp_set) # Still working to convert heat to kJ
Q_BAT = 36000 # Remove when function works

m = Q_convection(temp_data, housing, temp_set, h, step)[1]

from scipy.optimize import minimize, Bounds, LinearConstraint

def objfxn(x):
    return np.sum(np.square(x[end*2:end*3])) # we're only minimizing HVAC usage

lb = Q_CON.copy() # this is an equality constraint
ub = Q_CON.copy() # this is an equality constraint
lb.extend([Q_BAT]*end) # repeats the one value of Q_BAT the same number of times, this could be different if we have time dependent Q_Bat data
ub.extend([Q_BAT]*end) # same as lb because it's an equality constraint
x0start = lb.copy()
lb.extend([-Q_HVAC*10]*end) # maximum heat removal
ub.extend([Q_HVAC*10]*end) # maximum heat that we can generate. I don't know if this is right. If no heater, replace Q_HVAC with 0
lb.extend([-20+273]*(end)) # I just made up a minimum temperature
ub.extend([40+273]*(end)) # I just made up a maximum temperature
lb.extend([0]) # there's one extra temperature term, these are Kelvin, can't be below absolute zero
ub.extend([np.inf])
x0start.extend([2]*end)
x0start.extend([T_start]*(end+1))
tempArray = np.zeros((end,end+1))
for n in range(end):
    tempArray[n,n] = m*c_p
    tempArray[n, n+1] = -1*m*c_p
lcArray = np.hstack((np.identity(end), np.identity(end), np.identity(end), tempArray))
bounds = Bounds(lb,ub)
lc = LinearConstraint(lcArray, np.zeros(end), np.zeros(end))
res = minimize(objfxn, np.array(x0start), method = 'trust-constr', constraints = lc, bounds = bounds)
print(res.x) #items 0:end are Q_con, end:2*end are Q_Bat, 2*end:3*end are Q_HVAC (what we're interested in), and 3*end:-2 are the temperatures we care about

################################### Main ######################################
if __name__ == '__main__':

    components = read.create_dataframes(read.define_sheet_data('Battery_System_Components'), "Select a Configuration")
    cell = components[0]

    # Variable variables
    region = 0 # Currently 0 or 1
    start = 0 # 0 representing Jan 1st
    end = 8760 # 8760 representing Dec 31st
    step = 1 # Number of hours between recording data points

    # Determines temperature data from region over time period
    temp_data = monthly_temp(region, start, end)

    # Determines thermal data
    thermal_data = total_thermal(temp_data, h, step, f_to_k(temp_set))



    # Use to check output thermal data in degrees F
    x = []
    for i in thermal_data:

        x.append(k_to_f(i))





    # Use first plot format due to automatic updates to title
    time = np.arange(start,start+len(thermal_data),step)
    plt.plot(time, thermal_data)
    plt.xlabel("Time (Hour)")
    plt.ylabel("Housing Temp (K)")
    plt.title(f"Housing temp per {step} hour(s) over {np.floor((end-start)/730)} months")
    plt.show()

'''
    # Prints graph for temperature change
    time = np.arange(start,start+len(data),1)
    plt.plot(time, data)
    plt.xlabel("Time (Hour)")
    plt.ylabel("Temperature (K)")
    plt.title("Temperature per hour over one year")
    plt.show()
'''
