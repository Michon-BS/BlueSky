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

        self.tcol0 = 60.                 # After how many seconds old colour 

# Foreground data on line pieces
        self.lat0 = np.array([])
        self.lon0 = np.array([])
        self.lat1 = np.array([])
        self.lon1 = np.array([])
        self.time = np.array([])
        self.col  = np.array([]) 
        self.acid = []

# background copy of data
        self.bglat0 = np.array([])
        self.bglon0 = np.array([])
        self.bglat1 = np.array([])
        self.bglon1 = np.array([])
        self.bgtime = np.array([])
        self.bgcol  = np.array([]) 
        self.bgacid = []

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
        self.col = 255. *  \
                  (1.-np.minimum(self.tcol0,np.abs(t-self.time))/self.tcol0)

# Done
        return

#----------------------------------------------------------------------------
# Buffer trails: Move current stack to background

    def buffer(self):
        
        self.bglat0 = np.append(self.bglat0,self.lat0)
        self.bglon0 = np.append(self.bglon0,self.lon0)
        self.bglat1 = np.append(self.bglat1,self.lat1)
        self.bglon1 = np.append(self.bglon1,self.lon1)
        self.bgtime = np.append(self.bgtime,self.time)
# No color saved: bBackground: always 'old color' self.col0

        self.bgacid = self.bgacid + self.acid
        
        self.clearfg()  # Clear foreground trails

        return

#----------------------------------------------------------------------------
# Clear trails foreground

    def clearfg(self):   # Foreground

 # Data on foreground line pieces
        self.lat0 = np.array([])
        self.lon0 = np.array([])
        self.lat1 = np.array([])
        self.lon1 = np.array([])
        self.time = np.array([])
        self.col  = np.array([]) 
        self.acid = []

        return       # Clear trails

#----------------------------------------------------------------------------
# Clear trails background

    def clearbg(self):   # Background

 # Data on background line pieces
        self.bglat0 = np.array([])
        self.bglon0 = np.array([])
        self.bglat1 = np.array([])
        self.bglon1 = np.array([])
        self.bgtime = np.array([])
        self.bgacid = []

        return

#----------------------------------------------------------------------------
# Clear all data
    def clear(self):   # Foreground and background

        self.clearfg()
        self.clearbg()

        return           