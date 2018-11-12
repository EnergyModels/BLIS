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

#========================================================================
# Class to hold details of the solar power plant
#========================================================================
class Solar:
    
    #----------
    # Instantiate
    #----------
    def __init__(self, plantType = 'PV', capacity = 32.3, cost_install = 2004., cost_OM_fix = 22.02):
        
        # Properties:
        self.plantType        = plantType         # (string) Technology type
        self.capacity         = capacity          # (MW) capacity 
        self.cost_install     = cost_install      # ($/kW)
        self.cost_OM_fix      = cost_OM_fix       # ($/kW/year)
        
#========================================================================
# Class to hold details of the PowerPlant fuel
#========================================================================        
class Fuel:
    
    def __init__(self,fuelType='NATGAS',cost = 23.27,emissions = 0.18):
        self.fuelType  = fuelType   # name of fuel
        self.cost      = cost       # cost [$] per MWh thermal
        self.emissions = emissions  # CO2 emissions [tons] per MWh thermal


#========================================================================
# General class for energy storage
#========================================================================
class Storage:
    
    #----------
    # Instantiate
    #----------
    def __init__(self, capacity = 30.0, chargeRateMax= 30.0, dischargeRateMax = 30.0, roundTripEff = 90.0, tau = 30.0, cost_install = 2067., cost_OM_fix = 35.6):
        
        
        # Battery Properties:
            # Provided
        self.capacity         = capacity          # (MWh) storage capacity 
        self.chargeRateMax    = chargeRateMax     # (MW) Max Discharge Rate
        self.dischargeRateMax = dischargeRateMax  # (MW) Max Discharge Rate
        self.roundTripEff     = roundTripEff      # (%) Round trip efficiency, applied when energy is discharged
        self.tau              = tau               # (min) Time constant for slowing discharge rate when approaching empty
        self.cost_install     = cost_install      # ($/kW)
        self.cost_OM_fix      = cost_OM_fix       # ($/kW/year)
        
            # Derived
        self.chargeMin        = 0.0               # (MW-min)
        self.chargeMax        = capacity*60.0     # convert from MWh (provided) to MW-min (working units)
        
        # Battery Performance
        self.ramp           = 0.0 # MW
        self.dischargeRate  = 0.0 # MW
        self.chargeRate     = 0.0 # MW
        self.increase       = 0.0 # MW-min
        self.decrease       = 0.0 # MW-min
        self.charge         = 0.0 # MW-min

    #----------
    # Calculate Available Charge Rate (MW)
    #----------
    def getChargeRateAvail(self,dt):
        
        if self.charge < self.chargeMax:
            chargeRateAvail = min((self.chargeMax - self.charge)/dt,self.chargeRateMax)
        else:
            chargeRateAvail = 0.0

        # Debugging        
        if debug==True:
            print "chargeRateAvail" + str(chargeRateAvail)
            
        return chargeRateAvail
            
    #----------
    # Calculate Battery Discharge Rate Available (MW)
    #----------
    def getDischargeRateAvail(self,dt):
        
        if self.charge > self.chargeMin:
            dischargeRateAvail = min((self.charge - self.chargeMin)/dt/self.tau,self.dischargeRateMax)
        else:
            dischargeRateAvail = 0.0
        
        # Debugging
        if debug==True:
            print "dischargeRateAvail" + str(dischargeRateAvail)
            
        return dischargeRateAvail
    
    #----------
    # Update battery status
    #---------- 
    def update(self,dt,increase,decrease):
        
        charge_old = self.charge
        
        # Dis/charge batteries
            # Power Going to and from battery 
        self.dischargeRate      = decrease # MW
        self.chargeRate         = increase # MW
            # Power entering and exiting battery (apply efficiencies)
        self.decrease = decrease # MW
        self.increase = increase*self.roundTripEff/100.0 # MW (Only apply when storing)
            # Adjust battery charge
        self.charge = self.charge + self.increase*dt - self.decrease*dt # MW-min
        
        # Ramp Rate
        self.ramp     =  (self.charge-charge_old) / dt    # MW
        
#========================================================================
# Battery class, child of Storage
# Charge and discharge rates are set to be equal, otherwise classes are identical
#========================================================================
class Battery(Storage):
    
    def __init__(self, capacity = 30.0, rateMax= 30.0, roundTripEff = 90.0, cost_install = 2067., cost_OM_fix = 35.6):
        Storage.__init__(self, capacity = capacity, chargeRateMax= rateMax, dischargeRateMax = rateMax, roundTripEff = 90.0, cost_install = 2067., cost_OM_fix = 35.6)
        
    