

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
data = pd.read_csv('results_sizing.csv')


# Remove cases that used grid energy
# data = data[data['gridUsed_MWh']==0]

sns.pairplot(data,x_vars=['pvSize','capacity','rate'],y_vars=['LCOE','solarCurtail_pct','gridUsed_MWh'])
plt.savefig('results.png')