from pyrosm import OSM
from pyrosm import get_data
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import LineString
from create_polygons import create_tree_boundary, create_building_boundary, create_sharp_elevation_boundary
from classify_edges import high_speed_limit, sharp_turns, preprocess_edges
from srtm_lib_area import get_file_name, get_elevation
from destination_selection import get_lookout_points, get_water_points, get_closest_node, get_isolated_points
import random
osm = OSM("state_college_large.osm.pbf")

point = get_isolated_points(osm, 100, 100, 10)

plt.plot(point[0], point[1], 'ro')
plt.show()