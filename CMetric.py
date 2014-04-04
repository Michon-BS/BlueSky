""" 
Metric class definition : traffic metrics

Methods:
    Metric()                :  constructor

    update()                : add a command to the command stack
    close()                 : close file
   
Created by  : Jacco M. Hoekstra (TU Delft)
Date        : November 2013

Modifation  :
By          :
Date        :

"""

import time
from CoCaMetric import *
from CPAmetric import *
from tools import tim2txt


#----------------------------------------------------------------


class Metric():
    
    def __init__(self):    

# Create metrics file

        fname = time.asctime().replace(" ","-").replace(":","-")  \
                           +"met.txt"
        self.file = open("output/"+fname,"w")

# Write header
        self.write(0.0,"Header info tbd")        
        

# Last time for which Metrics.update was called 

        self.t0 = -9999   # force first time call

# Set time interval in seconds

        self.dt = 1  # [seconds]
        
        region = regions()
        
        self.cells = region.makeRegions()
        self.metricstime = 0
        self.tbegin = 0
        
        
        self.cellarea = region.cellArea()
        self.metric = (CoCaMetric(region),CPAmetric(self.cellarea))
        self.name = ("CoCa-Metric","CPA-Metric","Delete AC")
        self.metric_number = 1
        
    
        return

# Write: can be called from anywhere traf.metric.write( txt )
# Adds time stamp and ";"

    def write(self,t,line):
        self.file.write(tim2txt(t)+";"+line+chr(13)+chr(10))
        return        

# Update: to call for regular logging & runtime analysis

    def update(self,traf,sim,cmd):
        
# Only do something when time is there        
        if abs(sim.t-self.t0)<self.dt:
            return
        self.t0 = sim.t  # Update time for scheduler
        if self.metricstime == 0:
            self.tbegin = sim.t
            self.metricstime = 1
            print "METRICS STARTED"
            cmd.stack("AREA "+str(self.cellarea[2][0])+","+str(self.cellarea[2][1])+ \
               ","+str(self.cellarea[0][0])+","+str(self.cellarea[0][1]))



# A lot of smart Michon-code here, probably using numpy arrays etc.

        #self.metric.update_line(traf.ntraf,sim.t)
#        if sim.t >= 25200 and sim.t <= 25201:
#             cmd.stack("SAVEIC 7am")
#             print "done"

                
        
        if sim.t >= 0:
            if self.metric_number == 0:
                self.metric[self.metric_number].AircraftCell(traf,self.cells,sim.t-self.tbegin,sim)
            elif self.metric_number == 1:
                self.metric[self.metric_number].applymetric(traf,sim)
            
            
        deleteAC = []
        for i in range(0,traf.ntraf):
            if traf.avs[i] <= 0 and (traf.aalt[i]/ft) < 750 and traf.aspd[i] < 300:
                deleteAC.append(traf.id[i])

            elif traf.avs[i] <=0 and (traf.aalt[i]/ft) < 10:
                deleteAC.append(traf.id[i])
            
            if traf.avs[i] <=0 and traf.aspd[i] < 10:
                deleteAC.append(traf.id[i])
        
        for i in range(0,len(deleteAC)):
            traf.delete(deleteAC[i])

# Heartbeat for test
        self.write(sim.t,"NTRAF;"+str(traf.ntraf))
        return
    
    def plot(self,sim):

# Pause simulation
        sim.pause()
        
# Open a plot window attached to a command?

#    plot, showplot and other matplotlib commands

# Continue simulation
        sim.run()
        return      
    