import numpy as np
import matplotlib.pyplot as plt

# Function to compute the Haversine distance
def haversine_distance(coord1, coord2):
    R = 6371.0  # Earth radius in kilometers

    lat1, lon1 = np.radians(coord1)
    lat2, lon2 = np.radians(coord2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    distance = R * c
    return distance

# Function to initialize centroids using K-means++ algorithm with Haversine distance
def initialize_centroids(X, k):
    centroids = [X[np.random.choice(range(X.shape[0]))]]  # randomly choose the first centroid
    for _ in range(1, k):
        distances = np.min([np.array([haversine_distance(x, centroid) for x in X]) for centroid in centroids], axis=0)
        probabilities = distances / np.sum(distances)
        cumulative_probabilities = np.cumsum(probabilities)
        r = np.random.rand()
        for j, p in enumerate(cumulative_probabilities):
            if r < p:
                centroids.append(X[j])
                break
    return np.array(centroids)

# Function to assign clusters based on the closest centroid using Haversine distance
def assign_clusters(X, centroids):
    distances = np.array([[haversine_distance(x, centroid) for centroid in centroids] for x in X])
    return np.argmin(distances, axis=1)

# Function to update centroids by computing the mean of assigned points
def update_centroids(X, labels, k):
    centroids = []
    for i in range(k):
        cluster_points = X[labels == i]
        if len(cluster_points) == 0:
            centroids.append(X[np.random.choice(range(X.shape[0]))])
        else:
            lat_mean = cluster_points[:, 0].mean()
            lon_mean = cluster_points[:, 1].mean()
            centroids.append([lat_mean, lon_mean])
    return np.array(centroids)

# K-means++ algorithm using Haversine distance
def kmeans_plusplus(X, k, max_iters=100):
    centroids = initialize_centroids(X, k)
    for _ in range(max_iters):
        labels = assign_clusters(X, centroids)
        new_centroids = update_centroids(X, labels, k)
        if np.allclose(centroids, new_centroids, atol=1e-4):
            break
        centroids = new_centroids
    return centroids, labels


# Generating synthetic geographical data for demonstration (latitude, longitude)
#np.random.seed(42)
#X = np.vstack((np.random.randn(100, 2) * 0.1 + np.array([40.0, -100.0]),  # cluster near (40, -100)
#               np.random.randn(100, 2) * 0.1 + np.array([35.0, -80.0]),   # cluster near (35, -80)
#               np.random.randn(100, 2) * 0.1 + np.array([50.0, -90.0])))  # cluster near (50, -90)

# Running K-means++ algorithm
def run_no_plot(X, num_points):

    k = num_points // 50
    return kmeans_plusplus(X, k)

def run_plot(X, num_points):
    k = num_points // 50
    centroids, labels = kmeans_plusplus(X, k)
    # Plotting the results
    plt.scatter(X[:, 0], X[:, 1], c=labels, cmap='viridis', marker='o')
    plt.scatter(centroids[:, 0], centroids[:, 1], c='red', marker='x', s=100)
    plt.title('K-means++ Clustering with Haversine Distance')
    plt.xlabel('Latitude')
    plt.ylabel('Longitude')
    plt.show()
