"""Locate all grasslands above 2000m within 300m of a stream."""
import logging
LOGGER = logging.getLogger('grasslands_demo')
logging.basicConfig(level=logging.INFO)

from osgeo import gdal
import pygeoprocessing

# First, let's determine the stream network.
# To do this, we need to mosaic the DEM and reproject to the local projection

import os

OUTPUT_DIR = '/shared/grasslands_demo'
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

north_dem = '/data/N38W120.tif'
south_dem = '/data/N37W120.tif'

joined_dem = os.path.join(OUTPUT_DIR, 'joined_dem.tif')

yosemite_vector = '/data/yosemite.shp'
LOGGER.info('Starting union of DEMs')

import numpy
def _merge_dems(north_block, south_block):
    valid_mask = (north_block != -1) | (south_block != -1)
    out_matrix = numpy.empty(north_block.shape)
    out_matrix[:] = -1
    out_matrix[valid_mask] = numpy.maximum(north_block[valid_mask],
                                           south_block[valid_mask])
    return out_matrix

LOGGER.info('Merging DEMs')
pygeoprocessing.vectorize_datasets(
    dataset_uri_list=[north_dem, south_dem],
    dataset_pixel_op=_merge_dems,
    dataset_out_uri=joined_dem,
    datatype_out=gdal.GDT_Int16,
    nodata_out=-1.0,
    # We could calculate projected units by hand, but this is more convenient.
    pixel_size_out=30.0,
    bounding_box_mode='union',
    vectorize_op=False,
    aoi_uri=yosemite_vector,
)

# Next, we need to generate the stream layer.
# This will be an output raster with pixel values of 1 or 0 indicating whether
# the pixel is determined to be on a stream.
from pygeoprocessing.routing import routing

# Flow direction determines which pixels water flows into
LOGGER.info('Calculating flow direction')
flow_direction = os.path.join(OUTPUT_DIR, 'flow_direction.tif')
routing.flow_direction_d_inf(
    dem_uri=joined_dem,
    flow_direction_uri=flow_direction)

# Flow accumulation is the accumulated weight of all cells flowing
# into each downlope pixel in the raster.
LOGGER.info('Calculating flow accumulation')
flow_accumulation = os.path.join(OUTPUT_DIR, 'flow_accumulation.tif')
routing.flow_accumulation(
    flow_direction_uri=flow_direction,
    dem_uri=joined_dem,
    flux_output_uri=flow_accumulation,
    aoi_uri=yosemite_vector)

# After <threshold> number of pixels flow into a cell, the cell becomes a
# stream.
LOGGER.info('Delineating streams')
streams = os.path.join(OUTPUT_DIR, 'streams.tif')
routing.stream_threshold(
    flow_accumulation_uri=flow_accumulation,
    flow_threshold=250,
    stream_uri=streams)

# Now, we need to use the streams raster as an EDT mask
LOGGER.info('Calculating euclidean distance to streams')
edt_from_streams = os.path.join(OUTPUT_DIR, 'euclidean_dist_to_streams.tif')
pygeoprocessing.distance_transform_edt(
    input_mask_uri=streams,
    output_distance_uri=edt_from_streams)

# OK!  Now we add it all together with a call to vectorize_datasets
LOGGER.info('Finding high-elevation grasslands near streams')
lulc = '/data/landcover.tif'

# segfault if I do this: gdal.Open(lulc).GetRasterBand(1).GetNoDataValue()
lulc_nodata = pygeoprocessing.get_nodata_from_uri(lulc)
dem_nodata = pygeoprocessing.get_nodata_from_uri(joined_dem)
stream_nodata = pygeoprocessing.get_nodata_from_uri(edt_from_streams)

out_nodata = -1
def _find_grasslands(lulc_blk, dem_blk, stream_dist_blk):
    # All blocks will be the same dimensions

    # Create a mask of invalid pixels due to nodata values
    valid_mask = ((lulc_blk != lulc_nodata) &
                  (dem_blk != dem_nodata) &
                  (stream_dist_blk != stream_nodata))

    # grasslands are lulc code 10
    matching_grasslands = ((lulc_blk[valid_mask] == 10) &
                           (stream_dist_blk[valid_mask] <= 300) &
                           (dem_blk[valid_mask] >= 2000))

    out_block = numpy.empty(lulc_blk.shape)
    out_block[:] = 0
    out_block[~valid_mask] = out_nodata
    out_block[valid_mask] = matching_grasslands
    return out_block


def _find_grasslands_pixels(lulc_pixel, dem_pixel, stream_dist_pixel):
    if any(lulc_pixel == lulc_nodata,
           dem_pixel == dem_nodata,
           stream_dist_pixel == stream_nodata):
        return out_nodata
    elif all(lulc_pixel == 10,
             stream_dist_pixel <= 300,
             dem_pixel >= 2000):
        return 1
    return 0


pygeoprocessing.vectorize_datasets(
    dataset_uri_list=[lulc, joined_dem, edt_from_streams],
    dataset_pixel_op=_find_grasslands,
    dataset_out_uri=os.path.join(OUTPUT_DIR, 'high_elev_riparian_grasslands.tif'),
    datatype_out=gdal.GDT_Int16,
    nodata_out=out_nodata,
    # We could calculate projected units by hand, but this is more convenient.
    pixel_size_out=pygeoprocessing.get_cell_size_from_uri(joined_dem),
    bounding_box_mode='intersection',
    vectorize_op=False,  # we
    aoi_uri=yosemite_vector)



