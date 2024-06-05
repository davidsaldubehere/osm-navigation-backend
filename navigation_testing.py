from pyrosm import OSM
from pyrosm import get_data
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import LineString
from create_polygons import create_tree_boundary, create_tall_boundary, create_building_boundary

# Initialize the OSM parser object
osm = OSM("state_college_large.osm.pbf")
# Read nodes and edges of the 'driving' network
nodes, edges = osm.get_network(nodes=True, network_type="driving")
# Plot nodes and edges on a map
ax = edges.plot(figsize=(6,6), color="gray")
#ax = nodes.plot(ax=ax, color="red", markersize=2.5)
#print(edges.iloc[:5, -5:])

#Pick two random nodes
node1 = nodes.sample(1)
node2 = nodes.sample(1)

#get the longitude and latitude of the two nodes
node1_lon = node1['lon'].values[0]
node1_lat = node1['lat'].values[0]
node2_lon = node2['lon'].values[0]
node2_lat = node2['lat'].values[0]

plt.scatter(node1_lon, node1_lat, color='red', s=30)
plt.scatter(node2_lon, node2_lat, color='blue', s=30)

G = osm.to_graph(nodes, edges)

vseq = G.vs

#Get the index of the two nodes
node1_index = vseq.find(lon=node1_lon, lat=node1_lat) #Something odd is happening here with smaller maps
node2_index = vseq.find(lon=node2_lon, lat=node2_lat)

#Get the shortest path between the two nodes
path = G.get_shortest_paths(node1_index, to=node2_index, weights='length', output='vpath')[0]

#Get the coordinates of the nodes in the shortest path
path_coords_lat = np.array([vseq[i].attributes()['lat'] for i in path])
path_coords_lon = np.array([vseq[i].attributes()['lon'] for i in path])

plt.scatter(path_coords_lon, path_coords_lat, color='green', s=10)

#get tree polygons
tree_polygons = create_tree_boundary(osm)

for polygon in tree_polygons:
    x,y = polygon.exterior.xy
    #gives the list of x coordinates and a list of y coordinates of the polygon in a tuple with indexes to match points

    plt.plot(x, y)

building_polys = create_tall_boundary(osm)

for polygon in building_polys:
    x,y = polygon.exterior.xy
    plt.plot(x, y)

buildings = create_building_boundary(osm)
for polygon in buildings:
    x,y = polygon.exterior.xy
    plt.plot(x, y)
plt.show()


#Lets see if our route goes through tree areas by checking if each edge of the route intersects with any of the tree polygons


for i in range(len(path)-1):
    x, y = path_coords_lon[i], path_coords_lat[i]
    x2, y2 = path_coords_lon[i+1], path_coords_lat[i+1]
    edge = [(x, y), (x2, y2)]
    line = LineString(edge)
    for polygon in tree_polygons:
        if line.intersects(polygon):
            print("Route goes through a tree area")
            break
        else:
            continue
    else:
        continue



    break

plt.show()