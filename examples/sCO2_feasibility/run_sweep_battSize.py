#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
"""
BLIS - Balancing Load of Intermittent Solar:
A characteristic-based transient power plant model

Copyright (C) 2019. University of Virginia Licensing & Ventures Group (UVA LVG). All Rights Reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
import pandas as pd
import time
import numpy as np
import multiprocessing
from joblib import Parallel, delayed, parallel_backend
from blis import Solar, Fuel, Battery, PowerPlant, defaultInputs, HRES, baselineInputs

#=====================
# Function to enable parameter sweep
#=====================
def parameterSweep(dataFile, solarCapacity, inputs, inputs2, index):
    # Record time to solve
    t0 = time.time()
    
    # Load_Data - Expected Columns (units): DatetimeUTC (UTC format), t (min), dt (min), demand (MW), solar (MW)
    data         = pd.read_csv(dataFile) 
    
    # Solar Plant - All inputs are optional (default values shown below)
    solar        = Solar(plantType = 'PV', capacity = solarCapacity, cost_install = 2004., cost_OM_fix = 22.02) 
    
    # Battery Storage - All inputs are optional (default values shown below)
    batt         = Battery(capacity = inputs2.battSize, rateMax= inputs2.battSize, roundTripEff = 90.0, cost_install = 2067., cost_OM_fix = 35.6,initCharge = 100.0)
    
    # Fuel - All inputs are optional (default values shown below)
    fuel         = Fuel(fuelType='NATGAS',cost = 23.27,emissions = 0.18)
    
    # Create power plant
        # 1 - create pandas series of power plant characteristics
    plant_inputs                = defaultInputs(plantType = 'CCGT') # Start with CCGT default inputs and then adjust to specific case
    plant_inputs.plantType      = inputs.sheetname
    plant_inputs.Eff_A          = inputs.Eff_A
    plant_inputs.Eff_B          = inputs.Eff_B
    plant_inputs.Eff_C          = inputs.Eff_C
    plant_inputs.maxEfficiency  = inputs.maxEfficiency
    plant_inputs.rampRate       = inputs.rampRate
    plant_inputs.minRange       = inputs2.minRange
    plant_inputs.cost_install   = inputs.cost_install
    plant_inputs.cost_OM_fix    = inputs.cost_OM_fix
    plant_inputs.cost_OM_var    = inputs.cost_OM_var
    plant_inputs.co2CaptureEff  = inputs.co2CaptureEff
    
        # 2 - create power plant
    plant        = PowerPlant(plant_inputs)
    
    # Create HRES (controller is built-in), data and plant are only required inputs, all other components will revert to default if not specified
    hres         = HRES(data,plant,solar=solar,batt=batt,fuel=fuel,i=0.02,n=20)
    
    # Run Simulation
    results = hres.run()
        
    # Display Elapsed Time
    t1 = time.time()
    print "Time Elapsed: " + str(round(t1-t0,2)) + " s"

    # Combine inputs and results into output and then return
    inputs = inputs.drop('minRange')
    s_solarCapacity = pd.Series([solarCapacity],index=['solarCapacity_MW'])
    output = pd.concat([inputs,inputs2,s_solarCapacity,results],axis=0)
    return output

#=====================
# Main Program
#=====================
if __name__ == '__main__':
    
    #==============
    # User Inputs
    #==============
    studyName = "results_sweep_battSize"
    
    # Data files (Demand and solar data)
    # dataFile = "data063.csv" # Entire Year (used in article)
    dataFile = "data063_July.csv"  # Single Day
    # dataFile = "data063_Oct30th.csv" # Single Day
    solarCapacity = 32.3  # (MW) Needs to be the same length as dataFiles

    # Specify number of iterations per case
    # iterations = 10  # To test
    iterations = 26 # Used in article

    # Battery Sizes to investigate [1:1, MW:MWh]
    minRanges = [30.0, 40.0, 50.0]
    battSizes = np.linspace(0,100,iterations)

    # Monte Carlo Case Inputs (uses excel, each sheet is a separate study)
    xls_filename = "inputs_montecarlo.xlsx"
    sheetname = "sCO2"

    # Number of cores to use
    num_cores = multiprocessing.cpu_count()-1 # Consider saving one for other processes
    
    #==============
    # Run Simulations
    #==============

    # ------
    # Baseline Configuration Inputs
    # ------
    inputs = baselineInputs(xls_filename, sheetname)

    # ------
    # Design Sweep Inputs
    # ------
    count = 0
    cols = ['minRange', 'battSize']
    inputs2 = pd.DataFrame(columns=cols)
    # Iterate data files and corresponding solar capacity
    for minRange in minRanges:
        for battSize in battSizes:
                s = pd.Series([minRange, battSize], index=cols)
                s.name = count
                count = count + 1
                inputs2 = inputs2.append(s)
    n_cases = inputs2.shape[0]

    # ------
    # Run Sweeps
    # ------
    # Perform Simulations (Run all plant variations in parallel)
    with parallel_backend('multiprocessing', n_jobs=num_cores):
        output = Parallel(verbose=10)(delayed(parameterSweep)(dataFile, solarCapacity, inputs, inputs2.loc[index],index) for index in range(n_cases))

    # Combine outputs into single dataframe and save
    # df = pd.concat(output,axis=1)
    df = pd.DataFrame(output)
    # df = df.transpose()
    df.to_csv(studyName + '.csv')