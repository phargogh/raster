# approximately what percentage area of yosemite national park is above 3500m (11482 ft.)?
import os

from osgeo import gdal
import pygeoprocessing

OUTPUT_DIR = '/shared/high_elevation_area'
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

dem = os.path.join('/shared', 'grasslands_demo', 'joined_dem.tif')

# rasterize yosemite vector to create new layer
blank_raster = os.path.join(OUTPUT_DIR, 'yosemite.tif')
pygeoprocessing.new_raster_from_base_uri(
    base_uri=dem,
    output_uri=blank_raster,
    gdal_format='GTiff',
    nodata=-1,
    datatype=gdal.GDT_Byte,
    fill_value=0
)

# This will overwrite whatever pixel values are in the existing raster.
pygeoprocessing.rasterize_layer_uri(
    raster_uri=blank_raster,
    shapefile_uri='/data/yosemite.shp',
    burn_values=[1])

# use iterblocks to calculate the within the park and the area above 3500m.
import itertools
import time
start_time = time.time()
num_park_pixels = 0.
num_3500_pixels = 0.
for (park_data, park_block), (dem_info, dem_block) in itertools.izip(
        pygeoprocessing.iterblocks(blank_raster),
        pygeoprocessing.iterblocks(dem)):

    num_park_pixels += len(park_block[park_block == 1])
    num_3500_pixels += len(dem_block[(park_block == 1) & (dem_block >= 3500)])

print 'Iterblocks took %ss' % (time.time() - start_time)
print 'Park pixels: %s' % num_park_pixels
print 'High-elevation pixels %s' % num_3500_pixels
print 'Percentage of park land above 3500m: %s%%' % round(
    (num_3500_pixels / num_park_pixels) * 100, 2)

# Compare iterblocks time with pure-numpy approach.
start_time = time.time()
park_raster = gdal.Open(blank_raster)
park_array = park_raster.ReadAsArray()
num_park_pixels = len(park_array[park_array == 1])
dem_raster = gdal.Open(dem)
dem_array = dem_raster.ReadAsArray()
num_3500_pixels = len(dem_array[dem_array >= 3500])
print 'numpy took %ss' % (time.time() - start_time)
print 'Park pixels: %s' % num_park_pixels
print 'High-elevation pixels %s' % num_3500_pixels
print 'Percentage of park land above 3500m: %s%%' % round(
    (float(num_3500_pixels) / num_park_pixels) * 100, 2)
