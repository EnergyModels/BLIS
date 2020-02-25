
#BLIS - Balancing Load of Intermittent Solar:

## A characteristic-based transient power plant model

Copyright (C) 2019. University of Virginia Licensing & Ventures Group (UVA LVG). All Rights Reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

Requirements:

	Python 3.7 with the following libraries:
		pandas
		numpy
		joblib
		seaborn
		matplotlib
		time

---

To install:


With git and anaconda 3 installed:
1) Start anaconda 3 terminal\
    Windows: Anaconda Prompt (anaconda3)\
    Linux: start terminal 
    >module load anaconda
2) Change to directory for installation
    > cd directory 
3) Clone to desired directory (if git not installed, download directly from github)
    > git clone https://www.github.com/EnergyModels/blis
4) Move to blis directory
    > cd blis
5) Create and activate environment
    > conda env create\
    > source activate blis-py3
3) Install blis
    > pip install .
 
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
		    
		3) preprocess_solar - supporting scripts which process solar data into a form useable by BLIS
		
	projects
	    3) sCO2_feasibility - scripts and code used for the study "Feasibility of using sCO2 turbines to Balance Load in power grids with a high deployment of solar generation" by Bennett et al., available at https://doi.org/10.1016/j.energy.2019.05.143
		
        4) sCO2_feasibility_results - same as #3, with the results of the simulations provided as .csv files
		
---

Release history: \
- V1.0 - Uses Python 2.7, version used in "Feasibility of using sCO2 turbines to Balance Load in power grids with a high deployment of solar generation" by Bennett et al., available at https://doi.org/10.1016/j.energy.2019.05.143 \
- V2.0.0 - Updated to for Python 3.7 \


Notes:
- To run with SLURM files, replace ncpus = -1 with ncpus = int(os.getenv('NUM_PROCS'))
