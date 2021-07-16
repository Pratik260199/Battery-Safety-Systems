# short pieces of code to do quick data processing and calculations as part of MOST DAYS technoeconomic analysis 

import pandas as pd 
import numpy as np 
import csv
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import math

def calculateLCOS(ratedPower, storageDuration, eta_RTE, eta_discharge, eta_charge, capX_energy, capX_power, OM, elecPrice):
    # this list of parameters was specified by ARPA-E in their DAYS FOA 
  
    dutyProfile = pd.read_csv('Inputs/daysDutyProfile.csv')
    discountRate = 0.1 # 10%
    systemLifetime = 10 # was 20 # years
    discountFactors = 1/((1+discountRate)**np.arange(21)) # annual discount factors based on specified rate
    # pull annual electricity delivered based on system power & storage duration
    elecDelivered = dutyProfile[:int(storageDuration)]
    elecDelivered = sum(elecDelivered.cycles*ratedPower) 
    
    fullCycleEquivalent = elecDelivered / (ratedPower * storageDuration)
    capX = capX_energy / eta_discharge + capX_power / storageDuration
    elecCost = ((1 / eta_RTE) - 1) * fullCycleEquivalent * elecPrice
    OM = OM *capX #here O&M is a percentage of capX
    totalCost = capX + sum((elecCost + OM) * discountFactors[1:])
    totalElec = sum(fullCycleEquivalent * discountFactors[1:])
    LCOS = totalCost / totalElec
    return LCOS