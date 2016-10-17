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
* Developed to provide memory-efficient geoprocessing for InVEST, a suite of 
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

### When to use PyGeoProcessing:

Common use cases include:

* Your data is accessible on a single computer ("large but not big")
* You have limited memory or are in a 32-bit environment
* You need fast geoprocessing routines
* You don't have access to optimized GIS routines
* You need an easy way to perform operations on partially-overlapping raster data

### Why not just use GIS software?
* GIS usually requires a large installation with many dependencies
* Some GIS software is proprietary
* GIS doesn't always provide a pure-python interface

>## ``pygeoprocessing >= 0.3.0a22`` required!
> PyGeoProcessing is under active development, and fixes are released
> with regularity.  Be sure you have the latest changes!
> 
> ~~~
> >>> import pygeoprocessing
> >>> pygeoprocessing.__version__
> 0.3.0a22
> ~~~
> {: .python}
{: .callout}

### Local Operations: ``pygeoprocessing.raster_local_op``

Work through a multi-raster vectorize_datasets example
Maybe calculate erosivity or something?

### Focal Operations:  ``pygeoprocessing.raster_focal_op``

### Zonal Statistics: ``pygeoprocessing.aggregate_values``

Work through a gaussian filter example

### Block iteration: ``pygeoprocessing.iterblocks``

#### Note on execution speed

Compare iterblocks speed vs. reading a whole array into memory.

### Routing: ``pygeoprocessing.routing``

Delineate a watershed?


