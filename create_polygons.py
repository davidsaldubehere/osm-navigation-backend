from pyrosm import OSM
from pyrosm import get_data
import numpy as np
from scipy.spatial import ConvexHull
from shapely import Polygon
import matplotlib.pyplot as plt
#from kmeans import run_plot
from dbscan import run_plot, run_no_plot
from scipy.ndimage import gaussian_gradient_magnitude
from srtm_lib_area import get_elevation
from skimage.measure import find_contours

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
    
    labels, num_clusters = run_plot(tall_points)
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
#TODO: make sure your eps isnt too high
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
    labels, num_clusters = run_no_plot(points)
    
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

#TODO: The main issue is that the hgt files are not big enough to cover the entire area
#Piece together the hgt files
def create_sharp_elevation_boundary(osm, percentile=90, buffer=.0003):
    roads = osm.get_network(network_type="driving")
    nodes = osm._nodes

    lat_min, lat_max = nodes['lat'].min(), nodes['lat'].max()
    lon_min, lon_max = nodes['lon'].min(), nodes['lon'].max()

    elevation, lon_labels, lat_labels = get_elevation(lat_min, lat_max, lon_min, lon_max)

    #lon and lat labels are the points of elevation data

    plt.imshow(elevation, cmap='terrain', extent=(lon_min, lon_max, lat_min, lat_max))
    plt.colorbar(label='Elevation [m]')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Elevation data')

    gradient_magnitude = gaussian_gradient_magnitude(elevation, sigma=1)

    # Define a threshold for detecting sharp drop-offs
    threshold = np.percentile(gradient_magnitude, percentile)  # Example: top 10% of gradients

    sharp_edges = gradient_magnitude > threshold

    # Find contours in the binary mask
    contours = find_contours(sharp_edges, level=0.5)
    polygons = []
    for contour in contours:
        coords = [(lon_labels[int(p[1])], lat_labels[int(p[0])]) for p in contour]
        polygon = Polygon(coords)
        if polygon.is_valid:
            polygons.append(polygon)
    return polygons