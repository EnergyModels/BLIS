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
# Hardcoded Inputs:
debug = False # If True, additional information is presented to the console
plotDPI = 300
omitPeriod = 0 # Number of samples to ignore (5 hours to give sufficient start-up time)
threshold  = 0.001 # threshold for rounding (MW)

# General Imports:
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# BLIS Imports:
from blis import defaultInputs, PowerPlant, Solar, Fuel, Battery, Grid

#========================================================================
# Class to simulate and analyze Hybrid Renewable Energy System (HRES)
#========================================================================

class HRES:
    #========================================================================
    # Initialize HRES Simulation
    #========================================================================
    def __init__(self,data,plant,solar=Solar(),batt=Battery(),fuel=Fuel(),grid=Grid(),i=0.02,n=20):
        # Store Inputs
        self.data  = data
        self.solar = solar
        self.batt  = batt
        self.fuel  = fuel
        self.plant = plant
        self.grid  = grid
        self.i     = i   # (fraction) Interst rate 
        self.n     = n   # (years) System lifetime
        
        # Record number of datapoints
        self.steps = len(data)
        
        # Create pandas dataframe to hold time series performance
        rows = range(self.steps)
        cols = ['PowerRequest','PowerOutput','PowerRamp','HeatInput','Efficiency',
                'battCharge','battIncrease','battDecrease','battDischargeRate','battChargeRate','battRamp',
                'solarUsed','loadShed','deficit','gridUsed','Emissions']
        self.perf = pd.DataFrame(data=0.0,index=rows,columns = cols)
        
        #----
        # Create pandas series to store results
        #----
        attributes = ['demand_MWh','solar_MWh','powerOutput_MWh','heatInput_MWh','solarUsed_MWh','loadShed_MWh','gridUsed_MWh',
                      'fuelCost_dollars','LCOE','efficiency_pct','emissions_tons','deficit_max','deficit_min','deficit_pct_time',
                      'deficit_pct_energy','solarCurtail_pct','loadShed_pct_energy','loadShed_pct_time']
        self.results = pd.Series(index = attributes)
               
    #========================================================================
    # Update - empty control, needs to be updated by all children of HRES
    #========================================================================
    def update(self, datetimeUTC, dt, demand, solar):
                     
        #----------
        # Calculate Battery Dis/charge Rate Available
        #----------
        batt_c_rate = self.batt.getChargeRateAvail(dt)
        batt_d_rate = self.batt.getDischargeRateAvail(dt)
                
        
        if self.plant.capacity > 0.0:
            #----------
            # Power Plant Control 
            #----------    
            # Get Minimum Power Plant Request and 
            #     minimum generation possible for current timestep
            minPowerRequest = self.plant.minPowerRequest
            minGen = minPowerRequest + solar
            
            # If minimum generation will meet or exceed demand, request minimum power plant output
            # Otherwise, use solar and battery, then request additional production
            if minGen > demand or abs(minGen - demand) < threshold:
                powerRequest = minPowerRequest
            else:
                powerRequest = demand - solar - batt_d_rate
    
            # Keep Power Request at or below max plant capacity
            if powerRequest >self.plant.capacity:
                powerRequest =self.plant.capacity
                
            # Keep Power Request at or above min plant capacity
            if powerRequest <minPowerRequest:
                powerRequest = minPowerRequest
                
            # Keep power request at or above threshold
            if powerRequest < threshold:
                powerRequest = threshold
    
            # Update Power Plant Status
            self.plant.update(powerRequest,dt)

        #----------
        # Perform Energy Balance
        #----------
        supply = self.plant.powerOutput + solar
        diff   =  supply - demand
        
        battIncrease = 0.0
        battDecrease = 0.0
        solarUsed    = 0.0
        loadShed     = 0.0
        gridUsed     = 0.0
        
        # 1) Demand = Supply (within threshold)
        if (abs(diff) < threshold):
            solarUsed          = solar
            
        # 2) Supply > Demand            
        elif (diff > 0.0):
            
            # A) Charge Batteries
            if diff > batt_c_rate:
               battIncrease = batt_c_rate
            else:
               battIncrease = diff
            diff = diff - battIncrease # Update diff
            
            # B) Curtail Solar
            if diff < solar:
                solarUsed = solar - diff
            else:
                solarUsed = 0.0
            diff = diff - (solar - solarUsed) # Update diff
            
            # C) Shed Load
            loadShed = diff
            
        # 3) Demand > Supply
        else:
            # No excess suppply, so solar is fully used and no load is shed
            solarUsed          = solar
            
            # Discharge Batteries
            if abs(diff) > batt_d_rate:
               battDecrease = batt_d_rate
            else:
               battDecrease = abs(diff)
               
            # Update
            diff = diff + battDecrease
            
            # Use grid to make-up remaining difference
            if diff < self.grid.capacity:
                gridUsed = abs(diff)
            else:
                gridUsed = self.grid.capacity
        
        
        #----------
        # Calculate Emissions
        #----------  
        CO2_produced = (gridUsed * dt * self.grid.getEmissions(datetimeUTC)) + (self.plant.heatInput / 60.0 * dt * self.fuel.emissions)
        CO2_captured = CO2_produced * (self.plant.co2CaptureEff / 100.0)
        Emissions = CO2_produced - CO2_captured
        
        #----------
        # Update Battery
        #----------  
        self.batt.update(dt,battIncrease,battDecrease)

        #----------  
        # Check Energy Balance
        #----------  
        E_in = solar + self.plant.powerOutput + battDecrease + gridUsed
        E_out = demand + battIncrease + loadShed + (solar - solarUsed)
        E_balance = E_in - E_out        
            # Remainder of energy balance stored as deficit
        deficit            = E_balance
        
    
        #=======
        # Write to console if debugging
        #=======
        if debug == True:
            print "#-----------#"
            print "Batt Charge [MWh]: "  + str(self.batt.charge)
            print "---"
            print "solar             " + str(solar)
            print "powerOutput       " + str(self.plant.powerOutput)
            print "battDecrease      " + str(self.batt.decrease)
            print "Energy In    [MW]:"+ str(E_in)
            print "---"
            print "demand          " + str(demand)
            print "battIncrease    " + str(self.batt.increase)
            print "loadShed        " + str(loadShed)
            print "solarShed       " + str(solar - solarUsed)
            print "Energy Out [MW]:"+ str(E_out)
            print "---"
            print "Balance       [MW]:" + str(E_balance)
            print "#-----------#"
            
        #=======
        # Store performance of current timestep in a pandas series
        #=======
        attributes = ['PowerRequest','PowerOutput','PowerRamp','HeatInput','Efficiency',
                'battCharge','battIncrease','battDecrease','battDischargeRate','battChargeRate','battRamp',
                'solarUsed','loadShed','deficit','gridUsed','Emissions']
        perf = pd.Series(index = attributes)
        
        # Power plant
        perf.PowerRequest = self.plant.powerRequest
        perf.PowerOutput  = self.plant.powerOutput
        perf.PowerRamp    = self.plant.powerRamp
        perf.HeatInput    = self.plant.heatInput
        perf.Efficiency   = self.plant.efficiency
        # Battery
        perf.battCharge        = self.batt.charge
        perf.battIncrease      = self.batt.increase
        perf.battDecrease      = self.batt.decrease
        perf.battDischargeRate = self.batt.dischargeRate
        perf.battChargeRate    = self.batt.chargeRate
        perf.battRamp          = self.batt.ramp
        # Other
        perf.solarUsed      = solarUsed
        perf.loadShed       = loadShed
        perf.deficit        = deficit
        perf.gridUsed       = gridUsed
        perf.Emissions      = Emissions
        
        return perf

    #========================================================================
    # Run Simulation
    #========================================================================
    def run(self):
        
        # Simulate operation
        for step in range(self.steps):
            
            # Access current demand and time step
            datetimeUTC = self.data.loc[step,'DatetimeUTC']
            dt          = self.data.loc[step,'dt']
            demand      = self.data.loc[step,'demand']
            solar       = self.data.loc[step,'solar']
                        
            # Print Status (if debugging)
            if debug== True:
                print "\n\nStep: " + str(step)
                print "datetimeUTC : " + str(datetimeUTC)
                print "dt    (min) : " + str(dt)
                print "Demand (MW) : " + str(demand)
                print "Solar  (MW) : " + str(solar) 
                
            # Update System Operation
            self.perf.loc[step,:] = self.update(datetimeUTC, dt, demand, solar)
            
            # Store Current Performance
            
        # Analyze Results
        results = self.analyzeResults()
            
        return results
    
    #========================================================================
    # Analyze Results
    #========================================================================
    def analyzeResults(self):           
        data = self.data
        perf = self.perf
        
        # Check that enough data points exist for omitPeriod, if not use all data points
        if len(data)>omitPeriod:
            data = data.loc[omitPeriod:]
            perf = perf.loc[omitPeriod:]
                
        # Calculate Energy Use from Power ( MW to MWh)
            # Inputs
        df_demand              = data.loc[:]["demand"]         * data[:]["dt"]/60
        df_solar               = data.loc[:]["solar"]          * data[:]["dt"]/60
        df_powerOutput         = perf.loc[:]["PowerOutput"]    * data[:]["dt"]/60
        df_heatInput           = perf.loc[:]["HeatInput"]      * data[:]["dt"]/60
        df_solarUsed           = perf.loc[:]["solarUsed"]      * data[:]["dt"]/60
        df_loadShed            = perf.loc[:]["loadShed"]       * data[:]["dt"]/60
        df_deficit             = perf.loc[:]["deficit"]        * data[:]["dt"]/60
        df_gridUsed            = perf.loc[:]["gridUsed"]       * data[:]["dt"]/60
        
        # Sum for the year
        demand_MWh           = df_demand.sum()
        solar_MWh            = df_solar.sum()
        powerOutput_MWh      = df_powerOutput.sum()
        heatInput_MWh        = df_heatInput.sum()
        solarUsed_MWh        = df_solarUsed.sum()
        loadShed_MWh         = df_loadShed.sum()
        deficit_MWh          = df_deficit.sum()
        gridUsed_MWh         = df_gridUsed.sum()
        
        # Fuel Cost
        fuelCost_dollars = heatInput_MWh * self.fuel.cost  #$
            
        # Effective Efficiency
        if heatInput_MWh >0.0:
            efficiency_pct        = powerOutput_MWh/heatInput_MWh*100.0      # %
        else:
            efficiency_pct = 0.0
            
         # Deficit
        deficit_max     = perf.deficit.max()
        deficit_min     = perf.deficit.min()
        
        # Pct of the time with a deficit
        threshold = 0.001 # 1 kW (effectively roudning error)
        ind_under    = perf.deficit<(-1.0*threshold)
        t_total     = sum(data[:]["dt"])
        t_under     = sum(data[ind_under]["dt"]) 
        if t_under>0:
            deficit_pct_time     = float(t_under) / float(t_total)*100.0
            deficit_pct_energy   = -1.0*float(deficit_MWh)/float(demand_MWh)*100.0
        else:
            deficit_pct_time     = 0.0
            deficit_pct_energy   = 0.0
        
        # Solar Curtailment
        if solar_MWh > 0.0:
            solarCurtail_pct = 100.0 - float(solarUsed_MWh)/float(solar_MWh)*100.0
        else:
            solarCurtail_pct = 0.0
        
        # Load Shed Pct - energy
        if powerOutput_MWh > 0.0:
            loadShed_pct_energy     = float(loadShed_MWh)/float(powerOutput_MWh) * 100.0
        else:
            loadShed_pct_energy = 0.0
            
        # Load Shed Pct - time
        threshold = 0.001 # 1 kW (effectively roudning error)
        ind_over    = perf.loc[:]["loadShed"]>threshold
        t_over     = sum(data[ind_over]["dt"]) 
        if t_over > 0.0:
            loadShed_pct_time = float(t_over)/float(t_total) * 100.0
        else:
            loadShed_pct_time = 0.0
        
        #----
        # Emissions
        #----
        emissions = perf.loc[:]["Emissions"].sum()
        
        #----
        # LCOE
        #----
        # Calculate multiplier required to scale simulated time series to one year of data
        LCOE_scale = 365.25*24*60/t_total
        
        # I, Install Costs (with financing)
        plant_install_cost =    self.plant.cost_install * (1000.0 * self.plant.capacity)   # $
        PV_install_cost =       self.solar.cost_install * (1000.0 * self.solar.capacity )  # $
        batt_install_cost =     self.batt.cost_install  * (1000.0 * self.batt.capacity)    # $
        total_install_cost =    plant_install_cost + PV_install_cost + batt_install_cost
        I = -1.0*np.pmt(self.i,self.n,total_install_cost) # Apply financing
    
        # M, annual maintenace costs
        plant_var_OM  = self.plant.cost_OM_var  * LCOE_scale * powerOutput_MWh     # $
        plant_OM_fix  = self.plant.cost_OM_fix  * (1000.0 * self.plant.capacity)   # $
        OM_fix_PV     = self.solar.cost_OM_fix  * (1000.0 * self.solar.capacity )  # $
        OM_fix_batt   = self.batt.cost_OM_fix   * (1000.0 * self.batt.capacity)    # $
        grid_var_OM   = self.grid.cost_OM_var  * LCOE_scale * gridUsed_MWh     # $
        M = plant_var_OM + plant_OM_fix + OM_fix_PV + OM_fix_batt + grid_var_OM
    
        # F, annual fuel cost
        F = LCOE_scale * fuelCost_dollars # $
        
        # E, annual electricity generation
#        E = LCOE_scale * powerOutput_MWh * 1000.0 # kWH                    #!!!!!!!!
        E = LCOE_scale * demand_MWh * 1000.0 # kWH
    
        num = I + M + F
        denom = E
    
        LCOE = num / denom
    
        #----
        # Store results
        #----
        self.results.demand_MWh             = demand_MWh          # MWh
        self.results.solar_MWh              = solar_MWh           # MWh 
        self.results.powerOutput_MWh        = powerOutput_MWh     # MWh
        self.results.heatInput_MWh          = heatInput_MWh       # MWh
        self.results.solarUsed_MWh          = solarUsed_MWh       # MWh
        self.results.loadShed_MWh           = loadShed_MWh        # MWh
        self.results.gridUsed_MWh           = gridUsed_MWh        # MWh
        
        self.results.emissions_tons         = emissions           # tons
        
        self.results.fuelCost_dollars       = fuelCost_dollars    # $
        self.results.LCOE                   = LCOE                # $/kWH
        
        self.results.efficiency_pct         = efficiency_pct      # %
        self.results.deficit_max            = deficit_max         # MW
        self.results.deficit_min            = deficit_min         # MW
        self.results.deficit_pct_time       = deficit_pct_time    # %
        self.results.deficit_pct_energy     = deficit_pct_energy  # %
        self.results.solarCurtail_pct       = solarCurtail_pct    # %
        self.results.loadShed_pct_energy    = loadShed_pct_energy # %
        self.results.loadShed_pct_time      = loadShed_pct_time   # %
                
        # Return results
        return self.results
    
    
    #========================================================================
    # Save Time Series Data
    #========================================================================
    def save(self,casename='Results'):
        combine = pd.concat([self.data, self.perf],axis=1)        
        combine.to_csv(casename + ".csv")
        
    #========================================================================
    # Create Plots
    #========================================================================
    def plot_efficiency(self,caseName='Plot'):
        
        # Plot
        x = self.data.loc[:,'t'] - self.data.loc[0,'t']
        plt.plot(x,self.perf.loc[:,'Efficiency'], label='Efficiency')
        
        # Grid + legend
        plt.grid()
        plt.xlabel('Time (min)')
        plt.ylabel('Power Plant Efficiency (%)')
        
        # Save and close
        plotName = caseName + "_efficiency.png"
        plt.savefig(plotName,dpi=plotDPI)
        plt.close()
        return plotName
    
    def plot_EBalance(self,caseName='Plot'):
        
        # Use colorblind friendly palette
        colors = sns.color_palette("colorblind")
        
        # Create common time series
        x = self.data.loc[:,'t'] - self.data.loc[0,'t']
        
        for n in range(3):
        
            if n ==0:
                y1 = self.perf.loc[:,'PowerOutput']
                y2 = self.data.loc[:,'solar']
                y3 = self.perf.loc[:,'battDischargeRate']
                y4 = self.perf.loc[:,'gridUsed']
               
                y = np.vstack((y1,y2,y3,y4))
                pal = [colors[2],colors[4],colors[0],colors[5]]
                labels = ['Natural Gas','Solar PV','Battery','Grid']
                y_label = "Generation\n(MW)"
                # Don't label bottom
                labelbottom = 'off'
               
            elif n==1:       
                y1 = self.data.loc[:,'demand']
                y2 = self.data.loc[:,'solar']-self.perf.loc[:,'solarUsed']
                y3 = self.perf.loc[:,'loadShed']
                y4 = self.perf.loc[:,'battChargeRate']
               
                y = np.vstack((y1,y2,y3,y4))
                pal = [colors[1],colors[4],colors[3],colors[0]]                      
                labels = ['Demand','Solar Curtailment','Load Shed','Battery']           
                y_label = 'Use\n(MW)'
                # Don't label bottom
                labelbottom = 'off'
               
            elif n==2:       
                y = self.perf.loc[:,'battCharge']/60.0
                labels = ['Battery']
                pal = [colors[0]]
                y_label = 'Storage\n(MWh)'
                labelbottom = 'on'
        
            ax = plt.subplot(3 ,1, n + 1)
           
            if n==0 or n==1:
                ax.stackplot(x, y, labels=labels,colors=pal)
            else:
                ax.plot(x,y,label=labels[0])
                ax.set_xlabel('Time (min)')
            ax.set_ylabel(y_label)
           
           # Legend
            ax.legend(loc='center left',bbox_to_anchor=(1.0, 0.5),fancybox=True)
            box = ax.get_position()
            ax.set_position([box.x0, box.y0 + box.height, box.width*0.8, box.height])
            ax.legend(loc='center left',bbox_to_anchor=(1.0, 0.5),fancybox=True)
               
            plt.tick_params(labelbottom=labelbottom)
               
            # Set aspect ratio, based on https://jdhao.github.io/2017/06/03/change-aspect-ratio-in-mpl/
            ratio = 0.25
            xleft, xright = ax.get_xlim() # the abs method is used to make sure that all numbers are positive
            ybottom, ytop = ax.get_ylim() # because x and y axis of an axes maybe inversed.  
            ax.set_aspect(abs((xright-xleft)/(ybottom-ytop))*ratio)
               
               # Caption labels
            caption_labels = ['A','B','C','D','E','F']
            plt.text(0.05, 0.85, caption_labels[n], horizontalalignment='center',verticalalignment='center', transform=ax.transAxes,fontsize='medium',fontweight='bold')
    
        plt.tight_layout()
        plotName = caseName + "_EBalance.png"
        plt.savefig(plotName,dpi=1000,bbox_inches="tight")
        plt.close()
        return plotName
    
    
    def plot_pwrRamps(self,caseName='Plot'):
        
        # Plot
        # Exclude first data point for initialization
        x = self.data.loc[1:,'t'] - self.data.loc[0,'t']
        plt.plot(x,self.perf.loc[1:,'PowerRamp'], label='PowerRamp')

        # Grid + lables
        plt.grid()
        plt.ylabel('Power Plant Ramp Rate (MW)')
        plt.xlabel('Time (min)')
        
        # Save and close
        plotName = caseName + "_pwrRamps.png"
        plt.savefig(plotName,dpi=plotDPI)
        plt.close()
        return plotName
    
    def plot_battStatus(self,caseName='Plot'):        
        
        # Create common time series
        x = self.data.loc[:,'t'] - self.data.loc[0,'t']
        
        #Subplot 1
        plt.subplot(2,1,1)
        plt.plot(x,self.perf.loc[:,'battDischargeRate'], label='Battery Discharge Rate')
        plt.plot(x,self.perf.loc[:,'battChargeRate'], label='Battery Charge Rate')
        plt.ylabel('Power (MW)')
        plt.legend()
        plt.grid()
                
        #Subplot 2
        plt.subplot(2,1,2)
        plt.plot(x,self.perf.loc[:,'battCharge']/60.0, label='Battery Charge')
        plt.ylabel('Energy (MWh)')
        plt.xlabel('Time (min)')
        plt.legend()
        plt.grid()
        
        # Save and close
        plt.tight_layout()
        plotName = caseName + "_battStatus.png"
        plt.savefig(plotName,dpi=plotDPI)
        plt.close()
        return plotName


# ========================================================================
# Solar Battery Grid System (SBGS), child of HRES
# ========================================================================
class SBGS(HRES):

    def __init__(self, data, solar=Solar(), batt=Battery(), grid=Grid(capacity=1000.), i=0.02, n=20):
        # Create PowerPlant with 0.0 MW Capacity
        plant_inputs = defaultInputs(plantType='CCGT')
        plant_inputs.capacity = 0.0  # (MW)
        plant_inputs.maxEfficiency = 100.0  # (%)
        plant = PowerPlant(plant_inputs)

        # Create default fuel, will not be used
        fuel = Fuel()

        # All other inputs are passed on to HRES function
        HRES.__init__(self, data, plant=plant, solar=solar, batt=batt, fuel=fuel, grid=grid, i=0.02, n=20)