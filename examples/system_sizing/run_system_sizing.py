# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
"""
BLIS - Balancing Load of Intermittent Solar:
A characteristic-based transient power plant model

Copyright (C) 2019. University of Virginia Licensing & Ventures Group (UVA LVG). All Rights Reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
import pandas as pd
import time
import numpy as np
from joblib import Parallel, delayed, parallel_backend
from blis import Solar, Fuel, Battery, PowerPlant, defaultInputs, HRES
import os


# =====================
# Function to enable parameter sweep
# =====================
def parameterSweep(dataFile, inputs, inputs2, index):
    # Record time to solve
    t0 = time.time()

    # Load_Data - Expected Columns (units): DatetimeUTC (UTC format), t (min), dt (min), demand (MW), solar (MW)
    data = pd.read_csv(dataFile)
    data.loc[:, 'solar'] = data.loc[:, 'solar'] * inputs2.solarCapacity / 32.3

    # Solar Plant - All inputs are optional (default values shown below)
    solar = Solar(plantType='PV', capacity=inputs2.solarCapacity, cost_install=2004., cost_OM_fix=22.02)

    # Battery Storage - All inputs are optional (default values shown below)
    batt = Battery(capacity=inputs2.battSize, rateMax=inputs2.battSize, roundTripEff=90.0, cost_install=2067.,
                   cost_OM_fix=35.6, initCharge=100.0)

    # Fuel - All inputs are optional (default values shown below)
    fuel = Fuel(fuelType='NATGAS', cost=23.27, emissions=0.18)

    # Create power plant
    # 1 - create pandas series of power plant characteristics
    plant_inputs = defaultInputs(plantType='CCGT')  # Start with CCGT default inputs and then adjust to specific case
    plant_inputs.plantType = inputs.sheetname
    plant_inputs.Eff_A = inputs.Eff_A
    plant_inputs.Eff_B = inputs.Eff_B
    plant_inputs.Eff_C = inputs.Eff_C
    plant_inputs.maxEfficiency = inputs.maxEfficiency
    plant_inputs.rampRate = inputs.rampRate
    plant_inputs.minRange = inputs.minRange
    plant_inputs.cost_install = inputs.cost_install
    plant_inputs.cost_OM_fix = inputs.cost_OM_fix
    plant_inputs.cost_OM_var = inputs.cost_OM_var
    plant_inputs.co2CaptureEff = inputs.co2CaptureEff
    plant_inputs.capacity = inputs2.plantSize  # MW

    # 2 - create power plant
    plant = PowerPlant(plant_inputs)

    # Create HRES (controller is built-in), data and plant are only required inputs
    # all other components will revert to default if not specified
    hres = HRES(data, plant, solar=solar, batt=batt, fuel=fuel, i=0.02, n=20)

    # Run Simulation
    results = hres.run()

    # Display Elapsed Time
    t1 = time.time()
    print("Time Elapsed: " + str(round(t1 - t0, 2)) + " s")

    # Save simulation results
    if index == 0:
        casename = inputs.sheetname + '_PV' + str(inputs2.solarCapacity) + '_Batt' + str(inputs2.battSize)
        hres.save(casename=casename)

    # Combine inputs and results into output and then return
    output = pd.concat([inputs, inputs2, results], axis=0)
    return output


# =============================================================================#
# Create MonteCarlo Inputs
# Note: iterations must be an integer
# =============================================================================#
def designInputs(filename, sheetname):
    # Read Excel with inputs
    df_xls = pd.read_excel(filename, sheet_name=sheetname, index_col=0)

    # Create series to hold inputs
    parameters1 = df_xls.index.values
    parameters2 = np.append('sheetname', parameters1)
    s = pd.Series(data=0.0, index=parameters2)

    # Create Inputs
    for param in parameters1:
        s.loc[param] = df_xls.loc[param]["Average"]

    s.loc['sheetname'] = sheetname
    return s


# =====================
# Main Program
# =====================
if __name__ == '__main__':

    # ==============
    # User Inputs
    # ==============
    studyName = "results_system_sizing"

    # Data files (Demand and solar data)
    # dataFile = "data063.csv" # Entire Year (used in article)
    # dataFile = "data063_July.csv" # Single Month
    dataFile = "data063_Oct30th.csv"  # Single Day

    # Design Sweep
    solarCapacities = np.linspace(30, 300, 10)
    battSizes = np.linspace(0, 360, 13)  # Battery Sizes to investigate [1:1, MW:MWh]
    plantSizes = np.linspace(40, 52, 7)

    # Monte Carlo Case Inputs (uses excel, each sheet is a separate study)
    xls_filename = "inputs_system_sizing.xlsx"
    sheetnames = ["sCO2", "OCGT", "CCGT", "sCO2_CCS", "CCGT_CCS"]

    # Number of cores to use
    ncpus = -1  # int(os.getenv('NUM_PROCS'))

    # ==============
    # Run Simulations
    # ==============
    all_outputs = []

    # ------
    # Design Sweep Inputs
    # ------
    count = 0
    cols = ['plantSize', 'solarCapacity', 'battSize']
    inputs2 = pd.DataFrame(columns=cols)
    # Iterate data files and corresponding solar capacity
    for plantSize in plantSizes:
        for solarCapacity in solarCapacities:
            for battSize in battSizes:
                s = pd.Series([plantSize, solarCapacity, battSize], index=cols)
                s.name = count
                count = count + 1
                inputs2 = inputs2.append(s)
    n_cases = inputs2.shape[0]

    # ------
    # Iterate each Monte Carlo case
    # ------
    for sheetname in sheetnames:
        inputs = designInputs(xls_filename, sheetname)

        # Perform Simulations (Run all plant variations in parallel)
        with parallel_backend('multiprocessing', n_jobs=ncpus):
            output = Parallel(n_jobs=ncpus, verbose=5)(
                delayed(parameterSweep)(dataFile, inputs, inputs2.loc[index], index) for index in range(n_cases))

        # Add output to all_outputs
        all_outputs = all_outputs + output

        # Back-up results for current plantType
        df = pd.DataFrame(all_outputs)
        df.to_csv(studyName + '_pt' + str(count) + '.csv')
        count = count + 1

    # Combine outputs into single dataframe and save
    df = pd.DataFrame(all_outputs)
    df.to_csv(studyName + '.csv')
