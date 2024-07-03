
from pyrosm import OSM
from create_polygons import create_tree_boundary, create_building_boundary, \
    create_water_boundary, create_tall_boundary, create_sharp_elevation_boundary
from shapely.geometry import LineString
from classify_edges import high_speed_limit
import random
from destination_selection import get_lookout_points, get_water_points, get_closest_node, haversine
import numpy as np
import matplotlib.pyplot as plt
#First we get open the OSM data
osm = OSM("state_college.osm.pbf")
#Constant weights

#TRYING A NEW APPROACH WITH PENALTIES INSTEAD OF WEIGHTS
WOODS_WEIGHT = 10
TALL_BUILDINGS_WEIGHT = 10
ALL_BUILDINGS_WEIGHT = 10
WATER_WEIGHT = 10
CLIFF_WEIGHT = 10
HIGH_SPEED_WEIGHT = 10

MAX_DISTANCE_THRESHOLD = 5000
MIN_DISTANCE_THRESHOLD = 3

def process_edges(osm):


    #TODO: make this a preprocess step
    #Next we calculate the corresponding polygons that can be used in the path calculation
    wooded_area = create_tree_boundary(osm)
    tall_buildings = create_tall_boundary(osm)
    all_buildings = create_building_boundary(osm)
    water_area = create_water_boundary(osm)
    cliff_areas = create_sharp_elevation_boundary(osm)
    high_speed_edges = high_speed_limit(osm)
    #Show all the boundaries
    #Next we get the paths
    nodes, edges = osm.get_network(nodes=True, network_type="driving")
    #Print out statistics on the edges length



    edges['user_weight'] = edges['length'].copy()
    #We need to loop through each edge, see if it intersects with any of the polygons and add score accordingly
    #We can use the shapely library to check for intersections

    for i, edge in edges.iterrows():
        edge_coords = LineString(edge['geometry'])
        for polygon in wooded_area:
            if edge_coords.intersects(polygon):
                edges.at[i, 'user_weight'] += WOODS_WEIGHT
        for polygon in tall_buildings:
            if edge_coords.intersects(polygon):
                edges.at[i, 'user_weight'] += TALL_BUILDINGS_WEIGHT
        for polygon in all_buildings:
            if edge_coords.intersects(polygon):
                edges.at[i, 'user_weight'] += ALL_BUILDINGS_WEIGHT
        for polygon in water_area:
            if edge_coords.intersects(polygon):
                edges.at[i, 'user_weight'] += WATER_WEIGHT
        for polygon in cliff_areas:
            if edge_coords.intersects(polygon):
                edges.at[i, 'user_weight'] += CLIFF_WEIGHT
        #TODO: see if there is a better way for getting a unique key
        if edge["geometry"] in high_speed_edges: #We are using geometry as a unique key since no two edges can be at the same locations
            edges.at[i, 'user_weight'] += HIGH_SPEED_WEIGHT

    return nodes, edges

def free_mode(start_location=None):
    #The goal of this mode is to piece together a route from "good" edges and not rely on a destination

    #First I will find cycles that start and end at the start location that are within the distance requirements
    #Then I will just pick a high scoring cycle path

    #That way we only have the process the edges that are within a certain distance radius
    #lets temporarily assume that the start location is a random node

    latitude = start_location[0]
    longitude = start_location[1]

    nodes, edges = osm.get_network(nodes=True, network_type="driving")
    ax = edges.plot(figsize=(6,6), color="gray")
    nodes, edges = process_edges(osm)
    if start_location: #There may be an issue between using sample and get_closest_node
        start_node = get_closest_node(nodes, latitude, longitude)
    else:
        start_node = nodes.sample(1)
    G = osm.to_graph(nodes, edges)

    cycles = []

    def dfs(node, path=[], distance=0, score=0):

        if distance != 0:
            path.append(node)

        #plot the node
        #plt.scatter(vseq[node].attributes()['lon'], vseq[node].attributes()['lat'], color='blue', s=10)
        #plt.pause(0.001)

        if distance > MAX_DISTANCE_THRESHOLD:
            return

        if node == start_node and len(path) > 1:
            if distance < MIN_DISTANCE_THRESHOLD:
                return
            cycles.append((path, score))
            return
        for neighbor in G.neighbors(node, mode='OUT'):
            if neighbor not in path:
                edge = G.es[G.get_eid(node, neighbor)]
                dfs(neighbor, path + [node], distance + edge['length'], score + edge['user_weight'])
    vseq = G.vs

    start_node = vseq.find(id=start_node.id).index

    dfs(start_node)
    print(cycles)

    

    #for cycle in cycles:
    #    #plot cycles
    #    path = cycle[0]
    #    path_coords_lat = np.array([vseq[i].attributes()['lat'] for i in path])
    #    path_coords_lon = np.array([vseq[i].attributes()['lon'] for i in path])
    #    #choose a random color
    #    color = (random.random(), random.random(), random.random())
    #    plt.scatter(path_coords_lon, path_coords_lat, color=color, s=10)

start_location = ( 40.78669, -77.85047)
free_mode(start_location)
