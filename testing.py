from pyrosm import OSM
from pyrosm import get_data
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import LineString
from create_polygons import create_tree_boundary, create_building_boundary, create_sharp_elevation_boundary
from classify_edges import high_speed_limit, sharp_turns, preprocess_edges
from srtm_lib_area import get_file_name, get_elevation
from destination_selection import get_lookout_points, get_water_points
import random
osm = OSM("state_college_large.osm.pbf")

nodes, edges = osm.get_network(nodes=True, network_type="driving")

#Randomly choose a start
start_node = nodes.sample(1)
print(f'Start node is {start_node["geometry"]}')

result = get_lookout_points(osm, start_node)
for i in result:
    print(f'Viewpoint {i["name"]} is at {i["geometry"]}')