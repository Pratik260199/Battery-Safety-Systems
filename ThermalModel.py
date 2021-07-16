import ReadSheet as read

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
# Returns: list of heat data corresponding to each month
# Next steps: Determine linear model for daily temp change each month to include
# better understanding of daily usage
def Q_amb(clim, vol, rho, c_v):
    
    Q_ambient = []
    for i in clim.index:
    
        Q_ambient.append((f_to_k(read.find_num(clim, i, 'MLY-TMAX-NORMAL'))
                          - f_to_k(temp_set)) * vol * rho * c_v) # KJ
        # Units: ((K - K)) * m^3 * kg/m^3 * kJ/kg.K; = kJ
    
    return(Q_ambient)

# Determines heat contribution to storage unit based off battery conditions
def Q_bat():
    
    
    return

# Determines total heat of system
def Q_tot():
    
    return
###############################################################################

climate = read.create_dataframes(read.define_sheet_data('Climate Data'), 'month')
components = read.create_dataframes(read.define_sheet_data('Battery_System_Components'), "Select a Configuration")

cell = components[0]
module = components[1]
rack = components[2]
housing = components[3]

width = read.find_num(housing, housing.index[1], 'Width (mm)') / 1000 # m
height = read.find_num(housing, housing.index[1], 'Height (mm)') / 1000 # m
depth = read.find_num(housing, housing.index[1], 'Depth (mm)') / 1000 # m

vol = width * height * depth # m^3

Q_ambient = Q_amb(climate[0], vol, rho, c_v)
Q_hvac = BTU_to_kJ(read.find_num(housing, housing.index[2], 'BTU Rating (cooling)'))


