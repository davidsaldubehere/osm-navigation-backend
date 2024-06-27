
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
osm = OSM("state_college_large.osm.pbf")
#Constant weights
#Negative is better
WOODS_WEIGHT = -1000
TALL_BUILDINGS_WEIGHT = 1
ALL_BUILDINGS_WEIGHT = 1
WATER_WEIGHT = 1
CLIFF_WEIGHT = 1
HIGH_SPEED_WEIGHT = 1

MAX_DISTANCE_THRESHOLD = 15
MIN_DISTANCE_THRESHOLD = 1

#TODO: rewrite all of this with better searching with hashmaps

def process_edges(osm):


    #TODO: make this a preprocess step
    #Next we calculate the corresponding polygons that can be used in the path calculation
    wooded_area = create_tree_boundary(osm)
    #tall_buildings = create_tall_boundary(osm)
    #all_buildings = create_building_boundary(osm)
    #water_area = create_water_boundary(osm)
    #cliff_areas = create_sharp_elevation_boundary(osm)
    #high_speed_edges = high_speed_limit(osm)
    #Next we get the paths
    nodes, edges = osm.get_network(nodes=True, network_type="driving")
    #Print out statistics on the edges length
    print(edges['length'].describe())



    edges['user_weight'] = edges['length'].copy()
    #We need to loop through each edge, see if it intersects with any of the polygons and add score accordingly
    #We can use the shapely library to check for intersections

    for i in range(len(edges)):
        edge = edges.iloc[i]
        edge_coords = LineString(edge['geometry'])
        for polygon in wooded_area:
            if edge_coords.intersects(polygon):
                edge['user_weight'] += WOODS_WEIGHT
        #for polygon in tall_buildings:
        #    if edge_coords.intersects(polygon):
        #        edge['user_weight'] += TALL_BUILDINGS_WEIGHT
        #for polygon in all_buildings:
        #    if edge_coords.intersects(polygon):
        #        edge['user_weight'] += ALL_BUILDINGS_WEIGHT
        #for polygon in water_area:
        #    if edge_coords.intersects(polygon):
        #        edge['user_weight'] += WATER_WEIGHT
        #for polygon in cliff_areas:
        #    if edge_coords.intersects(polygon):
        #        edge['user_weight'] += CLIFF_WEIGHT
        ##TODO: see if there is a better way for getting a unique key
        #if edge["geometry"] in high_speed_edges: #We are using geometry as a unique key since no two edges can be at the same locations
        #    edge['user_weight'] += HIGH_SPEED_WEIGHT
    return nodes, edges
#TODO: add more options, only lookouts and water are available
def get_destination_nodes(nodes, start_node):
    #The options are random, bodies of water, parks, wooded areas, lookouts, large open areas/fields
    #We can add more options as we see fit
    destination_nodes = []
    for node in get_lookout_points(osm, start_node, 
        MAX_DISTANCE_THRESHOLD, MIN_DISTANCE_THRESHOLD):
        destination_nodes.append(node)
    for node in (get_water_points(osm, start_node,
        MAX_DISTANCE_THRESHOLD, MIN_DISTANCE_THRESHOLD)):
        destination_nodes.append(node)
    
    if len(destination_nodes) == 0: #Untested
        print("No destination nodes found")
        destination = None
        for index in range(len(nodes)):
            node = nodes.iloc[index]
            #see if it's far enough away
            distance = haversine(start_location[0], start_location[1], node.lon, node.lat)
            if distance < MAX_DISTANCE_THRESHOLD and distance > MIN_DISTANCE_THRESHOLD:
                destination_nodes.append(node["geometry"])

    return destination_nodes


#start location will be blank for now since we have no GPS data
def main(start_location=None):
    #lets temporarily assume that the start location is a random node

    latitude = start_location[0]
    longitude = start_location[1]

    nodes, edges = process_edges(osm)
    ax = edges.plot(figsize=(6,6), color="gray")
    if start_location: #There may be an issue between using sample and get_closest_node
        start_node = get_closest_node(nodes, latitude, longitude)
    else:
        start_node = nodes.sample(1)
    destinate_nodes = get_destination_nodes(nodes, start_node)
    #randomly select a destination node

    destination = random.choice(destinate_nodes) #WARNING, THIS POINT MAY NOT BE A VALID ROAD NODE (we will have to find the closest road node)

    #Get the closest node to the destination
    destination = get_closest_node(nodes, destination.y, destination.x)

    #Now we need to find a path from the start node to the destination node
    G = osm.to_graph(nodes, edges)

    #One thing I have noticed is that the geometry of the nodes contains more precision in coordinates than the lat and lon attributes
    #But this is the other way around in the igraph representaion
    vseq = G.vs
    print(f'start node: {start_node}\n\n')
    print(f'destination node: {destination}\n\n')

    #Get the index of the two nodes
    node1_index = vseq.find(id=start_node.id) #Something odd is happening here with smaller maps
    node2_index = vseq.find(id=destination.id)

    #Get the shortest path between the two nodes
    path = G.get_shortest_paths(node1_index, to=node2_index, weights='length', output='vpath')[0]

    #Get the coordinates of the nodes in the shortest path
    path_coords_lat = np.array([vseq[i].attributes()['lat'] for i in path])
    path_coords_lon = np.array([vseq[i].attributes()['lon'] for i in path])

    plt.scatter(path_coords_lon, path_coords_lat, color='green', s=10)
    plt.show()

start_location = (40.798329, -77.859202)
main(start_location)