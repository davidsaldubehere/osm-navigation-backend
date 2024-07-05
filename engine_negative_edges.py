
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
osm = OSM("state_college_mountains.osm.pbf") #for some reason it isn't working with the other file
#Constant weights

WOODS_WEIGHT = -5 #anything more and the results get very skewed
TALL_BUILDINGS_WEIGHT= 0
ALL_BUILDINGS_WEIGHT = 0
WATER_WEIGHT = 1
CLIFF_WEIGHT = 1
HIGH_SPEED_WEIGHT = 1
LOW_SPEED_WEIGHT = 1 #unused rn

MAX_DISTANCE_THRESHOLD = 1.5
MIN_DISTANCE_THRESHOLD = .6

#TODO: rewrite all of this with better searching with hashmaps

def process_edges(osm, plot_surface):


    #TODO: make this a preprocess step
    #Next we calculate the corresponding polygons that can be used in the path calculation

    #Preprocessing time doesn't matter, the shortest path does though
    wooded_area = create_tree_boundary(osm)

    #Show all the boundaries
    for polygon in wooded_area:
        x,y = polygon.exterior.xy
        plot_surface.plot(x, y, color='red')

    #add key
    plt.plot([],[], color='red', label='Wooded Area')

    plt.legend()


    #Next we get the paths
    nodes, edges = osm.get_network(nodes=True, network_type="driving")
    #Print out statistics on the edges length
    print(edges['length'].describe())



    #Create a column of zeros for the user weight
    edges['user_weight'] = edges['length'].copy() * .1

    #We need to loop through each edge, see if it intersects with any of the polygons and add score accordingly
    #We can use the shapely library to check for intersections

    for i, edge in edges.iterrows():
        edge_coords = LineString(edge['geometry'])
        for polygon in wooded_area:
            if edge_coords.intersects(polygon):
                edges.at[i, 'user_weight'] += WOODS_WEIGHT
    print(edges['user_weight'].describe())
    return nodes, edges
#TODO: add more options, only lookouts and water are available (we have a lot more work to do with this)

#TODO: We had some weird error where a Series object popped up in the destination nodes?? check this
#I think has something to do with the toursist node things
def get_destination_nodes(nodes, start_node):
    #The options are random, bodies of water, parks, wooded areas, lookouts, large open areas/fields
    #We can add more options as we see fit
    destination_nodes = []
    
    if len(destination_nodes) == 0: #Untested
        print("No prime destination nodes found, defaulting to all nodes")
        for index in range(len(nodes)):
            node = nodes.iloc[index]
            #see if it's far enough away
            distance = haversine(start_location[1], start_location[0], node.lon, node.lat)
            if distance < MAX_DISTANCE_THRESHOLD and distance > MIN_DISTANCE_THRESHOLD:
                destination_nodes.append(node["geometry"])
        if len(destination_nodes) == 0:
            print("CRITICAL ERROR: No destination nodes found")

    return destination_nodes


#start location will be blank for now since we have no GPS data
def destination_mode(start_location=None):
    #lets temporarily assume that the start location is a random node

    latitude = start_location[0]
    longitude = start_location[1]

    nodes, edges = osm.get_network(nodes=True, network_type="driving")
    ax = edges.plot(figsize=(6,6), color="gray")
    nodes, edges = process_edges(osm, ax)
    G = osm.to_graph(nodes, edges)
    #For some reason converting to a graph looses some nodes so lets get the nodes again
    nodes = pd.DataFrame([node.attributes() for node in G.vs])

    if start_location: #There may be an issue between using sample and get_closest_node
        start_node = get_closest_node(nodes, latitude, longitude)
    else:
        start_node = nodes.sample(1)
    destinate_nodes = get_destination_nodes(nodes, start_node)
    #randomly select a destination node
    try:
        destination = random.choice(destinate_nodes)
        destination = get_closest_node(nodes, destination.y, destination.x)

    except:
        print("ERROR WE HAVE A WEIRD TYPE THING GOING ON")
        print(destinate_nodes)
        destination = random.choice(destinate_nodes)
        destination = get_closest_node(nodes, destination.y, destination.x)

    #Now we need to find a path from the start node to the destination node
    

    #One thing I have noticed is that the geometry of the nodes contains more precision in coordinates than the lat and lon attributes
    #But this is the other way around in the igraph representaion
    vseq = G.vs

    #print(f'start node: {start_node}\n\n')
    #print(f'destination node: {destination}\n\n')

    #Get the index of the two nodes
    node1_index = vseq.find(id=start_node.id)
    node2_index = vseq.find(id=destination.id)

    #Get the shortest path between the two nodes
    #path = G.get_shortest_paths(node1_index, to=node2_index, weights='user_weight', output='vpath')[0]

    #Okay let's instead write a custom shortest path algorithm that doesn't allow for intersections
    #We will use Bellman Ford

    #We need to convert the edges to a list like [[sourceindex, endindex, weight], []...]

    edge_list = [[float(edge.source), float(edge.target), edge['user_weight']] for edge in G.es]

    #TODO: move the path calculation to the C extension

    print("starting path calculation")
    path1 = path_finding.bellman_ford_no_interesections(edge_list, len(vseq), node1_index.index, node2_index.index)

    print("finished path calculation")

    #Get the coordinates of the nodes in the shortest path
    path_coords_lat = np.array([vseq[i].attributes()['lat'] for i in path1])
    path_coords_lon = np.array([vseq[i].attributes()['lon'] for i in path1])

    plt.scatter(path_coords_lon, path_coords_lat, color='green', s=10)

    #Regular path
    path = G.get_shortest_paths(node1_index, to=node2_index, weights='length', output='vpath')[0]
    path_coords_lat = np.array([vseq[i].attributes()['lat'] for i in path])
    path_coords_lon = np.array([vseq[i].attributes()['lon'] for i in path])

    plt.scatter(path_coords_lon, path_coords_lat, color='blue', s=10)
    plt.show()



start_location = ( 40.78669, -77.85047)
destination_mode(start_location)
