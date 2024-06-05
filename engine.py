
from pyrosm import OSM
from create_polygons import create_tree_boundary, create_building_boundary, \
    create_water_boundary, create_tall_boundary, create_sharp_elevation_boundary
from shapely.geometry import LineString
from classify_edges import high_speed_limit
import random
#First we get open the OSM data
osm = OSM("state_college_large.osm.pbf")
#Constant weights
WOODS_WEIGHT = 1
TALL_BUILDINGS_WEIGHT = 1
ALL_BUILDINGS_WEIGHT = 1
WATER_WEIGHT = 1
CLIFF_WEIGHT = 1
HIGH_SPEED_WEIGHT = 1
def process_edges(osm):


    #TODO: make this a preprocess step
    #Next we calculate the corresponding polygons that can be used in the path calculation
    wooded_area = create_tree_boundary(osm)
    tall_buildings = create_tall_boundary(osm)
    all_buildings = create_building_boundary(osm)
    water_area = create_water_boundary(osm)
    cliff_areas = create_sharp_elevation_boundary(osm)
    high_speed_edges = high_speed_limit(osm)
    #Next we get the paths
    nodes, edges = osm.get_network(nodes=True, network_type="driving")
    edges['user_weight'] = edges['length'].copy()
    print(edges['user_weight'])
    #We need to loop through each edge, see if it intersects with any of the polygons and add score accordingly
    #We can use the shapely library to check for intersections

    for i in range(len(edges)):
        edge = edges.iloc[i]
        edge_coords = LineString(edge['geometry'])
        for polygon in wooded_area:
            if edge_coords.intersects(polygon):
                edge['user_weight'] += WOODS_WEIGHT
                print(f'edge {i} intersects wooded area')
        for polygon in tall_buildings:
            if edge_coords.intersects(polygon):
                edge['user_weight'] += TALL_BUILDINGS_WEIGHT
                print(f'edge {i} intersects tall buildings')
        for polygon in all_buildings:
            if edge_coords.intersects(polygon):
                edge['user_weight'] += ALL_BUILDINGS_WEIGHT
                print(f'edge {i} intersects all buildings')
        for polygon in water_area:
            if edge_coords.intersects(polygon):
                edge['user_weight'] += WATER_WEIGHT
                print(f'edge {i} intersects water area')
        for polygon in cliff_areas:
            if edge_coords.intersects(polygon):
                edge['user_weight'] += CLIFF_WEIGHT
                print(f'edge {i} intersects cliff area')
        if edge in high_speed_edges:
            edge['user_weight'] += HIGH_SPEED_WEIGHT
            print(f'edge {i} is a high speed edge')
    return nodes, edges

def get_destination_nodes(nodes):
    #So we either pick some body of water, some viewpoint, or some large field or park
    pass

def main(start_location):
    nodes, edges = process_edges(osm)
    destinate_nodes = get_destination_nodes(nodes)
    #randomly select a destination node
    destination = random.choice(destinate_nodes)
    #Lets find the closest node to the start location
