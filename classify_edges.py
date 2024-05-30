edge_dict = {}

#TODO: have it basically add the tag high or low to the edge instead of just filtering but we can do that later
#returns edges with a speed limit higher than the threshold
def high_speed_limit(osm, threshold=55):
    # Get the edges of the driving network
    nodes, edges = osm.get_network(nodes=True, network_type="driving")
    # Get the edges with a speed limit higher than the threshold
    #Max speed is formatted weird like 25 mph or None

    high_speed_edges = edges[edges['maxspeed'].apply(lambda x: int(x.split(' ')[0]) if x is not None else 0) >= threshold]
    return high_speed_edges

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
            edge_dict[(u, v)].append(connecting_edge['geometry'])
        except Exception as e:
            print(e)

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
            print(e)
    return edge_dict

#returns the edges that have a sharp turn, same TODO as above
def sharp_turns(osm, threshold = 45):
    #For each edge, get the angle between each of its connecting edges

    #If the sum of angles is above the threshold, then it is a sharp turn
    # Get the edges of the driving network
    nodes, edges = osm.get_network(nodes=True, network_type="driving")
    print(edges)
    print(nodes)
    sharp_turns = []

    