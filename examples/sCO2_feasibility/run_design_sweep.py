#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
"""
BLIS - Balancing Load of Intermittent Solar:
A characteristic-based transient power plant model

Copyright (C) 2018. University of Virginia Licensing & Ventures Group (UVA LVG). All Rights Reserved.

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
from blis import Solar, Fuel, Battery, PowerPlant, defaultInputs, HRES

#=====================
# Function to enable parameter sweep
#=====================
def parameterSweep(dataFile, plantSize, solarCapacity, battSize, inputs, index):
    # Record time to solve
    t0 = time.time()
    
    # Load_Data - Expected Columns (units): DatetimeUTC (UTC format), t (min), dt (min), demand (MW), solar (MW)
    data         = pd.read_csv(dataFile)
    df.loc[:,'solar'] = df.loc[:,'solar']*solarCapacity/32.3
    
    # Solar Plant - All inputs are optional (default values shown below)
    solar        = Solar(plantType = 'PV', capacity = solarCapacity, cost_install = 2004., cost_OM_fix = 22.02) 
    
    # Battery Storage - All inputs are optional (default values shown below)
    batt         = Battery(capacity = battSize, rateMax= battSize, roundTripEff = 90.0, cost_install = 2067., cost_OM_fix = 35.6)
    
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
    plant_inputs.minRange       = inputs.minRange
    plant_inputs.cost_install   = inputs.cost_install
    plant_inputs.cost_OM_fix    = inputs.cost_OM_fix
    plant_inputs.cost_OM_var    = inputs.cost_OM_var
    plant_inputs.co2CaptureEff  = inputs.co2CaptureEff
    plant_inputs.capacity       = plantSize  # MW
    
        # 2 - create power plant
    plant        = PowerPlant(plant_inputs)
    
    # Create HRES (controller is built-in), data and plant are only required inputs, all other components will revert to default if not specified
    hres         = HRES(data,plant,solar=solar,batt=batt,fuel=fuel,i=0.02,n=20)
    
    # Run Simulation
    results = hres.run()
        
    # Display Elapsed Time
    t1 = time.time()
    print "Time Elapsed: " + str(round(t1-t0,2)) + " s"

    # Save simulation results
    if index==0:
        casename = inputs.sheetname + '_PV' + str(solarCapacity) + '_Batt' + str(battSize)
        hres.save(casename=casename)

    # Combine inputs and results into output and then return
    s_plantCapacity = pd.Series([plantSize], index=['plantCapacity_MW'])
    s_solarCapacity = pd.Series([solarCapacity],index=['solarCapacity_MW'])
    s_battSize = pd.Series([battSize], index=['battSize_MW'])
    output = pd.concat([inputs,s_plantCapacity,s_solarCapacity,s_battSize,results],axis=0)
    return output

#=============================================================================#
# Create MonteCarlo Inputs
# Note: iterations must be an integer
#=============================================================================#
def designInputs(filename,sheetname):
    # Read Excel with inputs
    df_xls = pd.read_excel(filename, sheet_name=sheetname, index_col = 0)
    
    # Create Dataframe to hold inputs
    rows = range(iterations)
    parameters1 = df_xls.index.values
    parameters2 = np.append('sheetname',parameters1)
    df = pd.DataFrame(data=0.0,index=rows,columns = parameters2)
    
    # Create Inputs
    for param in parameters1:
        df.loc[:][param] = df_xls.loc[param]["Average"]

    df.loc[:,'sheetname'] = sheetname
    return df

#=====================
# Main Program
#=====================
if __name__ == '__main__':
    
    #==============
    # User Inputs
    #==============
    studyName = "Results_DesignSweep"
    
    # Data files (Demand and solar data)
    # dataFile = ["data063.csv"] # Entire Year (used in article)
    # dataFile = [ "data063_July.csv"]  # Single Month
    dataFile = ["data063_Oct30th.csv"]  # Single Day

    # Design Sweep
    solarCapacities = np.linspace(30,300,10)
    battSizes = np.linspace(0,270,10) # Battery Sizes to investigate [1:1, MW:MWh]
    plantSizes = np.linspace(10,55,10)

    # Monte Carlo Case Inputs (uses excel, each sheet is a separate study)
    xls_filename = "inputs_montecarlo1.xlsx"
    sheetnames   = ["sCO2","OCGT","CCGT","sCO2_CCS","CCGT_CCS"]
    
    # Specify number of iterations per case
    iterations = 1 # To test
    # iterations = 100 # Used in article
    
    # Number of cores to use
    num_cores = multiprocessing.cpu_count()-1 # Consider saving one for other processes
    
    
    
    
     ##########
    # GET TO RUN IN PARALLEL!!!!!
    #####
    count = 0
    cols = ['plantSize','solarCapacity','battSize']
    inputs2 = pd.DataFrame(columns=cols)
    # Iterate data files and corresponding solar capacity
    for plantSize in plantSizes:
        for solarCapacity in solarCapacities:
            for battSize in battSizes:
                s = pd.Series([plantSize,solarCapacity,battSize], index=cols)
                s.name = count
                inputs2 = inputs2.append(s)
    
    
    ##########
    # GET TO RUN IN PARALLEL!!!!!
    #####
    
    #==============
    # Run Simulations
    #==============
    all_outputs = []
    count = 0
    
    # Iterate each Monte Carlo case
    for sheetname in sheetnames:
    
        inputs = designInputs(xls_filename,sheetname)

        # Iterate data files and corresponding solar capacity
        for plantSize in plantSizes:

            # Iterate data files and corresponding solar capacity
            for solarCapacity in solarCapacities:

                # Iterate data files and corresponding solar capacity
                for battSize in battSizes:

                    # Perform Simulations (Run all plant variations in parallel)
                    with parallel_backend('multiprocessing', n_jobs=num_cores):
                        output = Parallel(verbose=10)(delayed(parameterSweep)(dataFile, plantSize, solarCapacity, battSize, inputs.loc[index],index) for index in range(iterations))

                    # Add output to all_outputs
                    all_outputs = all_outputs + output

        # Back-up results for current plantType
        df = pd.DataFrame(all_outputs)
        df.to_csv(studyName + '_pt' + str(count)+'.csv')
        count = count + 1
            
    # Combine outputs into single dataframe and save
    df = pd.DataFrame(all_outputs)
    df.to_csv(studyName + '.csv')