import ReadSheet as read
import matplotlib.pyplot as plt
import numpy as np
import pybamm

################################ Constants ####################################
rho = 1.225 # kg/m^3 ; Density of air
c_v = 0.718 # kJ/kg.K ; Specific heat with constant volume at 300K
temp_set = 75 # degrees F ; Baseline temp
h = 10 # W/m^2.K ; Convection heat transfer coefficient
c_p = .7585 # kJ/kg.K ; Specific heat at constant pressure (atmospheric)
          # Average of steel and air; Steel = 0.51, Air = 1.007
###############################################################################


################################ Functions ####################################
# Converts Fahrenheit to Kelvin
def f_to_k(f):

    k = ((f - 32.0) / 1.8) + 273.15

    return(k)

# Converts Kelvin to Fahrenheit
def k_to_f(k):

    f = 1.8 * (k - 273.15) + 32.0

    return(f)


# Converts British Thermal Units (BTU) to kiloJoules (kJ)
def BTU_to_kJ(BTU):

    kJ = BTU * 1055.056 / 1000

    return(kJ)


# Calculates the change in daily temperature per hour
def max_min_temp_diff(clim, month):
    #print(clim.drop(['month']))
    #print(month)
    #print(clim.index)
   # print(clim, str(month), 'MLY-TMAX-NORMAL')
   # print(clim.loc[month, ['MLY-TMAX-NORMAL']])
    max_temp = f_to_k(read.find_num(clim, month,['MLY-TMAX-NORMAL']))
    min_temp = f_to_k(read.find_num(clim, month,['MLY-TMIN-NORMAL']))
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

    # Read Climate data
    climate = read.create_dataframes(read.define_sheet_data('Climate Data'), 'month')
    climate_1 = climate[region]
    climate_2 = climate_1.drop(['month'])
    #print(climate_2)
    #climate = climate.drop(['month'])

    # Initializing lists
    avg = []
    minim = []
    maxim = []
    mnly = []
    #print(climate[region].index)
    # Determines changes between monthly max and mins
    for i in climate_2.index:
        #print(i+1)
        avg.append(max_min_temp_diff(climate_2, i))
        maxim.append(monthly_temp_diff(climate_2, i, 'MLY-TMAX-NORMAL'))
        minim.append(monthly_temp_diff(climate_2, i, 'MLY-TMIN-NORMAL'))

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

            day_min = f_to_k(read.find_num(climate_2, str(month), 'MLY-TMIN-NORMAL')) + mon_min_chg
            day_max = f_to_k(read.find_num(climate_2, str(month), 'MLY-TMAX-NORMAL')) + mon_max_chg
            for i in daily_temps(day_min, day_max, avg, months-1):
                mnly.append(i)

        # Looks for the end of the year and resets the date
        if j % 8760 == 0 and j != 0:
            months = 1

    return(mnly)


# Determines the heat generated by convection
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
    width = read.find_num(housing, 'Shipping Container', 'Width (mm)') / 1000 # m
    height = read.find_num(housing, 'Shipping Container', 'Height (mm)') / 1000 # m
    depth = read.find_num(housing, 'Shipping Container', 'Depth (mm)') / 1000 # m

    s_area = 2 * depth * height + 2 * height * width + 2 * depth * width
    s_used = s_area - depth * width

    m = (read.find_num(housing, 'Shipping Container', 'Weight (kg)') / s_area) * s_used

    for i in range(0,len(mnly),step):
        Q_ambient.append(h * s_area * (-mnly[i] + temp_set))


    return(Q_ambient, m)

# Determines heat contribution to storage unit based off battery conditions
# Pull thermal data from pybamm (set in terms of kJ)
# Inputs:
    # cell: Cell dataframe
    # temp_set: Set interior temperature
def Q_bat(temp_set, duration):
    components = read.create_dataframes(read.define_sheet_data('Battery_System_Components'), "Select a Configuration")
    cell = components[0]
    module = components[1]
    rack = components[2]
    housing = components[3]

    options = {"thermal": 'x-full'}
    model = pybamm.lithium_ion.SPMe(options=options)
    parameter_values = model.default_parameter_values

    if duration == 2:
        experiment = pybamm.Experiment(
            [
                ('Discharge at C/2 for 2 hours or until 3.3 V',
                 'Rest for 1 hours',
                 'Charge at C/2 until 4.1 V',
                 #'Hold at 4.1V until 50 mA',
                 'Rest for 1 hour')
            ] * 1
        )

    if duration == 4:
        experiment = pybamm.Experiment(
            [
                ('Discharge at C/4 for 4 hours or until 3.3 V',
                 'Rest for 1 hours',
                 'Charge at C/4 until 4.1 V',
                 #'Hold at 4.1V until 50 mA',
                 'Rest for 1 hour')
            ] * 1
        )
    if duration == 8:
        experiment = pybamm.Experiment(
            [
                ('Discharge at C/8 for 8 hours or until 3.3 V',
                 'Rest for 1 hours',
                 'Charge at C/8 until 4.1 V',
                         #'Hold at 4.1V until 50 mA',
                 'Rest for 1 hour')
            ] * 1
        )

    parameter_values['Ambient temperature [K]'] = temp_set

    parameter_values['Negative current collector thickness [m]'] = cell.loc['Negative Current Collector']['Thickness [m]']
    parameter_values['Positive current collector thickness [m]'] = cell.loc['Positive Current Collector']['Thickness [m]']
    parameter_values['Negative electrode active material volume fraction'] = read.find_num(cell, 'Anode Active Material', 'Material Ratio (% by mass)')
    parameter_values['Negative electrode porosity'] = read.find_num(cell, 'Anode Active Material', 'Porosity (%)')
    parameter_values['Negative electrode thickness [m]'] = read.find_num(cell, 'Anode Active Material', 'Thickness [m]')
    #parameter_values['Positive Electrode Chemistry (NCA/NMC with ratio, LFP)'] # No defaut value in pybamm
    parameter_values['Positive electrode active material volume fraction'] = read.find_num(cell, 'Cathode Active Material', 'Material Ratio (% by mass)')
    parameter_values['Positive electrode porosity'] = read.find_num(cell, 'Cathode Active Material', 'Material Ratio (% by mass)')
    parameter_values['Positive electrode thickness [m]'] = read.find_num(cell, 'Cathode Active Material', 'Thickness [m]')
    parameter_values['Separator porosity'] = read.find_num(cell, 'Separator', 'Porosity (%)')
    parameter_values['Separator thickness [m]'] = read.find_num(cell, 'Separator', 'Thickness [m]')

   #parameter_values['Electrode height [m]'] = read.find_num(cell, 'Anode Active Material', 'Length [mm]')/1000
    parameter_values['Electrode height [m]'] = read.find_num(cell, 'Anode Active Material', 'Length [mm]')/1000
    parameter_values['Electrode width [m]'] = read.find_num(cell, 'Anode Active Material', 'Width [mm]')/1000

    #parameters_values['']
    #print(parameter_values['Positive electrode specific capacity'])
    sim = pybamm.Simulation(model, parameter_values=parameter_values, experiment = experiment)
    sim.solve()

    bam_data = sim.solution['Volume-averaged total heating [W.m-3]'].entries
    #plt.plot(sim.solution['Time [h]'].entries, bam_data)
    #print(bam_data)

    q_out = np.zeros(24)
    q_out[18] = np.sum(bam_data[0:60])
    q_out[19] = np.sum(bam_data[60:120])

    if duration == 2:
        q_out[12] = np.sum(bam_data[180:240])
        q_out[13] = np.sum(bam_data[240:300])

    if duration == 4:
        q_out[20] = np.sum(bam_data[120:180])
        q_out[21] = np.sum(bam_data[180:240])
        q_out[11] = np.sum(bam_data[300:360])
        q_out[12] = np.sum(bam_data[360:420])
        q_out[13] = np.sum(bam_data[420:480])
        q_out[14] = np.sum(bam_data[480:600])
    if duration == 8:
        q_out[20] = np.sum(bam_data[120:180])
        q_out[21] = np.sum(bam_data[180:240])
        q_out[22] = np.sum(bam_data[240:300])
        q_out[23] = np.sum(bam_data[300:360])
        q_out[0] = np.sum(bam_data[360:420])
        q_out[1] = np.sum(bam_data[420:480])

        q_out[9] = np.sum(bam_data[540:600])
        q_out[10] = np.sum(bam_data[600:660])
        q_out[11] = np.sum(bam_data[660:720])
        q_out[12] = np.sum(bam_data[720:780])
        q_out[13] = np.sum(bam_data[660:720])
        q_out[14] = np.sum(bam_data[720:780])
        q_out[15] = np.sum(bam_data[780:840])
        q_out[16] = np.sum(bam_data[840:800])

    cells = read.find_num(module, 'Total Cells', 'Number per module')
    modules = read.find_num(rack, 'Modules', 'Number per rack')
    racks = read.find_num(housing, 'Racks', 'Number')

    bat_thick = read.find_num(cell, 'Anode Active Material', 'Thickness [m]') * 2 + .000025 * 35
    bat_width = read.find_num(cell, 'Anode Active Material', 'Width [mm]')/1000
    bat_len = read.find_num(cell, 'Anode Active Material', 'Length [mm]')/1000

    bat_volume = bat_thick * bat_width * bat_len #* cells * modules * racks
    q_out = q_out*60*60 #watts to J

    # kJ = ((W/m^3 / unitless) * m * m * m) / (J/kJ)
    #Q_BAT = (float(sum(heat_range))/float(len(heat_range))) * bat_thick * bat_width * (10**(-3)) * bat_len * (10**(-3)) * ((cells * modules * racks)**2) / 1000
    Q_BAT = q_out * bat_volume/1000
    return(Q_BAT)


def Q_hvac(housing, name):

    Q_HVAC = BTU_to_kJ(read.find_num(housing, 'HVAC', name)) # kJ

    return(Q_HVAC)


    # Calculates the total temperature inside housing
    # Inputs:
        # data: The estimated temperature data
        # h: See constant on line 10
        # step: Hours between temperatures
        # temp_set: Set interior temperature
def total_thermal(temp_data, h, step, temp_set, num_HVAC, T_prev):

    # Final equation: (Q_convection + Q_bat - Q_HVAC) / (m*c_p) + T_start = T_final
    # Update such that T_final becomes T_start after first iteration
    # T_start should be the ambient temperature at the starting time for first

    components = read.create_dataframes(read.define_sheet_data('Battery_System_Components'), "Select a Configuration")
    housing = components[3]


    T_final = []
    T_new = temp_data[0]
    T_start = temp_data[0]

    Q_HVAC = Q_hvac(housing, 'BTU Rating (cooling)')
    Q_CON = Q_convection(temp_data, housing, temp_set, h, step)[0]
    Q_BAT = Q_bat(temp_set) # Still working to convert heat to kJ

    m = Q_convection(temp_data, housing, temp_set, h, step)[1]


    for i in range(0,len(Q_CON)):
        #if 0 <= T_start <= 335:
        T_final.append(T_start)
        if T_start > temp_set:
            T_start = ((Q_CON[i] + Q_BAT - Q_HVAC * num_HVAC) / (m * c_p)) + T_new
            T_new = T_start
            # K = ((kJ + kJ - kJ) / (kg * kJ/kg.K)) + K
            '''
        elif T_start < f_to_k(10):
            T_start = ((Q_CON[i] + Q_BAT + Q_HVAC * num_HVAC) / (m * c_p)) + T_new
            T_new = T_start
            '''
        else:
            T_start = ((Q_CON[i] + Q_BAT - Q_HVAC * num_HVAC * .5) / (m * c_p)) + T_new
            T_new = T_start

        '''
        else:
            T_final.append(T_start)
            T_start = ((Q_CON[i] + Q_BAT - Q_HVAC * num_HVAC) / (m * c_p)) + T_new
            T_new = T_start
            c = 1
         '''


    if f_to_k((k_to_f(temp_set)-10)) <= sum(T_final)/len(T_final) and sum(T_final)/len(T_final) <= f_to_k((k_to_f(temp_set)+10)):
        print(f"HVAC is sufficiently good with {num_HVAC} HVAC unit(s)!")
        print(f"Average Internal Temperature: {sum(T_final)/len(T_final)} K")
    elif sum(T_final)/len(T_final) > T_prev:
        print(f"HVAC is sufficiently good with {num_HVAC} HVAC unit(s)!")
        print(f"Average Internal Temperature: < {T_prev} K")
    else:
        print(f"HVAC system is not sufficiently good with {num_HVAC} HVAC unit(s)!")
        num_HVAC += 1
        print(f"Average Internal Temperature: {sum(T_final)/len(T_final)} K")
        T_prev = sum(T_final)/len(T_final)
        T_final = total_thermal(temp_data, h, step, temp_set, num_HVAC, T_prev)



    return(T_final)

###############################################################################
# Rebecca - Thermal optimization
def thermalOptimization(data, h, step, temp_set, duration):
    components = read.create_dataframes(read.define_sheet_data('Battery_System_Components'), "Select a Configuration")
    cell = components[0]
    housing = components[3]

    # starting with one week
    T_start = temp_data[1]

    Q_HVAC = Q_hvac(housing, 'BTU Rating (cooling)') # does this unit match the others?
    Q_CON = Q_convection(temp_data, housing, temp_set, h, step)[0]
    Q_BAT = Q_bat(temp_set, 4)
    m = Q_convection(temp_data, housing, temp_set, h, step)[1]

    from scipy.optimize import minimize, Bounds, LinearConstraint

    def objfxn(x):
        return np.sum(np.square(x[end*2:end*3])) # we're only minimizing HVAC usage
    #print(Q_HVAC, np.average(Q_CON))
    lb = Q_CON.copy() # this is an equality constraint
    ub = Q_CON.copy() # this is an equality constraint
    lb.extend(np.tile(Q_BAT, int(len(temp_data)/24)))
    ub.extend(np.tile(Q_BAT, int(len(temp_data)/24)))
    x0start = lb.copy()
    lb.extend([-Q_HVAC*30]*len(temp_data)) # maximum heat removal
    ub.extend([Q_HVAC*30]*len(temp_data)) # maximum heat that we can generate. I don't know if this is right. If no heater, replace Q_HVAC with 0
    lb.extend([287]*(len(temp_data))) # I just made up a minimum temperature, 10 lower than setpoint
    ub.extend([307]*(len(temp_data))) # I just made up a maximum temperature, 10 higher than setpoint 
    lb.extend([0]) # there's one extra temperature term, these are Kelvin, can't be below absolute zero
    ub.extend([np.inf])
    x0start.extend([2]*len(temp_data))
    x0start.extend([T_start]*(len(temp_data)+1))
    tempArray = np.zeros((len(temp_data),len(temp_data)+1))
    for n in range(len(temp_data)):
        tempArray[n,n] = m*c_p
        tempArray[n, n+1] = -1*m*c_p
    lcArray = np.hstack((np.identity(len(temp_data)), np.identity(len(temp_data)), np.identity(len(temp_data)), tempArray))
    bounds = Bounds(lb,ub)
    lc = LinearConstraint(lcArray, np.zeros(len(temp_data)), np.zeros(len(temp_data)))
    res = minimize(objfxn, np.array(x0start), method = 'trust-constr', constraints = lc, bounds = bounds)
    #print(res.x) #items 0:end are Q_con, end:2*end are Q_Bat, 2*end:3*end are Q_HVAC (what we're interested in), and 3*end:-2 are the temperatures we care about
    return (res)
     #keeps matching number of datapoints
################################### Main ######################################

if __name__ == '__main__':

    components = read.create_dataframes(read.define_sheet_data('Battery_System_Components'), "Select a Configuration")
    cell = components[0]
    module = components[1]
    rack = components[2]
    housing = components[3]


    # Variable variables
    region = 0 # Currently 0 or 1
    start = 0 # 0 representing Jan 1st
    end = 8760 # 8760 representing Dec 31st
    step = 1 # Number of hours between recording data points
    duration = 8 #2, 4, or 8 hours

    # Determines temperature data from region over time period
    temp_data = monthly_temp(region, 0, 8760)
    day_start = 0
    day_end = 3
    temp_data = temp_data[day_start*24:day_end*24] #needs to be a multiple of 24 # I was getting some funkiness with different start/end points
    print(len(temp_data))

    T_prev = 1000000000
    num_HVAC = read.find_num(housing, 'HVAC', 'Number')

    # Determines thermal data (The units are off atm so thing look weird)
    #thermal_data = total_thermal(temp_data, h, step, f_to_k(temp_set), num_HVAC, T_prev)


    '''
    # Use to check output thermal data in degrees F
    x = []
    for i in thermal_data:

        x.append(k_to_f(i))
    '''

    '''
    # Plot of the temperature per hour in the housing
    time = np.arange(start,start+len(temp_data),step)
    plt.plot(time, temp_data, linestyle = 'solid')
    '''

    #x = sum(thermal_data)/len(thermal_data)

    r = thermalOptimization(temp_data, h, step, temp_set, duration)
    print(len(r.x))
    q_conv = r.x[0:len(temp_data)]
    q_bat = r.x[len(temp_data):2*len(temp_data)]
    q_hvac = r.x[2*len(temp_data):3*len(temp_data)]
    temps = r.x[3*len(temp_data):4*len(temp_data)]


    # Use first plot format due to automatic updates to title
    plt.figure()
    time = np.arange(day_start*24,day_start*24+len(temp_data),step)
    #plt.plot(time, thermal_data, linestyle = 'dotted', color ='blue', label = 'Estimated Interior Temperatures')
    plt.plot(time, temps, linestyle = 'dotted', color ='blue', label = 'Estimated Interior Temperatures')
    #plt.plot(time,temp_data, color ='green', label = 'Ambient Temperature')
    plt.xlabel("Time (Hour)")
    plt.ylabel("Housing Temp (K)")
    plt.title(f"Housing temp per {step} hour(s) over {int(np.floor((end-start)/730))} month(s)")
   # plt.axhline(y=x, label = 'Average Interior Temperature')
    plt.axhline(y=f_to_k(temp_set), linestyle = 'dashed', color='black', label ='Set Interior Temperature')
    plt.legend()
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
