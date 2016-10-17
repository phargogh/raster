---
title: "Introduction: Working with Raster Data"
teaching: 15
exercises: 0

questions:
- "What are the characteristics of a Raster?"
- "How can raster data be accessed through python?"

objectives:
- explore how to handle these types of datasets with python
- understand the basic characteristics of raster datasets

keypoints:
- gridded data that vary in space and time are common in many geospatial applcations (e.g. climatology)
- new tools are needed that can accommodate the complexity and size of modern multidimensional datasets
- GIS tools (e.g. QGIS, SAGA GIS) are usually needed to visualize these datasets

---
### Overview:

Scientists working with spatial data often need to manipulate datasets structured as arrays.  A common example is in working with hydrological modelling (e.g. where will water flow in a storm event?) using topographical data gathered from the US Geological Survey, or based on aerial or lidar photography gathered from a plane flying below the clouds.


### Characteristics of a Raster:

#### Coordinate Reference System

Raster datasets are fundamentally images, where each pixel has a value.  The spatial element of this dataset, however, lies in its Coordinate Reference System (CRS).  Here's an example CRS, represented as <a href="https://en.wikipedia.org/wiki/Well-known_text">Well-Known text </a>:

{% highlight text %}
PROJCS["NAD83 / UTM zone 10N",                          # The Coordinate system
    GEOGCS["NAD83",
        DATUM["North_American_Datum_1983",              # The datum (shape of the earth)
            SPHEROID["GRS 1980",6378137,298.257222101,
                AUTHORITY["EPSG","7019"]],
            AUTHORITY["EPSG","6269"]],
        PRIMEM["Greenwich",0,
            AUTHORITY["EPSG","8901"]],
        UNIT["degree",0.01745329251994328,
            AUTHORITY["EPSG","9122"]],
        AUTHORITY["EPSG","4269"]],
    UNIT["metre",1,
        AUTHORITY["EPSG","9001"]],
    PROJECTION["Transverse_Mercator"],                  # Specific projection
    PARAMETER["latitude_of_origin",0],
    PARAMETER["central_meridian",-123],
    PARAMETER["scale_factor",0.9996],
    PARAMETER["false_easting",500000],
    PARAMETER["false_northing",0],
    AUTHORITY["EPSG","26910"],
    AXIS["Easting",EAST],
    AXIS["Northing",NORTH]]

{% endhighlight %}

{% highlight python%}
from osgeo import gdal

dataset = gdal.Open('path/to/raster.tif')
dataset.GetProjection()
{% endhighlight %}

This collection of numbers and standards describes how to transform the 3-dimensional surface of the earth into a 2-dimensional image.  Getting projections right is a tricky business, and one that takes a great deal of expertise.


#### Affine GeoTransform
Unfortunately, the CRS by itself is not enough to place the raster on the planet.  To do this, we need the Affine Geotransform, which allows us to map pixel coordinates into georeferenced space.


{% highlight python %}
from osgeo import gdal

dataset = gdal.Open('path/to/raster.tif')
dataset.GetGeoTransform()
{% endhighlight %}

{% highlight text %}

[ ... geotransform ...]

{% endhighlight %}


How the geotransform is used to calculate pixel coordinates in space:

    Xgeo = GT(0) + Xpixel*GT(1) + Yline*GT(2)
    Ygeo = GT(3) + Xpixel*GT(4) + Yline*GT(5)

Note that this significantly affects how pixels are indexed.  'North' could be either an
increase or decrease in the row index, depending on the geotransform.

Include an image of this effect, with a corresponding geotransform.

#### NoData Value

Raster datasets commonly make use of a **Nodata Value**, a numeric value that represents the lack of information in a pixel.  Visually, this is often represented as transparency.

SHOW AN IMAGE HERE

{% highlight python %}
from osgeo import gdal

dataset = gdal.Open('path/to/raster.tif')
band = dataset.GetRasterBand(1)
band.GetNoDataValue()
{% endhighlight %}

#### Bands

Bands are layers of values, where all layers share the same CRS and geotransform (so they overlap perfectly).  Depending on the source of your raster, you may have multiple bands with numeric values that represent different things.  A DEM might have a single band where values represent the height of a pixel relative to sea level.  Or you could use a landsat image, which uses three bands, one each for Red, Green, and Blue.

SHOW AN IMAGE OR TWO HERE WITH BAND EXAMPLES

{% highlight python %}
from osgeo import gdal

dataset = gdal.Open('path/to/raster.tif')
dataset.RasterCount
{% endhighlight %}

### Challenges with handling geospatial data

* Projections warp information, can lead to inaccuracies
* Size of raster data can be challenging to work around in a program
