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
from blis import Solar, Grid, Battery, SBGS
import os


# =====================
# Function to enable parameter sweep
# =====================
def parameter_sweep(batt_size):
    # Record time to solve
    t0 = time.time()

    # Load_Data - Expected Columns (units): DatetimeUTC (UTC format), t (min), dt (min), demand (MW), solar (MW)
    data = pd.read_csv('data063_Oct30th.csv')

    # Solar Plant - All inputs are optional (default values shown below)
    solar = Solar(plantType='PV', capacity=32.3, cost_install=2004., cost_OM_fix=22.02)

    # Battery Storage - All inputs are optional (default values shown below)
    batt = Battery(capacity=batt_size, rateMax=batt_size, roundTripEff=90.0, cost_install=2067., cost_OM_fix=35.6,
                   initCharge=100.0)
    # Grid Electricity Supply - All inputs are optional (default values shown below)
    grid = Grid(capacity=1000.0, maxEmissions=0.5, emissionCurve_hr=np.linspace(1, 24, 24),
                emissionCurve_pct=np.linspace(100, 100, 24), cost_OM_var=100.0)

    # Create SBGS (controller is built-in)
    # data is only required inputs, all other components will revert to default if not specified
    hres = SBGS(data, solar=solar, batt=batt, grid=grid, i=0.02, n=20)

    # Run Simulation
    results = hres.run()

    # Display Elapsed Time
    t1 = time.time()
    print("Time Elapsed: " + str(round(t1 - t0, 2)) + " s")

    # Extract LCOE
    return results


# =====================
# Main Program
# =====================
if __name__ == '__main__':
    # Parameter to vary
    param_array = np.linspace(0., 100., num=101)
    param_name = 'battSize_MWh'

    # Number of cores to use
    ncpus = -1  # int(os.getenv('NUM_PROCS'))

    # Run Simulations
    with parallel_backend('multiprocessing', n_jobs=ncpus):
        output = Parallel(n_jobs=ncpus, verbose=5)(delayed(parameter_sweep)(param) for param in param_array)

        # Move input and output into a dataframe
    df_in = pd.DataFrame(param_array)
    df_in.columns = [param_name]
    df_out = pd.DataFrame(output)
    df = pd.concat([df_in, df_out], axis=1)

    # Save results
    df.to_csv('parameter_sweep_results.csv')
