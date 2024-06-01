from __future__ import print_function
import os
import numpy as np

SRTM_DICT = {'SRTM1': 3601, 'SRTM3': 1201}

# Get the type of SRTM files or use SRTM1 by default
SRTM_TYPE = os.getenv('SRTM_TYPE', 'SRTM1')
SAMPLES = SRTM_DICT[SRTM_TYPE]

# put uncompressed hgt files in HGT_DIR, defaults to 'hgt'
HGTDIR = os.getenv('HGT_DIR', 'hgt')


def get_elevation(min_lat, max_lat, min_lon, max_lon):
    hgt_file = get_file_name(min_lat, min_lon, max_lat, max_lon)
    if hgt_file:
        return read_elevation_from_file(hgt_file, min_lat, min_lon, max_lat, max_lon)
    # Treat it as data void as in SRTM documentation
    # if file is absent
    return -32768

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

def get_file_name(min_lat, min_lon, max_lat, max_lon):
    """
    Returns filename such as N27E086.hgt, concatenated
    with HGTDIR where these 'hgt' files are kept

    Only one file can be used for now (for now)
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
    
    assert hgt_file == hgt_file_1, "Only one hgt file can be used at a time, make sure the region is small enough to fit in one hgt file"

    hgt_file_path = os.path.join(HGTDIR, hgt_file)
    #print("file path: %s" % hgt_file_path)
    if os.path.isfile(hgt_file_path):
    #    print("valid file path: %s" % hgt_file_path)
        return hgt_file_path
    else:
        return None