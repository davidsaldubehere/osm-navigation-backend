
from pyrosm import OSM
from create_polygons import create_tree_boundary, create_building_boundary, \
    create_water_boundary, create_tall_boundary, create_sharp_elevation_boundary
from shapely.geometry import LineString
from classify_edges import high_speed_limit
import random
from destination_selection import get_lookout_points, get_water_points, get_closest_node, haversine
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import path_finding # type: ignore
#First we get open the OSM data
osm = OSM("lewistown.osm.pbf")

nodes, edges = osm.get_network(nodes=True, network_type="driving")

edges.plot()

edges_no_access = edges[edges['access'].apply(lambda x: x is not None and x in ['no', 'private'])]

for edge in edges_no_access['geometry']:
    x,y = edge.xy
    plt.plot(x, y, color='red')

plt.show()