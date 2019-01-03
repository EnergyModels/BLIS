
#BLIS - Balancing Load of Intermittent Solar:
#A characteristic-based transient power plant model

Copyright (C) 2018. University of Virginia Licensing & Ventures Group (UVA LVG). All Rights Reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

Requirements:

	Python 2.7 with the following libraries:
		pandas
		numpy
		multiprocessing
		joblib
		seaborn
		matplotlib
		time

---

To install:
    1) Git clone to desired directory or download from git website and unzip
    2) Open anaconda2 prompt (or other package manager)
    3) Change directory to within blis folder such that "blis" and "examples" are subdirectories
    4) 'pip install .'
    5) Open an example file and run in a python environment
    
---

File Overview:

	blis:
	    power_plant	- defines PowerPlant class
		fuel - defines class Fuel
		solar - defines class Solar
		storage - defines classes Storage, and Battery
		grid - defines class Grid
		hres - defines HRES (Hybrid Renewable Energy System) class, alternative control schemes are intended to be children of HRES
		     - also defines SBGS (solar-battery-grid system) class

	examples:
		1) hres - hybrid renewable energy system
		    run_single_case 	- demonstration of running a single day using a CCGT with data file data063_Oct30th
		    run_parameter_sweep - demonstration of parameterizing the model using data file data063_Oct30th
		    data063_Oct30th 	- one day of demand and solar data (MW) for Oct 30, 2017    
		
		2) sbgs - solar-battery-grid system
		    same test files as hres, for a different energy system
		    
		3) sCO2_feasibility - coming soon
		
---
