from pyrosm import OSM
from pyrosm import get_data
import numpy as np
from scipy.spatial import ConvexHull
from shapely import Polygon
import matplotlib.pyplot as plt
#from kmeans import run_plot
from dbscan import run_plot, run_no_plot
# Initialize the OSM parser object


#TODO: we need more types of greenery to include
def create_tree_boundary(osm, buffer = .0003):
    boundaries = []
    natural = osm.get_natural()
    # We need wood and tree
    #filter out all rows that are not trees or wood
    natural = natural[natural['natural'].isin(['tree', 'wood'])]
    tree_polys = natural[natural['geometry'].apply(lambda x: x.geom_type) == 'Polygon']['geometry']

    #The issue is that the trees are not in a single polygon
    #We need to create clusters first and then create a polygon around the clusters
    #We can use some sort of algorithm to get the shell of the clusters

    #first we will get the coordinates of the trees
    tree_points = natural[natural['geometry'].apply(lambda x: x.geom_type) == 'Point']['geometry']
    tree_coords = np.vstack([np.array([point.x, point.y]) for point in tree_points])
    labels, num_clusters = run_no_plot(tree_coords)
        # Extracting points for each cluster
    clusters = []
    for label in np.unique(labels):
        if label == -1:
            continue  # Skip noise points
        cluster_points = tree_coords[labels == label]
        clusters.append(cluster_points)

    # Computing convex hull for each cluster
    convex_hulls = []
    for cluster_points in clusters:
        hull = ConvexHull(cluster_points)
        convex_hulls.append(hull)

        # Convert convex hulls to Shapely polygons
    # Convert convex hulls to Shapely polygons
    shapely_polygons = []
    for hull in convex_hulls:
        vertices = hull.points[hull.vertices]
        polygon = Polygon(vertices)
        polygon = polygon.buffer(buffer) # Buffer the polygon slightly
        shapely_polygons.append(polygon)

    #we also need to buffer the tree polygons
    tree_polys = [poly.buffer(buffer) for poly in tree_polys]

    #plot the polygons
    #for polygon in shapely_polygons:
    #    x,y = polygon.exterior.xy
    #    plt.plot(x, y)
    #plt.show()
    return shapely_polygons+ tree_polys

#TODO: Combine this method with the create_building_boundary method
#TODO: make sure your eps isnt too high
def create_tall_boundary(osm, threshold=10):
    buildings = osm.get_buildings()

    #First lets make sure height is a column (sparse areas may not have height)

    if 'height' not in buildings.columns:
        return []

    tall = buildings['height'].astype(float) > threshold
    #get the indices of the tall buildings
    tall_indices = buildings[tall].index
    tall = buildings.loc[tall_indices]
    tall_polys = tall[tall['geometry'].apply(lambda x: x.geom_type) == 'Polygon']['geometry'] #should be all polygons but just a precaution
    #get the points of each tall building polygon
    tall_points = [poly.exterior.xy for poly in tall_polys]

    #Has a really weird format with a list of tuples of two arrays
    x_points, y_points = [], []
    for tuple_thing in tall_points:
        x,y = tuple_thing
        x_points.extend(x)
        y_points.extend(y)

    tall_points = np.vstack(list(zip(x_points, y_points)))
    
    labels, num_clusters = run_no_plot(tall_points)
    # Extracting points for each cluster
    clusters = []
    for label in np.unique(labels):
        if label == -1:
            continue  # Skip noise points
        cluster_points = tall_points[labels == label]
        clusters.append(cluster_points)
    
    # Computing convex hull for each cluster
    convex_hulls = []
    for cluster_points in clusters:
        hull = ConvexHull(cluster_points)
        convex_hulls.append(hull)
    # Convert convex hulls to Shapely polygons
    shapely_polygons = []
    for hull in convex_hulls:
        vertices = hull.points[hull.vertices]
        polygon = Polygon(vertices)
        shapely_polygons.append(polygon)
    return shapely_polygons

def create_building_boundary(osm, buffer=.0003):

    #get the number of buildings, cluster the buildings, then get convex hull of isolated areas without buildings
    buildings = osm.get_buildings()
    polys = buildings[buildings['geometry'].apply(lambda x: x.geom_type) == 'Polygon']['geometry'] #should be all polygons but just a precaution
    points = [poly.exterior.xy for poly in polys]

    #Has a really weird format with a list of tuples of two arrays
    x_points, y_points = [], []
    for tuple_thing in points:
        x,y = tuple_thing
        x_points.extend(x)
        y_points.extend(y)

    points = np.vstack(list(zip(x_points, y_points)))
    labels, num_clusters = run_plot(points, eps=.01)
    
    # Extracting points for each cluster
    clusters = []
    for label in np.unique(labels):
        if label == -1:
            continue  # Skip noise points
        cluster_points = points[labels == label]
        clusters.append(cluster_points)
    
    # Computing convex hull for each cluster
    convex_hulls = []
    for cluster_points in clusters:
        hull = ConvexHull(cluster_points)
        convex_hulls.append(hull)
    # Convert convex hulls to Shapely polygons
    shapely_polygons = []
    for hull in convex_hulls:
        vertices = hull.points[hull.vertices]
        polygon = Polygon(vertices)
        shapely_polygons.append(polygon)
    return shapely_polygons