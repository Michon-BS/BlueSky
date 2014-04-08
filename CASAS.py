""" 
ASAS class
   
Created by  : Jacco M. Hoekstra (TU Delft)
Date        : November 2013

Modifation  :
By          :
Date        :

"""



#----------------------------------------------------------------

# Create a confict database
# Inputs:
#    lat [deg]  = array with traffic latitude
#    lon [deg]  = array with traffic longitude
#    alt [m]    = array with traffic altitude 
#    trk [deg]  = array with traffic track angle
#    gs [m/s]   = array with ground speed [m/s]
#    vs [m/s]   = array with vertical speed [m/s]
#
# Outputs:
#    swconfl = 2D array with True/False for conflict
#    dtconfl = time to conflict
 
import numpy as np
from aero_np import latlondist, nm

class ASAS():
    def __init__(self,tlook, R, dh):
        self.swasas = False
        self.dtlookahead = tlook  # [s] lookahead time
        self.R           = R      # [m] Horizontal separation minimum
        self.dh          = dh     # [m] Vertical separation minimum
        return

# Generate a conflict database    
    def ASAS_state(self,traflat,traflon,trafalt,traftrk,trafgs,trafvs):

        qdr,dist = latlondist_vector(traflat,traflon,traflat,traflon)

# Calculate horizontal closest point of approach (CPA)        
        qdrrad = np.radians(qdr)
        dx = np.array(dist*np.sin(qdrrad))
        dy = np.array(dist*np.cos(qdrrad))
        
        trkrad = np.radians(trk)
        u = trafgs*np.sin(trkrad)
        v = trafgs*np.cos(trkrad)
        
        du = np.array(u - u.T)
        dv = np.array(v - v.T)
        
        tcpa = -(du*dx + dv*dy) /      \
                 (du*du + dv*dv         \
                 + np.array(np.eye(du[:,0].size)))

# Calculate CPA positions
        xcpa = dx + tcpa*du
        ycpa = dy + tcpa*dv

        distcpa2 = xcpa*xcpa+ycpa*ycpa  # distance at CPA squared

# Vertical crossing of disk (-dh,+dh)
        dalt  = trafalt-trafalt.T
        dvs = trafvs-trafvs.T

        tcrosshi = (dalt+self.dh)/dvs
        tcrosslo = (dalt-self.dh)/dvs

        tcross   = np.minimum(tcrosshi,tcrosslo)

        self.swconfl = (dist <= self.R +                               \
                         (tcpa >= 0.)*(tcpa <= self.dtlookahead)*      \
                         (distcpa2<self.R*self.R)*                     \
                         (tcross >= 0.)*(tcross <= self.dtlookahead))

# TODO: Calculate CPA positions of traffic in lat/lon

# First try simplest method (mercator)

        return
                
        
        

    
    