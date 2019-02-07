

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
