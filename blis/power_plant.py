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
# Hardcoded Inputs:
debug = False  # If True, additional information is presented to the console

# General Imports:
import pandas as pd


# BLIS Imports:
# N/A

# ========================================================================
# Prepare PowerPlant Inputs
# ========================================================================
def emptyInputs():
    # Create DataFrame
    attributes = ['plantType', 'capacity', 'maxEfficiency', 'rampRate', 'minRange', 'startTime', 'stopTime',
                  'Eff_A', 'Eff_B', 'Eff_C',
                  'cost_install', 'cost_OM_fix', 'cost_OM_var', 'co2CaptureEff']
    plant_inputs = pd.Series(index=attributes)
    return plant_inputs


def defaultInputs(plantType='CCGT'):
    # Create DataFrame
    plant_inputs = emptyInputs()

    # Default values
    if plantType == 'CCGT':
        # Default values
        plant_inputs.plantType = "CCGT"  # Technology type (string)
        plant_inputs.capacity = 51.3  # MW
        plant_inputs.maxEfficiency = 53.44  # %
        plant_inputs.rampRate = 64.94  # MW/min
        plant_inputs.minRange = 36.43  # %
        plant_inputs.startTime = 33.13  # min
        plant_inputs.stopTime = 5.0  # min
        plant_inputs.Eff_A = -6.94E-03  # Efficiency Curve Ax^2 + Bx + C
        plant_inputs.Eff_B = 1.28E+00
        plant_inputs.Eff_C = 4.08E+01
        plant_inputs.cost_install = 1260.0  # ($/kW)
        plant_inputs.cost_OM_fix = 11.11  # ($/kW/year)
        plant_inputs.cost_OM_var = 3.54  # ($/MWh)
        plant_inputs.co2CaptureEff = 0.0  # Carbon Capture Efficiency (%)

    elif plantType == 'OCGT':
        # Default values
        plant_inputs.plantType = "OCGT"  # Technology type (string)
        plant_inputs.capacity = 51.3  # MW
        plant_inputs.maxEfficiency = 38.33  # %
        plant_inputs.rampRate = 72.77  # MW/min
        plant_inputs.minRange = 46.11  # %
        plant_inputs.startTime = 10.0  # min
        plant_inputs.stopTime = 5.0  # min
        plant_inputs.Eff_A = -1.09E-02  # Efficiency Curve Ax^2 + Bx + C
        plant_inputs.Eff_B = 2.03E+00
        plant_inputs.Eff_C = 5.44E+00
        plant_inputs.cost_install = 750.0  # ($/kW)
        plant_inputs.cost_OM_fix = 17.67  # ($/kW/year)
        plant_inputs.cost_OM_var = 3.54  # ($/MWh)
        plant_inputs.co2CaptureEff = 0.0  # Carbon Capture Efficiency (%)

    # Return DataFrame
    return plant_inputs


# ========================================================================
# Instantiate PowerPlant
# ========================================================================
class PowerPlant:

    def __init__(self, plant_inputs):

        # Define Plant Characteristics
        self.type = plant_inputs.plantType  # Technology type (string)
        self.capacity = plant_inputs.capacity  # MW
        self.maxEfficiency = plant_inputs.maxEfficiency  # %
        self.rampRate = plant_inputs.rampRate  # MW/min
        self.minRange = plant_inputs.minRange  # %
        self.startTime = plant_inputs.startTime  # min
        self.stopTime = plant_inputs.stopTime  # min
        self.Eff_A = plant_inputs.Eff_A  # Efficiency Curve Ax^2 + Bx + C
        self.Eff_B = plant_inputs.Eff_B  # -
        self.Eff_C = plant_inputs.Eff_C  # -
        self.cost_install = plant_inputs.cost_install  # ($/kW)
        self.cost_OM_fix = plant_inputs.cost_OM_fix  # ($/kW/year)
        self.cost_OM_var = plant_inputs.cost_OM_var  # ($/MWh)
        self.co2CaptureEff = plant_inputs.co2CaptureEff  # Carbon Capture Efficiency (%)

        # Derived Characteristics
        self.minPowerRequest = self.minRange / 100.0 * self.capacity
        self.partLoadRange = [plant_inputs.minRange / 100.0, 1.0]  # list (fractions)

        # Initialize Operation
        self.status = "ON"  # ON, STARTING, OFF
        self.range = 1.0
        self.efficiency = self.maxEfficiency  # -1.0 indicates it is not active
        self.powerRequest = self.capacity
        self.powerOutput = self.capacity
        self.powerRamp = 0.0
        self.heatInput = self.powerOutput / (self.efficiency / 100.0)
        self.timeSinceStart = self.startTime  # -1.0 indicates it is not active
        self.timeSinceStop = -1.0  # -1.0 indicates it is not active

    # ========================================================================
    # Get Plant Status
    # ========================================================================
    def getStatusNum(self):

        if self.status == "OFF":
            statusNum = 1
        elif self.status == "STARTING":
            statusNum = 2
        elif self.status == "ON":
            statusNum = 3

        return statusNum

    # ========================================================================
    # Print Commands
    # ========================================================================
    # Display Power Plant Definition
    def printDef(self):
        print("\nPower Plant Definition")
        print("Type                 : " + self.type)
        print("Capacity (MW)        : " + str(self.capacity))
        print("Max Efficiency (%)   : " + str(self.maxEfficiency))
        print("Ramp Rate (MW/min)   : " + str(self.rampRate))
        print("Part Load Range (fr) : " + str(self.partLoadRange[0]) + " - " + str(self.partLoadRange[1]))
        print("Start Time (min)     : " + str(self.startTime))
        print("Stop Time (min)      : " + str(self.stopTime))

    # Display Power Plant Current Performance       
    def printPerf(self):
        print("\nPower Plant Current Performance")
        print("Status                 : " + self.status)
        print("Range                  : " + str(self.range))
        print("Efficiency (%)         : " + str(self.efficiency))
        print("Power Requestt (MW)    : " + str(self.powerRequest))
        print("Power Output (MW)      : " + str(self.powerOutput))
        print("Heat Input (MW)        : " + str(self.heatInput))
        print("Time Since Start (min) : " + str(self.timeSinceStart))
        print("Time Since Stop (min)  : " + str(self.timeSinceStop))

    # ========================================================================
    # Return Operation as a list (for import into a dataframe)
    # ========================================================================
    def getOpList(self):

        df_list = []
        df_list.append(self.status)
        df_list.append(self.range)
        df_list.append(self.efficiency)
        df_list.append(self.powerRequest)
        df_list.append(self.powerOutput)
        df_list.append(self.heatInput)
        df_list.append(self.timeSinceStart)
        df_list.append(self.timeSinceStop)

        return df_list

    # ========================================================================
    # Operational Commands
    # ========================================================================
    def start(self):
        if self.status == "OFF":
            self.status = "STARTING"
        else:
            print("Error: Unit is already starting")
        pass

    def stop(self):
        if self.status == "ON" or self.status == "STARTING":
            self.status = "OFF"
            self.range = 0.0
            self.efficiency = -1.0
            self.powerOutput = 0.0
            self.heatInput = 0.0
            self.timeSinceStart = -1.0
        else:
            print("Error: Unit is already stopping")
        pass

    # ========================================================================
    # Update Plant Operation
    # ========================================================================
    def update(self, pwr, dt):
        self.powerRequest = pwr
        # ----------
        # OFF
        # ----------
        if self.status == "OFF":
            # Increase counter since stop ( if it has been previously stopped)
            if self.timeSinceStop > 0.0:
                self.timeSinceStop = self.timeSinceStop + dt
            pass

        # ----------
        # STARTING
        # ----------
        elif self.status == "STARTING":
            # Increase counter since start
            self.timeSinceStart = self.timeSinceStart + dt

            # Switch to ON state
            if self.timeSinceStart > self.startTime:
                self.status = "ON"
                self.timeSinceStop = -1.0  # -1.0 indicates it is not active
                # Initialize Performance (sets self.efficiency, self.powerOutput, and self.heatInput)
                self.initPwr()
        # ----------
        # ON
        # ----------
        elif self.status == "ON":
            # Increase counter since start
            self.timeSinceStart = self.timeSinceStart + dt

            # Update Performance (sets self.efficiency, self.powerOutput, and self.heatInput)
            self.updatePwr(pwr, dt)

        # Return Power Out and Heat In
        return self.powerOutput, self.heatInput, self.efficiency

    # ========================================================================
    # Internal Subroutine for initializing power production (switch from STARTING to ON states)
    # ========================================================================
    def initPwr(self):
        self.range = self.partLoadRange[0]  # start at minimum of operating range
        self.powerOutput = self.range * self.capacity  # start at minimum
        self.efficiency = self.calcEff(self.powerOutput)
        self.heatInput = self.powerOutput / (self.efficiency / 100.0)

    # ========================================================================
    # Internal Subroutine for updating power production
    # ========================================================================
    def updatePwr(self, pwr, dt):

        # To help keep Track of plant ramp rate
        powerOutput_old = self.powerOutput

        # Check if power request is within range
        if self.minPowerRequest <= pwr and pwr <= self.capacity:

            # Check if power request is within ramp rate capability
            rampReq = abs(self.powerOutput - pwr)
            rampPossible = self.rampRate * dt
            if rampReq < rampPossible:
                ramp = rampReq
            else:
                ramp = rampPossible

            if debug:
                print("\n UpdatePwr")
                print("Current Power Output   (MW) : " + str(self.powerOutput))
                print("Requested Power Output (MW) : " + str(pwr))
                print("Ramp Rate (MW/min)          : " + str(self.rampRate))
                print("Time Step (min)             : " + str(dt))
                print("Ramp Request (MW/min)       : " + str(rampReq))
                print("Ramp Possible (MW/min)      : " + str(rampPossible))
                print("Actual Ramp (MW/min)        : " + str(ramp))

            # Decrease Production
            if pwr < self.powerOutput:
                self.powerOutput = self.powerOutput - ramp

            # Increase Production
            elif self.powerOutput < pwr:
                self.powerOutput = self.powerOutput + ramp

            if debug:
                print("New Power Output            : " + str(self.powerOutput))

        else:
            print("\nWarning: Power request is out of range")
            print("pwrRequest: " + str(pwr))
            print("Min allowed: " + str(self.minPowerRequest))
            print("Max allowed: " + str(self.capacity))

        self.range = self.powerOutput / self.capacity
        self.efficiency = self.calcEff(self.powerOutput)
        self.heatInput = self.powerOutput / (self.efficiency / 100.0)
        self.powerRamp = (self.powerOutput - powerOutput_old) / dt  # MW/min

    # ========================================================================
    # Method for calculating efficiency at a given power output
    # Does not set efficiency, thus it could be used by a control scheme to determine where to operate
    # ========================================================================
    def calcEff(self, pwr):
        # Calculate where power request falls within operation range
        load_fr = pwr / self.capacity * 100.0

        # Calculate Efficiency, -1 means it is out of range
        if load_fr < self.partLoadRange[0] * 100.0:
            eff = -1
        elif load_fr > self.partLoadRange[1] * 100.0:
            eff = -1
        else:
            eff_fr = self.Eff_A * load_fr ** 2 + self.Eff_B * load_fr + self.Eff_C
            eff = self.maxEfficiency * eff_fr / 100.0

            if debug:
                print("Load Fraction       [%] : " + str(load_fr))
                print("Efficiency Fraction [%] : " + str(eff_fr))
                print("Efficiency          [%] : " + str(eff))

        return eff
