from pyrosm import OSM
from pyrosm import get_data
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import LineString
from create_polygons import create_tree_boundary, create_building_boundary
from classify_edges import high_speed_limit, sharp_turns, preprocess_edges
osm = OSM("nyc.osm.pbf")

#high = high_speed_limit(osm)

#high.plot(figsize=(6,6), color="gray")



#edges = preprocess_edges(osm)
#sharp = sharp_turns(osm, threshold=45)
#So we have a list of linestrings
#We can plot them
#for line in sharp:
#    x,y = line.xy
#    plt.plot(x, y)

buildings = create_building_boundary(osm)
for polygon in buildings:
    x,y = polygon.exterior.xy
    #plt.plot(x, y)

plt.show()