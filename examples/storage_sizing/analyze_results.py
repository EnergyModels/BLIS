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
import seaborn as sns
import matplotlib.pyplot as plt
data = pd.read_csv('results_sizing.csv')


# Remove cases that used grid energy
# data = data[data['gridUsed_MWh']==0]


LCOE_filter = 1.0 # $/kWh
#gridUsed_MWh_filter = 944. # 1 day
gridUsed_MWh_filter = 6605. # 1 week
gridUsed_MWh_filter = 20000. # 

sns.pairplot(data,x_vars=['pvSize','capacity','rate'],y_vars=['LCOE','solarCurtail_pct','gridUsed_MWh'])
plt.savefig('results_raw.png')

data_filter_LCOE = data[data['LCOE']<LCOE_filter]
sns.pairplot(data_filter_LCOE,x_vars=['pvSize','capacity','rate'],y_vars=['LCOE','solarCurtail_pct','gridUsed_MWh'])
plt.savefig('results_filer_LCOE.png')

data_filter_grid = data[data['gridUsed_MWh']<gridUsed_MWh_filter]
sns.pairplot(data_filter_grid,x_vars=['pvSize','capacity','rate'],y_vars=['LCOE','solarCurtail_pct','gridUsed_MWh'])
plt.savefig('results_filter_grid.png')

data_filter_comb = data[(data['LCOE']<LCOE_filter)&(data['gridUsed_MWh']<gridUsed_MWh_filter)]
sns.pairplot(data_filter_comb,x_vars=['pvSize','capacity','rate'],y_vars=['LCOE','solarCurtail_pct','gridUsed_MWh'])
plt.savefig('results_filter_comb.png')
