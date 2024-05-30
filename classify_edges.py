from pyrosm import OSM
from pyrosm import get_data
import numpy as np
from scipy.spatial import ConvexHull
from shapely import Polygon
import matplotlib.pyplot as plt
#from kmeans import run_plot
from dbscan import run_plot, run_no_plot

#returns edges with a speed limit higher than the threshold
def high_speed_limit(osm, threshold=55):
    # Get the edges of the driving network
    nodes, edges = osm.get_network(nodes=True, network_type="driving")
    # Get the edges with a speed limit higher than the threshold
    #Max speed is formatted weird like 25 mph or None

    high_speed_edges = edges[edges['maxspeed'].apply(lambda x: int(x.split(' ')[0]) if x is not None else 0) >= threshold]
    return high_speed_edges