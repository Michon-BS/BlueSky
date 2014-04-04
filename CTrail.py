""" 
Traffic trails class definition    : Data for trails

Methods:
    Trails()            :  constructor

Members: see create

Created by  : Jacco M. Hoekstra
Date        : September 2013

Modifation  :
By          :
Date        :
------------------------------------------------------------------
"""

import numpy as np

class Trails():
    
    def __init__(self,dttrail=30.):

        self.dt = dttrail               # Resolution of trail pieces in time

        self.col0 = np.array([[0],[0],[200]])           # Old trail colour
        self.col1 = np.array([[0],[255],[255]])        # New trail colour
        self.tcol0 = 60.                # After how many seconds old colour 

# Data on line pieces
        self.lat0 = np.array([])
        self.lon0 = np.array([])
        self.lat1 = np.array([])
        self.lon1 = np.array([])
        self.time = np.array([])
        self.col  = np.array([]) 
        self.acid = []
        return

#----------------------------------------------------------------------------
# Add linepieces for trails based on traffic data

    def update(self,t,aclat,aclon,lastlat,lastlon,lasttim,acid):

# Check for update
        delta = t-lasttim
        idxs = np.where(delta > self.dt)[0]

# Use temporary list for fast append
        lstlat0 = []
        lstlon0 = []
        lstlat1 = []
        lstlon1 = []
        lsttime = []

# Add all a/c which need the update        
#        if len(idxs)>0:
#            print "len(idxs)=",len(idxs)
        for i in idxs:

# Add to lists            
            lstlat0.append(lastlat[i])
            lstlon0.append(lastlon[i])
            lstlat1.append(aclat[i])
            lstlon1.append(aclon[i])
            lsttime.append(t)
            self.acid.append(acid[i])

# Update aircraft record
            lastlat[i] = aclat[i]
            lastlon[i] = aclon[i]
            lasttim[i] = t

# Add resulting linepieces
        self.lat0 = np.concatenate((self.lat0,np.array(lstlat0)))
        self.lon0 = np.concatenate((self.lon0,np.array(lstlon0)))
        self.lat1 = np.concatenate((self.lat1,np.array(lstlat1)))
        self.lon1 = np.concatenate((self.lon1,np.array(lstlon1)))
        self.time = np.concatenate((self.time,np.array(lsttime)))

# Update colours
        self.col = 1.-np.minimum(self.tcol0,np.abs(t-self.time))/self.tcol0

# Done
        return
#----------------------------------------------------------------------------
# Clear trails

    def clear(self):

 # Data on line pieces
        self.lat0 = np.array([])
        self.lon0 = np.array([])
        self.lat1 = np.array([])
        self.lon1 = np.array([])
        self.time = np.array([])
        self.col  = np.array([]) 
        self.acid = []
        return       