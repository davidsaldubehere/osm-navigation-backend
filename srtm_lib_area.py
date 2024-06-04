from __future__ import print_function
import os
import numpy as np
from math import floor, ceil
SRTM_DICT = {'SRTM1': 3601, 'SRTM3': 1201}

# Get the type of SRTM files or use SRTM1 by default
SRTM_TYPE = os.getenv('SRTM_TYPE', 'SRTM1')
SAMPLES = SRTM_DICT[SRTM_TYPE]

# put uncompressed hgt files in HGT_DIR, defaults to 'hgt'
HGTDIR = os.getenv('HGT_DIR', 'hgt')


def get_elevation(min_lat, max_lat, min_lon, max_lon):
    hgt_files, directions = get_file_name(min_lat, min_lon, max_lat, max_lon)
    if len(hgt_files)==1:
        return read_elevation_from_file(hgt_files[0], min_lat, min_lon, max_lat, max_lon)
    elif len(hgt_files) > 1:
        return read_elevations_from_files(hgt_files, min_lat, min_lon, max_lat, max_lon, directions)
    # Treat it as data void as in SRTM documentation
    # if file is absent
    return -32768

def read_elevations_from_files(hgt_files, min_lat, min_lon, max_lat, max_lon, directions):
    elevation_data = None
    for count, file_name in enumerate(hgt_files):
        with open(file_name, 'rb') as hgt_data:
            
            elevations = np.fromfile(
                hgt_data,  # binary data
                np.dtype('>i2'),  # data type
                SAMPLES * SAMPLES  # length
            ).reshape((SAMPLES, SAMPLES))

        if directions[count] != "START":
            if directions[count] == 'VERTICAL':
                elevation_data = np.vstack((elevation_data, elevations))
            elif directions[count] == 'HORIZONTAL':
                elevation_data = np.hstack((elevation_data, elevations))
        else:
            elevation_data = elevations

        # Define the target shape

    #TODO: Find a better way to make it a square again (Probably will have to make verticle strips and then hstack them)
    # Calculate the number of columns needed to reach 1000 columns
    num_dummy_columns = SAMPLES*len(hgt_files) - elevation_data.shape[1]

    # Create a 1000x800 array of dummy values (e.g., zeros)
    dummy_values = np.zeros((SAMPLES*len(hgt_files), num_dummy_columns))

    # Horizontally stack the original array with the dummy values
    elevation_data = np.hstack((elevation_data, dummy_values))


    min_lat_row = int(round((min_lat - int(min_lat)) * (SAMPLES*len(hgt_files) - 1), 0))
    min_lon_row = int(round((min_lon - int(min_lon)) * (SAMPLES*len(hgt_files) - 1), 0))
    max_lat_row = int(round((max_lat - int(max_lat)) * (SAMPLES*len(hgt_files) - 1), 0))
    max_lon_row = int(round((max_lon - int(max_lon)) * (SAMPLES*len(hgt_files) - 1), 0))

    #we have to invert the latitude indexes because latitude increases as we go up
    #but the hgt file has the latitude increasing as we go down

    min_lat_row, max_lat_row = SAMPLES - 1 - max_lat_row, SAMPLES - 1 - min_lat_row + 1
    elevation_subset = elevations[min_lat_row:max_lat_row, min_lon_row:max_lon_row + 1]
    lon_vals = np.linspace(min_lon, max_lon, elevation_subset.shape[1])
    lat_vals = np.linspace(max_lat, min_lat, elevation_subset.shape[0])
    return elevation_data[min_lat_row:max_lat_row, min_lon_row:max_lon_row].astype(int), lon_vals, lat_vals
    
            



def read_elevation_from_file(hgt_file, min_lat, min_lon, max_lat, max_lon):
    with open(hgt_file, 'rb') as hgt_data:
        # HGT is 16bit signed integer(i2) - big endian(>)
        elevations = np.fromfile(
            hgt_data,  # binary data
            np.dtype('>i2'),  # data type
            SAMPLES * SAMPLES  # length
        ).reshape((SAMPLES, SAMPLES))
        min_lat_row = int(round((min_lat - int(min_lat)) * (SAMPLES - 1), 0))
        min_lon_row = int(round((min_lon - int(min_lon)) * (SAMPLES - 1), 0))
        max_lat_row = int(round((max_lat - int(max_lat)) * (SAMPLES - 1), 0))
        max_lon_row = int(round((max_lon - int(max_lon)) * (SAMPLES - 1), 0))


        #we have to invert the latitude indexes because latitude increases as we go up
        #but the hgt file has the latitude increasing as we go down
        min_lat_row, max_lat_row = SAMPLES - 1 - max_lat_row, SAMPLES - 1 - min_lat_row + 1

        elevation_subset = elevations[min_lat_row:max_lat_row, min_lon_row:max_lon_row + 1]

        lon_vals = np.linspace(min_lon, max_lon, elevation_subset.shape[1])
        lat_vals = np.linspace(max_lat, min_lat, elevation_subset.shape[0])

        return elevations[min_lat_row:max_lat_row, min_lon_row:max_lon_row].astype(int), lon_vals, lat_vals


        #return elevations[SAMPLES - 1 - lat_row, lon_row].astype(int)
#TODO: If it crosses hemispheres, this will not work
def get_file_name(min_lat, min_lon, max_lat, max_lon):
    """
    Returns filename such as N27E086.hgt, concatenated
    with HGTDIR where these 'hgt' files are kept
    """
    if min_lat >= 0:
        ns = 'N'
    elif min_lat < 0:
        ns = 'S'

    if min_lon >= 0:
        ew = 'E'
    elif min_lon < 0:
        ew = 'W'

    if max_lat >= 0:
        ns_1 = 'N'
    elif max_lat < 0:
        ns_1 = 'S'
    
    if max_lon >= 0:
        ew_1 = 'E'
    elif max_lon < 0:
        ew_1 = 'W'

    hgt_file = "%(ns)s%(lat)02d%(ew)s%(lon)03d.hgt" % \
               {'lat': abs(min_lat), 'lon': abs(min_lon), 'ns': ns, 'ew': ew}
    
    
    hgt_file_1 = "%(ns)s%(lat)02d%(ew)s%(lon)03d.hgt" % \
               {'lat': abs(max_lat), 'lon': abs(max_lon), 'ns': ns_1, 'ew': ew_1}
    
    if hgt_file != hgt_file_1:
        directions = ['START'] #We need this data in order to know how to concatenate the elevation data
        #We need to calculate the necessary files to read
        if int(min_lat) != int(max_lat):
            lats_to_read = list(range(int(min_lat), int(max_lat) + 1)) if min_lat < max_lat else list(range(int(max_lat), int(min_lat) - 1))
        else:
            lats_to_read = [int(min_lat)]
        
        if int(min_lon) != int(max_lon):
            lons_to_read = list(range(int(min_lon), int(max_lon) + 1)) if min_lon < max_lon else list(range(int(max_lon), int(min_lon) - 1))
        else:
            lons_to_read = [int(min_lon)]

        print(f"Area crosses multiple hgt files. Reading from lats {lats_to_read} and lons {lons_to_read}")

        max_section = lats_to_read if len(lats_to_read) > len(lons_to_read) else lons_to_read

        #extend the other list to match the length of the max list
        if len(lats_to_read) > len(lons_to_read):
            lons_to_read.extend([int(min_lon)] * (len(lats_to_read) - len(lons_to_read)))
        else:
            lats_to_read.extend([int(min_lat)] * (len(lons_to_read) - len(lats_to_read)))

        #TODO Diagonal extensions are not supported. It either needs to be all horizontal or all vertical
        prev = None
        file_paths = []
        for lat, lon in zip(lats_to_read, lons_to_read):
            hgt_file = "%(ns)s%(lat)02d%(ew)s%(lon)03d.hgt" % \
           {'lat': abs(lat), 'lon': abs(lon), 'ns': 'N' if lat >= 0 else 'S', 'ew': 'E' if lon >= 0 else 'W'}
            if prev is not None:
                #Calculate the direction we just moved 
                if lat == prev[0]:
                    directions.append('VERTICAL')
                else:
                    directions.append('HORIZONTAL')
            prev = (lat, lon)
            file_paths.append(os.path.join(HGTDIR, hgt_file))
        return file_paths, directions

    else:

        return [os.path.join(HGTDIR, hgt_file)], []

