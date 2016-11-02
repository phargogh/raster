---
title: "Efficient raster computation with PyGeoProcessing"
teaching: 20 
exercises: 15 
questions:
- "What problems can PyGeoProcessing help me solve?"
- "When should I use PyGeoProcessing?"
objectives:
- "Understand how to execute local (pixel stack) operations"
- "Understand how to execute focal (convolution) operations"
- "Understand how to route a DEM"
keypoints:
- "PyGeoProcessing provides programmable operations for efficient raster computations"
- "Looping in python is slow; improve speed by iterating over blocks"
---

### What is PyGeoProcessing?

* Under active development by the [Natural Capital Project](https://naturalcapitalproject.org)
* Developed to provide memory-efficient geoprocessing for InVEST 
    ([website](http://naturalcapitaproject.org/invest), [PyPI](https://pypi.python.org/pypi/natcap.invest), a suite of 
    spatially-relevant Ecosystem Service models so that decision-makers running older or
    low-powered systems can run our software and make better-informed landuse/marine spatial
    planning decisions.
* Key features:
    * Memory-efficiency is top priority
    * Computational efficiency is 2nd priority
    * Programmable raster stack calculation
    * D-infinity routing:
        * Flow direction
        * watershed delineation
    * Convolutions
    * Dinstance transforms
    * Helper functions for:
        * iterating over raster blocks
        * extracting key raster metadata
        * aligning and resampling stacks of rasters
        * Creating new datasets

### What PyGeoProcessing can do for you

#### When it makes sense to use PyGeoProcessing
* Your data is accessible on a single computer ("*large* but not *big*")
* You have limited memory or are in a 32-bit programming environment

#### Why not just use GIS software?
* Most GIS installations are very large, and may break your script with each upgrade.
* GIS don't always provide pure-python interfaces

#### Why not just use ``numpy`` directly on full matrices?
If you can, go for it!  PyGeoProcessing is best for cases where your data are large
enough that you cannot fit it all into main memory, and for efficiently automating
complex workflows.  It won't be relevent for every use case.


### Local Operations: ``pygeoprocessing.vectorize_datasets``

Local operations create a single output layer that is a function of various input layers.
Most GIS tools provide a Raster Calculator that does something similar.

To be able to use ``vectorize_datasets`` effectively, we need to first be able to define our
problem in terms of block-level operations.

A trivial example would be to add pixels together.

In PyGeoProcessing, ``pygeoprocessing.vectorize_datasets`` allows us to do this with all
of the flexibility of the python programming language.

#### Special case: reclassification ``pygeoprocessing.reclassify_dataset_uri``




Work through a multi-raster vectorize_datasets example
Maybe calculate erosivity or something?

### Focal Operations:  ``pygeoprocessing.raster_focal_op``

* Focal operations are technicallly the class,
    * pygeoprocessing only has convolutions at the moment
    * true focal operations could be defined via iterblocks, or by looping over each pixel and indexing accordingly

Demonstrate a gaussian filter.


### Zonal Statistics: ``pygeoprocessing.aggregate_values``

Work through a gaussian filter example

### Routing: ``pygeoprocessing.routing``

Delineate a watershed?

### Block iteration: ``pygeoprocessing.iterblocks``

General-purpose block iterations

#### Note on execution speed

Compare iterblocks speed vs. reading a whole array into memory.
Why is this slow?


