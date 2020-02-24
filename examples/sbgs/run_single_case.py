# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
"""
BLIS - Balancing Load of Intermittent Solar:
A characteristic-based transient power plant model

Copyright (C) 2019. University of Virginia Licensing & Ventures Group (UVA LVG). All Rights Reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
import pandas as pd
import numpy as np
import time
from blis import Solar, Grid, Battery, SBGS

# Record time to solve
t0 = time.time()

# Load_Data - Expected Columns (units): DatetimeUTC (UTC format), t (min), dt (min), demand (MW), solar (MW)
filename = 'data063_Oct30th.csv'
data = pd.read_csv(filename)

# Solar Plant - All inputs are optional (default values shown below)
solar = Solar(plantType='PV', capacity=32.3, cost_install=2004., cost_OM_fix=22.02)

# Battery Storage - All inputs are optional (default values shown below)
batt = Battery(capacity=30.0, rateMax=30.0, roundTripEff=90.0, cost_install=2067., cost_OM_fix=35.6, initCharge=100.0)

# Grid Electricity Supply - All inputs are optional (default values shown below)
grid = Grid(capacity=1000.0, maxEmissions=0.5, emissionCurve_hr=np.linspace(1, 24, 24),
            emissionCurve_pct=np.linspace(100, 100, 24), cost_OM_var=100.0)

# Create SBGS (controller is built-in), data is only required inputs, all other components will revert to default if not specified
hres = SBGS(data, solar=solar, batt=batt, grid=grid, i=0.02, n=20)

# Run Simulation
results = hres.run()

# Create Plots and save time series data
saveName = 'Results_SBGS_SampleDay_Oct30th'
hres.save(saveName)
hres.plot_battStatus(caseName=saveName)
hres.plot_EBalance(caseName=saveName)
# hres.plot_efficiency(caseName = saveName) # No PowerPlant is used
# hres.plot_pwrRamps(caseName = saveName) # No PowerPlant is used


# Display Elapsed Time
t1 = time.time()
print("Time Elapsed: " + str(round(t1 - t0, 2)) + " s")
