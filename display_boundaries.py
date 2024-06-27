from pyrosm import OSM
from create_polygons import create_tree_boundary, create_building_boundary, \
    create_water_boundary, create_tall_boundary, create_sharp_elevation_boundary
from shapely.geometry import LineString
from classify_edges import high_speed_limit
import random
from destination_selection import get_lookout_points, get_water_points, get_closest_node, haversine
import numpy as np
import matplotlib.pyplot as plt

osm = OSM("state_college_large.osm.pbf")
wooded_area = create_tree_boundary(osm)
tall_buildings = create_tall_boundary(osm)
all_buildings = create_building_boundary(osm)
water_area = create_water_boundary(osm)
cliff_areas = create_sharp_elevation_boundary(osm)
high_speed_edges = high_speed_limit(osm)

#Show all the boundaries
fig, ax = plt.subplots()
for polygon in wooded_area:
    x,y = polygon.exterior.xy
    ax.plot(x, y, color='green')
for polygon in tall_buildings:
    x,y = polygon.exterior.xy
    ax.plot(x, y, color='red')
for polygon in all_buildings:
    x,y = polygon.exterior.xy
    ax.plot(x, y, color='blue')
for polygon in water_area:
    x,y = polygon.exterior.xy
    ax.plot(x, y, color='orange')
for polygon in cliff_areas:
    x,y = polygon.exterior.xy
    ax.plot(x, y, color='black')
for edge in high_speed_edges:
    x,y = edge.xy
    ax.plot(x, y, color='purple')

#add key
ax.plot([],[], color='green', label='Wooded Area')
ax.plot([],[], color='red', label='Tall Buildings')
ax.plot([],[], color='blue', label='All Buildings')
ax.plot([],[], color='orange', label='Water Area')
ax.plot([],[], color='black', label='Cliff Area')
ax.plot([],[], color='purple', label='High Speed Limit')
ax.legend()
plt.show()