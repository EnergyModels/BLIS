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
import pandas as pd

# Data-file details
filename = "PVLibSolarData.csv"
timezone_original = 'UTC'
timezone_new = 'US/Eastern'

# Version details
range1 = ['2017-07-01', '2017-07-31']
range1_name = 'July'
range2 = ['2017-10-30', '2017-10-30']
range2_name = 'Oct30th'

# -----
# Read-in data file
# -----
df = pd.read_csv(filename)

# -----
# Convert timezone
# -----
df.index = pd.to_datetime(df.loc[:, 'DatetimeUTC'])
df.index = df.index.tz_localize(timezone_original)
df.index = df.index.tz_convert(timezone_new)

# -----
# Initial Calculations
# -----
df_out = pd.DataFrame(columns=['dt', 'hour', 'demand', 'solar'])
df_out.index.name = 'Datetime'
df_out['dt'] = df.loc[:, 'dt']
df_out['hour'] = df.index.hour
df_out['demand'] = df.loc[:, 'demand']

for i in range(2):

    # -----
    # Case specific calculations
    # -----
    if i == 0:
        # Case 1 - 1% solar
        case = 'data001'
        df_out['solar'] = df.loc[:, 'UVA_Rooftop']

    else:
        # Case 2 - 63% solar
        case = 'data063'
        df_out['solar'] = df.loc[:, 'Rooftop_and_32MWTracker']

    # A - Entire Timeperiod
    savename = case + '.csv'
    df_out.to_csv(savename, index=False)

    # B - Range1
    savename = case + '_' + range1_name + '.csv'
    df_out[range1[0]:range1[1]].to_csv(savename, index=True)

    # C - Range2
    savename = case + '_' + range2_name + '.csv'
    df_out[range2[0]:range2[1]].to_csv(savename, index=True)
