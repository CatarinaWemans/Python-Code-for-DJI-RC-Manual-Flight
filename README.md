------------------------------------- **PROGRAM FUNCTIONALITIES** -------------------------------------------

**Requisite:** 
1. Create a "local KML file" in Google Earth by drawing a "path" with the desired flight plan. Export as KML;
2. Import the KML file to the RC -> “Mission Flight” - “KML Import” - “Waypoint”;
3. Open the flight plan and define the height/altitude and add a POI if desired. Save it and export.

**What the program does:**
- Prompts the KML file with the waypoints (step 3);
- Changes the gimbal pitch angle for every waypoint at the same time for two different occasions:
  1. A fixed value (prompted by the program);
  2. Different values, calculating the angle for a prompted point of interest (POI).
- Adds the "ShootPhoto" action to every waypoint.

For both cases, the RC only allows you to change each point at a time.

**Note:** If the prompted POI is different from the one originally present in the KML file, it will automatically substitute the prompted one.

--------------------------------------- **PROGRAM LIMITATIONS** ---------------------------------------------

1. The remote’s software creates a wayline that accompanies the waypoints, implying redundancy in the data. If there is a need to change the waypoints' location after this process, it has to be done directly in the remote. Changing it in Google Earth alters the waypoint's coordinates, but the wayline does not follow the altered waypoint, corrupting the KML file;

2. If your POI is situated in a higher plane than the defined flight height, you should acknowledge the DJI specs for your drone's gimbal pitch (GP) angle limitations. The program will accept all positive angles, but most GPs will not physically go past 20 or 30 degrees.
