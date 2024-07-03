import numpy as np
from shapely.geometry import LineString


def get_cartesian(lat=None,lon=None):
    lat, lon = np.deg2rad(lat), np.deg2rad(lon)
    R = 6371 # radius of the earth
    x = R * np.cos(lat) * np.cos(lon)
    y = R * np.cos(lat) * np.sin(lon)
    #z = R *np.sin(lat)
    return x,y#,z

edge_dict = {}

#TODO: have it basically add the tag high or low to the edge instead of just filtering but we can do that later
#returns edge ids with a speed limit higher than the threshold
def high_speed_limit(osm, threshold=55):
    # Get the edges of the driving network
    nodes, edges = osm.get_network(nodes=True, network_type="driving")
    # Get the edges with a speed limit higher than the threshold
    #Max speed is formatted weird like 25 mph or None or 'none' for some reason
    high_speed_edges = edges[edges['maxspeed'].apply(lambda x: int(x.split(' ')[0]) if (x is not None and x != "none" ) else 0) >= threshold]
    #return the edge ids
    return set(high_speed_edges['geometry'])

#I guess you could just do it while calculating the edges, but this could be better for a preprocessing step
def preprocess_edges(osm):
    #The issue is that the edge lookup is edge -> node -> edge, and we want to be able to find connecting edges without having to go through the nodes
    #We can do this by creating a dictionary of edges to their connecting edges

    #Get the edges of the driving network
    nodes, edges = osm.get_network(nodes=True, network_type="driving") #returns geo dataframes
    combined = list(zip(edges['u'], edges['v'], edges['geometry']))
    #Create a dictionary of edges to their connecting edges
    edges.set_index('v', inplace=True) #MUCH MUCH faster than using loc
    for i in range(len(combined)):
        
        #Get the nodes that the edge connects
        u = combined[i][0]
        v = combined[i][1]
        geometry = combined[i][2]
        #find the edge with v = node1
        #find the edge with u = node2
        #add the edges to the dictionary
        edge_dict[(u, v, geometry)] = list()
        
        try:
            
            connecting_edge = edges.loc[u]
            edge_dict[(u, v, geometry)].append(connecting_edge['geometry'])
        except Exception as e:
            #print(e)
            pass

    edges.set_index('u', inplace=True)
    for i in range(len(combined)):
        
        #Get the nodes that the edge connects
        v = combined[i][1]
        u = combined[i][0]
        geometry = combined[i][2]

        #find the edge with v = node1
        #find the edge with u = node2
        #add the edges to the dictionary       
            
        try:
            connecting_edge = edges.loc[v]
            edge_dict[(u, v, geometry)].append(connecting_edge['geometry'])
        except Exception as e:
            #print(e)
            pass
    return edge_dict

#returns the edges that have a sharp turn, same TODO as above
#TODO: some weird stuff is happening with geoseries geometry instead of linestring. also there could be like a 4 way intersection that I have to account for
def sharp_turns(osm, threshold = 45):
    #For each edge, get the angle between each of its connecting edges

    #If the sum of angles is above the threshold, then it is a sharp turn
    # Get the edges of the driving network
    nodes, edges = osm.get_network(nodes=True, network_type="driving")

    sharp = []

    
    #We want to loop through the edges and get the connecting edges
    for key in edge_dict.keys():
        if len(edge_dict[key]) != 2 or type(edge_dict[key][0]) != LineString or type(edge_dict[key][1]) != LineString:
            continue
        #Get the angle between the connecting edges
        lat1, lon1 = key[2].coords[0][0], key[2].coords[0][1]
        lat2, lon2 = key[2].coords[-1][0], key[2].coords[-1][1]

        x1, y1 = get_cartesian(lat1, lon1)
        x2, y2 = get_cartesian(lat2, lon2)

        #Do for connecting edges
        clat1, clon1 = edge_dict[key][0].coords[0][0], edge_dict[key][0].coords[0][1]
        clat2, clon2 = edge_dict[key][0].coords[-1][0], edge_dict[key][0].coords[-1][1]

        cx1, cy1 = get_cartesian(clat1, clon1)
        cx2, cy2 = get_cartesian(clat2, clon2)

        dlat1, dlon1 = edge_dict[key][1].coords[0][0], edge_dict[key][1].coords[0][1]
        dlat2, dlon2 = edge_dict[key][1].coords[-1][0], edge_dict[key][1].coords[-1][1]

        dx1, dy1 = get_cartesian(dlat1, dlon1)
        dx2, dy2 = get_cartesian(dlat2, dlon2)

        #Convert to vectors
        a = np.array([x2-x1, y2-y1])
        b = np.array([cx2-cx1, cy2-cy1])
        c = np.array([dx2-dx1, dy2-dy1])

        #Get the angle between the vectors
        angle1 = np.degrees(np.arccos(np.dot(a, b)/(np.linalg.norm(a)*np.linalg.norm(b))))
        angle2 = np.degrees(np.arccos(np.dot(a, c)/(np.linalg.norm(a)*np.linalg.norm(c))))
        if angle1 + angle2 > threshold:
            sharp.append(key[2])
    return sharp