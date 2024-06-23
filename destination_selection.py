from pyrosm import OSM
from math import radians, cos, sin, asin, sqrt
from create_polygons import create_water_boundary
from shapely.geometry import Polygon
import geopandas as gpd
import matplotlib.pyplot as plt


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 3956 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r

def get_lookout_points(osm, start, max_distance_threshold=15, min_distance_threshold=1):
    tourist_filter = {"tourism": True}
    tourist_filter = {"tourism": True}
    tourist_spots = osm.get_pois(custom_filter=tourist_filter)
    viewpoints = tourist_spots[tourist_spots['tourism'] == 'viewpoint']
    if len (viewpoints) == 0:
        print("No viewpoints found")
        return []
    #extract the coordinates of the start point
    start_lon = start['geometry'].x
    start_lat = start['geometry'].y

    #we only really want the viewpoints that are within half the straight line distance of the start point
    safe_viewpoints = []
    #print(f'\n\nThe viewpoints are {viewpoints["geometry"]}   \n\n')
    for count, viewpoint in enumerate(viewpoints['geometry']):
        
        #extract the coordinates of the viewpoint
        viewpoint_lon = viewpoint.x
        viewpoint_lat = viewpoint.y
        distance = haversine(start_lon, start_lat, viewpoint_lon, viewpoint_lat)
        print(f'\n\nThe distance is {distance}   \n\n')
        if distance < max_distance_threshold and distance > min_distance_threshold:
            safe_viewpoints.append(viewpoints.iloc[count])
        else:
            print(f'Warning: viewpoint {viewpoints.iloc[count]["name"]} is too far away at {distance} miles')
    return safe_viewpoints

def get_water_points(osm, start, max_distance_threshold=20, min_distance_threshold=1):
    water_areas = create_water_boundary(osm) #get the centroids of the water areas
    if len(water_areas) == 0:
        print("No water areas found")
        return []
    #extract the coordinates of the start point
    start_lon = start['geometry'].x
    start_lat = start['geometry'].y

    #we only really want the water areas that are within half the straight line distance of the start point
    safe_water_areas = []
    for water_area in water_areas:
        #extract the coordinates of the water area
        water_lon = water_area.centroid.x
        water_lat = water_area.centroid.y
        distance = haversine(start_lon, start_lat, water_lon, water_lat)
        if distance < max_distance_threshold and distance > min_distance_threshold:
            safe_water_areas.append(water_area)
    
    if len(safe_water_areas) > 3:
        #we want to keep the top 50% of areas based on area

        #first we need to project the water areas to a metric projection
        # Define a projection (e.g., EPSG:4326 to EPSG:3857)

        #TODO: I am almost 90% sure that this is going to break with different types of bodies of water
        geometries = gpd.GeoSeries(safe_water_areas, crs="EPSG:4326")
        projected_geometry = geometries.to_crs("epsg:4326") #TODO: invesetigate if this is the best projection
        projected_polygons_area = [x.area for x in projected_geometry]


        #sort the areas
        safe_water_areas = [x.centroid for _, x in sorted(zip(projected_polygons_area, safe_water_areas), key=lambda pair: pair[0], reverse=True)]
        safe_water_areas = safe_water_areas[:len(safe_water_areas)//2]
    #THIS ACTUALLY WORKS I TESTED IT
    return safe_water_areas