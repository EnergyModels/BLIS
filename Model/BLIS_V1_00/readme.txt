#========================================================================
BLIS - Balancing Load of Intermittent Solar:
A characteristic-based transient power plant model

Copyright (C) 2018. University of Virginia Licensing & Ventures Group (UVA LVG). All Rights Reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#========================================================================
BLIS Version 1.00

Requirements:

	Python 2.7 with the following libraries:
		pandas
		numpy
		multiprocessing
		joblib
		seaborn
		matplotlib
		time

File Overview:
	Core software of BLIS:
		PowerPlant			- defines PowerPlant class
		Components			- defines classes Solar, Fuel, Storage, Battery
		HRES 				- defines HRES (Hybrid Renewable Energy System) class, alternative control schemes are intended to be children of HRES

	Examples:
		Run_SingleCase 			- demonstration of running a single day using a CCGT with data file data063_Oct30th
		Run_ParameterSweep         	- demonstration of parameterizing the model using data file data063_Oct30th
		data063_Oct30th 		- one day of demand and solar data (MW) for Oct 30, 2017
#========================================================================