""" 
Keyboard class definition : keyboard & mouse input processing class

Methods:
    Keyboard()                         :  constructor

    update(sim,cmd,scr,traf)           : Check for input & process it
    radarclick(pos,command,scr,traf)   : Process click on radar window to
                                         to insert data in edit window

Created by  : Jacco M. Hoekstra (TU Delft)
Date        : September 2013

Modifation  :
By          :
Date        :

"""


import pygame as pg
from math import *

class Keyboard:
    def __init__(self):

        self.dragedit = False  # Edit window initially not connected to mouse
        self.lastcmd  = ""     # previously typed command line
        return
    
    def update(self,sim,cmd,scr,traf):

# Get events        
        for event in pg.event.get():
            if event.type==pg.QUIT:
                sim.stop()




            elif event.type==pg.KEYDOWN:

# Alphanumeric key
                if event.key>31 and event.key<127:
                    scr.editwin.insert(str(event.unicode).upper())

                elif event.key==13: # ENTER
                    cmdline = scr.editwin.getline()
                    scr.editwin.enter()
                    if len(cmdline)>0:
                        self.lastcmd = cmdline
                        cmd.stack(cmdline)

                elif event.key==8:   # BACKSPACE
                    scr.editwin.backspace()

                elif event.key==27: # ESCAPE
                    sim.stop()

                elif event.key ==pg.K_F3: # F3: Insert last command
                    scr.editwin.insert(self.lastcmd.strip().upper()+" ")
                   
# Display keys
                elif event.key == 269: # Num lock minus
                    cmd.stack("ZOOM OUT")
                elif event.key == 270: # Num lock pluus
                    cmd.stack("ZOOM IN")

                elif event.key == 273: # Cursor up
                    cmd.stack("PAN UP")
                elif event.key == 274: # Num lock up
                    cmd.stack("PAN DOWN")
                elif event.key == 275: # Num lock down
                    cmd.stack("PAN RIGHT")
                elif event.key == 276: # Num lock right
                    cmd.stack("PAN LEFT")

                elif event.key ==pg.K_F11: # F11: Toggle full screen
                    
                    scr.swfullscreen = not scr.swfullscreen 
                    scr.fullscreen(scr.swfullscreen)

                else: #TEST OPTION
                    pass
#                    scr.editwin.insert(str(event.key))
                        
#debug                    print cmdline

# TBD            scr.insedit(chr(ikey))
#  End of keys selection


# Mouse events:
#    MOUSEMOTION      pos, rel, buttons
#    MOUSEBUTTONUP    pos, button
#    MOUSEBUTTONDOWN  pos, button

# Mouse button 1 release: enter value in edit line
            elif event.type==pg.MOUSEBUTTONUP:

# Reselase edit window if necessary
                if event.button==1:
                    if self.dragedit:
                        scr.editwin.winx = event.pos[0]-self.dragdx
                        scr.editwin.winy = event.pos[1]-self.dragdy
                        scr.editwin.winy = scr.editwin.fontedit.linedy *       \
                              (scr.editwin.winy/scr.editwin.fontedit.linedy)
                        scr.editwin.rect = pg.Rect(scr.editwin.winx,scr.editwin.winy, \
                             scr.editwin.bmpdx,scr.editwin.bmpdy)
                        scr.redrawedit = True

# In all other cases process as radar click
                    else:
                        self.radarclick(event.pos,cmd,scr,traf)

# Make sure edit window is released
                self.dragedit = False

# Mouse button down: lock onto edit window if insied edit window     

            elif event.type==pg.MOUSEBUTTONDOWN:
                if event.button==1:
                    if scr.editwin.rect.collidepoint(event.pos):
                        self.dragedit=True
                        self.dragdx = event.pos[0]-scr.editwin.winx
                        self.dragdy = event.pos[1]-scr.editwin.winy
                        scr.redrawedit = True

# Mouse motion: drag edit widnow with mouse, if necessary
# Ehck also for mouse button 1                    
            elif self.dragedit and event.type==pg.MOUSEMOTION:
                pressed = pg.mouse.get_pressed()[0]
                if not pressed:
                    self.dragedit = False
                else:
                    scr.editwin.winx = event.pos[0]-self.dragdx
                    scr.editwin.winy = event.pos[1]-self.dragdy
                    scr.editwin.rect = pg.Rect(scr.editwin.winx,scr.editwin.winy, \
                             scr.editwin.bmpdx,scr.editwin.bmpdy)
                    scr.redrawedit = True             
               
#========== End of Update=========
        return
    
# Process click in radar window
    
    def radarclick(self,pos,command,scr,traf):

# Not in navdisp mode
        if scr.swnavdisp:   return

#---------- Interpret current edit line

        cmdline = scr.editwin.getline()

        while cmdline.find(",,")>=0:
            cmdline = cmdline.replace(",,",",@,") # Mark empty arguments

# Replace comma's by space
        cmdline = cmdline.replace(","," ")            

# Split using spaces
        cmdargs = cmdline.split()     # Make list of cmd arguments

# Adjust for empty arguments
        for i in range(len(cmdargs)):
            if cmdargs[i]=="@":
                cmdargs[i]=""
        numargs = len(cmdargs)-1

# Save command
        if numargs>=0:
            cmd = cmdargs[0]
        else:
            cmd=""

# Check for acid first in command line

        if numargs >=1:
            if cmd != "" and traf.id.count(cmd) >0:
                acid = cmd
                cmd = cmdargs[1]
                cmdargs[1] = acid

            if numargs>=1:
                    acid = cmdargs[1]
                    
# -------- Process click
# Double click on aircaft = POS command

        if numargs==0 and traf.id.count(cmdargs[0])>0:
            scr.editwin.enter()
            command.stack("POS "+cmdargs[0])

# No command: insert nearest aircraft id

        if cmd=="" :
            lat,lon = scr.xy2ll(pos[0],pos[1])
            idx = traf.findnearest(lat,lon)
            if idx>=0:
                scr.editwin.insert(traf.id[idx]+" ")
  
# Insert: nearestaircraft id
        elif (cmd =="HDG" or cmd=="POS" or cmd=="SPD" or cmd=="ALT" or \
              cmd == "DEL" or cmd=="VS" or cmd=="MOVE" or cmd=="ND" or\
              cmd == "NAVDISP")    \
              and numargs == 0:

            lat,lon = scr.xy2ll(pos[0],pos[1])
            idx = traf.findnearest(lat,lon)
            if idx>=0:
                scr.editwin.insert(traf.id[idx]+" ")
                


# Insert: lat,lon position        
        elif (cmd=="CRE" and numargs==2) or    \
             (cmd=="MOVE" and numargs==1) or   \
             (cmd=="AREA" and (numargs==0 or numargs==2)) or \
             (cmd=="PAN" and numargs==0)    or  \
             (cmd=="DIST" and (numargs==0 or numargs==2)):

            lat,lon = scr.xy2ll(pos[0],pos[1])
            scr.editwin.insert(" "+str(lat)+","+str(lon)+" ")

            if cmd=="PAN":
                cmdline = scr.editwin.getline()
                scr.editwin.enter()
                if len(cmdline)>0:
                    command.stack(cmdline)
#Insert: heading
        elif (cmd=="CRE" and numargs==4) or     \
             (cmd=="HDG" and numargs == 1) or   \
             (cmd=="MOVE" and numargs == 4):

# Read start position from line

            if cmd=="CRE":
                try:
                    lat = float(cmdargs[3])
                    lon = float(cmdargs[4])
                    synerr = False
                except:
                    synerr = True
            elif cmd=="MOVE":
                try:
                    lat = float(cmdargs[2])
                    lon = float(cmdargs[3])
                    synerr = False
                except:
                    synerr = True
            else:
                if traf.id.count(acid)>0:
                    idx = traf.id.index(acid)
                    lat = traf.lat[idx]
                    lon = traf.lon[idx]
                    synerr = False
                else:
                    synerr = True
            
# Estimate heading using clicked position

            if not synerr:
                lat1,lon1 = scr.xy2ll(pos[0],pos[1])
                dy =  lat1-lat
                dx = (lon1-lon)*cos(radians(lat))
                hdg = degrees(atan2(dx,dy))%360.

                scr.editwin.insert(" "+str(int(hdg))+" ")

# Insert ENTER if hdg command
                if cmd=="HDG":
                    cmdline = scr.editwin.getline()
                    scr.editwin.enter()
                    if len(cmdline)>0:
                        self.lastcmd = cmdline
                        command.stack(cmdline)
        return
        
    
