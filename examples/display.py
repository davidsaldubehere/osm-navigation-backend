from pyrosm import OSM
from pyrosm import get_data
import matplotlib.pyplot as plt


# Initialize the OSM parser object
osm = OSM("state_college_large.osm.pbf")
natural = osm.get_natural()
roads = osm.get_network(network_type="driving")
buildings = osm.get_buildings()
landuse = osm.get_landuse()
tourist_filter = {"tourism": True}
tourist_spots = osm.get_pois(custom_filter=tourist_filter)
viewpoints = tourist_spots[tourist_spots['tourism'] == 'viewpoint']

if viewpoints.empty:
    print("No viewpoints found")
else:

    viewpoints.plot(column='name', legend=True, figsize=(10,6))



landuse.plot(column='landuse', legend=True, figsize=(10,6))
buildings.plot(column="building", figsize=(10,6), legend=True, legend_kwds=dict(loc='upper left', ncol=2, bbox_to_anchor=(1, 1)))
natural.plot(column='natural', legend=True, figsize=(10,6))
roads.plot(column='highway', legend=True, figsize=(10,6))

plt.show()