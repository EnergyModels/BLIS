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
from blis import Solar, Fuel, Battery, PowerPlant, defaultInputs, HRES

# Record time to solve
t0 = time.time()

# Load_Data - Expected Columns (units): DatetimeUTC (UTC format), t (min), dt (min), demand (MW), solar (MW)
filename = 'data063_Oct30th.csv'
#filename = 'data063.csv'
data = pd.read_csv(filename)

# Solar Plant - All inputs are optional (default values shown below)
solar = Solar(plantType = 'PV', capacity = 32.3, cost_install = 2004., cost_OM_fix = 22.02)

# Battery Storage - All inputs are optional (default values shown below)
batt = Battery(capacity = 30.0, rateMax= 30.0, roundTripEff = 90.0, cost_install = 2067., cost_OM_fix = 35.6,initCharge = 0.0)

# Fuel - All inputs are optional (default values shown below)
fuel = Fuel(fuelType='NATGAS',cost = 23.27,emissions = 0.18)

# Create power plant
    # 1 - create pandas series of power plant characteristics
plant_inputs = defaultInputs(plantType = 'CCGT') # Start with CCGT default inputs and then adjust to specific case
plant_inputs.plantType      = "sCO2"
plant_inputs.Eff_A          = -5.60E-03
plant_inputs.Eff_B          = 1.05E+00
plant_inputs.Eff_C          = 5.00E+01
plant_inputs.maxEfficiency  = 53.1
plant_inputs.rampRate       = 50.0
plant_inputs.minRange       = 30.0
    # 2 - create power plant
plant        = PowerPlant(plant_inputs)

# Create HRES (controller is built-in), data and plant are only required inputs, all other components will revert to default if not specified
hres         = HRES(data,plant,solar=solar,batt=batt,fuel=fuel,i=0.02,n=20)

# Run Simulation
results = hres.run()

# Create Plots and save time series data
saveName = 'Results_SampleDay_Oct30th_sCO2'
hres.plot_battStatus(caseName = saveName)
hres.plot_EBalance(caseName = saveName)
hres.plot_efficiency(caseName = saveName)
hres.plot_pwrRamps(caseName = saveName)
hres.save(saveName)
results.to_csv(saveName+'_Analysis.csv')

# Display Elapsed Time
t1 = time.time()
print "Time Elapsed: " + str(round(t1-t0,2)) + " s"