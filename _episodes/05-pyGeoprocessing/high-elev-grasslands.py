"""Locate all grasslands above 2000m within 300m of a stream."""
from osgeo import gdal
import pygeoprocessing

# First, let's determine the stream network.
# To do this, we need to mosaic the DEM and reproject to the local projection

import os
OUTPUT_DIR = '/shared/grasslands_demo'

north_dem = '/data/ASTGTM2_N38W120_dem.tif'
south_dem = '/data/ASTGTM2_N37W120_dem.tif'

joined_dem = os.pathljoin(OUTPUT_DIR, 'joined_dem.tif')

import subprocess
subprocess.check_call(
    'gdal_merge.py -o {output_filename} -of GTiff {north} {south}'.format(
        output_filename=joined_dem,
        north=north_dem,
        south=south_dem))


from osgeo import osr
srs = osr.SpatialReference()
srs.ImportFromEPSG(32611)
utm11n_wkt = srs.ExportToWkt()

reprojected_dem = os.path.join(OUTPUT_DIR, 'joined_reprojected_dem.tif')
pygeoprocessing.reproject_dataset_uri(
    original_dataset_uri=joined_dem,
    pixel_spacing=30.0,  # output pixel size, in projected linear units
    output_wkt=utm11n_wkt,
    resampling_method='nearest',  # available options may depend on GDAL build
    output_uri=reprojected_dem)

# Next, we need to generate the stream layer.
# This will be an output raster with pixel values of 1 or 0 indicating whether
# the pixel is determined to be on a stream.
from pygeoprocessing.routing import routing

# Flow direction determines which pixels water flows into
flow_direction = os.path.join(OUTPUT_DIR, 'flow_direction.tif')
routing.flow_direction_d_inf(
    dem_uri=reprojected_dem,
    flow_direction_uri=flow_direction)

# Flow accumulation is the accumulated weight of all cells flowing
# into each downlope pixel in the raster.
flow_accumulation = os.path.join(OUTPUT_DIR, 'flow_accumulation.tif')
yosemite_vector = '/data/yosemite.shp'
routing.flow_accumulation(
    flow_direction_uri=flow_direction,
    dem_uri=reprojected_dem,
    flux_output_uri=flow_accumulation,
    aoi_uri=yosemite_vector)

# After <threshold> number of pixels flow into a cell, the cell becomes a
# stream.
streams = os.path.join(OUTPUT_DIR, 'streams.tif')
routing.stream_threshold(
    flow_accumulation_uri=flow_accumulation,
    flow_threshold=1000,
    stream_uri=streams)

# Now, we need to use the streams raster as an EDT mask
edt_from_streams = os.path.join(OUTPUT_DIR, 'euclidean_dist_to_streams.tif')
pygeoprocessing.distance_transform_edt(
    input_mask_uri=streams,
    output_distance_uri=edt_from_streams)

# OK!  Now we add it all together with a call to vectorize_datasets
lulc = '/data/landcover.tif'

# segfault if I do this: gdal.Open(lulc).GetRasterBand(1).GetNoDataValue()
lulc_nodata = pygeoprocessing.get_nodata_from_uri(lulc)
dem_nodata = pygeoprocessing.get_nodata_from_uri(reprojected_dem)
stream_nodata = pygeoprocessing.get_nodata_from_uri(edt_from_streams)

out_nodata = -1
import numpy
def _find_grasslands(lulc_blk, dem_blk, stream_dist_blk):
    # All blocks will be the same dimensions

    # Create a mask of invalid pixels due to nodata values
    nodata_mask = (lulc_blk != lulc_nodata &
                  dem_blk != dem_nodata &
                  stream_dist_blk != stream_nodata)

    # grasslands are lulc code 10
    matching_grasslands = (lulc_blk[nodata_mask] == 10 &
                           stream_dist_blk[nodata_mask] <= 300 &
                           dem_blk[nodata_mask] >= 2000)

    out_block = numpy.empty(lulc_blk.shape)
    out_block[:] = 0
    out_block[nodata_mask] = out_nodata
    out_block[~nodata_mask] = matching_grasslands
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
    dataset_uri_list=[lulc, reprojected_dem, edt_from_streams],
    dataset_pixel_op=_find_grasslands,
    dataset_out_uri=os.path.join(OUTPUT_DIR, 'high_elev_riparian_grasslands.tif'),
    datatype_out=gdal.GDT_Int16,
    nodata_out=out_nodata,
    # We could calculate projected units by hand, but this is more convenient.
    pixel_size_out=pygeoprocessing.get_cell_size_from_uri(reprojected_dem),
    bounding_box_mode='intersection',
    vectorize_op=False,  # we
    aoi_uri=yosemite_vector)



