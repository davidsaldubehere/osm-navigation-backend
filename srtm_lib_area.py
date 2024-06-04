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
    hgt_files = get_file_name(min_lat, min_lon, max_lat, max_lon)
    if len(hgt_files)==1:
        return read_elevation_from_file(hgt_files[0], min_lat, min_lon, max_lat, max_lon)
    elif len(hgt_files) > 1:
        return read_elevations_from_files(hgt_files, min_lat, min_lon, max_lat, max_lon)
    # Treat it as data void as in SRTM documentation
    # if file is absent
    print(f"Could not find hgt file for {min_lat, min_lon, max_lat, max_lon}")
    return -32768

def read_elevations_from_files(hgt_files, min_lat, min_lon, max_lat, max_lon):
    elevation_data = None
    queue = None
    v_strip_height = int(max_lat) - int(min_lat)
    v_strip_height = 1 if v_strip_height == 0 else v_strip_height + 1

    for count, file_name in enumerate(hgt_files): #count starts at 0
        with open(file_name, 'rb') as hgt_data:
            
            elevations = np.fromfile(
                hgt_data,  # binary data
                np.dtype('>i2'),  # data type
                SAMPLES * SAMPLES  # length
            ).reshape((SAMPLES, SAMPLES))

            #calculates the height of the vertical strip
            print(count)

            if (count+1) % v_strip_height == 0:
                queue = np.vstack((queue, elevations))
                if elevation_data is None:
                    elevation_data = queue
                else:

                    elevation_data = np.hstack((elevation_data, queue))

                #empty queue
                queue = None
            else:
                if queue is None:
                    queue = elevations
                
                else:
                    queue = np.vstack((elevations, queue))

    #return early to test
    #return elevation_data, np.linspace(min_lon, max_lon, elevation_data.shape[1]), np.linspace(max_lat, min_lat, elevation_data.shape[0])

    #target shape is max dimension squared
    print(f"Final shape: {elevation_data.shape}")
    #max_dim = max(elevation_data.shape)
    lat_samples = elevation_data.shape[0]
    lon_samples = elevation_data.shape[1]
    #target_shape = (max_dim, max_dim)
    #pad the elevation data to make it square
    #elevation_data = np.pad(elevation_data, ((0, target_shape[0] - elevation_data.shape[0]), (0, target_shape[1] - elevation_data.shape[1])), mode='constant', constant_values=-32768)


    #calculate the indexes of the subset
    min_lat_offset = min_lat - int(min_lat) if min_lat >= 0 else abs(int(min_lat))+1 - abs(min_lat)
    min_lon_offset = min_lon - int(min_lon) if min_lon >= 0 else abs(int(min_lon))+1 - abs(min_lon)
    max_lat_offset = max_lat - int(max_lat) if max_lat >= 0 else abs(int(max_lat))+1 - abs(max_lat)
    max_lon_offset = max_lon - int(max_lon) if max_lon >= 0 else abs(int(max_lon))+1 - abs(max_lon)
    #Now we have to find the rows and columns that correspond to the subset
    #It goes base row = (int(lat/lon) - start_row ) * SAMPLES + offset * SAMPLES

    start_row = int(min_lat)
    start_col = int(min_lon)
    min_lat_row = round(abs(start_row - int(min_lat)) * SAMPLES + min_lat_offset * SAMPLES)
    min_lon_row = round(abs(start_col - int(min_lon)) * SAMPLES + min_lon_offset * SAMPLES)
    max_lat_row = round(abs(start_row - int(max_lat)) * SAMPLES + max_lat_offset * SAMPLES)
    max_lon_row = round(abs(start_col - int(max_lon)) * SAMPLES + max_lon_offset * SAMPLES)


    #we have to invert the latitude indexes because latitude increases as we go up
    #but the hgt file has the latitude increasing as we go down

    #min_lat_row, max_lat_row = lat_samples - 1 - max_lat_row,  lat_samples - 1 - min_lat_row + 1
    print(f"min_lat_row: {min_lat_row}, min_lon_row: {min_lon_row}, max_lat_row: {max_lat_row}, max_lon_row: {max_lon_row}")

    elevation_subset = elevations[min_lat_row:max_lat_row, min_lon_row:max_lon_row]
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
        #if len(lats_to_read) > len(lons_to_read):
        #    lons_to_read.extend([int(min_lon)] * (len(lats_to_read) - len(lons_to_read)))
        #else:
        #    lats_to_read.extend([int(min_lat)] * (len(lons_to_read) - len(lats_to_read)))

        #TODO Diagonal extensions are not supported. It either needs to be all horizontal or all vertical
        prev = None
        file_paths = []
        #for lat, lon in zip(lats_to_read, lons_to_read):
        #    hgt_file = "%(ns)s%(lat)02d%(ew)s%(lon)03d.hgt" % \
        #   {'lat': abs(lat), 'lon': abs(lon), 'ns': 'N' if lat >= 0 else 'S', 'ew': 'E' if lon >= 0 else 'W'}
        #    if prev is not None:
        #        #Calculate the direction we just moved 
        #        if lat == prev[0]:
        #            directions.append('VERTICAL')
        #        else:
        #            directions.append('HORIZONTAL')
        #    prev = (lat, lon)
        #    file_paths.append(os.path.join(HGTDIR, hgt_file))

        #second method where we try to create vertical strips
        for lon in lons_to_read:
            for lat in lats_to_read[::-1]: #Don't ask why I need to reverse this
                hgt_file = "%(ns)s%(lat)02d%(ew)s%(lon)03d.hgt" % \
                {'lat': abs(lat), 'lon': abs(lon), 'ns': 'N' if lat >= 0 else 'S', 'ew': 'E' if lon >= 0 else 'W'}
                file_paths.append(os.path.join(HGTDIR, hgt_file))

        #returns verticle strips
        print(f"Returning {file_paths}")
        return file_paths

    else:

        return [os.path.join(HGTDIR, hgt_file)]

