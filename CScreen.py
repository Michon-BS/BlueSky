""" 
Screen class definition : contains radar & edit screen data & methods

Methods:
    Screen(sim)         :  constructor

    echo(msg)           : print something at screen
    update(sim,traf)    : Draw a new frame of screen
    ll2xy(lat,lon)      : lat/lon[deg] to pixel coordinate conversion
    xy2ll(x,y)          : pixel to lat/lon[de]g conversion    
    zoom(factor)        : zoom in/out
    pan(lat,lon)        : pan to lat,lon position

Members: see constructor

Created by  : Jacco M. Hoekstra (TU Delft)
Date        : September 2013

Modifation  :
By          :
Date        :

"""
from math import *
import time

import pygame as pg
import numpy as np

import splash
from fastfont import CFastfont
from CEditWin import EditWin
from aero_np import ft,kts,nm,latlondist,qdrdist,qdrpos
from tools import tim2txt



#-----------------------------------------------------------------

black    = (0,0,0)
darkgrey = (25,25,48)
grey     = (84,84,114)
darkblue = (25,25,64,100)
white    = (255,255,255)
green    = (0,255,0)
blue     = (0,0,255)
lightgreyblue = (130,150,190)  # waypoint symbol color
lightgreygreen = (149,215,179)  # grid color
lightcyan = (0,255,255)  # FIR boundaries

class Screen:
    def __init__(self,sim):
        pg.init()

# Read Screen configuration file:
        print "Reading scr_cfg.dat"

        lst = np.genfromtxt(sim.datadir+"scr_cfg.dat", comments='#',dtype='i4')

        self.swfullscreen = int(lst[0])==0

        self.width  = int(lst[1]) # default value to create variable
        self.height = int(lst[2]) # default value to create variable

# Dimensions radar window
        self.lat1 = 54. # [deg] upper limit display
        self.lat0 = 50. # [deg] lowerlimit display
        self.lon0 = -1. # [deg] left side of screen       
        
        dellat = self.lat1-self.lat0

        avelat = (self.lat0+self.lat1)*0.5

        dellon = dellat*self.width/(self.height*cos(radians(avelat)))
        avelon = (self.lon0+dellon/2.+180.)%360.-180.

        self.lon1 = (self.lon0 + dellon+180.)%360.-180.

        self.ctrlat = avelat
        self.ctrlon = avelon


# Update rate radar:
        self.radardt = 0.10 # 10x per sec 0.25  # 4x per second max
        self.radt0   = -999. # last time drawn
        self.maxnrwp = 1000  # max nr apts+wpts to be drawn

#----------------------------SYMBOLS-----------------------------

# Read graphics for acsymbol (normal = green) + amber
        self.acsymbol=[]
        for i in range(60):
            self.acsymbol.append(pg.image.load
                              (sim.datadir+"graphics/acsymbol/acsymbol" \
                                 +str(i)+".png"))

        self.ambacsymbol=[]
        for i in range(60):
            self.ambacsymbol.append(pg.image.load
                              (sim.datadir+"graphics/amb-acsymbol/amb-acsymbol" \
                                 +str(i)+".png"))

# Lable lines& default no trails
        self.swlabel = 3


# Read and scale waypoint symbol
        wptgif         = pg.image.load(sim.datadir+"graphics/waypoint.gif")
        self.wptsymbol = pg.transform.scale(wptgif,(10,7))
        self.wpsw      = 1 # 0=None, 1 = VOR 2 = non-digit ones, 3 =all

# Read and scale airport symbol
        aptgif         = pg.image.load(sim.datadir+"graphics/airport.gif")
        self.aptsymbol = pg.transform.scale(aptgif,(12,9))
        self.apsw      = 1  # 0 = None, 1 = Large, 2 = All

#--------------------------------MAPS---------------------------------
# Read map of world
        self.mapbmp    = pg.image.load(sim.datadir+"graphics/world.jpg")
        w,h = self.mapbmp.get_size()

# Two ref positions for scaling, convert to scaling factors x=a*lat+b
        x1,y1,lat1,lon1 = 0.,0.,90.,-180.
        x2,y2,lat2,lon2 = w,h,-90.,180.
        self.mapax = (x2-x1)/(lon2-lon1)
        self.mapbx = x2-self.mapax*lon2
        self.mapay = (y2-y1)/(lat2-lat1)
        self.mapby = y2-self.mapay*lat2

        self.swsat = True

# Nav display projection mode
        self.swnavdisp = False
        self.ndacid = ""
        self.ndlat  = 0.0
        self.ndlon  = 0.0
        self.ndhdg  = 0.0
#------------------------WINDOW SETUP and scaling--------------------------

# Empty tuple to force reselection waypoints & airports to be drawn
        self.navsel = () # Empty tuple to force reselection waypoints to be drawn
        self.satsel = () # Empty tuple to force reselection satellite imagery to be drawn

            
# Set up window            
        splash.destroy()  # does pg.display.quit()!
        pg.display.init()

# Full screen
        di = pg.display.Info()
        if self.swfullscreen:
            self.width  = di.current_w
            self.height = di.current_h
            reso = (self.width,self.height)
            self.win = pg.display.set_mode(reso,pg.FULLSCREEN)
# Windowed                        
        else:
            self.height = min(self.height,di.current_h*90/100)
            self.width = min(self.width,di.current_w*90/100)
            reso = (self.width,self.height)
            self.win = pg.display.set_mode(reso)

        pg.display.set_caption("BlueSky Open ATM Simulator (F11 = Full Screen)",
                               "BlueSky")
        iconbmp = pg.image.load('icon.gif')        
        pg.display.set_icon(iconbmp)


        self.radbmp = self.win.copy()
        self.redrawradbg = True  # Switch to redraw background

#---------------------RADAR FONTS & EDIT WINDOW-----------------------------

# Set up fonts
        self.fontrad = CFastfont(self.win,'Arial',14,green,False,False) # name, size, bold,italic
        self.fontnav = CFastfont(self.win,'Arial',10,lightgreyblue,False,False) # name, size, bold,italic

 # Edit window: 6 line of 64 chars
        self.editwin = []
        nch = lst[3]    # number of chars per line
        nlin = lst[4]   # number of lines in windows
        winx = lst[5]   # x-coordinate in pixels of left side
        winy = self.height-lst[6] # y-coordinate in pixels of bottom
        self.editwin = EditWin(self.win,nch,nlin,winx,winy)


#-------------------------COASTLINE DATA--------------------------------------

# Init geo (coastline)  data    
        f = open("data/coastlines.dat",'r')
        print "Reading coastlines.dat"
        lines = f.readlines()
        f.close()
        records = []
        for line in lines:
            if not (line.strip()=="" or line.strip()[0]=='#'):
                arg = line.split()
                if len(arg)==3:
                    records.append([arg[0],float(arg[1]),float(arg[2])])

        print len(records)," records read."
        
# Convert pen up/pen down format of coastlines to numpy arrays with lat/lon

        coastlat0 = []
        coastlon0 = []
        coastlat1 = []
        coastlon1 = []
        clat,clon = -1,-1

        for rec in records:
            lat,lon = rec[1],rec[2]
            if rec[0]=='D' :
                coastlat0.append(clat)
                coastlon0.append(clon)
                coastlat1.append(lat)
                coastlon1.append(lon)
            clat,clon = lat,lon

        self.coastlat0 = np.array(coastlat0)
        self.coastlon0 = np.array(coastlon0)
        self.coastlat1 = np.array(coastlat1)
        self.coastlon1 = np.array(coastlon1)

        del coastlat0,coastlon0,coastlat1,coastlon1        # Clear memory
        
        self.geosel = ()  # Force reselect first time coastlines
        self.firsel = ()  # Force reselect first time FIR lines

        print "    ",len(self.coastlat0)," lines added."


# Set default coastlines & FIRs on:
        self.swgeo = True
        self.swfir = True
        self.swgrid = False
    
        return
#---------------------------------------------------------------------------

    def echo(self,msg):
        self.editwin.echo(msg)
        return
        
#---------------------------------------------------------------------------
# Update: Draw a new frame

    def update(self,sim,traf):

# Navdisp mode: get center:
        if self.swnavdisp:
            i = traf.id2idx(self.ndacid)
            if i>=0:
                self.ndlat = traf.lat[i]
                self.ndlon = traf.lon[i]
                self.ndcrs = traf.trk[i]
            else:
                self.swnavdisp = False
        else:
            self.ndcrs = 0.0
            
        
# Radar window
# --------------Background

        if self.redrawradbg or self.swnavdisp:
            if self.swnavdisp or not self.swsat:
                self.radbmp.fill(darkgrey)

#--------------Satellite image
            else:
                navsel = (self.lat0,self.lat1, \
                          self.lon0,self.lon1)
                if not self.satsel==navsel:

# Map cutting and scaling: normal case
                    if self.lon1>self.lon0:
                        x0 = max(0,self.lon0*self.mapax + self.mapbx)
                        x1 = min(self.mapbmp.get_width()-1, \
                                   self.lon1*self.mapax + self.mapbx)
    
                        y1 = min(self.mapbmp.get_height()-1, \
                                   self.lat0*self.mapay + self.mapby)
                        y0 = max(0,self.lat1*self.mapay + self.mapby)
    
                        selrect = pg.Rect(x0,y0,abs(x1-x0),abs(y1-y0))
                        mapsel = self.mapbmp.subsurface(selrect)
                        self.submap = pg.transform.scale(mapsel, \
                                                     (self.width,self.height) )

                        self.radbmp.blit(self.submap,(0,0))

# Wrap around case: clip two segments
                    else:
                        
                        w0 = int(self.width*(180.-self.lon0) /    \
                                                 (180.0-self.lon0+self.lon1+180.))
                        w1 = int(self.width-w0)

# Left part
                        x0 = max(0,self.lon0*self.mapax + self.mapbx)
                        x1 = self.mapbmp.get_width()-1
    
                        y1 = min(self.mapbmp.get_height()-1, \
                                   self.lat0*self.mapay + self.mapby)
                        y0 = max(0,self.lat1*self.mapay + self.mapby)

    
                        selrect = pg.Rect(x0,y0,abs(x1-x0),abs(y1-y0))
                        mapsel = self.mapbmp.subsurface(selrect)
                        self.submap = pg.transform.scale(mapsel, \
                                                     (w0,self.height) )
                        self.radbmp.blit(self.submap,(0,0))

# Right half
                        x0 = 0
                        x1 = min(self.mapbmp.get_width()-1, \
                                   self.lon1*self.mapax + self.mapbx)
    
                        selrect = pg.Rect(x0,y0,abs(x1-x0),abs(y1-y0))
                        mapsel = self.mapbmp.subsurface(selrect)
                        self.submap = pg.transform.scale(mapsel, \
                                                     (w1,self.height) )
                        self.radbmp.blit(self.submap,(w0,0))
                        self.submap = self.radbmp.copy()

                    
                    self.satsel = navsel

# Map blit only
                else:                
                    self.radbmp.blit(self.submap,(0,0))

# Draw lat/lon grid

            if self.swgrid and not self.swnavdisp:
                ngrad = int(self.lon1-self.lon0)

                if ngrad >= 10:
                    step = 10
                    i0 = step*int(self.lon0/step)
                    j0 = step*int(self.lat0/step)
                else:
                    step = 1
                    i0 = int(self.lon0)
                    j0 = int(self.lon0)

                for i in range(i0,int(self.lon1+1.),step):
                    x,y = self.ll2xy(self.ctrlat,i)
                    pg.draw.line(self.radbmp,lightgreygreen, \
                                 (x,0),(x,self.height))

                for j in range(j0,int(self.lat1+1.),step):
                    x,y = self.ll2xy(j,self.ctrlon)
                    pg.draw.line(self.radbmp,lightgreygreen, \
                                 (0,y),(self.width,y))
    
#------ Draw coastlines

            if self.swgeo:
#                cx,cy = -1,-1
                geosel = (self.lat0,self.lon0,self.lat1,self.lon1)
                if self.geosel!=geosel:
                    self.geosel = geosel
                    
                    self.cstsel = np.where(
                                  self.onradar(self.coastlat0,self.coastlon0)+ \
                                  self.onradar(self.coastlat1,self.coastlon1))
                                  
#                    print len(self.cstsel[0])," coastlines"
                    self.cx0,self.cy0 = self.ll2xy(self.coastlat0,self.coastlon0)
                    self.cx1,self.cy1 = self.ll2xy(self.coastlat1,self.coastlon1)         

                for i in list(self.cstsel[0]):
                    pg.draw.line(self.radbmp,grey,(self.cx0[i],self.cy0[i]), \
                                                  (self.cx1[i],self.cy1[i]))
#------ Draw FIRs

            if self.swfir:
                self.firx0,self.firy0 = self.ll2xy(traf.navdb.firlat0,   \
                                                   traf.navdb.firlon0)
                                                   
                self.firx1,self.firy1 = self.ll2xy(traf.navdb.firlat1,   \
                                                   traf.navdb.firlon1)         

                for i in range(len(self.firx0)):
                    pg.draw.line(self.radbmp,lightcyan,
                                 (self.firx0[i],self.firy0[i]), 
                                 (self.firx1[i],self.firy1[i]))

# -----------------Waypoint & airport symbols

# Check whether we need to reselect waypoint set to be drawn

            navsel = (self.lat0,self.lat1, \
                      self.lon0,self.lon1)
            if self.navsel!= navsel:
                self.navsel = navsel                

# Make list of indices of waypoints & airports on screen

                self.wpinside = list(np.where(self.onradar(traf.navdb.wplat,  \
                                                      traf.navdb.wplon))[0])

                self.wptsel = []                
                for i in self.wpinside:
                    if self.wpsw == 3 or \
                      (self.wpsw == 1 and len(traf.navdb.wpid[i])==3) or \
                      (self.wpsw == 2 and  traf.navdb.wpid[i].isalpha()):                               
                                   self.wptsel.append(i)                    
                self.wptx,self.wpty = self.ll2xy(traf.navdb.wplat,traf.navdb.wplon)


                self.apinside = list(np.where(self.onradar(traf.navdb.aplat,\
                                                      traf.navdb.aplon))[0])

                self.aptsel = []                
                for i in self.apinside:
                    if self.apsw==2 or (self.apsw == 1 and \
                                             traf.navdb.apmaxrwy[i]>1000.):                               
                        self.aptsel.append(i)
                self.aptx,self.apty = self.ll2xy(traf.navdb.aplat,traf.navdb.aplon)

                   
#------- Draw waypoints

            if self.wpsw>0:
#                print len(self.wptsel)," waypoints"
                if len(self.wptsel)<self.maxnrwp:
                    wptrect = self.wptsymbol.get_rect()
                    for i in self.wptsel:
    #                    wptrect.center = self.ll2xy(traf.navdb.wplat[i],  \
    #                                                traf.navdb.wplon[i])
                        wptrect.center = self.wptx[i],self.wpty[i]
                        self.radbmp.blit(self.wptsymbol,wptrect)


# If waypoint label bitmap does not yet exist, make it
                        if not traf.navdb.wpswbmp[i]:
                            traf.navdb.wplabel[i] = pg.Surface((50,30),0,self.win)
                            self.fontnav.printat(traf.navdb.wplabel[i],0,0, \
                                                     traf.navdb.wpid[i])
                            traf.navdb.wpswbmp[i] = True
                            
# In any case, blit it
                        xtxt = wptrect.right + 2
                        ytxt = wptrect.top
                        self.radbmp.blit(traf.navdb.wplabel[i],(xtxt,ytxt),\
                                                    None,pg.BLEND_ADD)

    
                        if not traf.navdb.wpswbmp[i]:                    
                            xtxt = wptrect.right + 2
                            ytxt = wptrect.top
                            
#                            self.fontnav.printat(self.radbmp,xtxt,ytxt, \
#                                                         traf.navdb.wpid[i])

#------- Draw airports
            if self.apsw>0:         
#                if len(self.aptsel)<800:
    
                    aptrect = self.aptsymbol.get_rect()            
    
    
#                    print len(self.aptsel)," airports"
    
                    for i in self.aptsel:
    #                    aptrect.center = self.ll2xy(traf.navdb.aplat[i],  \
    #                                                traf.navdb.aplon[i])
                        aptrect.center = self.aptx[i],self.apty[i]
                        self.radbmp.blit(self.aptsymbol,aptrect)

# If airport label bitmap does not yet exist, make it
                        if not traf.navdb.apswbmp[i]:
                            traf.navdb.aplabel[i] = pg.Surface((50,30),0,self.win)
                            self.fontnav.printat(traf.navdb.aplabel[i],0,0, \
                                                     traf.navdb.apid[i])
                            traf.navdb.apswbmp[i] = True
                            
# In either case, blit it
                        xtxt = aptrect.right + 2
                        ytxt = aptrect.top
                        self.radbmp.blit(traf.navdb.aplabel[i],(xtxt,ytxt),\
                                                    None,pg.BLEND_ADD)
                            
#                            self.fontnav.printat(self.radbmp,xtxt,ytxt, \
#                                                     traf.navdb.apid[i])

    
#--------- Draw traffic area
            if traf.swarea and not self.swnavdisp:
                
                if traf.area == "Square":
                    x0,y0 = self.ll2xy(traf.arealat0,traf.arealon0)
                    x1,y1 = self.ll2xy(traf.arealat1,traf.arealon1)
    
                    pg.draw.line(self.radbmp,blue,(x0,y0),(x1,y0))
                    pg.draw.line(self.radbmp,blue,(x1,y0),(x1,y1))
                    pg.draw.line(self.radbmp,blue,(x1,y1),(x0,y1))
                    pg.draw.line(self.radbmp,blue,(x0,y1),(x0,y0))
                
                #FIR CIRCLE
                if traf.area == "Circle":
                    
                    lat2_circle,lon2_circle = qdrpos(traf.metric.fir_circle_point[0],traf.metric.fir_circle_point[1],180,traf.metric.fir_circle_radius)

                    x_circle,y_circle = self.ll2xy(traf.metric.fir_circle_point[0], traf.metric.fir_circle_point[1])
                    x2_circle,y2_circle = self.ll2xy(degrees(lat2_circle),degrees(lon2_circle))
                    radius = int(abs(y2_circle-y_circle))
                    
                    pg.draw.circle(self.radbmp,blue,(int(x_circle),int(y_circle)),radius, 2)


#            print pg.time.get_ticks()*0.001-t0," seconds to draw coastlines"

#---------- Draw background trails
            if traf.swtrails:
                traf.trails.buffer() # move all new trails to background

                trlsel = list( np.where(
                           self.onradar(traf.trails.bglat0,traf.trails.bglon0)+ \
                           self.onradar(traf.trails.bglat1,traf.trails.bglon1))[0])
    
                x0,y0 = self.ll2xy(traf.trails.bglat0,traf.trails.bglon0)
                x1,y1 = self.ll2xy(traf.trails.bglat1,traf.trails.bglon1)         

                for i in trlsel:
                    pg.draw.aaline(self.radbmp,(0,0,255),    \
                                        (x0[i],y0[i]),(x1[i],y1[i]))
                


## Draw metrics cells (by which switch?)
#                
#            cx,cy = self.ll2xy(traf.metric.regions.cellarea[3][0],   \
#                               traf.metric.regions.cellarea[3][1])           
#            for cell in traf.metric.regions.cellarea:
#                
#                x,y = self.ll2xy(cell[0],cell[1])
#                if ((cx>0 and cy>0 and \
#                     cx < self.width and cy < self.height) or (x>0 and y>0 \
#                    and x < self.width and y<self.height)):
#                   
#                    pg.draw.line(self.radbmp,green,(cx,cy),(x,y))
#                    cx,cy = x,y                


# Reset background drawing switch
            self.redrawradbg = False

# Blit background        
        self.win.blit(self.radbmp,(0,0))

# Decide to redraw radar picture of a/c
        syst = pg.time.get_ticks()*0.001
        redrawrad = self.redrawradbg or abs(syst-self.radt0)>=self.radardt
       
        if redrawrad:
            self.radt0 = syst # Update lats drawing time of radar


# Select which aircraft are within screen area
            trafsel = np.where((traf.lat>self.lat0)*(traf.lat<self.lat1) * \
                               (traf.lon>self.lon0)*(traf.lon<self.lon1))[0]
            
# ------------------- Draw aircraft
# Convert lat,lon to x,y

            trafx, trafy = self.ll2xy(traf.lat,traf.lon)
            if traf.swtrails:
                ltx,lty = self.ll2xy(traf.lastlat,traf.lastlon)

            for i in trafsel:

# Get index of ac symbol, based on heading and its rect object
                isymb = int((traf.trk[i]-self.ndcrs)/6.)%60
                pos   = self.acsymbol[isymb].get_rect()

# Draw aircraft symbol    
                pos.centerx = trafx[i]
                pos.centery = trafy[i]
                dy = self.fontrad.linedy*7/6
     
                self.win.blit(self.acsymbol[isymb],pos)

# Draw last trail part
                if traf.swtrails:
                    pg.draw.line(self.win,(0,255,255),
                             (ltx[i],lty[i]), (trafx[i],trafy[i]))

     
# Label text
                label = []
                if self.swlabel>0:
                    label.append(traf.id[i]) # Line 1 of label: id
                else:
                    label.append(" ")
                if self.swlabel>1:
                    label.append(str(int(traf.alt[i]/ft))) # Line 2 of label: altitude
                else:
                    label.append(" ")
                if self.swlabel>2:
                    cas = traf.cas[i]/kts
                    label.append(str(int(round(cas))))# line 3 of label: speed
                else:
                    label.append(" ")

 
# Check for changes in traffic label text   
                if not label[:3]==traf.label[i][:3]:

                    traf.label[i] =[]
                    labelbmp = pg.Surface((100,60),0,self.win)

                    self.fontrad.printat(labelbmp,0,0,label[0]) 
                    self.fontrad.printat(labelbmp,0,dy,label[1])
                    self.fontrad.printat(labelbmp,0,2*dy,label[2])

                    traf.label[i].append(label[0])
                    traf.label[i].append(label[1])
                    traf.label[i].append(label[2])
                    traf.label[i].append(labelbmp)
# Blit label
                dest = traf.label[i][3].get_rect()
                dest.top = trafy[i]-5
                dest.left = trafx[i]+15
                self.win.blit(traf.label[i][3],dest,None,pg.BLEND_ADD)
                
# Draw aircraft trails which are on screen
            if traf.swtrails:
                trlsel = list( np.where(
                           self.onradar(traf.trails.lat0,traf.trails.lon0)+ \
                           self.onradar(traf.trails.lat1,traf.trails.lon1))[0])
    
                x0,y0 = self.ll2xy(traf.trails.lat0,traf.trails.lon0)
                x1,y1 = self.ll2xy(traf.trails.lat1,traf.trails.lon1)         

                for i in trlsel:
                    pg.draw.line(self.win,(0,int(traf.trails.col[i]),255),   \
                                        (x0[i],y0[i]),(x1[i],y1[i]))

# Redraw background => buffer ; if >1500 foreground linepieces on screen
                if len(trlsel)>1500:
                     self.redrawradbg = True

# Draw edit window
        self.editwin.update()


        if self.redrawradbg or redrawrad or self.editwin.redraw:
    
            self.win.blit(self.editwin.bmp,(self.editwin.winx,self.editwin.winy))

# Draw frames

            pg.draw.rect(self.win,white,self.editwin.rect,1)
            pg.draw.rect(self.win,white,pg.Rect(1,1,self.width-1,self.height-1),1)

# Add debug line
            self.fontrad.printat(self.win,5,5,tim2txt(sim.t))
            self.fontrad.printat(self.win,5,5+self.fontrad.linedy, \
                     "ntraf = "+str(traf.ntraf))             
            self.fontrad.printat(self.win,5,5+2*self.fontrad.linedy, \
                   "Freq="+str(int(len(sim.dts)/max(0.001,sum(sim.dts)))))
    
# Frame ready, flip to screen
    
            pg.display.flip()

        
        return
#---------------------------------------------------------------------------
    
    def ll2xy(self,lat,lon):  

# RADAR mode:
        if not self.swnavdisp:
# Convert lat/lon to pixel x,y

# Normal case
            if self.lon1>self.lon0:
                x = self.width*(lon - self.lon0)/(self.lon1-self.lon0)

# Wrap around:
            else:
                dellon = 180.-self.lon0+self.lon1+180.
                xlon   = lon + (lon<0.)*360.
                x      = (xlon-self.lon0)/dellon*self.width
    
            y = self.height*(self.lat1 - lat)/(self.lat1-self.lat0)
# NAVDISP mode:
        else:

            qdr,dist = qdrdist(self.ndlat,self.ndlon,lat,lon)
            alpha    = np.radians(qdr-self.ndcrs)
            base     = 30.*(self.lat1-self.lat0)
            x       = dist*np.sin(alpha)/base*self.height + self.width/2
            y       = -dist*np.cos(alpha)/base*self.height + self.height/2
                
        return np.rint(x),np.rint(y)

#---------------------------------------------------------------------------

    def xy2ll(self,x,y):
        lat = self.lat0+(self.lat1-self.lat0)*(self.height-y)/self.height 

# Normal case
        if self.lon1>self.lon0:
            lon = self.lon0+(self.lon1-self.lon0)*x/self.width

# Wrap around:
        else:
            dellon = 360.+self.lon1-self.lon0
            xlon = self.lon0+x/self.width
            lon = xlon-360.*(lon>180.)
        
# Convert pixel x,y to lat/lan [deg]
        return lat,lon

#---------------------------------------------------------------------------

# Return boolean (also numpy array) with on or off radar screen (range check)
    def onradar(self,lat,lon):

# Radar mode
        if not self.swnavdisp:
# Normal case
            if self.lon1>self.lon0:
                sw = (lat > self.lat0) * (lat < self.lat1) * \
                    (lon > self.lon0) * (lon <self.lon1) == 1
                           
# Wrap around:
            else:
                sw = (lat > self.lat0) * (lat < self.lat1) * \
                    ((lon > self.lon0) + (lon <self.lon1)) == 1
# Else NAVDISP mode
        else:
            base = 30.*(self.lat1-self.lat0)
            dist = latlondist(self.ndlat,self.ndlon,lat,lon)/nm
            sw   = dist < base            
            
           
        return sw
#---------------------------------------------------------------------------

# Zoom-function
        
    def zoom(self,factor):

        oldvalues = self.lat0,self.lat1,self.lon0,self.lon1

# Zoom factor: 2.0 means halving the display size in degrees lat/lon
# ZOom out with e.g. 0.5

        ctrlat = (self.lat0+self.lat1)/2.
        dellat2 = (self.lat1-self.lat0)/2./factor
        self.lat0 = ctrlat-dellat2
        self.lat1 = ctrlat+dellat2

# Normal case
        if self.lon1>self.lon0:
            ctrlon = (self.lon0+self.lon1)/2.
            dellon2 = (self.lon1-self.lon0)/2./factor

# Wrap around
        else:
            ctrlon = (self.lon0+self.lon1+360.)/2
            dellon2 = (360.+self.lon1-self.lon0)/2./factor
            

            
# Wrap around
        self.lon0 = (ctrlon-dellon2+180.)%360. - 180.
        self.lon1 = (ctrlon+dellon2+180.)%360. - 180.

# Avoid getting out of range        
        if self.lat0<-90 or self.lat1>90.:
              self.lat0,self.lat1,self.lon0,self.lon1 = oldvalues
              
        self.redrawradbg = True
        self.navsel = ()
        self.satsel = ()
        self.geosel = ()

        return

#---------------------------------------------------------------------------

# Pan-function
        
    def pan(self,lat,lon):

# Maintain size        
        dellat2 = (self.lat1-self.lat0)*0.5

# Avoid getting out of range        
        self.ctrlat = max(min(lat,90.-dellat2),dellat2-90.)

# Allow wrap around of longitude
        dellon2 = dellat2*self.width/(self.height*cos(radians(self.ctrlat)))
        self.ctrlon = (lon + 180.)%360 - 180.

        self.lat0 = self.ctrlat - dellat2
        self.lat1 = self.ctrlat + dellat2
        self.lon0 = (self.ctrlon - dellon2+180.)%360. - 180.
        self.lon1 = (self.ctrlon + dellon2+180.)%360. - 180.


# Redraw background  
        self.redrawradbg = True
        self.navsel = ()
        self.satsel = ()
        self.geosel = ()

#        print "Pan lat,lon:",lat,lon
#        print "Latitude  range:",int(self.lat0),int(self.ctrlat),int(self.lat1)
#        print "Longitude range:",int(self.lon0),int(self.ctrlon),int(self.lon1)
#        print "dellon2 =",dellon2

        return

#---------------------------------------------------------------------------

# Switch to (True) /from (False) full screen mode

    def fullscreen(self,switch): # full screen switch

# Reset screen

        pg.display.quit()
        pg.display.init()

        di = pg.display.Info()

        pg.display.set_caption("BlueSky Open ATM Simulator (F11 = Full Screen)",
                                  "BlueSky")
        iconbmp = pg.image.load('icon.gif')        
        pg.display.set_icon(iconbmp)

        if switch:
# Full screen mode
            self.width  = di.current_w
            self.height = di.current_h
            reso = (self.width,self.height)
            self.win = pg.display.set_mode(reso,pg.FULLSCREEN|pg.HWSURFACE)
        else:
# Windowed                        
            self.height = min(self.height,di.current_h*90/100)
            self.width = min(self.width,di.current_w*90/100)
            reso = (self.width,self.height)
            self.win = pg.display.set_mode(reso)

# Adjust scaling
        dellat = self.lat1-self.lat0
        avelat = (self.lat0+self.lat1)/2.

        dellon = dellat*self.width/(self.height*cos(radians(avelat)))

        self.lon1 = self.lon0 + dellon


        self.radbmp = self.win.copy()

# Force redraw and reselect
        self.redrawradbg = True
        self.satsel = ()
        self.navsel = ()
        self.geosel = ()

        return
