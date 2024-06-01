from srtm_lib_area import get_elevation
import matplotlib.pyplot as plt
#The downloaded data is off by 1 lol

#print(get_elevation(40.799492, -77.844489))

lat_min, lat_max = 40.7775, 40.7950  # Latitude bounds
lon_min, lon_max = -77.865, -77.835  # Longitude bounds

elevation, lon_labels, lat_labels = get_elevation(lat_min, lat_max, lon_min, lon_max)

#lon and lat labels are the points of elevation data

plt.imshow(elevation, cmap='terrain', extent=(lon_min, lon_max, lat_min, lat_max))
plt.colorbar(label='Elevation [m]')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Elevation data')
plt.show()