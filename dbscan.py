import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN

def run_plot(X, eps=.1, min_samples=5):
    # DBSCAN clustering
    dbscan = DBSCAN(eps=eps/6371, min_samples=min_samples, metric='haversine')
    labels = dbscan.fit_predict(np.radians(X))
    num_clusters = len(set(labels))

    # Plotting the results
    plt.scatter(X[:, 0], X[:, 1], c=labels, cmap='viridis', marker='o')
    plt.title('DBSCAN Clustering')
    plt.xlabel('Latitude')
    plt.ylabel('Longitude')
    plt.show()
    return labels, num_clusters

def run_no_plot(X, eps=.1, min_samples=5):
    # DBSCAN clustering with .1 km being the maximum distance between two samples in a cluster and 5 samples being the minimum number of samples in a cluster to not be considered noise
    dbscan = DBSCAN(eps=eps/6371, min_samples=min_samples, metric='haversine')
    labels = dbscan.fit_predict(np.radians(X))
    num_clusters = len(set(labels))
    return labels, num_clusters