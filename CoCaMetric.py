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
            

class CoCaMetric():
    
    def __init__(self,regions):
        
        
        self.region = regions
        self.oldaircraft = np.zeros((1000,1), dtype = [('callsign','|S10'),('cellnumber',int), ('time',int),('totaltime',int)])       
        self.newaircraft = np.zeros((1000,1), dtype = [('callsign','|S10'),('cellnumber',int), ('time',int),('totaltime',int)])
        #self.cells = np.zeros((self.region.nlevels*self.region.ncells*self.region.ncells,1), dtype = [('cellnumber',int),('interactions',int),('ntraf',int)])
        #for i in range(0,len(self.cells)):
        #    self.cells['cellnumber'][i] = i + 1
#        plt.close()
        
        self.numberofcells = self.region.ncells*self.region.ncells*self.region.nlevels
        
        names = []
        for i in range(0,self.numberofcells):
            names.append("cell"+str(i))
            
        formats = []
        for i in range(0,self.numberofcells):
            formats.append("|S10")
            
        ndtype = {'names':names, 'formats':formats}
        self.cells = np.zeros((500,6), dtype = ndtype)
        self.resettime = 5 #seconds
        self.deltaresettime = self.resettime
        self.iteration = 0
        
        formats = []
        for i in range(0,self.numberofcells):
            formats.append(float)
            
        ndtype = {'names':names, 'formats':formats}
        oneday = 86400 # second in one day
        numberofrows = oneday / self.resettime
        numberofrows = 3
        self.precocametric = np.zeros((numberofrows,5), dtype = ndtype)
        self.cocametric = np.zeros((numberofrows,6), dtype = ndtype)
        plt.ion()
        
        
        
        #plt.colorbar()
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



    
    def findCell(self,cells,lat,lon,fl):
        i = 0
        j = 0
        k = 0
        
        for i in range(0,len(cells),self.region.ncells*self.region.nlevels):
            if (cells[0,0]) <= lat < (cells[0,0]+0.6):
                break
            if (cells[i,0] < lat < cells[0,0] and cells[i,0] > cells[-1,0]) :
                break
            else:
                i = -10000
        
        if i > -1 :
            
            for j in range(0,self.region.ncells*self.region.nlevels,self.region.nlevels):

                if cells[i+j,1] > lon and lon < (cells[-1,1]+0.6) and lon > cells[0,1]:
                    j = j - self.region.nlevels
                    break
                if cells[i+j,1]+0.6 > lon and lon < (cells[-1,1]+0.6) and lon > cells[0,1]:
                    break
                else:
                    j = -10000
   
            if j > - 1:
                for k in range(0,self.region.nlevels,1):
                    if cells[i+j+k,2] > fl and fl < (cells[-1,2]+self.region.deltaFL) and fl > cells[0,2]:
                        k = k -1
                        break                
                    else:
                        k = -10000
                                                      
        if (i+j+k) < 0:
            i=-1
            j=0
            k=0
        
        return i+j+k
    
       
        
#    def plot_interactions(self):
#        
#        plotcells = np.sort(self.cells, axis = 0, order='interactions')[-3:]
#        
#        
#        
#        label = np.vstack(plotcells['cellnumber'])
#        x = np.arange(len(label))
#        y1 = np.vstack(plotcells['interactions'])
#        
#        
#        colLabels=("Interactions","")
#        nrows, ncols = len(x)+1, len(colLabels)
#        hcell, wcell = 0.3, 0.5
#        hpad, wpad = 0, 0.5    
#        fig1=plt.figure(num = 1, figsize=(ncols*wcell+wpad, nrows*hcell+hpad))
#        ax = fig1.add_subplot(111)
#        ax.axis('off')
#        
#        #do the table
#        ax.table(cellText=y1,colLabels=colLabels, rowLabels = label ,loc='center')        
#        
#        
##        plt.bar(x,y)
##        plt.xticks(x,str(label))
#         #plt.show()
#        
#        
#        return
    
#    def cell_interactions(self,cellN):
#        
#        # Interactions
#        itemscount = np.array(collections.Counter(cellN).items())
#        if len(itemscount) > 0:
#            for number in range(0,self.region.ncells*self.region.ncells*self.region.nlevels):
#                j = np.where(itemscount[:,0] == number)
#                
#                if np.size(j) == 0:
#                    
#                    self.cells['interactions'][number] = 0
#                else:
#                    
#                    self.cells['interactions'][number] = itemscount[j,1]*(itemscount[j,1]-1)
#            
#            self.plot_interactions()
#        
#        return
#    
#    
#    
#    def celltime(self,time):
#        
#        
#        
#        for i in range(0,len(self.newaircraft)):
#            
#            j = np.where(self.oldaircraft['callsign'] == self.newaircraft['callsign'][i])[0]
#            
#            if np.size(j) == 1:
#                
#                if self.oldaircraft['cellnumber'][j] == self.newaircraft['cellnumber'][i]:
#                    self.newaircraft['time'][i] = time - self.oldaircraft['totaltime'][i]                   
#                    
#                else:
#                    self.newaircraft['totaltime'][i] = time - self.oldaircraft['totaltime'][i]
#                    self.cells['ntraf'][i] = self.cells['ntraf'][i] + 1
#            
#        self.oldaircraft = self.newaircraft
#        
#        
#        return self.newaircraft  
    
    def cellPlot(self,traf):
        



                 
        cell = [floor(x/12) for x in traf.cell]
        count = collections.Counter(cell)
        count = np.array(count.items())
        
        flcells = count
        if np.size(count)>0:        
            flcells = count[:,0]    
        #plotdata
    
        z = np.array([0])
        for number in range(0,self.region.ncells*self.region.ncells):
            i = np.where(flcells == (number))           
            
            if np.size(i) == 0:
                z = np.append(z,0)
            else:
                i = i[0]
                z = np.append(z,count[i,1])
                
        z = np.delete(z, (0), axis=0)    
        zdata = np.reshape(z,(-1,self.region.ncells))
        fig = plt.figure(1)
        ax = fig.add_subplot(1, 1, 1)
        ax.imshow(zdata, interpolation='nearest')
        
           
        #plt.savefig("output/images/coca_20120727-79am-"+str(self.iteration)+".PNG")
        plt.show()
        
        
        return
        
    def applyMetric(self):
        
        for i in range(0,self.numberofcells):
            name = 'cell'+str(i)
            
            l = self.iteration                        
                        
            times = []
            headings = []
            speeds = []
            vspeeds = []
            actimes = []
            
            for j in range(0,len(self.cells[name])):
                if self.cells[name][j][1] != "":                  
                    times.append(float(self.cells[name][j][1]))
                    headings.append(float(self.cells[name][j][2]))
                    speeds.append(float(self.cells[name][j][3]))
                    vspeeds.append(float(self.cells[name][j][4]))
                    actimes.append(float(self.cells[name][j][1]))
            
            indices = np.argsort(times)
            times.sort()

            headings = [headings[z] for z in indices]
            speeds = [speeds[y] for y in indices]
            vspeeds = [vspeeds[x] for x in indices]
            actimes = [actimes[w] for w in indices]
            
            
            for w in range(0,len(vspeeds)):
                if vspeeds[w] <= 500 and vspeeds[w] >= (-500):
                    vspeeds[w] = 0
                elif vspeeds[w] > 500:
                    vspeeds[w] = 1
                elif vspeeds[w] < (-500):
                    vspeeds[w] = -1

            

            self.precocametric[name][l][0] = (sum(times)/self.deltaresettime)
            
            acinteractions = []            
            spdinteractions = []
            hdginteractions = []
            vspdinteractions = []

            if len(times) > 1:
                for k in range(0,len(times)):
                    aircraft = len(times)
                    
                    time = times[0]/self.deltaresettime
                    actime = actimes[0]/self.deltaresettime
                    acinteractions.append(aircraft*(aircraft-1)*(actime**aircraft))
                    
                   
                    counter = 0
                    for t in range(0,1):
                        for u in range(t+1,len(speeds)):
                            if abs(speeds[t]-speeds[u]) > 35:
                                counter = counter + 1  
                    spdinteractions.append(2*counter*(time**(counter+1)))
                    

                    counter = 0
                    for t in range(0,1):
                        for u in range(t+1,len(headings)):
                            if abs(headings[t]-headings[u]) > 20:
                                counter = counter + 1 
                    hdginteractions.append(2*counter*(time**(counter+1)))
                                        
                    
                    counter = 0
                    for t in range(0,1):
                        for u in range(t+1,len(vspeeds)):
                            if vspeeds[t] != vspeeds[u]:
                                counter = counter + 1
                    vspdinteractions.append(2*counter*(time**(counter+1)))
                    
                    for x in range(1,len(actimes)):
                        actimes[x] = actimes[x] - actimes[0]
                    
                    del actimes[0]
                    del times[0]
                    del vspeeds[0]
                    del speeds[0]
                    del headings[0]

                self.precocametric[name][l][1] = sum(acinteractions)
                self.precocametric[name][l][2] = sum(spdinteractions)
                self.precocametric[name][l][3] = sum(hdginteractions)
                self.precocametric[name][l][4] = sum(vspdinteractions)
                
                self.cocametric[name][l][1] = self.precocametric[name][l][1] / self.precocametric[name][l][0]
                self.cocametric[name][l][2] = self.precocametric[name][l][2] / self.precocametric[name][l][0]
                self.cocametric[name][l][3] = self.precocametric[name][l][3] / self.precocametric[name][l][0]
                self.cocametric[name][l][4] = self.precocametric[name][l][4] / self.precocametric[name][l][0]
                self.cocametric[name][l][0] = self.cocametric[name][l][1] * (self.cocametric[name][l][2] + self.cocametric[name][l][3] + self.cocametric[name][l][4])
            

  
        print "Iteration number: "+str(self.iteration+1)
        print "Reset time = "+str(self.resettime)

        
        
        return
    
    def reset(self):
        
        #self.applyMetric()        
        
        
        names = []
        for i in range(0,self.numberofcells):
            names.append("cell"+str(i))
            
        formats = []
        for i in range(0,self.numberofcells):
            formats.append("|S10")
            
        ndtype = {'names':names, 'formats':formats}
        self.cells = np.zeros((500,6), dtype = ndtype)
        
        return
    
    def AircraftCell(self,traf,cells,time,sim):
         
        if floor(time) >= self.resettime:
            sim.pause()            
            self.reset()
            self.resettime = self.resettime + self.deltaresettime
            self.iteration = self.iteration + 1
            filedata = "output/data/coca_20120727-78am-1hour.npy"
            #self.cellPlot(traf)
            #np.save(filedata,self.cocametric)
            sim.play()
        
        traf.cell = []

        for i in range(traf.ntraf):
            lat = traf.lat[i]
            lon = traf.lon[i]
            fl = traf.alt[i]/ft
            cellN = self.findCell(cells,lat,lon,fl)
            
            if cellN > 0:
                traf.cell = np.append(traf.cell, cellN)
                name = 'cell'+str(cellN)

                index = np.where(traf.id[i] == self.cells[name][:,[0]])[0]                
                if len(index) != 1:

                    j = 0
                    for j in range(0,len(self.cells[name])):
                        if self.cells[name][j][0] == "":
                            break
                    self.cells[name][j][0] = traf.id[i]
                    self.cells[name][j][1] = time
                    self.cells[name][j][2] = traf.ahdg[i]
                    self.cells[name][j][3] = eas2tas(traf.aspd[i],traf.aalt[i])/kts
                    self.cells[name][j][4] = traf.avs[i]/fpm
                    self.cells[name][j][5] = time
                if len(index) == 1:
                    createtime = float(self.cells[name][index[0]][5])
                    self.cells[name][index[0]][1] = str(time - createtime)
                
                
                    
#                self.newaircraft['callsign'][i] = traf.id[i]
#                self.newaircraft['cellnumber'][i] = 
               
                     
        return
   
class regions():    

    def __init__(self):
        self.lat = 53.8
        self.lon = 2
        self.fll = 8500
        self.flu = 41500
        self.bearingS = 180
        self.bearingE = 90
        self.deltaFL = 3000
        self.distance = 20
        self.ncells = 12
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

