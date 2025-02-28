#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 13:26:39 2024

@author: louis
"""

import numpy as np
import spiceypy.spiceypy as sp
import pandas as pd

#Spice meta-kernel to load all the necessary kernels to use moon ME frame etc  
sp.furnsh("/Users/louis/Desktop/Thèse UCSD/Internships/LPI - Summer 2024/Codes/Sun illumination/spice_data/naif0012.tls")
sp.furnsh("/Users/louis/Desktop/Thèse UCSD/Internships/LPI - Summer 2024/Codes/Sun illumination/spice_data/de441.bsp")
sp.furnsh("/Users/louis/Desktop/Thèse UCSD/Internships/LPI - Summer 2024/Codes/Sun illumination/spice_data/moon_080317.tf")
sp.furnsh("/Users/louis/Desktop/Thèse UCSD/Internships/LPI - Summer 2024/Codes/Sun illumination/spice_data/pck00010.tpc")
sp.furnsh("/Users/louis/Desktop/Thèse UCSD/Internships/LPI - Summer 2024/Codes/Sun illumination/spice_data/moon_pa_de421_1900-2050.bpc")



start_date_UTC = "2035 Jan 01 00:00:00"# Start date in UTC
start_date_ET = sp.str2et(start_date_UTC)

nb_days = 366 #spans the whole year
delta_t = 86400 #86400= 1 day 



end_date_ET = start_date_ET + nb_days * delta_t 
dates_ET = np.linspace(start_date_ET,end_date_ET,nb_days+1)
dates_UTC = sp.et2utc(dates_ET,"C",prec=0)

sub_lat = []
relevant_dates_UTC =[]

for i in range(0,nb_days+1):
    spoint,trgepc,srfvec = sp.subslr("INTERCEPT/ELLIPSOID", "MOON", dates_ET[i], "MOON_ME", "NONE", "MOON")
    r, lon,lat = sp.reclat( srfvec)
    lat_deg = np.rad2deg(lat)
    if lat_deg <= -1.5:
        sub_lat.append(lat_deg)
        relevant_dates_UTC.append(dates_UTC[i])
        


data ={'Dates':relevant_dates_UTC,
       'Subsolar Latitudes': sub_lat}



df = pd.DataFrame(data)
print(df)

