# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
"""
BLIS - Balancing Load of Intermittent Solar:
A characteristic-based transient power plant model

Copyright (C) 2020. University of Virginia Licensing & Ventures Group (UVA LVG). All Rights Reserved.

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
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

##======================
## Version 1 - Consumption by Fuel Source
##======================
## Input Data
## Source: https://www.eia.gov/electricity/data.php#gencapacity
#yr = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]
#solar =[0,0,0,0,0,0,20908,313221] # MWh
#NG = [16999125,18332373,25037749,22651167,20881566,33284216,40904843,44507088] # MWh
#total = [72966456,66670859,70739235,76896565,77137438,84411592,92554876,90417351] # MWh
#
#
## Move to DataFrame
#df = pd.DataFrame(columns = ['yr','solar','NG','total','pct_solar','pct_NG'])
#df.yr = yr
#df.solar = solar
#df.NG = NG
#df.total = total
#df.pct_solar = df.solar / df.total * 100.0
#df.pct_NG = df.NG / df.total * 100.0
#
#plt.figure(1)
#plt.plot(df.yr, df.solar, label = 'Solar')
#plt.plot(df.yr, df.NG, label = 'Natural Gas')
#plt.plot(df.yr, df.total, label = 'Total')
#plt.xlabel('Year')
#plt.ylabel('VA Electricity Consumption by Source (MWh)')
#
#plt.figure(2)
#plt.plot(df.yr, df.pct_solar, label = 'Solar')
#plt.plot(df.yr, df.pct_NG, label = 'Natural Gas')
#plt.xlabel('Year')
#plt.ylabel('VA Electricity Consumption by Source (%)')
#
#
##======================
## Version 2 - Cumulative Installs
##======================
#
#yr = [2010,2011,2012,2013,2014,2015,2016,2017,2018]
#yr_proj = [2018,2019,2020,2021,2022,2023,2024,2025]
#solar_act = [0,0,0,0,0,0,136,520,694]
#ng_act = [2867.4,3457.4,3457.4,3457.4,5538.4,5538.4,6896.4,6896.4,8484.4]
#solar_proj1 = []
#solar_proj2 = []
#ng_proj1 = []
#ng_proj2 = []
#solar_mult = [1.1,1.4]
#ng_mult = [1.05,1.1]
#
#solar_proj1.append(solar_act[-1])
#solar_proj2.append(solar_act[-1])
#ng_proj1.append(ng_act[-1])
#ng_proj2.append(ng_act[-1])
#
#for y in yr_proj[1:]:
#    solar_proj1.append(solar_proj1[-1]*solar_mult[0])
#    solar_proj2.append(solar_proj2[-1] * solar_mult[1])
#    ng_proj1.append(ng_proj1[-1]*ng_mult[0])
#    ng_proj2.append(ng_proj2[-1] * ng_mult[1])
#
#plt.figure(3)
#convert = 1/1000.
#ng_act = np.array(ng_act)*convert
#solar_act = np.array(solar_act)*convert
#ng_proj1 = np.array(ng_proj1)*convert
#ng_proj2 = np.array(ng_proj2)*convert
#solar_proj1 = np.array(solar_proj1)*convert
#solar_proj2 = np.array(solar_proj2)*convert
#
#plt.plot(yr, ng_act, label = 'Natural Gas',color='brown',linestyle='-')
#plt.plot(yr, solar_act, label = 'Solar',color='orange',linestyle='-')
## plt.plot(yr_proj, ng_proj, label = 'Natural Gas - Projected',color='brown',linestyle='--')
## plt.plot(yr_proj, solar_proj, label = 'Solar - Projected',color='orange',linestyle='--')
#
#plt.fill_between(yr_proj,ng_proj1,ng_proj2, label = 'Natural Gas - Projected',color='brown',alpha=0.5,hatch='x')
#plt.fill_between(yr_proj,solar_proj1,solar_proj2, label = 'Solar - Projected',color='orange',alpha=0.5,hatch='x')
#plt.legend (loc='upper left')
#plt.xlabel('Year')
#plt.ylabel('Active Power Plants (GW)')
#plt.savefig('Fig1_Projections_v2.png',dpi=1000)
#

#======================
# Version 3 - Cumulative Installs
#======================
sns.set_style('white')
pal = sns.color_palette('colorblind')
yr = [2009,2010,2011,2012,2013,2014,2015,2016,2017,2018]
solar_act = [0,0,0,0,0,0,0,136,520,694]
ng_act = [2867.4,2867.4,3457.4,3457.4,3457.4,5538.4,5538.4,6896.4,6896.4,8484.4]

ind = 0

yr_proj = np.arange(2009,2030,1)
solar_coeff = np.polyfit(yr[ind:],solar_act[ind:],2)
ng_coeff = np.polyfit(yr,ng_act,2)


solar_proj = []
ng_proj = []

for y in yr_proj:
    solar_proj.append(solar_coeff[0]*y**2+solar_coeff[1]*y+solar_coeff[2])
    ng_proj.append(ng_coeff[0]*y**2+ng_coeff[1]*y+ng_coeff[2])

plt.figure(4)
convert = 1/1000.
ng_act = np.array(ng_act)*convert
solar_act = np.array(solar_act)*convert
ng_proj = np.array(ng_proj)*convert
solar_proj = np.array(solar_proj)*convert


colors = [sns.xkcd_rgb["sienna"],sns.xkcd_rgb["golden"]]

plt.plot(yr, ng_act, label = 'Natural Gas',color=colors[0],marker='.',linestyle='None',markersize=15)
plt.plot(yr, solar_act, label = 'Solar',color=colors[1],marker='.',linestyle='None',markersize=15)
plt.plot(yr_proj, ng_proj,color=colors[0],linestyle='--',linewidth=2.5)
plt.plot(yr_proj[ind:], solar_proj[ind:], color=colors[1],linestyle='--',linewidth=2.5)
plt.plot([2009,2026],[5,5], color=colors[1],label='VA Solar Target',linestyle='-',linewidth=2.5)

plt.xlim(left=2009,right=2025)
plt.ylim(bottom=0,top=20)

plt.rcParams.update({'font.size': 16})

plt.legend (loc='upper center')
plt.xlabel('Year')
plt.ylabel('Active Power Plants (GW)')
plt.savefig('Fig1_Projections.png',dpi=1000)
plt.close()
