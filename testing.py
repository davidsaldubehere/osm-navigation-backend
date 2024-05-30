from pyrosm import OSM
from pyrosm import get_data
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import LineString
from create_polygons import create_tree_boundary, create_tall_boundary, create_building_boundary
osm = OSM("state_college_mountains.osm.pbf")



buildings = create_building_boundary(osm)
for polygon in buildings:
    x,y = polygon.exterior.xy
    plt.plot(x, y)

plt.show()