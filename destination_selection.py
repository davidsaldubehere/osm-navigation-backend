from pyrosm import OSM
from math import radians, cos, sin, asin, sqrt
from create_polygons import create_water_boundary
from pyproj import Proj, transform
from shapely.geometry import Polygon

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

def get_lookout_points(osm, start, max_distance_threshold=20, min_distance_threshold=5):
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
    for viewpoint in viewpoints:
        #extract the coordinates of the viewpoint
        viewpoint_lon = viewpoint['geometry'].x
        viewpoint_lat = viewpoint['geometry'].y
        distance = haversine(start_lon, start_lat, viewpoint_lon, viewpoint_lat)
        if distance < max_distance_threshold and distance > min_distance_threshold:
            safe_viewpoints.append(viewpoint)
    return safe_viewpoints

def get_water_points(osm, start, max_distance_threshold=20, min_distance_threshold=5):
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
        proj_wgs84 = Proj(init='epsg:4326')  # WGS84
        proj_meters = Proj(init='epsg:3857')  # Mercator

        # Project the polygon to a planar coordinate system
        projected_polygons_area = [Polygon(
            [transform(proj_wgs84, proj_meters, x, y) for x, y in polygon.exterior.coords]
        ).area for polygon in safe_water_areas]

        #sort the areas
        safe_water_areas = [x.centroid for _, x in sorted(zip(projected_polygons_area, safe_water_areas), key=lambda pair: pair[0], reverse=True)]
        
        #keep the top 50%
        safe_water_areas = safe_water_areas[:len(safe_water_areas)//2]
    
    return safe_water_areas
