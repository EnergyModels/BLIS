import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

#======================
# Version 1 - Consumption by Fuel Source
#======================
# Input Data
# Source: https://www.eia.gov/electricity/data.php#gencapacity
yr = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]
solar =[0,0,0,0,0,0,20908,313221] # MWh
NG = [16999125,18332373,25037749,22651167,20881566,33284216,40904843,44507088] # MWh
total = [72966456,66670859,70739235,76896565,77137438,84411592,92554876,90417351] # MWh


# Move to DataFrame
df = pd.DataFrame(columns = ['yr','solar','NG','total','pct_solar','pct_NG'])
df.yr = yr
df.solar = solar
df.NG = NG
df.total = total
df.pct_solar = df.solar / df.total * 100.0
df.pct_NG = df.NG / df.total * 100.0

plt.figure(1)
plt.plot(df.yr, df.solar, label = 'Solar')
plt.plot(df.yr, df.NG, label = 'Natural Gas')
plt.plot(df.yr, df.total, label = 'Total')
plt.xlabel('Year')
plt.ylabel('VA Electricity Consumption by Source (MWh)')

plt.figure(2)
plt.plot(df.yr, df.pct_solar, label = 'Solar')
plt.plot(df.yr, df.pct_NG, label = 'Natural Gas')
plt.xlabel('Year')
plt.ylabel('VA Electricity Consumption by Source (%)')


#======================
# Version 2 - Cumulative Installs
#======================

yr = [2010,2011,2012,2013,2014,2015,2016,2017,2018]
yr_proj = [2018,2019,2020,2021,2022,2023,2024,2025]
solar_act = [0,0,0,0,0,0,136,520,694]
ng_act = [2867.4,3457.4,3457.4,3457.4,5538.4,5538.4,6896.4,6896.4,8484.4]
solar_proj1 = []
solar_proj2 = []
ng_proj1 = []
ng_proj2 = []
solar_mult = [1.1,1.4]
ng_mult = [1.05,1.1]

solar_proj1.append(solar_act[-1])
solar_proj2.append(solar_act[-1])
ng_proj1.append(ng_act[-1])
ng_proj2.append(ng_act[-1])

for y in yr_proj[1:]:
    solar_proj1.append(solar_proj1[-1]*solar_mult[0])
    solar_proj2.append(solar_proj2[-1] * solar_mult[1])
    ng_proj1.append(ng_proj1[-1]*ng_mult[0])
    ng_proj2.append(ng_proj2[-1] * ng_mult[1])

plt.figure(3)
convert = 1/1000.
ng_act = np.array(ng_act)*convert
solar_act = np.array(solar_act)*convert
ng_proj1 = np.array(ng_proj1)*convert
ng_proj2 = np.array(ng_proj2)*convert
solar_proj1 = np.array(solar_proj1)*convert
solar_proj2 = np.array(solar_proj2)*convert

plt.plot(yr, ng_act, label = 'Natural Gas',color='brown',linestyle='-')
plt.plot(yr, solar_act, label = 'Solar',color='orange',linestyle='-')
# plt.plot(yr_proj, ng_proj, label = 'Natural Gas - Projected',color='brown',linestyle='--')
# plt.plot(yr_proj, solar_proj, label = 'Solar - Projected',color='orange',linestyle='--')

plt.fill_between(yr_proj,ng_proj1,ng_proj2, label = 'Natural Gas - Projected',color='brown',alpha=0.5,hatch='x')
plt.fill_between(yr_proj,solar_proj1,solar_proj2, label = 'Solar - Projected',color='orange',alpha=0.5,hatch='x')
plt.legend (loc='upper left')
plt.xlabel('Year')
plt.ylabel('VA Power Plant Installations by Source (GW)')
plt.savefig('Fig1_Projections.png',dpi=1000)
