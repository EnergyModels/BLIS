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
from blis import Solar, Fuel, Battery, PowerPlant, defaultInputs, HRES, monteCarloInputs

#=====================
# Function to enable parameter sweep
#=====================
def parameterSweep(dataFile, solarCapacity, battSize, inputs, index):
    # Record time to solve
    t0 = time.time()
    
    # Load_Data - Expected Columns (units): DatetimeUTC (UTC format), t (min), dt (min), demand (MW), solar (MW)
    data         = pd.read_csv(dataFile) 
    
    # Solar Plant - All inputs are optional (default values shown below)
    solar        = Solar(plantType = 'PV', capacity = solarCapacity, cost_install = 2004., cost_OM_fix = 22.02) 
    
    # Battery Storage - All inputs are optional (default values shown below)
    batt         = Battery(capacity = battSize, rateMax= battSize, roundTripEff = 85.0, cost_install = 2067., cost_OM_fix = 35.6,initCharge = 100.0)
    
    # Fuel - All inputs are optional (default values shown below)
    fuel         = Fuel(fuelType='NATGAS',cost = 10.58,emissions = 0.18)
    
    # Create power plant
        # 1 - create pandas series of power plant characteristics
    plant_inputs                = defaultInputs(plantType = 'CCGT') # Start with CCGT default inputs and then adjust to specific case
    plant_inputs.capacity       = 51.3  # MW
    plant_inputs.plantType      = inputs.sheetname
    plant_inputs.Eff_A          = inputs.Eff_A
    plant_inputs.Eff_B          = inputs.Eff_B
    plant_inputs.Eff_C          = inputs.Eff_C
    plant_inputs.maxEfficiency  = inputs.maxEfficiency
    plant_inputs.rampRate       = inputs.rampRate
    plant_inputs.minRange       = inputs.minRange
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
    s_solarCapacity = pd.Series([solarCapacity],index=['solarCapacity_MW'])
    s_battSize = pd.Series([battSize], index=['battSize_MW'])
    output = pd.concat([inputs,s_solarCapacity,s_battSize,results],axis=0)
    return output

#=====================
# Main Program
#=====================
if __name__ == '__main__':
    
    #==============
    # User Inputs
    #==============
    studyName = "results_monte_carlo"
    
    # Data files (Demand and solar data)
    dataFiles = ["data001.csv","data063.csv"] # Entire Year (used in article)
    # dataFiles = ["data001_July.csv", "data063_July.csv"]  # Single Month (used in article)
    # dataFiles = ["data001_Oct30th.csv","data063_Oct30th.csv"] # Single Day
    solarCapacities = [0.635,32.635]  # (MW) Needs to be the same length as dataFiles

    # Battery Sizes to investigate [1:1, MW:MWh]
    battSizes = [0, 30.0]

    # Monte Carlo Case Inputs (uses excel, each sheet is a separate study)
    xls_filename = "inputs_montecarlo.xlsx"
    # sheetnames   = ["sCO2","OCGT","CCGT","sCO2_CCS","CCGT_CCS"]
    sheetnames = ["sCO2", "OCGT", "CCGT"]
    
    # Specify number of iterations per case
    # iterations = 10 # To test
    iterations = 100 # Used in article
    # Number of cores to use
    num_cores = multiprocessing.cpu_count()-1 # Consider saving one for other processes
    
    #==============
    # Run Simulations
    #==============
    all_outputs = []
    count = 0
    
    # Iterate each Monte Carlo case
    for sheetname in sheetnames:
    
        inputs = monteCarloInputs(xls_filename,sheetname,iterations)
        
        # Iterate data files and corresponding solar capacity
        for (dataFile,solarCapacity) in zip(dataFiles,solarCapacities):

            # Iterate data files and corresponding solar capacity
            for battSize in battSizes:

                # Perform Simulations (Run all plant variations in parallel)
                with parallel_backend('multiprocessing', n_jobs=num_cores):
                    output = Parallel(verbose=10)(delayed(parameterSweep)(dataFile, solarCapacity, battSize, inputs.loc[index],index) for index in range(iterations))

                # Add output to all_outputs
                all_outputs = all_outputs + output
                # Move output to dataframe and save (if iterations greater than 10)
                if iterations > 10:
                    df = pd.DataFrame(output)
                    df.to_csv(studyName + '_pt' + str(count)+'.csv')
                    count = count + 1
            
    # Combine outputs into single dataframe and save
    df = pd.DataFrame(all_outputs)
    df.to_csv(studyName + '.csv')
