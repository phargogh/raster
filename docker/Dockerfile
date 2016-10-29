FROM continuumio/anaconda
RUN apt-get install -y gcc
RUN apt-get install -y g++
RUN apt-get install -y tar git curl nano wget dialog net-tools build-essential
RUN apt-get install -y pyqt4-dev-tools
RUN mkdir /data
RUN apt-get -y install python-gdal
RUN conda install rasterio
RUN pip install pygeoprocessing
RUN conda install numpy
RUN conda install cython
RUN conda install shapely
COPY /data/ /data