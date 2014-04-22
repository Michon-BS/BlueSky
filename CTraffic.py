""" 
Traffic class definition    : Traffic data

Methods:
    Traffic()            :  constructor
    
    create(acid,actype,aclat,aclon,achdg,acalt,acspd) : create aircraft
    delete(acid)         : delete an aircraft from traffic data
    update(sim)          : do a numerical integration step
    findnearest(lat,lon) : find nearest a/c to lat/lon position

Members: see create

Created by  : Jacco M. Hoekstra
Date        : September 2013

Modifation  :
By          :
Date        :
------------------------------------------------------------------
"""

import numpy as np
import random
from math import *

from aero import fpm, kts, nm, g0, eas2tas, tas2eas, tas2cas, density, Rearth
from aero_np import vatmos, vcas2tas, vtas2cas, qdrdist, latlondist

from CMetric import Metric
from CNavdb import Navdatabase
from CRoute import Route
from CTrail import Trails

#-----------------------------------------------------------------

class Traffic():
    def __init__(self):
        self.dts = []

        self.ntraf = 0

        # Traffic list & arrays definition

        # !!!IMPORTANT NOTE!!!
        # Anny variables added here should also be added in the Traffic
        # methods self.create() (append) and self.delete() (delete)
        # which can be found directly below __init__

        # Traffic basic flight data
        self.id = []  # identifier (string)
        self.type = []  # aircaft type (string)
        self.lat = np.array([])  # latitude [deg]
        self.lon = np.array([])  # longitude [deg]
        self.trk = np.array([])  # track angle [deg]
        self.tas = np.array([])  # true airspeed [m/s]
        self.cas = np.array([])  # callibrated airspeed [m/s]
        self.alt = np.array([])  # altitude [m]
        self.vs = np.array([])  # vertical speed [m/s]
        self.rho = np.array([])  # atmospheric air density [m/s]

        # Traffic performance data
        self.avsdef = np.array([])  # [m/s]default vertical speed of autopilot
        self.aphi = np.array([])  # [rad] bank angle setting of autopilot
        self.ax = np.array([])  # [m/s2] absolute value of longitudinal accelleration

        # Traffic autopilot settings
        self.ahdg = np.array([])  # selected heading [deg]
        self.aspd = np.array([])  # selected spd(eas) [m/s]
        self.aalt = np.array([])  # selected alt[m]
        self.avs = np.array([])  # selected vertical speed [m/s]

        # Traffic navigation information
        self.orig = []  # Four letter code of origin airport
        self.dest = []  # Four letter code of destination airport


        # LNAV route navigation
        self.swlnav = np.array([])  # Lateral (HDG) based on nav?
        self.swvnav = np.array([])  # Vertical/longitudinal (ALT+SPD) based on nav info

        self.actwplat = np.array([])  # Active WP latitude
        self.actwplon = np.array([])  # Active WP longitude
        self.actwpalt = np.array([])  # Active WP altitude to arrive at
        self.actwpspd = np.array([])  # Active WP speed

        # Route info
        self.route = []

        # ASAS info per aircraft:
        self.iconf = np.array([])  # index in 'conflicting' aircraft database

        # Display information on label
        self.label = []  # Text and bitmap of traffic label
        self.trailcol = []  # Trail color: default 'Blue'

        # Area
        self.inside = []

        # Scheduling of FMS and ASAS

        self.t0fms = -999.  # last time fms was called
        self.dtfms = 0.9  # interval for ASAS

        self.t0asas = -999.  # last time ASAS was called
        self.tasas = 1.01  # interval for FMS

        #-----------------------------------------------------------------------------
        # Not per aircraft data

        # Import navigation data base

        self.navdb = Navdatabase("global")  # Read nav data from global folder

        # Traffic area: delete traffic when it leaves this area (so not when outside)
        self.swarea = False
        self.arealat0 = 0.0  # [deg] lower latitude defining area
        self.arealat1 = 0.0  # [deg] upper latitude defining area
        self.arealat0 = 0.0  # [deg] lower longitude defining area
        self.arealat1 = 0.0  # [deg] upper longitude defining area
        self.areafloor = -999999.0  # [m] Delete when descending through this h
        self.areadt = 5.0  # [s] frequency of area check (simtime)
        self.areat0 = -100.  # last time checked

        # Taxi switch
        self.swtaxi = False  # Default OFF: delwte traffic below 1500 ft

        # Research Area ("Square" for Square, "Circle" for Circle area)
        self.area = ""

        # Metrics
        self.metricSwitch = 0
        self.metric = Metric()

        # Bread crumbs for trails
        self.lastlat = []
        self.lastlon = []
        self.lasttim = []
        self.trails = Trails()
        self.swtrails = False  # Default switched off
        return

    #--------------------------------------------------------------------

    def create(self, acid, actype, aclat, aclon, achdg, acalt, acspd):

        # Check if not already exist
        if self.id.count(acid.upper()) > 0:
            return  # already exists do nothing

        # Increase number of aircraft
        self.ntraf = self.ntraf + 1

        # Process input
        self.id.append(acid.upper())
        self.type.append(actype)
        self.lat = np.append(self.lat, aclat)
        self.lon = np.append(self.lon, aclon)
        self.trk = np.append(self.trk, achdg)  # TBD: add conversion hdg => trk
        self.alt = np.append(self.alt, acalt)

        self.vs = np.append(self.vs, 0.)
        self.rho = np.append(self.rho, density(acalt))
        self.tas = np.append(self.tas, acspd)
        self.cas = np.append(self.cas, tas2cas(acspd, acalt))


        # Type specific data (temporarily default values)
        self.avsdef = np.append(self.avsdef, 1500. * fpm)  # default vertical speed of autopilot
        self.aphi = np.append(self.aphi, radians(25.))  # bank angle setting of autopilot
        self.ax = np.append(self.ax, kts)  # absolute value of longitudinal accelleration

        # Traffic autopilot settings: hdg[deg], spd (CAS,m/s), alt[m], vspd[m/s]
        self.ahdg = np.append(self.ahdg, achdg)  # selected heading [deg]
        self.aspd = np.append(self.aspd, tas2eas(acspd, acalt))  # selected spd(eas) [m/s]
        self.aalt = np.append(self.aalt, acalt)  # selected alt[m]
        self.avs = np.append(self.avs, 0.)  # selected vertical speed [m/s]

        # Traffic navigation information
        self.dest.append("")
        self.orig.append("")

        # LNAV route navigation
        self.swlnav = np.append(self.swlnav, False)  # Lateral (HDG) based on nav
        self.swvnav = np.append(self.swvnav, False)  # Vertical/longitudinal (ALT+SPD) based on nav info

        self.actwplat = np.append(self.actwplat, 0.0)  # Active WP latitude
        self.actwplon = np.append(self.actwplon, 0.0)  # Active WP longitude
        self.actwpalt = np.append(self.actwpalt, 0.0)  # Active WP altitude
        self.actwpspd = np.append(self.actwpspd, 0.0)  # Active WP speed

        # Route info
        self.route.append(Route(self.navdb))  # create empty route connected with nav databse

        # ASAS info: no conflict => -1
        self.iconf = np.append(self.iconf, -1.0)  # index in 'conflicting' aircraft database

        # Area variable set to False to avoid deletion upon creation outside
        self.inside.append(False)

        # Display information on label
        self.label.append(['', '', '', 0])

        # Bread crumbs for trails
        self.trailcol.append(self.trails.defcolor)
        self.lastlat = np.append(self.lastlat, aclat)
        self.lastlon = np.append(self.lastlon, aclon)
        self.lasttim = np.append(self.lasttim, 0.0)
        return

    #--------------------------------------------------------------------

    def delete(self, acid):

        try:  # prevent error due to not found

            idx = self.id.index(acid)
        except:
            return False

        del self.id[idx]
        del self.type[idx]

        # Traffic basic data
        self.lat = np.delete(self.lat, idx)
        self.lon = np.delete(self.lon, idx)
        self.trk = np.delete(self.trk, idx)
        self.alt = np.delete(self.alt, idx)
        self.vs = np.delete(self.vs, idx)
        self.tas = np.delete(self.tas, idx)
        self.cas = np.delete(self.cas, idx)
        self.rho = np.delete(self.rho, idx)


        # Type specific data (temporarily default values)
        self.avsdef = np.delete(self.avsdef, idx)
        self.aphi = np.delete(self.aphi, idx)
        self.ax = np.delete(self.ax, idx)

        # Traffic autopilot settings: hdg[deg], spd (CAS,m/s), alt[m], vspd[m/s]
        self.ahdg = np.delete(self.ahdg, idx)
        self.aspd = np.delete(self.aspd, idx)
        self.aalt = np.delete(self.aalt, idx)
        self.avs = np.delete(self.avs, idx)

        # Traffic navigation variables
        del self.dest[idx]
        del self.orig[idx]

        self.swlnav = np.delete(self.swlnav, idx)
        self.swvnav = np.delete(self.swvnav, idx)

        self.actwplat = np.delete(self.actwplat, idx)
        self.actwplon = np.delete(self.actwplon, idx)
        self.actwpalt = np.delete(self.actwpalt, idx)
        self.actwpspd = np.delete(self.actwpspd, idx)

        # Route info
        del self.route[idx]

        # ASAS info
        self.iconf = np.delete(self.iconf, idx)

        # Metrics, area
        del self.inside[idx]

        # Traffic display data: label
        del self.label[idx]

        # Delete bread crumb data
        self.lastlat = np.delete(self.lastlat, idx)
        self.lastlon = np.delete(self.lastlon, idx)
        self.lasttim = np.delete(self.lasttim, idx)
        del self.trailcol[idx]


        # Decrease number fo aircraft
        self.ntraf = self.ntraf - 1

        return True

    #--------------------------------------------------------------------

    def update(self, sim, cmd):

        if (sim.mode == sim.op and sim.dt > 0.0 and self.ntraf > 0):
            self.dts.append(sim.dt)

            # Test: add 10000 random aircraft
            #            if sim.t>1.0 and self.ntraf<1000:
            #                for i in range(10000):
            #                   acid="KL"+str(i)
            #                   aclat = random.random()*180.-90.
            #                   aclon = random.random()*360.-180.
            #                   achdg = random.random()*360.
            #                   acalt = (random.random()*18000.+2000.)*0.3048
            #                   self.create(acid,'B747',aclat,aclon,achdg,acalt,350.)
            #

            #-------------------------------- Atmosphere
            self.T, self.rho, self.p = vatmos(self.alt)


            #---------------------------- Performance limits

            # Todo  !

            # limit speed, calc fuel usage based on CD-CL and specific fuel consumption

            # Define proc speeds

            #-----------------  FMS NAVIGATION
            # FMS LNAV mode:
            qdr, dist = qdrdist(self.lat, self.lon, self.actwplat, self.actwplon)

            # Check whether shift based dist [nm] is required, set closer than 2 nm
            iwpclose = np.where(dist < 2.0)[0]

            # Shift where necessary
            for i in iwpclose:
                lat, lon, alt, spd, lnavon = self.route[i].getnextwp()

                self.swlnav[i] = lnavon
                self.swvnav[i] = lnavon

            # Set headings based on swlnav
            self.ahdg = np.where(self.swlnav, qdr, self.ahdg)


            #-------------------- Basic Autopilot  modes

            eps = np.array(self.ntraf * [0.01])  # almost zero for misc purposes

            # HDG HOLD/SEL mode: ahdg = ap selected heading
            delhdg = (self.ahdg - self.trk + 180.) % 360 - 180.  #[deg]
            #            print delhdg
            omega = np.degrees(g0 * np.tan(self.aphi) / \
                               np.maximum(self.tas, eps))

            hdgsel = np.abs(delhdg) > np.abs(2. * sim.dt * omega)

            self.trk = (self.trk + sim.dt * omega * hdgsel * np.sign(delhdg)) % 360.

            # ALT HOLD/SEL mode: ahdg = ap selected heading
            #                 optionally: avs = ap selected vert speed

            delalt = self.aalt - self.alt  # [m]
            swvs = (np.abs(self.avs) > eps)
            vspd = swvs * self.avs + (1. - swvs) * self.avsdef * np.sign(delalt)
            swaltsel = np.abs(delalt) > np.abs(2. * sim.dt * np.abs(vspd))
            self.vs = swaltsel * vspd

            # SPD HOLD/SEL mode: aspd = autopilot selected speed (first only eas)
            aptas = vcas2tas(self.aspd, self.alt)
            delspd = aptas - self.tas
            swspdsel = np.abs(delspd) > 0.4  # <1 kts = 0.514444 m/s
            ax = np.minimum(abs(delspd / sim.dt), self.ax)
            self.tas = swspdsel * (self.tas + ax * np.sign(delspd) * sim.dt) + \
                       (1. - swspdsel) * aptas

            self.cas = vtas2cas(self.tas, self.alt)

            # Kinematics: update lat,lon,alt

            self.alt = swaltsel * (self.alt + self.vs * sim.dt) + \
                       (1. - swaltsel) * self.aalt

            ds = sim.dt * self.tas

            self.lat = self.lat + np.degrees(ds * np.cos(np.radians(self.trk)) \
                                             / Rearth)

            self.lon = self.lon + np.degrees(ds * np.sin(np.radians(self.trk)) \
                                             / np.cos(np.radians(self.lat)) / Rearth)

            # Update trails when switched on
            if self.swtrails:
                self.trails.update(sim.t, self.lat, self.lon,
                                   self.lastlat, self.lastlon,
                                   self.lasttim, self.id, self.trailcol)
            else:
                self.lastlat = self.lat
                self.lastlon = self.lon
                self.lattime = sim.t

            # Update metrics
            if self.metricSwitch == 1:
                self.metric.update(self, sim, cmd)


                # ---AREA check---------------------------------------------------------------
                # Update area once per areadt seconds:
        if self.swarea and abs(sim.t - self.areat0) > self.areadt:

            # Update loop timer
            self.areat0 = sim.t

            # Chekc all aicraft
            for i in xrange(self.ntraf):

                # Current status
                if self.area == "Square":
                    inside = self.arealat0 <= self.lat[i] <= self.arealat1 and \
                             self.arealon0 <= self.lon[i] <= self.arealon1 and \
                             self.alt[i] >= self.areafloor and \
                             (self.alt[i] >= 1500 or self.swtaxi)
                elif self.area == "Circle":

                    ## Average of lat
                    latavg = (radians(self.lat[i]) + radians(self.metric.fir_circle_point[0])) / 2
                    cosdlat = (cos(latavg))

                    #Distance x to centroid
                    dx = (self.lon[i] - self.metric.fir_circle_point[1]) * cosdlat * 60
                    dx2 = dx * dx

                    #Distance y to centroid
                    dy = self.lat[i] - self.metric.fir_circle_point[0]
                    dy2 = dy * dy * 3600

                    #Radius squared
                    r2 = self.metric.fir_circle_radius * self.metric.fir_circle_radius

                    #Inside if smaller
                    inside = (dx2 + dy2) < r2

                # Compare with previous: when leaving area: delete command
                if self.inside[i] and not inside:
                    cmd.stack("DEL " + self.id[i])

                # Update area status
                self.inside[i] = inside

        return

    #--------------------------------------------------------------------

    def findnearest(self, lat, lon):

        # Find nearest aircraft

        if self.ntraf > 0:
            d2 = (lat - self.lat) ** 2 + cos(radians(lat)) * (lon - self.lon) ** 2
            idx = np.argmin(d2)
            del d2
            return idx
        else:
            return -1
            #--------------------------------------------------------------------
            # Find index of aircraft id

    def id2idx(self, acid):
        try:
            return self.id.index(acid.upper())
        except:
            return -1

            #--------------------------------------------------------------------
            # Change color of aircraft trail

    def changeTrailColor(self, color, idx):
        #        print color
        #        print idx
        #        print "     " + str(self.trails.colorsOfAC[idx])
        self.trailcol[idx] = self.trails.colorList[color]
        #        print "     " + str(self.trails.colorsOfAC[idx])
        return