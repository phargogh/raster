import os
import tempfile
import logging

from osgeo import gdal, ogr
import pygeoprocessing

logging.basicConfig()

WGS84UTM11N = """PROJCS["WGS 84 / UTM zone 11N",
    GEOGCS["WGS 84",
        DATUM["WGS_1984",
            SPHEROID["WGS 84",6378137,298.257223563,
                AUTHORITY["EPSG","7030"]],
            AUTHORITY["EPSG","6326"]],
        PRIMEM["Greenwich",0,
            AUTHORITY["EPSG","8901"]],
        UNIT["degree",0.01745329251994328,
            AUTHORITY["EPSG","9122"]],
        AUTHORITY["EPSG","4326"]],
    UNIT["metre",1,
        AUTHORITY["EPSG","9001"]],
    PROJECTION["Transverse_Mercator"],
    PARAMETER["latitude_of_origin",0],
    PARAMETER["central_meridian",-117],
    PARAMETER["scale_factor",0.9996],
    PARAMETER["false_easting",500000],
    PARAMETER["false_northing",0],
    AUTHORITY["EPSG","32611"],
    AXIS["Easting",EAST],
    AXIS["Northing",NORTH]]"""


def reproject_raster_to_epsg3718(in_filename, out_filename, cell_size):
    print 'Reprojecting %s -> %s' % (in_filename, out_filename)
    pygeoprocessing.reproject_dataset_uri(
        original_dataset_uri=in_filename,
        pixel_spacing=cell_size,
        output_wkt=WGS84UTM11N,
        resampling_method='nearest',
        output_uri=out_filename)

def convert_vector_extents_to_vector(in_vector, out_vector_uri):
    """Build a vector with 1 polygon that represents the raster's bounding box.

        raster_uri - a URI to a GDAL raster from which our output vector should
            be created
        sample_vector_uri - a URI to an OGR datasource that we will write on
            disk.  This output vector will be an ESRI Shapefile format.

        Returns Nothing."""

    _vector = ogr.Open(in_vector)
    _layer = _vector.GetLayer()
    layer_srs = _layer.GetSpatialRef()
    extent = _layer.GetExtent()

    driver = ogr.GetDriverByName('ESRI Shapefile')
    out_vector = driver.CreateDataSource(out_vector_uri)
    layer_name = str(os.path.basename(os.path.splitext(out_vector_uri)[0]))
    out_layer = out_vector.CreateLayer(layer_name, srs=layer_srs)

    poly_ring = ogr.Geometry(type=ogr.wkbLinearRing)

    # make a polygon for the bounding box
    poly_ring.AddPoint(extent[0], extent[2]),
    poly_ring.AddPoint(extent[1], extent[2]),
    poly_ring.AddPoint(extent[1], extent[3]),
    poly_ring.AddPoint(extent[0], extent[3]),
    poly_ring.AddPoint(extent[0], extent[2]),
    polygon = ogr.Geometry(ogr.wkbPolygon)
    polygon.AddGeometry(poly_ring)

    feature = ogr.Feature(out_layer.GetLayerDefn())
    feature.SetGeometry(polygon)
    out_layer.CreateFeature(feature)
    out_vector.SyncToDisk()

    ogr.DataSource.__swig_destroy__(out_vector)
    feature = None
    out_layer = None
    out_vector = None


def prepare_landcover(lulc_path, clip_to_vector, out_lulc_path):
    # LULC doesn't have a nodata value set, which causes problems.
    ds = gdal.Open(lulc_path, gdal.GA_Update)
    band = ds.GetRasterBand(1)
    band.SetNoDataValue(255.0)
    band.FlushCache()
    band = None
    ds.FlushCache()
    ds = None

    # Create a sample raster to clip to based on the vector extents provided.
    tempdir = tempfile.mkdtemp(dir=os.getcwd())

    print 'New vector from bounding box of %s' % clip_to_vector
    boundingbox_vector = os.path.join(tempdir, 'sierra_bbox.shp')
    convert_vector_extents_to_vector(clip_to_vector, boundingbox_vector)

    # reproject the vector to the target projection
    print 'Reprojecting %s' % boundingbox_vector
    projected_vector = os.path.join(tempdir, 'sierra_bbox_projected.shp')
    pygeoprocessing.reproject_datasource_uri(boundingbox_vector, WGS84UTM11N,
                                             projected_vector)

    extents_file = os.path.join(tempdir, 'sierra_extents.tif')
    print 'Creating raster from sierra bbox vector at %s' % extents_file
    pygeoprocessing.create_raster_from_vector_extents_uri(
        projected_vector,
        pixel_size=50.0,
        gdal_format=gdal.GDT_Byte,
        nodata_out_value=255.0,
        output_uri=extents_file)

    # The extents file is filled with nodata, which causes some operations to
    # crash when trying to calculate raster statistics.
    sierra_ds = gdal.Open(extents_file, gdal.GA_Update)
    sierra_band = sierra_ds.GetRasterBand(1)
    sierra_band.Fill(0)
    sierra_band.FlushCache()
    sierra_band = None
    sierra_ds.FlushCache()
    sierra_ds = None

    reprojected_lulc = os.path.join(tempdir, 'lulc_reprojected.tif')
    reproject_raster_to_epsg3718(
        lulc_path, reprojected_lulc,
        pygeoprocessing.get_cell_size_from_uri(lulc_path))

    # Clip the input LULC by clip_to
    print 'Clipping LULC %s -> %s' % (reprojected_lulc, extents_file)
    clipped_lulc = os.path.join(tempdir, 'lulc_clipped.tif')
    pygeoprocessing.vectorize_datasets(
        [reprojected_lulc, extents_file],
        dataset_pixel_op=lambda x, y: y,
        dataset_out_uri=clipped_lulc,
        datatype_out=pygeoprocessing.get_datatype_from_uri(reprojected_lulc),
        nodata_out=pygeoprocessing.get_nodata_from_uri(reprojected_lulc),
        pixel_size_out=pygeoprocessing.get_cell_size_from_uri(reprojected_lulc),
        bounding_box_mode='intersection',
        assert_datasets_projected=False
    )


if __name__ == '__main__':
    output_dir = 'reprojected'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # reproject yosemite vector
    pygeoprocessing.reproject_datasource_uri('yosemite.shp', WGS84UTM11N,
                                             os.path.join(output_dir, 'yosemite.shp'))

    # reproject DEMs
    for aster_name in ['ASTGTM2_N38W120', 'ASTGTM2_N37W120']:
        raster_filename = os.path.join(aster_name, '%s_dem.tif' % aster_name)
        ds = gdal.Open(raster_filename, gdal.GA_Update)
        band = ds.GetRasterBand(1)
        band.SetNoDataValue(-1)
        band.FlushCache()
        band = None
        ds = None

        out_raster = os.path.join(output_dir,
                                  '%s.tif' % aster_name.split('_')[1])
        reproject_raster_to_epsg3718(raster_filename, out_raster, 30)

    # prepare LULC
    south_sierra_vector = 'ExistingVegSouthSierra2000_2008_v1.gdb'
    prepare_landcover('LCType.tif', south_sierra_vector,
                      os.path.join(output_dir, 'landcover.tif'))
