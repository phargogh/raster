---
title: "Using GDAL"
teaching: 30
exercises: 15
questions:
- "What functionality does GDAL offer?"
- "What raster dataset formats are supported?"
- "How do I interact with raster data within a python program?"
objectives:
- "Understand the basic components of a raster dataset"
- "Read from and write to raster datasets"
- "Perform numpy operations on a raster's values"
keypoints:
- "GDAL is useful for reading/writing/transforming raster datasets"
- "Errors can be handled pythonically"
- "Pixel values can be extracted to a numpy array"
---

# What is GDAL (Geospatial Data Abstraction Library)?

* C/C++ library for reading, writing, and reprojecting raster and vector datasets
    * Provides a single abstract data model for interacting with all supported formats
    * Spatial reprojections provided by [PROJ.4](http://proj4.org/), a library for 
      performing conversions between cartographic projections (currently maintained
      by Frank Warmerdam).
* Originally developed as a side project by Frank Warmerdam (first release in 2000)
* Major open-source member of the Open Source Geospatial Foundation
* OGR (GDAL-provided library for handing vector data) is also part of the project
* Together, GDAL/OGR contains 1.1M lines of code (not including comments and whitespace
* Almost ubiquitous in geospatial applications

# Supported Formats:

As of the latest version of GDAL, 142 formats are supported, but builds for various platforms may omit support for some formats.  The docker images for this tutorial include a GDAL build with support for 124 formats, including a few that have both raster and vector layers.

>## Not all formats are supported equally
>GDAL's drivers do not support all formats equally, and differences are 
> listed in `gdalinfo --formats`.
> * ``ro`` - read-only support
> * ``rw`` - reading and writing to existing files (and making copies) supported
> * ``rw+`` - reading, writing and creation of new files supported
> * ``v`` - the format supports streaming through virtual filesystem API.  Streaming sources include compressed archives (such as ``.tar.gz``) and remote file servers (such as HTTP, FTP)
> * ``s`` - the format support subdatasets
{: .callout}

{% highlight bash%}
$ gdalinfo --formats
Supported Formats:
  VRT -raster- (rw+v): Virtual Raster
  GTiff -raster- (rw+vs): GeoTIFF
  NITF -raster- (rw+vs): National Imagery Transmission Format
  RPFTOC -raster- (rovs): Raster Product Format TOC format
  ...
  # There are lots more, results depend on your build
{% endhighlight %}

Specifics about each format can be found with the ``--format`` parameter.  Let's take a look
at the GeoTiff format, which is well-supported and has many possible creation options.

{% highlight bash%}
$ gdalinfo --format GTiff
{% endhighlight %}

GDAL also has prose documentation available for each format, including detailed information
about creation options available on their website at: 
[http://www.gdal.org/formats_list.html](http://www.gdal.org/formats_list.html).

## GDAL CLI Utilities

GDAL provides a number of command-line utilities to automate common processes.  To see the utilities available on your system:

{% highlight text%}
$ ls -la /usr/local/bin/gdal*
{% endhighlight %}

A full listing of GDAL utilities is available on the [GDAL website](http://gdal.org/gdal_utilities.html). A few that might be particularly useful to you include:

* ``gdalinfo`` - Describe relevant information about a raster, will include the Raster Attribute Table in XML, if one exsits.
* ``gdal_translate`` - Copy contents of an existing raster image to a new one, with new creation options.
* ``gdal_merge.py`` - We'll use this to merge our two DEMs together into a single raster file.
* ``gdalmanage`` - Identify raster datatypes, and/or delete, rename, and copy files in a dataset. 

Each of these GDAL utilities automate certain pieces of commonly-used functionality.  Python scripts can also be used as examples for how to use the GDAL python API for those
writing software that interfaces directly with the SWIG API.

## Access to GDAL libraries

GDAL is a C++ library, but you don't need to write your software in C++ to use it.

Official bindings available for other languages:
* Python [PyPI](http://pypi.python.org/pypi/GDAL)
* C#
* Ruby
* Java
* Perl
* PHP

Of course, you can write your software in C++ if you like :)  For the purposes of this tutorial, we'll interact with the official python bindings.

# Sample datasets

We'll use a couple of datasets for this tutorial, all of which are in ``/data``
on the ``geohackweek2016/raster`` docker image.

These datasets are projected in WGS84/UTM zone 11N, as they are located in the southern
Sierra Nevada mountains in California.

## ASTER DEMs

ASTER GDEM is a product of METI and NASA.

|-----------------------|-----------------------|
| ``/data/N38W120.tif`` | ``/data/N37W120.tif`` |
|-----------------------|-----------------------|
| ![DEM 1](N38W120.png) | ![DEM 1](N37W120.png) |
|-----------------------|-----------------------|

Let's take a look at one of these rasters with ``gdalinfo``:

~~~
$ gdalinfo /data/N38W120.tif
~~~
{: .shell}

Note a few relevant details about the raster:

    * Data type of raster is 16-bit integer
    * The raster is compressed with ``DEFLATE`` mode
    * Pixel values range from 1272 - 3762
    * Note block size is a whole row of pixels.

## Land-Use / Land-Cover

This Land-use/land-cover raster is a part of a global climatology dataset produced by the USGS Land-Cover Institute.

Download from: http://landcover.usgs.gov/global_climatology.php

Citation: Broxton, P.D., Zeng, X., Sulla-Menashe, D., Troch, P.A., 2014a: A Global Land Cover Climatology Using MODIS Data. J. Appl. Meteor. Climatol., 53, 15931605. doi:http://dx.doi.org/10.1175/JAMC-D-13-0270.1 

|-------------------------|
| ``/data/landcover.tif`` |
|-------------------------|
| ![LULC](landcover.png)  |
|-------------------------|

# Using GDAL

We'll interact primarily with GDAL through their official python bindings.

## Begin by importing these libraries

~~~
from osgeo import gdal
~~~

### Open the dataset

First we open the raster so we can explore its attributes, as in the introduction.  GDAL will detect the format if it can, and return a *gdal.Dataset* object.

~~~
ds = gdal.Open('/data/N37W120.tif')
~~~
{: .python}

You'll notice this seemed to go very fast. That is because this step does not 
actually ask Python to read the data into memory. Rather, GDAL is just scanning 
the contents of the file to allow us access to certain critical characteristics.

>## Filepath encodings:
> GDAL expects the path to the raster to be ASCII or UTF-8, which is a common 
> filesystem encoding on linux and macs. Windows is often
> [ISO-8859-1 (Latin-1)](https://en.wikipedia.org/wiki/ISO/IEC_8859-1), or else
> uses a codepage most similar to your locale.
> This will only be an issue with python 2.x, as the ``str`` type in python3 is
> assumed to be encoded as UTF-8.
{: .callout}

>## Note on Error Handling:
> While GDAL's python bindings have become much more pythonic, errors are not
> automatically raised as python exceptions.  Instead, the default error behavior
> is to print a message to your stdout console and return ``None`` from the operation.
>
> If you experience ``AttributeError: 'NoneType' object has no attribute 'foo'``, this
> may be why.
>
> #### Pythonic Error Handling
> ~~~
> gdal.UseExceptions()
> ~~~
> {: .python}
{: .callout}



### Inspecting the Dataset:

Since rasters can be very, very large, GDAL will not read its contents into 
memory until we need to access those values.  Various formats support different
amounts of data (GeoTiff, should support exabytes-large files), so GDAL provides
various methods to access attributes of the dataset without reading in all
of the pixel values.

As with any python library, the methods available from the ``ds`` object can be
read through with ``help()``.

~~~
help(ds)
~~~
{: .python}

### Driver

Since GDAL will happily open any dataset it knows how to open, one of the attributes
we can query is the driver that was used:

~~~
ds.GetDriver().LongName
ds.GetDriver().ShortName
~~~
{: .python}

You'll recognize these names from when we previously looked into ``gdalinfo --format(s)``.  Either of these format names are acceptable for internal GDAL or if we're creating our own raster datasets.

### Coordinate Reference System:

Each dataset can have a coordinate reference system defined, which we can retrieve as Well-Known Text (WKT).

~~~
ds.GetProjection()
~~~
{: .python}

This isn't especially easy to read, but it is a valid projection string.  We can also print this
nicely with a couple of extra steps, using the ``osgeo.osr`` module for manipulating spatial references.

~~~
from osgeo import osr

raster_wkt = ds.GetProjection()
spatial_ref = osr.SpatialReference()
spatial_ref.ImportFromWkt(raster_wkt)
print spatial_ref.ExportToPrettyWkt()
~~~
{: .python}

If you're familiar with GIS software, the PROJ.4 projection string may be more useful:

~~~
print spatial_ref.ExportToProj4()
~~~
{: .python}

### Dimensions

Dimensions are accessed as attributes of the Dataset class.  X size represents the 
number of columns, Y size represents the number of rows.

~~~
ds.RasterXSize
ds.RasterYSize
~~~
{: .python}


### Block Sizes

Rasters are stored on disk in contiguous chunks called _blocks_, which become very useful
when trying to optimize your application for speed of execution.  We'll cover more on that
later, but for now, you can access the block size like so:

~~~
ds.GetBlockSize()
~~~
{: .python}

In this case, the blocksize is one row at a time, but different rasters can be laid
out differently on disk (represented by different block sizes).  The landcover
raster, for example, has a very different blocksize:

~~~
lulc_ds = gdal.Open('/data/landcover.tif')
lulc.GetBlockSize()
~~~
{: .python}

![LULC blocksizes](landcover-blocks.png)

## Reading Raster Values

Several GDAL objects have ``ReadAsArray()`` methods:

* ``gdal.Dataset``
* ``gdal.Band``
* ``gdal.RasterAttributeTable``

~~~
array = ds.ReadAsArray()
~~~
{: .python}

In our case, the raster ``/data/N37W120.tif`` only contains a single band, so 
both ``ds.ReadAsArray()`` and ``band.ReadAsArray()`` will return the same array.
The number of bands can be checked before loading the array:

~~~
ds.RasterCount
~~~
{: .python}

Even if there is only 1 band in the raster, you can still retrieve the band object
before accessing the raster's array. Note that some attributes, especially 
nodata value and band-specific metadata.
For a full listing of band attributes, see the 
[GDAL Data Model documentation](http://www.gdal.org/gdal_datamodel.html) and the 
[python API docs](http://www.gdal.org/python/osgeo.gdal.Band-class.html).

~~~
band = ds.GetRasterBand(1)
array = band.ReadAsArray()
nodata = band.GetNoDataValue()
metadata = band.GetMetadata()
~~~
{: .python}


While ``ReadAsArray()`` can be used to read the whole array into memory,
you can also specify a subset of the raster or band to open with a few
optional parameters to ``ReadAsArray()``.

~~~
band = ds.GetRasterBand(1)
full_array = band.ReadAsArray()

# Start at index (100, 100) and read in an array 250 pixels wide
array_part = band.ReadAsArray(
    xoff=100,
    yoff=100,
    xsize=250,
    ysize=250)
~~~
{: .python}

![Blocks read in and discarded for a small window of values](N37W120-read-blocks.png)

## Copying Raster Datasets

### Copying files without GDAL:

~~~
import os
os.copyfile(
    '/path/to/raster.tif',
    '/path/to/newraster.tif')
~~~
{: .python}

Or if your raster is a whole folder (as with ESRI Binary Grids):

~~~
import shutil
shutil.copytree(
    '/path/to/rasterdir',
    '/path/to/newrasterdir')
~~~
{: .python}

### Copying files with GDAL CLI utilities

~~~
gdalmanage copy /data/N37W120.tif /tmp/N37W120_copy.tif
~~~
{: .shell}


### Copying files with GDAL SWIG bindings 
~~~
from osgeo import gdal
driver = gdal.GetDriverByName('GTiff')
new_ds = driver.CreateCopy('/path/to/new_raster.tif', ds)
new_ds = None  # flush the dataset to disk and close the underlying objects.
~~~
{: .python}


### Creating new files with GDAL

~~~
from osgeo import gdal
driver = gdal.GetDriverByName('GTiff')
new_ds = driver.Create(
    'path/to/new_raster.tif',
    400,  # xsize
    600,  # ysize
    1,    # number of bands
    gdal.GDT_Float32,  # The datatype of the pixel values
    options=[  # Format-specific creation options.
        'TILED=YES',
        'BIGTIFF=IF_SAFER',
        'BLOCKXSIZE=256',  # must be a power of 2
        'BLOCKYSIZE=256'   # also power of 2, need not match BLOCKXSIZE
    ])

# fill the new raster with nodata values
new_ds.SetNoDataValue(-1)
new_ds.fill(-1)

# When all references to new_ds are unset, the dataset is closed and flushed to disk
new_ds = None
~~~
{: .python}

## Writing to a raster

Unlike reading to an array, writing only happens at the band level.

~~~
writeable_ds = gdal.Open('/path/to/raster.tif', gdal.GA_Update)
band = writeable_ds.GetRasterBand(1)

array = band.ReadAsArray()
array += 1
band.WriteArray(array)

band = None
ds = None
~~~
{: .python}

> ## A note about python's memory model
>
> GDAL's python bindings interact with low-level C++ libraries, where memory is managed very
> explicitly.  Python uses a system of reference counting to determine when python objects
> should be cleaned up and their memory freed.  This can sometimes lead to situations where
> GDAL expects certain objects to exist in memory, but Python has cleaned them up already.
> When this happens, the OS detects that GDAL is reaching into memory it's not supposed to
> access (which could be a security hazard), and kills the application via a Segmentation
> Fault.
{: .callout}

### Other libraries that make use of GDAL:

Show some examples of what might be different about these libraries.

* rasterio
* PostGIS
* GeoDjango (via postGIS)

Exercises:
 - Create a trivial raster from scratch with small dimensions
 - Reproject a DEM into a new CRS 
 - Virtual Raster formats - why they can be awesome.

Things to elaborate on:
 - Virtual filesystems vs. Virtual rasters (VRT)
