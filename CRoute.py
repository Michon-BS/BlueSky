
""" 
Route class definition   : Route data for an aircraft (basic FMS functionality)

Methods:
    Route()              :  constructor

    addwpt(name,wptype,lat,lon,alt) : Add waypoint (closest to la/lon whene from navdb
    
Members: 

Created by  : Jacco M. Hoekstra
Date        : September 2013

Modifation  :
By          :
Date        :
------------------------------------------------------------------
"""

import numpy as np
from math import *

#-----------------------------------------------------------------

class Route():

    def __init__(self,navdb):

# Add pointer to self navdb object
        self.navdb  = navdb

        self.nwp    = 0
        self.wpname = []
        self.wptype = []
        self.wplat  = []
        self.wplon  = []
        self.wpalt  = []
        self.wpspd  = []
        self.iactwp = -1

# Waypoint types:
        self.wplatlon = 0   # lat/lon waypoint        
        self.wpnav    = 1   # VOR/nav database waypoint
        self.orig     = 2   # Origin airport
        self.dest     = 3   # Destination airport

#

        return

#--------------Adds waypoint an returns index of waypoint

    def appendwp(self,name,wptype,lat,lon,alt,spd):

# Be default we trust, distrust needs to be earned
        wpok = True   # waypoint check

# Lat/lon type: newly defined, copy lat/lon vaues from call
        if wptype == self.wplatlon:
            self.wpname.append(name)
            self.wplat.append((lat+180.)%360.-180.)
            self.wplon.append((lon+ 90.)%360.- 90.)
            self.wpalt.append(alt)
            self.wpspd.append(spd)
            
# NAVDB waypoint: find name closest to lat/lon            
        elif wptype == self.wpnav:
            i = self.navdb.getwpidx(name.upper().strip(),lat,lon)
            wpok = (i >= 0)

            if wpok:
                self.wpname.append(name)
                self.wplat.append(self.navdb.wplat[i])
                self.wplon.append(self.navdb.wplon[i])
                self.wpalt.append(alt)
                self.wpspd.append(spd)

# Airport waypoint/destination name is unique:            
        elif wptype == self.orig or wptype==self.dest:
            i = self.navdb.getapidx(name.upper().strip())
            wpok = (i >= 0)
            if wpok:

# Is new waypoint destination?
                if wptype==self.dest:

# First remove old destination
                   if len(self.wptype)>=1:
                       if self.wptype[-1]==self.dest:
                           self.delwp(-1)

# First remove old origin
                if wptype==self.orig:
                    if len(self.wptype)>=1:
                        if self.wptype[0]==self.orig:
                            self.delwp(0)
# Add origin at psotion 0
                    self.wpname = [name]+self.wpname
                    self.wplat = [self.navdb.wplat[i]]+self.wplat
                    self.wplon = [self.navdb.wplon[i]]+self.wplon
                    self.wpalt = [alt]+self.wpalt
                    self.wpspd = [spd]+self.wpname
                    self.wptype = [wptype]+self.wptype

# Other waypoints append
                else:                    
                    
                    self.wpname.append(name)
                    self.wplat.append(self.navdb.aplat[i])
                    self.wplon.append(self.navdb.aplon[i])
                    self.wpalt.append(alt)
                    self.wpspd.append(spd)

        if wpok:
            self.nwp = len(self.wpname)
            idx = self.nwp - 1
            if len(self.wplat)==1:
                self.iactwp = 0
        else:
            idx = -1


        return idx

# Go to next wp and return data

    def getnextwp(self):

        if self.iactwp+1<self.nwp:
            self.iactwp = self.iactwp + 1
            lnavon = True
        else:
            lnavon = False

        return self.wplat[self.iactwp],self.wplon[self.iactwp],   \
               self.wpalt[self.iactwp],self.wpspd[self.iactwp],   \
               lnavon
        
    def delwp(i):
       del wpname[-1]
       del wplat[-1]
       del wplon[-1]
       del wpalt[-1]
       del wpspd[-1]
       del wptype[-1]
       return 