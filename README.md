# Lunar-South-Polar-illumination-maps-
These codes have been created in order to compute solar illumination maps for a research project at the Lunar and Planetary Institute in Houston, TX. This work has implications for permanently shadowed regions (PSRs) scientific studies in the context of the upcoming Artemis III mission. 

These codes has the following characteristics:

1) A Python algorithm has been developed in order to automate the process of making the request, download, and saving the illumination maps from the QuickMap software.
The targeted areas are the 13 NASA selected Candidate Landing Regions (CLR) (https://www.nasa.gov/news-release/nasa-identifies-candidate-regions-for-landing-next-americans-on-moon/) that eventually got reduced to only 9 more recently (October 2024) (https://www.nasa.gov/news-release/nasa-provides-update-on-artemis-iii-moon-landing-regions/) in the south polar region in the Artemis Exploration Zone (AEZ). 

2) Get the illumination map ('S' for Sun in the settings) OR the combining constraint of the Sun + Earth direct view ('S+E' in the code's settings) at a certain time and a certain place on the Moon's surface and save them under a chosen repository. 

2) Compute the average of the illumination maps over the selected time period. The time periods are selected using the 'Compute_SubsolarLat.py' code that highlights the number of consecutive day per year when the Sun has a low enough latitude in order to illuminate the south polar region. For more information check out: https://www.lpi.usra.edu/lunar/tools/lunarseasoncalc/

3) Create a movie of the illumination maps for a cool representation. (see the uploaded example)

4) Keep the georeferencing metadata for each maps so that they can be further used in ARCGis or any other software using GeoTIFF files. 


