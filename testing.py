from pyrosm import OSM
from pyrosm import get_data
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import LineString
from create_polygons import create_tree_boundary, create_building_boundary, create_sharp_elevation_boundary
from classify_edges import high_speed_limit, sharp_turns, preprocess_edges
from srtm_lib_area import get_file_name, get_elevation
osm = OSM("state_college_mountains.osm.pbf")

#high = high_speed_limit(osm)

#high.plot(figsize=(6,6), color="gray")



#edges = preprocess_edges(osm)
#sharp = sharp_turns(osm, threshold=45)
#So we have a list of linestrings
#We can plot them
#for line in sharp:
#    x,y = line.xy
#    plt.plot(x, y)

#buildings = create_building_boundary(osm)
#for polygon in buildings:
#    x,y = polygon.exterior.xy
    #plt.plot(x, y)
39.516849, -77.263645

40.894421, -74.032337


lat_min, lat_max = 39.1, 40.99999  # Latitude bounds
lon_min, lon_max = -78.99999, -78  # Longitude bounds

#print(get_file_name(lat_min, lon_min, lat_max, lon_max))

elevation, lon_labels, lat_labels = get_elevation(lat_min, lat_max, lon_min, lon_max)
print(elevation.shape)

#plot the elevation data as heat map
plt.imshow(elevation, cmap='terrain', extent=(lon_min, lon_max, lat_min, lat_max))
plt.colorbar(label='Elevation [m]')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Elevation data')
plt.show()