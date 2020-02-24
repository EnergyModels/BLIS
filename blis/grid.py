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
import numpy as np


# ========================================================================
# Class to hold details of the grid (default is it does not have any capacity, to align with V1_00 which did not have this feature)
# ========================================================================
class Grid:

    # ----------
    # Instantiate
    # ----------
    def __init__(self, capacity=0.0, maxEmissions=0.5, emissionCurve_hr=np.linspace(1, 24, 24),
                 emissionCurve_pct=np.linspace(100, 100, 24), cost_OM_var=100.0):
        # Capacity
        self.capacity = capacity  # (MW)

        # Emissions:
        self.maxEmissions = maxEmissions  # CO2 emissions [tons] per MWh electric
        self.emissionCurve_hr = emissionCurve_hr  # ($/kW/year)
        self.emissionCurve_pct = emissionCurve_pct  # ($/MWh)

        # Costs:
        self.cost_OM_var = cost_OM_var  # ($/MWh)

    # ----------
    # Get current emission factor
    # ----------
    def getEmissions(self, datetimeUTC):
        # Calculate current emission factor based on datetimeUTC
        emissions = self.maxEmissions

        # Convert from (tons/MWh) to (tons/MW-min)
        emissions = emissions

        return emissions  # tons per MW-min electric
