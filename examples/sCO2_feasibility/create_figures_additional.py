import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns
import numpy as np


# %%=============================================================================#
# Figure 12 - Emission vs. LCOE
results_filename = "Results_MonteCarlo1.csv"
savename = "Fig12_Emissions_vs_LCOE.png"
# =============================================================================#
# Import results
df = pd.read_csv(results_filename)

# Prepare results for plotting
# Create series for plantType
labels = {'OCGT': '$OCGT$','OCGT_Batt': '$OCGT$','CCGT': '$CCGT$','CCGT_Batt': '$CCGT$','sCO2': '$sCO_2$','sCO2_Batt': '$sCO_2$'}
df = df.assign(plantType=df.sheetname)
for key in labels.keys():
    df.loc[(df.plantType == key), 'plantType'] = labels[key]

# Create series for pct_solar
df = df.assign(pct_solar=df.solarCapacity_MW)
df.loc[(df.pct_solar == 0.513), 'pct_solar'] = 1.0
df.loc[(df.pct_solar == 32.3), 'pct_solar'] = 63.0

# Filter results
df2 = df[(df.LCOE > 0) & (df.emissions_tons > 0) ]

# Convert from tons to Mtons
df2.loc[:,'emissions_tons'] = df2.loc[:,'emissions_tons'] / 1000.0


# Version 1
g = sns.FacetGrid(df2,col="battSize",row="pct_solar",hue="plantType")
g = (g.map(plt.scatter, "LCOE", "emissions_tons", edgecolor="w").add_legend())
g.set_axis_labels("LCOE (US Dollars)", "Emissions (MTons)")
g.savefig('Fig12_Emissions_vs_LCOE_V1.png')

# Version 2
g = sns.FacetGrid(df2,hue="plantType")
g = (g.map(plt.scatter, "LCOE", "emissions_tons", edgecolor="w").add_legend())
g.set_axis_labels("LCOE (US Dollars)", "Emissions (MTons)")
g.savefig('Fig12_Emissions_vs_LCOE_V2.png')


# Version 3
sns.set_style("darkgrid")
g = sns.FacetGrid(df2,col="battSize",row="pct_solar",hue="plantType",despine=True)
g = (g.map(plt.hist, "emissions_tons",histtype="step",linewidth=3).add_legend())
g.set(ylim=(0,25))
g.set_axis_labels("Emissions (MTons)")
g.set_titles("")
g.savefig('Fig12_Emissions_V3.png')