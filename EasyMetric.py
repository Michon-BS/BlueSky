# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from aero import *
from math import degrees
import pygame as pg
import collections

#from CScreen import Screen
#
#cx,cy = -1,-1            
#            for i in traf.metric.regions.cellarea:
#                
#                x,y = self.ll2xy(i[0],i[1])
#                print(x,y)
#                if ((cx>0 and cy>0 and \
#                     cx < self.width and cy < self.height) or (x>0 and y>0 \
#                    and x < self.width and y<self.height)):
#                   
#                pg.draw.lines(self.win,green,(cx,cy),(x,y))
#                cx,cy = x,y
            

class EasyMetric():
    
    def __init__(self):
        
#        plt.close()
#        plt.ion()
#        self.plotntraf,= plt.plot([], [])
        
        #self.plotbar, = plt.bar([],[])
        return
    
    def update_line(self,ntraf,t):
               
#        if t < 0.1:
#            
#            self.__init__()
#        
#        t = int(t)
#        self.plotntraf.set_xdata(np.append(self.plotntraf.get_xdata(), t))
#        self.plotntraf.set_ydata(np.append(self.plotntraf.get_ydata(), ntraf))
#        plt.plot(t,ntraf,'b--o')
#        ax = plt.gca()        
#        ax.relim()
#        ax.autoscale_view()
        
        return
        
#    def update_bar(self,trafcell,t):
#               
#        if t < 0.1:
#            
#            self.__init__
#        
#        t = int(t)
#        self.plotbar.set_xdata(np.append(self.plotbar.get_xdata(), t))
#        self.plotbar.set_ydata(np.append(self.plotbar.get_ydata(), trafcell))
#        plt.plot(t,ntraf,'b--o')
#        ax = plt.gca()        
#        ax.relim()
#        ax.autoscale_view()
#        
#        return    


class findCell():
    
    def __init__(self):
        
               
        
        return
    
    def findCell(self,regions,lat,lon,fl):
        i = 0
        j = 0
        k = 0
        ncells = 25
        nlevels = 12
        for i in range(0,len(regions),ncells*nlevels):

            if (regions[i,0] < lat < regions[0,0] and regions[i,0] > regions[-1,0]) :
                break
            else:
                i = -1000
                
        for j in range(0,ncells*nlevels,nlevels):
            if regions[i+j,1] > lon and regions[i+j,1] < regions[-1,1] and lon > regions[0,1]:
                j = j - nlevels
                break
            else:
                j = -1000
                
        for k in range(0,nlevels,1):
            if regions[i+j+k,2] > fl and regions[i+j+k,2] < regions[-1,2] and fl > regions[0,2]:
                k = k -1
                break                
            else:
                k = -1000
                                                      
        if (i+j+k) < 0:
            i=-1
            j=0
            k=0
                      
        return i+j+k
    
    def cellACcount(self,cellN):
        
        cell = [floor(x/12) for x in cellN]
        count = collections.Counter(cell)
        count = np.array(count.items())
        
        cells = count
        if np.size(count)>0:        
            cells = count[:,0]
        
        
        #plotdata
    
        z = np.array([0])
        
        for number in range(0,25*25):
            i = np.where(cells == (number))           
            
            if np.size(i) == 0:
                z = np.append(z,0)
            else:
                i = i[0]
                z = np.append(z,count[i,1])
        
        z = np.delete(z, (0), axis=0)    
        zdata = np.reshape(z,(-1,25))
        
#        plt.imshow(zdata, interpolation='nearest')
#        plt.colorbar()
#        plt.show()
        
        return
    
    
    def cellAC(self,traf,sim,regions):
        
        traf.cell = []
               
        for i in range(traf.ntraf):
            lat = traf.lat[i]
            lon = traf.lon[i]
            fl = traf.alt[i]/ft
            cellN = self.findCell(regions,lat,lon,fl)
                            
            #print(cellN)
            traf.cell = np.append(traf.cell, cellN)
          
        self.cellACcount(traf.cell) 
        return
   
class Cells3D():

    def __init__(self):

        self.lat = 55
        self.lon = 1
        self.fll = 8500
        self.flu = 41500
        self.bearingS = 180
        self.bearingE = 90
        self.deltaFL = 3000
        self.distance = 20
        self.ncells = 25
        self.nlevels = 12
        
        return

     
    
    def addbox(self,lat,lon,regions):
        
        
        for i in range(0,self.ncells):
            for j in range(0,self.ncells):                
                for k in range(self.fll,self.flu+self.deltaFL,self.deltaFL):
                    box = np.array([lat,lon,k])
                    regions = np.vstack([regions,box])
            
                lat,lon = qdrpos(lat,lon,self.bearingE,self.distance)
                lat = degrees(lat)
                lon = degrees(lon)
            lon = self.lon
            lat,lon = qdrpos(lat,lon,self.bearingS,self.distance)
            lat = degrees(lat)
            lon = degrees(lon)

        return regions
        
    def cellArea(self,regions):
        point1 = [regions[0,0],regions[0,1]]
        point2 = [regions[self.ncells*self.nlevels-1,0],regions[self.ncells*self.nlevels-1,1]]
        point3 = [regions[(self.ncells-1)*self.ncells*self.nlevels,0],regions[(self.ncells-1)*self.ncells*self.nlevels,1]]
        point4 = [regions[self.ncells*self.ncells*self.nlevels-1,0],regions[self.ncells*self.ncells*self.nlevels-1,1]]
        self.cellarea = np.array([point1,point2,point3,point4])
#        print self.cellarea

        return self.cellarea    
    
    def makeRegions(self):
        
        regions = np.array([0,0,0])
            
        lat = self.lat
        lon = self.lon
        
          
        regions = self.addbox(lat,lon,regions)
        regions = np.delete(regions, (0), axis=0)
        
        
        
        return regions

