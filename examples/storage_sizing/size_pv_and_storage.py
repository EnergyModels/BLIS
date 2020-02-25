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
from blis import Solar, Grid, Battery, SBGS, monteCarloInputs
import os


# =====================
# Function to enable parameter sweep
# =====================
def parameterSweep(inputs):
    # Record time to solve
    t0 = time.time()

    # Load_Data - Expected Columns (units): DatetimeUTC (UTC format), t (min), dt (min), demand (MW), solar (MW)
    data = pd.read_csv('data063.csv')

    # Scale data to match provided pvSize
    data.solar = data.solar * inputs.pvSize / 32.3

    # Solar Plant - All inputs are optional (default values shown below)
    solar = Solar(plantType='PV', capacity=inputs.pvSize, cost_install=2004., cost_OM_fix=22.02)

    # Battery Storage - All inputs are optional (default values shown below)
    batt = Battery(capacity=inputs.capacity, rateMax=inputs.rate, roundTripEff=inputs.eff,
                   cost_install=inputs.costInstall, cost_OM_fix=inputs.costOM,
                   initCharge=0.0)

    # Grid Electricity Supply - All inputs are optional (default values shown below)
    grid = Grid(capacity=1000.0, maxEmissions=0.5, emissionCurve_hr=np.linspace(1, 24, 24),
                emissionCurve_pct=np.linspace(100, 100, 24), cost_OM_var=100.0)

    # Create SBGS (controller is built-in), data is only required inputs, all other components will revert to default if not specified
    hres = SBGS(data, solar=solar, batt=batt, grid=grid, i=0.02, n=20)

    # Run Simulation
    results = hres.run()

    # Display Elapsed Time
    t1 = time.time()
    print
    "Time Elapsed: " + str(round(t1 - t0, 2)) + " s"

    # Combine inputs and results into output and then return
    output = pd.concat([inputs, results], axis=0)
    return output


# =====================
# Main Program
# =====================
if __name__ == '__main__':

    # ==============
    # User Inputs
    # ==============
    studyName = "results_sizing"

    # Monte Carlo Case Inputs (uses excel, each sheet is a separate study)
    xls_filename = "inputs_sizing.xlsx"
    # sheetnames = ["CAES", "BATT", "UTES", "Flywheel"]
    sheetnames = ["CAES"]

    # Specify number of iterations per case
    iterations = 500  # To test
    # iterations = 100 # Used in article

    # Number of cores to use
    num_cores = multiprocessing.cpu_count() - 1  # Consider saving one for other processes

    # ==============
    # Run Simulations
    # ==============
    all_outputs = []
    count = 0

    # Iterate each Monte Carlo case
    for sheetname in sheetnames:

        inputs = monteCarloInputs(xls_filename, sheetname, iterations)

        # Perform Simulations (Run all plant variations in parallel)
        with parallel_backend('multiprocessing', n_jobs=num_cores):
            output = Parallel(verbose=10)(
                delayed(parameterSweep)(inputs.loc[index]) for index in range(iterations))

            # Add output to all_outputs
        all_outputs = all_outputs + output
        # Move output to dataframe and save (if iterations greater than 10)
        if iterations > 10:
            df = pd.DataFrame(output)
            df.to_csv(studyName + '_pt' + str(count) + '.csv')
            count = count + 1

    # Combine outputs into single dataframe and save
    df = pd.DataFrame(all_outputs)
    df.to_csv(studyName + '.csv')
