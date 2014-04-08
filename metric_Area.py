# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 13:09:18 2014

@author: Dennis Michon
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from aero import *
from math import degrees
import pygame as pg
import collections
import itertools as IT

class metric_Area():    

    def __init__(self):
        self.lat = 55.5
        self.lon = 1.7
        self.fll = 8500
        self.flu = 41500
        self.bearingS = 180
        self.bearingE = 90
        self.deltaFL = 3000
        self.distance = 20
        self.ncells = 18
        self.nlevels = 12
 
        self.regions = np.array([0,0,0])   
    
    
    def addbox(self,lat,lon):
        
        lat_0 = lat
        lat_00 = lat
        lon_0 = lon
        londiviser = 1
        for i in range(1,self.ncells+1):
            for j in range(1,self.ncells+1):                
                for k in range(self.fll,self.flu+self.deltaFL,self.deltaFL):
                    box = np.array([lat,lon,k])
                    self.regions = np.vstack([self.regions,box])
            
                if i == 1:
                    
                    lat,lon = qdrpos(lat,lon,self.bearingE,self.distance)
                    lat = degrees(lat)
                    lon = degrees(lon)
                    londiviser = (lon - lon_0) / self.ncells
                else:
                    lat,lon = qdrpos(lat,lon,self.bearingE,self.distance)
                    lat = degrees(lat)
                    lon = lon_0 + londiviser * j
            
            lat_0 = lat_00            
            lat,lon = qdrpos(lat_0,lon_0,self.bearingS,self.distance*i)
            lat = degrees(lat)
            lon = degrees(lon)
            lat_0 = lat

        return
        
    def cellArea(self):
        point1 = [self.regions[0,0],self.regions[0,1]]
        point2 = [self.regions[self.ncells*self.nlevels-1,0],self.regions[self.ncells*self.nlevels-1,1]]
        point3 = [self.regions[(self.ncells-1)*self.ncells*self.nlevels,0],self.regions[(self.ncells-1)*self.ncells*self.nlevels,1]]
        point4 = [self.regions[self.ncells*self.ncells*self.nlevels-1,0],self.regions[self.ncells*self.ncells*self.nlevels-1,1]]
        self.cellarea = np.array([point4,point2,point1,point3])
        #print self.cellarea

        return self.cellarea    
    
    def makeRegions(self):
        
        
            
        lat = self.lat
        lon = self.lon
        
          
        self.addbox(lat,lon)
        self.regions = np.delete(self.regions, (0), axis=0)
        
        
        
        return self.regions


    def area_of_polygon(self,x, y):
       
        area = 0.0
        for i in xrange(-1, len(x) - 1):
            area += x[i] * (y[i + 1] - y[i - 1])
        return area / 2.0
    
    def centroid_of_polygon(self,points):
        
        area = self.area_of_polygon(*zip(*points))
        
        result_x = 0
        result_y = 0
        N = len(points)
        
        points = IT.cycle(points)
        
        x1, y1 = next(points)
        for i in range(N):
            x0, y0 = x1, y1
            x1, y1 = next(points)
            cross = (x0 * y1) - (x1 * y0)
            result_x += (x0 + x1) * cross
            result_y += (y0 + y1) * cross
        result_x /= (area * 6.0)
        result_y /= (area * 6.0)
        return (result_x, result_y)
        
        
    def FIR_circle(self,navdb,firname_user,fir_radius):
        
        fir_lat = []
        fir_lon = []
        fir = []
        for i in range(0,len(navdb.fir)):
            if firname_user == navdb.fir[i][0]:
                fir_lat.append(navdb.fir[i][1])
                fir_lon.append(navdb.fir[i][2])
                fir.append((fir_lat[-1],fir_lon[-1]))
        
        fir = fir[0]
        fir = zip(fir[0],fir[1])
        fir_centroid = self.centroid_of_polygon(fir)
        
        return fir_centroid,fir_radius
        


