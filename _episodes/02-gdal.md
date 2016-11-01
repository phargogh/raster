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

### What is GDAL (Geospatial Data Abstraction Library)?

* C++ library originally developed as a side project by Frank Warmerdam
* Has become a major open-source member of the Open Source Geospatial Foundation
* OGR (GDAL-provided library for handing vector data) is also part of the project.
* Together, GDAL/OGR contains 1.1M lines of code (not including comments and whitespace.
* Almost ubiquitous in geospatial applications.


* originally developed by employees (Stephan Hoyer, Alex Kleeman and Eugene Brevdo) at [The Climate Corporation](https://climate.com/)
* xaray extends some of the core functionality of Pandas:
    * operations over _named_ dimensions
    * selection by label instead of integer location
    * powerful groupby functionality
    * database-like joins

### Supported Formats:

As of the latest version of GDAL, 142 formats are supported, but builds for various platforms may omit support for some formats.  The docker images for this tutorial include a GDAL build with support for 124 formats, including a few that have both raster and vector layers.

>## Not all formats are supported equally
>GDAL's drivers do not support all formats equally, and differences are 
> listed in `gdalinfo --formats`.
> * ``ro`` - read-only support
> * ``rw`` - reading and writing to existing files (and making copies) supported
> * ``rw+`` - reading, writing and creation of new files supported
> * ``v`` - the format supports virtual I/O
> * ``a`` - the format support subdatasets
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

### Access to GDAL libararies

GDAL is a C++ library, but you don't need to write your software in C++ to use it.

Official bindings [available for other languages](https://trac.osgeo.org/gdal/browser/trunk/gdal/swig?order=name):
* Python [(PyPI page)](http://pypi.python.org/pypi/GDAL)
* C# 
* Ruby
* Java
* Perl
* PHP

Of course, you can write your software in C++ if you like :)

## Using GDAL

### Sample dataset

Need to pick a dataset and show how to download it.

### begin by importing these libraries

~~~
import matplotlib
from osgeo import gdal
~~~

### Open the dataset

First we open the raster so we can explore its attributes, as in the introduction.  GDAL will detect the format if it can, and return a *gdal.Dataset* object.

~~~
ds = gdal.Open('data/N38W120.tif')
~~~
{: .python}

>## Filepath encodings in python 2.x:
> GDAL expects the path to the raster to be ASCII or UTF-8.
> This is common on linux and macs, but Windows is usually
> [ISO-8859-1 (Latin-1)](https://en.wikipedia.org/wiki/ISO/IEC_8859-1).
> Windows users can work around this by specifying the string encoding:
>
> ~~~
> ds = gdal.Open(unicode('data/N38W120.tif', 'utf-8'))
> ~~~
> or
> ~~~
> ds = gdal.Open('data/N38W120.tif'.decode('utf-8'))
> ~~~
>
> In Python 3.x, strings are encoded as UTF-8 by default.
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


You'll notice this seemed to go very fast. That is because this step does not actually ask Python to read the data into memory. Rather, GDAL is just scanning the contents of the file.. 

### Inspecting the Dataset contents:

Since rasters can be very, very large, GDAL will not read its contents into memory unless requested.

[API documentation here](http://gdal.org/python/osgeo.gdal.Band-class.html)

~~~
help(ds)
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

## Reading Raster Values

Several GDAL objects have ``ReadAsArray()`` methods:

* ``gdal.Dataset``
* ``gdal.Band``
* ``gdal.RasterAttributeTable``

~~~
array = ds.ReadAsArray()
~~~
{: .python}

To only read a specific band:

~~~
ds = gdal.Open('path/to/raster.tif')
band = ds.GetRasterBand(1)
array = band.ReadAsArray()
~~~
{: .python}

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

### Copying files with GDAL

~~~
from osgeo import gdal
driver = gdal.GetDriverByName('GTiff')
new_ds = driver.CreateCopy('/path/to/new_raster.tif', ds)
new_ds = None
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

> ## GDAL is not your typical python library!
> GDAL is first and foremost a C++ library, and while the bindings provided allow
> us to use it from python, there are several ways in which these libraries behave
> differently from typical python packages:
>
> #### API mirrors the original C++ 
> Most python packages these days adhere to [PEP8](https://www.python.org/dev/peps/pep-0008/),
> but the GDAL bindings mirror the C++ function calls as closely as possible.
>
> #### Errors do not raise exceptions by default
>
> #### Python crashes if we're not careful with object management
>
{: .callout}



## Basic visualization

Use matplotlib for some basic image previews.

### Other libraries that make use of GDAL:

Show some examples of what might be different about these libraries.

* rasterio
* PostGIS
* GeoDjango (via postGIS)
