
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
#First we get open the OSM data
osm = OSM("state_college.osm.pbf")
#Constant weights

WOODS_WEIGHT = -10
TALL_BUILDINGS_WEIGHT= 1
ALL_BUILDINGS_WEIGHT = 1
WATER_WEIGHT = 1
CLIFF_WEIGHT = 2
HIGH_SPEED_WEIGHT = 1
LOW_SPEED_WEIGHT = 1 #unused rn

MAX_DISTANCE_THRESHOLD = 30
MIN_DISTANCE_THRESHOLD = .2

#TODO: rewrite all of this with better searching with hashmaps

def process_edges(osm, plot_surface):


    #TODO: make this a preprocess step
    #Next we calculate the corresponding polygons that can be used in the path calculation
    wooded_area = create_tree_boundary(osm)
    cliff_areas = create_sharp_elevation_boundary(osm)

    #Show all the boundaries
    for polygon in wooded_area:
        x,y = polygon.exterior.xy
        plot_surface.plot(x, y, color='red')
    for polygon in cliff_areas:
        x,y = polygon.exterior.xy
        plot_surface.plot(x, y, color='black')

    #add key
    plt.plot([],[], color='red', label='Wooded Area')
    plt.plot([],[], color='black', label='Cliff Area')

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
        for polygon in cliff_areas:
            if edge_coords.intersects(polygon):
                edges.at[i, 'user_weight'] += CLIFF_WEIGHT

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
    node1_index = vseq.find(id=start_node.id) #This doesn't always work for some reason
    node2_index = vseq.find(id=destination.id)

    #Get the shortest path between the two nodes
    #path = G.get_shortest_paths(node1_index, to=node2_index, weights='user_weight', output='vpath')[0]

    #Okay let's instead write a custom shortest path algorithm that doesn't allow for intersections
    #We will use Bellman Ford


    def bellman_modified():
        distances = {}
        previous = {}
        #loop through each vertice and set the distance to infinity
        for vertice in G.vs:
            distances[vertice.index] = float('inf')
            previous[vertice.index] = None
        distances[node1_index.index] = 0

        for vertice in G.vs:
            for edge in G.es:
                if distances[edge.source] + edge['user_weight'] < distances[edge.target] and not check_path_intersection(previous, edge.source, edge.target, node1_index.index):
                    distances[edge.target] = distances[edge.source] + edge['user_weight']
                    previous[edge.target] = edge.source

        return distances, previous
    def check_path_intersection(prev, source, target, start):
        path = set()
        path.add(target)
        while source != start:
            if source in path:
                return True
            source =  prev[source]
        return False
    
    distances, previous = bellman_modified()

    #Get the shortest path
    path = []
    current = node2_index.index
    while current != None:
        path.append(current)
        current = previous[current]

    path = path[::-1]


    #Get the coordinates of the nodes in the shortest path
    path_coords_lat = np.array([vseq[i].attributes()['lat'] for i in path])
    path_coords_lon = np.array([vseq[i].attributes()['lon'] for i in path])

    plt.scatter(path_coords_lon, path_coords_lat, color='green', s=10)
    plt.show()



start_location = ( 40.78669, -77.85047)
destination_mode(start_location)
