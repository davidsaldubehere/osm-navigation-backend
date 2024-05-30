from pyrosm import OSM
from pyrosm import get_data
import numpy as np
from scipy.spatial import ConvexHull
from shapely import Polygon
import matplotlib.pyplot as plt
#from kmeans import run_plot
from dbscan import run_plot, run_no_plot

def high_speed_limit(osm, threshold=55):
    