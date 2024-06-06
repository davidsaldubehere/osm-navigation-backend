from srtm_lib_area import get_elevation
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_gradient_magnitude
import numpy as np
from skimage.measure import find_contours
from shapely.geometry import Polygon
#The downloaded data is off by 1 lol

#Also min is bottom left, max is top right (unless you are in the southern hemisphere)

lat_min, lat_max = 37.095, 37.578 # Latitude bounds
lon_min, lon_max = -122.667, -122.200  # Longitude bounds

elevation, lon_labels, lat_labels = get_elevation(lat_min, lat_max, lon_min, lon_max)
#lon and lat labels are the points of elevation data

plt.imshow(elevation, cmap='terrain', extent=(lon_min, lon_max, lat_min, lat_max))
plt.colorbar(label='Elevation [m]')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Elevation data')

gradient_magnitude = gaussian_gradient_magnitude(elevation, sigma=1)
# Define a threshold for detecting sharp drop-offs
threshold = np.percentile(gradient_magnitude, 90)  # Example: top 10% of gradients

sharp_edges = gradient_magnitude > threshold

# Find contours in the binary mask
contours = find_contours(sharp_edges, level=0.5)
polygons = []
for contour in contours:
    coords = [(lon_labels[int(p[1])], lat_labels[int(p[0])]) for p in contour]
    polygon = Polygon(coords)
    if polygon.is_valid:
        polygons.append(polygon)

for polygon in polygons:
    x,y = polygon.exterior.xy
    #gives the list of x coordinates and a list of y coordinates of the polygon in a tuple with indexes to match points

    plt.plot(x, y)

plt.show()