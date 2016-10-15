---
title: "Efficient raster computation with PyGeoProcessing"
teaching: 45
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

* Your data is large but not big (your data can fit on a single computer)
* You have limited memory or are in a 32-bit environment
* You have a sequence of common geoprocessing steps to automate


### Why not just use GIS software?
* GIS usually requires a large installation
* Some GIS software is proprietary


### Local Operations

Work through a multi-raster vectorize_datasets example
Maybe calculate erosivity or something?

### Focal Operations

Work through a gaussian filter example

### iterblocks

Compare iterblocks speed vs. reading a whole array into memory.

### Routing



