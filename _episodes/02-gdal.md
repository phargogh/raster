---
title: "Using GDAL"
teaching: 30
exercises: 15
questions:
- "What functionality does xarray offer?"
- "When should I use xarray?"
objectives:
- "selection and subsetting of array datasets using labeled indexing"
- "grouping data and applying statistical functions across multiple dimensions"
- "visualizing 1 and 2 dimensional slices of array data"
keypoints:
- xarray 
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

Official bindings available for other languages:
* Python (<a href="http://pypi.python.org/pypi/GDAL">PyPI</a>)
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
ds = gdal.Open('<rootDir>/raster.tif')
~~~
{: .python}

>## Filepath encodings:
> GDAL expects the path to the raster to be ASCII or UTF-8.
> This is common on linux and macs, but Windows is usually
> [ISO-8859-1 (Latin-1)](https://en.wikipedia.org/wiki/ISO/IEC_8859-1).
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
> GDAL uses a stack to allow configuration of its error handling.  This allows us to
> push an error handler when needed, and pop it when we're finished.
>
> ~~~
> def _gdal_error_handler(*args):
>    """Raise an exception when a GDAL exception occurs."""
>    raise ValueError(*args)
> 
> gdal.PushErrorHandler(_gdal_error_handler)
> # Do something that requires this exception
>
> # Pop the handler from the stack when we're finished.
> gdal.PopErrorHandler()
> ~~~
> {: .python}
{: .callout}


You'll notice this seemed to go very fast. That is because this step does not actually ask Python to read the data into memory. Rather, GDAL is just scanning the contents of the file.. 

### Inspecting the Dataset contents:

Since rasters can be very, very large, GDAL will not read its contents into memory unless requested.

~~~
help(ds)
~~~
{: .python}

## Dataset Properties

Xarray datasets have a number of [properties](http://xarray.pydata.org/en/stable/data-structures.html#dataarray) that you can view at any time:

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

### Other libraries that make use of GDAL:

Show some examples of what might be different about these libraries.

* rasterio
* PostGIS
* GeoDjango (via postGIS)

