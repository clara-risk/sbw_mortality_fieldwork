#coding: utf-8
import geopandas as gpd
from shapely.geometry import Polygon, Point
import pyproj
import numpy as np
import sys,os
import time
import matplotlib.pyplot as plt
import math
import random
from random import randint
import itertools
import pandas as pd
from osgeo import ogr, gdal, osr

def load_ndarray(shapefile,dirname,file_name):

    ini_array = np.load(dirname+file_name)

    return ini_array 

def make_tiff(shapefile,array,proj,file_out):
    '''Output the np array as a tiff
    Parameters
    shapefile (str): path to study area shapefile 
    array (np array) = input 2d np array
    proj (str): information about the output tiff, such as projection, only supports NAD83 Ontario MNR Lambert, WGS84 UTM zone 15N, &
    Canada_Albers_Equal_Area_Conic
    IT NEEDS TO BE THE SAME AS THE SHAPEFILE YOU ORIGINALLY USED
    file_out (str): where you will save to including name and extention
    res (int): X and Y resolution in m 
    '''
    #Get reference geotranform from shapefile:
    na_map = gpd.read_file(shapefile)
    bounds = na_map.bounds
    xmax = bounds['maxx']+200000 
    xmin= bounds['minx']-200000 
    ymax = bounds['maxy']+200000 
    ymin = bounds['miny']-200000

    pixelHeight = 10000
    pixelWidth = 10000
    res = 10000
    num_col = int((xmax - xmin) / pixelHeight)+1
    num_row = int((ymax - ymin) / pixelWidth)+1

    
    #Process array - so in Python, it uses origin bottom left but in spatial imagery it's top left :( 
    #https://gis.stackexchange.com/questions/345595/raster-projection-is-inverted-python-gdal
    #We need to flip & transpose the array before outputting to raster
    
    #new_array = np.flipud(array.T)
    new_array = np.flipud(array)

    #shapefile with the from projection
    driver = gdal.GetDriverByName('GTiff')

    if proj == 'MNR_lambert':
        
        srs = 'PROJCS["NAD83 / Ontario MNR Lambert",GEOGCS["NAD83",DATUM["North_American_Datum_1983",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],AUTHORITY["EPSG","6269"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4269"]],UNIT["metre",1,AUTHORITY["EPSG","9001"]],PROJECTION["Lambert_Conformal_Conic_2SP"],PARAMETER["standard_parallel_1",44.5],PARAMETER["standard_parallel_2",53.5],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-85],PARAMETER["false_easting",930000],PARAMETER["false_northing",6430000],AUTHORITY["EPSG","3161"],AXIS["Easting",EAST],AXIS["Northing",NORTH]]'
    elif proj == 'UTM_zone15N': 
        srs = 'PROJCS["WGS 84 / UTM zone 15N",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],UNIT["metre",1,AUTHORITY["EPSG","9001"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-93],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],AUTHORITY["EPSG","32615"],AXIS["Easting",EAST],AXIS["Northing",NORTH]]'
    elif proj == 'canada_albers': 
        srs = 'PROJCS["Canada_Albers_Equal_Area_Conic",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137,298.257222101]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Albers"],PARAMETER["False_Easting",0],PARAMETER["False_Northing",0],PARAMETER["central_meridian",-96],PARAMETER["Standard_Parallel_1",50],PARAMETER["Standard_Parallel_2",70],PARAMETER["latitude_of_origin",40],UNIT["Meter",1]]'
    else:
        print('Not a valid projection!')

        

    #set spatial reference and transformation
    sourceprj = osr.SpatialReference(srs)

    output_file = driver.Create(file_out, num_col, num_row, 1, gdal.GDT_Float32)
    output_file.SetGeoTransform((xmin, res, 0, ymax, 0, -res))
    output_file.SetProjection(srs)
    output_file.GetRasterBand(1).WriteArray(new_array, 0, 0)
            
    dataSource = None
    output_file = None
    


if __name__ == "__main__":

    dirname = os.path.abspath(os.path.dirname(__file__))

    shapefile = dirname+'/study_area/QC_ON_albers_dissolve.shp'

    in_array = load_ndarray(shapefile,dirname+'/data/','duration3_RF.npy')

    make_tiff(shapefile,in_array,'canada_albers',dirname+'/tiff/duration3.tif')
    

    
