---
title: "Efficient raster computation with PyGeoProcessing"
teaching: 20 
exercises: 15 
questions:
- "What problems can PyGeoProcessing address?"
- "When should I use PyGeoProcessing?"
objectives:
- "Understand how to execute a pygeoprocessing-style workflow"
- "Identify when and how PyGeoProcessing can benefit an analysis"
keypoints:
- "PyGeoProcessing provides programmable operations for efficient raster computations"
- "Looping in python is slow; improve speed by iterating over blocks"
---

# What is PyGeoProcessing?

![NatCap Logo](natcap-logo.png)
![InVEST Logo](invest-logo.png)
![PyGeoProcessing Logo](pygeoprocessing-logo.png)


* [PyGeoProcessing](https://bitbucket.org/richpsharp/pygeoprocessing) is a 
    python library of geospatial processing routines developed 
    and maintained by the Natural Capital Project (NatCap).
* Development began in 2011 as NatCap began migrating the [Integrated 
    Valutation of Ecosystem Services and Tradeoffs (InVEST)](http://naturalcapitalproject.org/invest)
    software to an open-source platform.
    * InVEST is a software tool that helps decision-makers understand tradeoffs
        in land-use and marine spatial planning decisions in terms of the benefits
        provided by nature ("Ecosystem Services")
    * Early versions of InVEST were free geoprocessing scripts based on ArcGIS
        * Quickly ran into limitations of the platform:
            * Difficult to batch-process lots of runs
            * Very difficult to link different models together
            * Model runs were very slow, sometimes taking days or weeks to run complex analyses
    * The first free, purely open-source InVEST models were released in 2011
    * Development of the new InVEST required a portable replacement of the
        geoprocessing routines required by the models, but none existed at the 
        time.
    * PyGeoProcessing evolved from this need, and was released as its own
        open-source project in 2015, announced at FOSS4G-NA.
* PyGeoProcessing is designed with the same functional requirements of InVEST:
    * Work within memory-constrained python environments (e.g. 32-bit python installations)
    * Support very large datasets on a local filesystem
    * Geoprocessing routines must be computationally efficient
* PyGeoProcessing is under active development, and is being continually improved

* **Key features**:
    * Programmable raster stack calculator
    * 2D Convolution with an arbitrary kernel
    * Euclidean Distance transform
    * Reclassification
    * D-infinity routing:
        * Stream network delineation
        * Distance to stream
        * Flow direction
        * Pixel export
        * watershed delineation
    * Helper functions for:
        * iterating over raster blocks
        * aligning and resampling stacks of rasters
        * extracting key raster metadata
        * Creating new raster datasets

### What PyGeoProcessing can do for you

#### When it makes sense to use PyGeoProcessing
* You need a reproducible workflow for your analysis
* Your analysis needs to be run many times (such as in optimization routines)
* Your data is accessible on a single computer ("*large* but not *big*")
* You have limited memory or are in a 32-bit programming environment


#### Why not just use GIS software?
* Most GIS installations are very large, and may break your script with each upgrade (ArcGIS is notorious for this)
* GIS don't always provide pure-python interfaces, or can't execute scripts from the command-line
* You can't ``pip install`` your GIS software


#### Why not just use ``numpy`` directly on extracted matrices?
If you can, go for it!  PyGeoProcessing is best for cases where your data are large
enough that you cannot fit it all into main memory, for efficiently automating
complex workflows, and for common nontrivial operations.
It won't be relevent for every use case.

Some operations that require a lot of looping, though, are especially challenging to
do in python.  In a python loop, every iteration needs to be able to handle all of the
possible types that a value might be.  For every line of python, at least 20 lines of C++
are executed.  This means that if your dataset is of any reasonable size and you need
to visit every pixel, you  may want to consider compiling a cython extension.

Consider this simple python function.

~~~
def foo():
    count = 0
    for i in xrange(100):
        count += i
~~~
{: .python}

Compare it with the [C code that must be executed](loop-overhead.html) to do
something this simple.  For this reason, you may need to compile your focal
operations to get them to run fast.


## Single-output example workflow: Locate Steep, High-Elevation Grasslands in Yosemite

~~~
import os
import logging
LOGGER = logging.getLogger('grasslands_demo')
logging.basicConfig(level=logging.INFO)

from osgeo import gdal
import pygeoprocessing

OUTPUT_DIR = '/shared/grasslands_demo'
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
~~~
{: .python}

For this tutorial, we'll be making use of three rasters and one vector, 
all of which have already been projected ino a local coordinate system.

~~~
north_dem = '/data/N38W120.tif'
south_dem = '/data/N37W120.tif'
landcover = '/data/landcover.tif'
yosemite_vector = '/data/yosemite.shp'
~~~
{:.python}


### Joining our two DEMs
|-----------------------|-----------------------|
| ``/data/N38W120.tif`` | ``/data/N37W120.tif`` |
|-----------------------|-----------------------|
| ![DEM 1](N38W120.png) | ![DEM 1](N37W120.png) |
|-----------------------|-----------------------|
| ASTER GDEM is a product of METI and NASA.     |
|-----------------------------------------------|

~~~
LOGGER.info('Merging DEMs')
import numpy
def _merge_dems(north_block, south_block):
    """Merge the two DEMs, picking the max value where overlap occurs."""
    valid_mask = (north_block != -1) | (south_block != -1)
    out_matrix = numpy.empty(north_block.shape)
    out_matrix[:] = -1
    out_matrix[valid_mask] = numpy.maximum(north_block[valid_mask],
                                           south_block[valid_mask])
    return out_matrix

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
~~~
{:.python}

NEED AN IMAGE OF THIS


### Calculate Slope

~~~
LOGGER.info('Calculating slope')
slope_raster = os.path.join(OUTPUT_DIR, 'slope.tif')
pygeoprocessing.calculate_slope(
    dem_dataset_uri=joined_dem,
    slope_uri=slope_raster)
~~~
{:.python}

NEED AN IMAGE OF THIS

### Locate Steep, High-Elevation Grasslands

~~~
lulc_nodata = pygeoprocessing.get_nodata_from_uri(lulc)
dem_nodata = pygeoprocessing.get_nodata_from_uri(joined_dem)
slope_nodata = pygeoprocessing.get_nodata_from_uri(slope_raster)

out_nodata = -1
def _find_grasslands(lulc_blk, dem_blk, slope_blk):
    # All blocks will be the same dimensions

    # Create a mask of invalid pixels due to nodata values
    valid_mask = ((lulc_blk != lulc_nodata) &
                  (dem_blk != dem_nodata) &
                  (slope_blk!= slope_nodata))

    # grasslands are lulc code 10
    matching_grasslands = ((lulc_blk[valid_mask] == 10) &
                           (slope_blk[valid_mask] >= 45) &
                           (dem_blk[valid_mask] >= 2000))

    out_block = numpy.empty(lulc_blk.shape)
    out_block[:] = 0
    out_block[~valid_mask] = out_nodata
    out_block[valid_mask] = matching_grasslands
    return out_block


pygeoprocessing.vectorize_datasets(
    dataset_uri_list=[lulc, joined_dem, slope_raster],
    dataset_pixel_op=_find_grasslands,
    dataset_out_uri=os.path.join(OUTPUT_DIR, 'high_elev_steep_grasslands.tif'),
    datatype_out=gdal.GDT_Int16,
    nodata_out=out_nodata,
    # We could calculate projected units by hand, but this is more convenient.
    pixel_size_out=pygeoprocessing.get_cell_size_from_uri(joined_dem),
    bounding_box_mode='intersection',
    vectorize_op=False,  # we
    aoi_uri=yosemite_vector)
~~~
{:.python}

NEED AN IMAGE OF THIS



### Local Operations: ``pygeoprocessing.vectorize_datasets``

Local operations create a single output layer that is a function of various input layers.
Most GIS tools provide a Raster Calculator that does something similar.

To be able to use ``vectorize_datasets`` effectively, we need to first be able to define our
problem in terms of block-level operations.

A trivial example would be to add pixels together.

In PyGeoProcessing, ``pygeoprocessing.vectorize_datasets`` allows us to do this with all
of the flexibility of the python programming language.

### Focal Operations:  ``pygeoprocessing.raster_focal_op``

* Focal operations are technicallly the class,
    * pygeoprocessing only has convolutions at the moment
    * true focal operations could be defined via iterblocks, or by looping over each pixel and indexing accordingly

Demonstrate a gaussian filter.


### Zonal Statistics: ``pygeoprocessing.aggregate_values``

* example: find the median elevation of all DEM pixels under the yosemite polygon.

### Routing: ``pygeoprocessing.routing``

Possibilities:
* Calculate slope for yosemite area.
* Calculate the stream network layer

Delineate a watershed.

### Block iteration: ``pygeoprocessing.iterblocks``

Block iteration allows us to:

* Incrementally read in reasonable amounts of raster data and perform matrix operations on it
* Keep track of a block's location in the context of the raster.

#### Note on execution speed

~~~
from osgeo import gdal
import time
def timeit():
    start_time = time.time()
    ds = gdal.Open('data/landcover.tif')
    array = ds.GetRasterBand(1).ReadAsArray()
    print array.sum()
    print 'Took %s' % time.time() - start_time

timeit()
~~~

In this case, we have a raster that should fit into the system's main memory, so 
this operation should be pretty quick.


* Locate all grasslands within 200m of streams above 2000m elevation.
    * Inputs to vectorize_datasets:
        * Mosaiced DEMs in the same projection (EPSG:32611), clipped to yosemite AOI
        * Stream layer generated from DEM with known threshold.
        * EDT generated from stream layer
    * Function required:
        * Mask out areas of nodata
        * If lulc is grassland and EDT < 200 and DEM >= 2000, 1 else 0 
    * Output type = Int16, nodata=-1


* work through a vectorize_datasets workflow:
    * Read in a CSV table
    * Reclassify the LULC
    * Take the DEMs, unproject them, join the two together, reproject them.
    * Route the DEM, figure out the stream network.
    * Use vectorize_datasets to locate perform some equation on the layers.

* work through another workflow:
    * use iterblocks to find the number of pixels that meet some criteria in the whole raster.
    * time it!  Compare with reading a whole array into memory, and/or with a numpy.memmap array.

