from pyrosm import OSM
from pyrosm import get_data
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import LineString
from create_polygons import create_tree_boundary, create_tall_boundary, create_building_boundary
from classify_edges import high_speed_limit
osm = OSM("state_college_mountains.osm.pbf")

high = high_speed_limit(osm)

high.plot(figsize=(6,6), color="gray")


buildings = create_building_boundary(osm)
for polygon in buildings:
    x,y = polygon.exterior.xy
    plt.plot(x, y)

plt.show()