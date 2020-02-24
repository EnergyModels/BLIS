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
import matplotlib.pyplot as plt 
import seaborn as sns

# Set Color Palette
colors = sns.color_palette("colorblind")

# Set resolution for saving figures
DPI = 1000

# %%=============================================================================#
#  Post-Processing
# =============================================================================#
results_filename = "results_system_sizing.csv"
# Import results
df_raw = pd.read_csv(results_filename)

# Create series for plantType
labels = {'OCGT': '$OCGT$','CCGT': '$CCGT$','sCO2': '$sCO_2$','sCO2_CCS': '$sCO_2+CCS$', 'CCGT_CCS': '$CCGT+CCS$',}
df_raw = df_raw.assign(plantType=df_raw.sheetname)
for key in labels.keys():
    df_raw.loc[(df_raw.plantType == key), 'plantType'] = labels[key]

# Convert from tons to Mtons
df_raw.loc[:,'emissions_tons'] = df_raw.loc[:,'emissions_tons'] / 1000.0

# Filter results (df_raw -> df)
df = df_raw[(df_raw.LCOE > 0) & (df_raw.emissions_tons > 0) & (df_raw.gridUsed_MWh < 0.01)]

# %%===========================================================================#
# Find Pareto Front
#=============================================================================#
bin_width = 0.02
ind = []
for value in labels.values():
    
    if sum(value==df.plantType)>0:
        
        df3 = df.loc[(df.plantType == value)]
        
        low = 0.0
        high = bin_width
        
        while high<df3.LCOE.max():
            
            df4 = df3.loc[(df.LCOE > low) & (df.LCOE < high)]
            if df4.shape[0]>0:
                index = df4['emissions_tons'].idxmin()
                ind.append(index)
            low = high
            high = high + bin_width

df_pareto = df.loc[ind]

# %%===========================================================================#
# Figure - Emission vs. LCOE Raw
savename = 'Fig_Emissions_vs_LCOE_Raw.png'
# =============================================================================#
g = sns.FacetGrid(df,hue="plantType")
g = (g.map(plt.scatter, "LCOE", "emissions_tons", edgecolor="w").add_legend())
g.set_axis_labels("LCOE (US Dollars)", "Emissions (MTons)")
g.savefig(savename)
            

# %%===========================================================================#
# Figure - Pair Plot
# =============================================================================#
ind = df.loc[:,'sheetname']=='sCO2'

g = sns.PairGrid(df[ind],hue="plantType",x_vars=['plantSize','solarCapacity','battSize'],y_vars=["LCOE", "emissions_tons"])
g = (g.map(plt.scatter, edgecolor="w").add_legend())
g.savefig("Fig_AllPlants.png")

g = sns.relplot(x="LCOE", y="emissions_tons",hue="plantType",data=df)
g.savefig("Fig_AllPlants.png")

g = sns.PairGrid(df[ind],hue="plantType",vars=["LCOE", "emissions_tons",'plantSize','solarCapacity','battSize'])
g = (g.map(plt.scatter, edgecolor="w").add_legend())
g.savefig("Fig_sCO2.png")


# %%===========================================================================#
# Figure - Emission vs. LCOE Pareto Front (Design)
savename = 'Fig_Design_Emissions_vs_LCOE_Pareto.png'
# =============================================================================#

#  Configurations
plantTypes = labels.values()
dot_colors = [colors[0],colors[1],colors[2],colors[3],colors[4]]
markers    = ['o','x','+','v','>']

x_var = 'LCOE'
x_label = 'LCOE (US Dollars)'
y_vars = ['emissions_tons','plantSize','solarCapacity','battSize']
y_labels = ["Emissions (MTons)","Plant Capacity (MW)","Solar Capacity (MW)","Battery Size (MWh)"]

f,a = plt.subplots(4,1,sharex=True)#, sharey=True
for ax,y_var,y_label in zip(a,y_vars,y_labels):
    
    for plantType,dot_color,marker in zip(plantTypes,dot_colors,markers):
        
        df_pareto2 = df_pareto[(df_pareto.plantType == plantType)]
        ax.plot(df_pareto2.loc[:,x_var],df_pareto2.loc[:,y_var],color=dot_color,marker=marker,label=plantType)
        
        ax.set_ylabel(y_label)
        if y_var == y_vars[-1]:
            ax.set_xlabel
            
plt.savefig(savename)

# %%===========================================================================#
# Figure - Emission vs. LCOE Pareto Front (Other Parameters)
savename = 'Fig_Design_Emissions_vs_LCOE_Pareto_Addl.png'
# =============================================================================#

#  Configurations
plantTypes = labels.values()
dot_colors = [colors[0],colors[1],colors[2],colors[3],colors[4]]
markers    = ['o','x','+','v','>']

x_var = 'LCOE'
x_label = 'LCOE (US Dollars)'
y_vars = ['emissions_tons','solarCurtail_pct','loadShed_pct_energy','gridUsed_MWh']
y_labels = ["Emissions (MTons)","Solar Curtailment (%)","Load Shed (%)","Grid Used (MWh)"]

f,a = plt.subplots(4,1,sharex=True)#, sharey=True
for ax,y_var,y_label in zip(a,y_vars,y_labels):
    
    for plantType,dot_color,marker in zip(plantTypes,dot_colors,markers):
        
        df_pareto2 = df_pareto[(df_pareto.plantType == plantType)]
        ax.plot(df_pareto2.loc[:,x_var],df_pareto2.loc[:,y_var],color=dot_color,marker=marker,label=plantType)
        
        ax.set_ylabel(y_label)
        if y_var == y_vars[-1]:
            ax.set_xlabel
            
plt.savefig(savename)
