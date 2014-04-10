""" 
Commandstack class definition : command stack & processing class

Methods:
    Commandstack()          :  constructor

    stack(cmdline)          : add a command to the command stack
    openfile(scenname)      : start playing a scenario file scenname.SCN
                              from scenario folder
    savefile(scenname,traf) : save current traffic situation as 
                              scenario file scenname.SCN
    checkfile(t)            : check whether commands need to be 
                              processed from scenario file
    
    process(sim,traf,scr)   : central command processing method
                              (with long elif tree with all commands)
   
Created by  : Jacco M. Hoekstra (TU Delft)
Date        : September 2013

Modifation  :
By          :
Date        :

"""


from math import *
from random import random,randint
import os

from aero import kts,ft,fpm, nm, lbs,      \
                 qdrdist,cas2tas,mach2tas,tas2cas,tas2eas,density
from tools import txt2alt,txt2spd
from dialogs import fileopen as opendialog

#-----------------------------------------------------------------

class Commandstack:


    def __init__(self):
        self.cmdstack=[]
        self.scenlines = []
        self.scentime = 9999999.
        self.linenr = 0
        
        try:

           f  = open("./data/icfile.dat","r")
           lines = f.readlines()
           f.close()
           i = 0
           while lines[i]=="#":  # Skip comment lines
              i=i+1
           isep = lines[i].find("=")
           if isep>0:
               fname = lines[i][isep+1:].strip()
#               print "init scn fname=",fname
               self.openfile(fname)
               
        except:
           pass            
        return

    def stack(self,cmdline): # Stack one or more commands separated by ";"
        cline = cmdline.strip() # remove leading & trailing spaces
        if cline.count(";")==0:
            self.cmdstack.append(cline.upper()) #pass on in upper case only
        else:
            clinelst = cline.split(";")
            for line in clinelst:
                self.cmdstack.append(line.upper()) #pass on in upper case only
            
        return

    def openfile(self,scenname):

# No filename: empty start
        if len(scenname.strip())==0:
#            print "empty start"
            self.scenlines=[]

# Save also empty ic file for next time
            f  = open("./data/icfile.dat","w")
            f.write("icfile= "+chr(13)+chr(10))
            f.write(" ")
            f.close()
            
            return

# Add .scn extension if necessary            
        if scenname.lower().find(".scn")<0:
            scenname = scenname+".scn"

# If it is with a path don't touch it, else add path
        if scenname.find("/")<0:
            scenfile = "./scenario/"+scenname.lower()
        else:
            scenfile = scenname

        print "Reading scenario file: ",scenfile

# Read lines into buffer
        self.linenr = 0        
        if os.path.exists(scenfile):
            fscen = open(scenfile,'r')
            self.scenlines = fscen.readlines()
            fscen.close()
            i = 0
            while i<len(self.scenlines):
                if len(self.scenlines[i].strip())<=12 or \
                                      self.scenlines[i][0]=="#":
         
                    del self.scenlines[i]
                else:
                    i = i+1
         

#Optional?            scenlines.sort()

## Set timer until what is read
#
## Time stamp: hh:mm:ss.hh>
#
#            tstamp = self.scenlines[0][:11]
#            ihr = int(tstamp[:2])
#            imin = int(tstamp[3:5])
#            isec = float(tstamp[6:8]+"."+tstamp[9:11])
            self.scentime = 0.

# Save ic file for next time
            f  = open("./data/icfile.dat","w")
            f.write("icfile="+scenfile+chr(13)+chr(10))
            f.write(" ")
            f.close()
        else:
            print"Error: cannot find file:",scenfile

        return
       
    def checkfile(self,sim):

# Only when in operate
        if sim.mode!=sim.op:
            return

# Limit umber of lines to process per call
        n = 0
        nmax = 500  # Max number of commands read per update cycle

        while sim.t>=self.scentime and n<nmax                           \
                   and self.linenr<len(self.scenlines):
            line = self.scenlines[self.linenr]
            self.linenr = self.linenr+1
            
            if line[0]!="#" and len(line.strip())>12:
                self.stack(line[12:])            
                n = n+1
    
            if self.linenr<len(self.scenlines):
                line = self.scenlines[self.linenr]
                try:                    
                    tstamp = self.scenlines[self.linenr][:11]
                    ihr = int(tstamp[:2])
                    imin = int(tstamp[3:5])
                    isec = float(tstamp[6:8]+"."+tstamp[9:11])
                    self.scentime = ihr*3600.+imin*60.+isec
                except:
                    self.linenr = self.linenr+1
            else:
                self.scentime = 999999999.
        return
        
    def saveic(self,fname,sim,traf):

# Add extension .scn if not already present
        if fname.find(".scn")<0 and fname.find(".SCN"):
            fname=fname+".scn"

# If it is with path don't touch it, else add path
        if fname.find("/")<0:
            scenfile = "./scenario/"+fname.lower()
# Open file
        try:
            f = open(scenfile,"w")
        except: 
            return -1

# Write files
        timtxt = "00:00:00.00>"

        for i in range(traf.ntraf):

# CRE acid,type,lat,lon,hdg,alt,spd
            cmdline = "CRE "+traf.id[i]+","+traf.type[i]+","+     \
                repr(traf.lat[i]) + "," + repr(traf.lon[i])+","+  \
                repr(traf.trk[i]) + "," + repr(traf.alt[i]/ft)+","+  \
                repr(tas2cas(traf.tas[i],traf.alt[i])/kts)
                
            f.write(timtxt+cmdline+chr(13)+chr(10))

# VS acid,vs            
            if abs(traf.vs[i])>0.05: # 10 fpm dead band
                if traf.avs[i]>0.05:
                    vs_ = traf.avs[i]/fpm
                else:
                    vs_ = traf.vs[i]/fpm
                
                cmdline = "VS "+traf.id[i]+","+repr(vs_)
                f.write(timtxt+cmdline+chr(13)+chr(10))

# Autopilot commands
# Altitude
            if abs(traf.alt[i]-traf.aalt[i]) > 10.:
                cmdline = "ALT "+traf.id[i]+","+repr(traf.aalt[i]/ft)

# Heading as well when heading select
            delhdg = (traf.trk[i]-traf.ahdg[i]+180.)%360.-180.
            if abs(delhdg) > 0.5:
                cmdline = "ALT "+traf.id[i]+","+repr(traf.aalt[i]/ft)

# Speed select? => Record
            rho = density(traf.alt[i]) # alt in m!
            aptas = sqrt(1.225/rho)*traf.aspd[i]
            delspd = aptas- traf.tas[i]

            if abs(delspd) > 0.4:
                cmdline = "SPD "+traf.id[i]+","+repr(traf.aspd[i]/kts)
                
# DEST acid,dest-apt
            if traf.dest[i]!="":
                cmdline = "DEST " + traf.id[i] + "," + traf.dest[i]
                f.write(timtxt+cmdline+chr(13)+chr(10))
                 
# ORIG acid,orig-apt
            if traf.orig[i]!="":
                cmdline = "ORIG "+traf.id[i]+","+ \
                          traf.dest[i]
                f.write(timtxt+cmdline+chr(13)+chr(10))

# Saveic: should close
        f.close()                

        return 0

    def process(self,sim,traf,scr): #process and empty command stack


# Process stack of commands

        for cmdline in self.cmdstack:

# Use both comma and space as aseparatotr: two commas mean an empty argument
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

# Empty line: next command                    
            if len(cmdargs)==0 or cmdline.strip()=="":
                continue
        
            cmd = cmdargs[0]

#debug            print cmdargs
            numargs = len(cmdargs)-1

# First check for alternate syntax: acid cmd args 2-3
                        
            if cmd != "" and traf.id.count(cmd) >0:
                if numargs>=1:
                    acid = cmd
                    cmd = cmdargs[1]
                    cmdargs[1] = acid
                    cmdargs[0] = cmd
                else:
                    cmdargs.append(cmdargs[0])
                    cmdargs[0] = 'POS'
                    cmd='POS'
                    numargs = 1

# Assume syntax is ok (default)
            syntax = True

# Catch general errors
            if True:    # optional to switch error protection off
#            try:

#----------------------------------------------------------------------
# Command interpreter branches
#----------------------------------------------------------------------

# QUIT/STOP/END/Q: stop program    
                if cmd == "QUIT" or cmd == "STOP" or cmd == "END" \
                   or cmd=="EXIT" or cmd[0] == "Q":
                       
                    sim.stop()
    
                    
#----------------------------------------------------------------------                    
# CRE: CREate command: Create an aircraft           
                elif cmd[:3]=="CRE":
                    if numargs<=1:
                        scr.echo("CRE acid,type,lat,lon,hdg,alt,spd")
                        continue           # next command
                    elif numargs>=2:
                        acid = cmdargs[1].upper()  # arguments are strings
                        actype = cmdargs[2]  # arguments are strings
                        if traf.id.count(acid)>0:
                            scr.echo("CRE error: "+acid+" already exists.")
                            continue
# Decode with check
                    aclat = float(cmdargs[3]) # deg
                    aclon = float(cmdargs[4]) # deg
                    achdg = float(cmdargs[5]) # deg
                    acalt = txt2alt(cmdargs[6])*ft  # m

                    if acalt<=-900:
                        syntax = False
                        acalt = 0.
                        
# Speed
                    acspd = txt2spd(cmdargs[7],acalt) # kts/M => m/s
                    if acspd < 0.:
                        syntax = False
     
#                    print cmdargs
                    
                    if syntax:
                        traf.create(acid,actype,aclat,aclon,achdg,acalt,acspd)
                    else:
                        print "Syntax error in command"
                        scr.echo("Syntax error in command")
                        scr.echo("CRE acid,type,lat,lon,hdg,alt,spd")
                        continue

#----------------------------------------------------------------------    
# POS command: traffic info;
                elif cmd=="POS":
                    if numargs >=1:
                        acid = cmdargs[1]
    
# Does aircraft exist?
                        idx = traf.id2idx(acid)
                        if idx<0:
                            scr.echo("POS: "+acid+" not found.")
                            
# print info on aircraft if found
                        else:    
                             scr.echo("Info on "+acid+" "+traf.type[idx])
                             scr.echo("Pos = "+str((traf.lat[idx],traf.lon[idx])))
                             scr.echo(str(int(traf.tas[idx]/kts))+" kts at " \
                                             +str(int(traf.alt[idx]/ft))+" ft")
                             scr.echo("Hdg = "+str(int(traf.trk[idx])))
                             scr.echo("Dest = "+traf.dest[idx])
    
                    else:
                        syntax =False
                        
#----------------------------------------------------------------------    
# MOVE command: Move aircraft: MOVE acid, lat,lon[,alt,hdg,spd,vspd]
                elif cmd=="MOVE":
                    if numargs >=1:
                        acid = cmdargs[1]
                        
    
# Does aircraft exist?
                        idx = traf.id2idx(acid)
                        if idx<0:
                            scr.echo("MOVE: "+acid+" not found.")
                            idx  = -1
                            
# Move aircraft for which there are data
                        if idx>=0:
    
                            if numargs>=3:  # Position lat,lon
                                if cmdargs[2]!="":
                                    lat = float(cmdargs[2])
                                    traf.lat[idx] = lat
                                if cmdargs[3]!="":
                                    lon = float(cmdargs[3])
                                    traf.lon[idx] = lon

                            if numargs>=4 and cmdargs[4]!="":  # altitude
                                alt = txt2alt(cmdargs[4])
                                traf.alt[idx] = alt*ft
                                traf.aalt[idx] = alt*ft

                            if numargs>=5 and cmdargs[5]!="":  # heading(track)
                                traf.trk[idx] = float(cmdargs[5])
                                traf.ahdg[idx] = traf.trk[idx]

                            if numargs>=6 and cmdargs[6]!="":  # speed
                                acspd = txt2spd(cmdargs[6],traf.alt[idx])
               
                                if acspd > 0.:                                
                                   traf.tas[idx] = acspd
                                   traf.aspd[idx]= tas2eas(traf.tas[idx],traf.alt[idx])
                                else:
                                    syntax = False

                            if numargs>=7 and cmdargs[7]!="":  # vertical speed
                               #print "cmdargs[7]=",cmdargs[7]                               
                               traf.vs[idx] = float(cmdargs[7])*fpm
                            
                         
                    else:
                        scr.echo("MOVE acid,lat,lon,[alt,hdg,spd,vspd]")

#----------------------------------------------------------------------    
# DEL: Delete command: delete an aircraft
                elif cmd=="DEL":
                    if numargs == 1:
                        if cmdargs[1]!="DEL":
                            success = traf.delete(cmdargs[1].upper())
                        else:
                            succes = traf.delete(cmdargs[0].upper())
                    if not success:
                        if not (cmdargs[1]=="DEL"):                    
                           scr.echo("DEL: "+cmdargs[1]+" not found.")
                        else:
                           scr.echo("DEL: "+cmdargs[1]+" not found.")
                        

#----------------------------------------------------------------------    
# ALT command: altitude [ft] , [VS [fpm]] altitude autopilot command
                elif cmd=="ALT":
                    if numargs<2:
                        scr.echo("ALT acid,alt[ft]")
                    elif numargs >= 2:
                        acid = cmdargs[1].upper()
                        idx = traf.id2idx(acid)
                        if idx >= 0:
                            try:
                                traf.aalt[idx]=float(cmdargs[2])*ft
                                traf.swvnav[idx] =False

                                delalt = traf.aalt[idx]-traf.alt[idx]

# Check for VS with opposite sign => use default vs by setting autopilot vs to zero
                                if traf.avs[idx]*delalt<0. and abs(traf.avs[idx])>0.01:
                                    traf.avs[idx] = 0.

# Check for optional VS argument                                    
                                if numargs == 3:
                                    traf.avs[idx]=float(cmdargs[3])*fpm

                            except:
                                syntax = False
                                
                        else:
                            scr.echo(cmd+": "+acid+" not found.")

                    else:
                        syntax = False            
#----------------------------------------------------------------------    
# HDG heading [deg,true] heading autpilot command
                elif cmd=="HDG":
                    if numargs<2:
                        scr.echo("HDG acid,hdg[deg,True]")
                    elif numargs == 2:
                        acid = cmdargs[1].upper()
                        idx = traf.id.index(acid)
                        if idx >= 0:
                            traf.ahdg[idx]= float(cmdargs[2])
                            traf.swlnav[idx] =False
                        else:
                            scr.echo(cmd+": "+acid+" not found.")
                    else:
                        syntax = False            

#----------------------------------------------------------------------    
# SPD speed [kts, CAS] Speed autopilot command
# Todo: add Mach, and note how currently EAS is stored not CAS!

                elif cmd=="SPD":
                    if numargs<2:
                        scr.echo("SPD acid,spd[kts,EAS]")
                    elif numargs == 2:
                        acid = cmdargs[1].upper()
                        idx = traf.id2idx(acid)
                        if idx >= 0:
#                            cascmd = float(cmdargs[2])*kts
#                            tascmd = cas2tas(cascmd,traf.alt[idx])
#                            eascmd = tas2eas(tascmd,traf.alt[idx])

                            eascmd = float(cmdargs[2])*kts
                            traf.aspd[idx] = eascmd
                            traf.swvnav[idx] =False

                        else:
                            scr.echo(cmd+": "+acid+" not found.")
                    else:
                        syntax = False            

#----------------------------------------------------------------------    
# VS vertspeed [ft/min] Vertical speed auropilot command
                elif cmd=="VS":
                    if numargs<2:
                        scr.echo("VS acid,vspd [ft/min]")
                    elif numargs == 2:
                        acid = cmdargs[1]
                        idx = traf.id2idx(acid)
                        if idx >= 0:
                            traf.avs[idx]=float(cmdargs[2])*fpm
                        else:
                            scr.echo(cmd+": "+acid+" not found.")
                    else:
                        syntax = False            
                   
#----------------------------------------------------------------------    
# DEST/ORIG: Destination/Origin command: set destination/origin airport            
                elif cmd=="DEST" or cmd=="ORIG":
                    if numargs == 2:
                        acid = cmdargs[1]
                        idx = traf.id2idx(acid)
                        if idx >= 0:

# Destination is default waypoint
                            if cmd=="DEST":                        
                                traf.dest[idx]=cmdargs[2].upper().strip()
                                iwp = traf.route[idx].appendwp(traf.dest[idx],
                                                         traf.route[idx].dest,
                                                         traf.lat[idx],traf.lon[idx],
                                                         0.0,traf.cas[idx])
# If only waypoint: activate
                                if iwp==0:
                                    traf.actwplat[idx]=traf.route[idx].wplat[iwp]
                                    traf.actwplon[idx]=traf.route[idx].wplon[iwp]
                                    traf.actwpalt[idx]=traf.route[idx].wpalt[iwp]
                                    traf.actwpspd[idx]=traf.route[idx].wpspd[iwp]
                                    traf.swlnav[idx] = True

# If not found, say so                                    
                                elif iwp<0:    
                                    scr.echo(traf.dest[idx] + " not found.")
                                  
# Origin: bookkepeing only for now                                
                            else:
                                traf.orig[idx]=cmdargs[2]
    
                        else:
                            scr.echo(cmd+": " + acid + " not found.")
                    else:
                        syntax = False

#----------------------------------------------------------------------                         
# ZOOM command (or use ++++  or --  to zoom in or out)            
                elif cmd[:4]=="ZOOM" or cmd[0]=="+" or cmd[0]=="=" or cmd[0]=="-":
                    if cmd[0]!="Z":
                        nplus = cmd.count("+")+cmd.count("=") #= equals + (same key)
                        nmin  = cmd.count("-")
                        zoomfac = sqrt(2)**nplus/(sqrt(2)**nmin)
                        scr.zoom(zoomfac)
                    else:
                        syntax = len(cmdargs)==2
                        if syntax:
                            if cmdargs[1]=="IN":
                                scr.zoom(1.4142135623730951) # sqrt(2.)
          
                            elif cmdargs[1]=="OUT":
                                scr.zoom(0.70710678118654746) #1./sqrt(2.)
                            else:
                                syntax = False
                           
                        if not syntax:
                            print "Syntax error in command"
                            scr.echo("Syntax error in command")
                            scr.echo("ZOOM IN/OUT")
                            continue # Skip default syntyax message

#----------------------------------------------------------------------
# PAN command            
                elif cmd[:4]=="PAN":
                                        
                    if not (numargs==1 or numargs==2):
                        scr.echo("Syntax error in command")
                        scr.echo("PAN LEFT/RIGHT/UP/DOWN/acid/airport/navid")
                        continue
# LEFT/RIGHT/UP/DOWN
                    elif numargs==1:
                        if cmdargs[1]=="LEFT":
                            scr.pan(scr.ctrlat,scr.lon0)
      
                        elif cmdargs[1]=="RIGHT":
                            scr.pan(scr.ctrlat,scr.lon1)
    
                        elif cmdargs[1]=="UP":
                            scr.pan(scr.lat1,scr.ctrlon)
    
                        elif cmdargs[1]=="DOWN":
                            scr.pan(scr.lat0,scr.ctrlon)

# Try aicraft id, waypoint of airport
                        else:
                            i = traf.id2idx(cmdargs[1])
                            if i>=0:
                                scr.pan(traf.lat[i],traf.lon[i])
                            else:
                                i = traf.navdb.getwpidx(cmdargs[1],\
                                                  scr.ctrlat,scr.ctrlon)
                                if i>=0:
                                    scr.pan(traf.navdb.wplat[i],  \
                                            traf.navdb.wplon[i])
                                else:
                                    i = traf.navdb.getapidx(cmdargs[1])
                                    if i>=0:
                                        scr.pan(traf.navdb.aplat[i], \
                                                traf.navdb.aplon[i])
                                    else:
                                        scr.echo(cmdargs[1]+" not found.")
                                    
# PAN to lat,lon position
                            
                    elif numargs==2:
                        lat = float(cmdargs[1])
                        lon = float(cmdargs[2])
                        scr.pan(lat,lon)

# NAVDISP/ND  acid:  Activate Navdisplay mode
                elif cmd=="ND" or cmd=="NAVDISP":

                    if numargs<1:  # Help text
                        scr.echo("NAVDISP acid/OFF")
                        if scr.swnavdisp:
                            scr.echo("Ownship is"+scr.ndacid)
                        else:
                            scr.echo("NAVDISP is off")

# Or switch off
                    elif cmdargs[1]=="OFF":
                            scr.swnavdisp = False
                            scr.redrawradbg = True
                            scr.geosel = ()
                            scr.firsel = ()

# Follow aircraft
                        
                    else:
                        i = traf.id2idx(cmdargs[1])
                        if i>=0:
                            scr.ndacid = cmdargs[1]
                            scr.swnavdisp = True
                            scr.redrawradbg = True
                            scr.geosel = ()
                            scr.firsel = ()
                        else:
                            scr.echo("NAVDISP: "+cmdargs[1]+" not found.")
                        
                        
#----------------------------------------------------------------------                    
# IC scenfile: command: restart with new filename (.scn will be added if necessary)
                elif cmd=="IC":
                    sim.mode = sim.init
    
# If no arg is given: check
                    if numargs>=1:
                        filename = cmdargs[1]
                    else:
                        filename = opendialog()
    
                    if filename.strip()!="":
                        scr.echo("Opening "+filename+" ...")
    
# Open file in ./scenario subfolder
                    self.scentime = 0.
                    sim.t = 0.
    
                    self.openfile(filename)
#----------------------------------------------------------------------    
# OP: Continue to run
                elif cmd=="OP" or cmd=="START" or cmd=="CONTINUE" or cmd=="RUN":
                   sim.play()

#----------------------------------------------------------------------            
# HOLD/PAUSE: HOLD/PAUSE mode
                elif cmd=="HOLD" or cmd=="PAUSE":
                   sim.pause()

#----------------------------------------------------------------------    
# SAVE/SAVEIC Save current traffic situation as IC scn file
                elif cmd=="SAVEIC":
                    if numargs<=0:
                        scr.echo("SAVEIC needs filename")
                    else:
                        errcode = self.saveic(cmdargs[1],sim,traf)
                        if errcode==-1:
                            scr.echo("SAVEIC: Error writing file")

#----------------------------------------------------------------------    
# DT: set value of DT for FIXDT mode            
                elif cmd=="DT":
                    if numargs<1:
                        scr.echo("DT [dt] sets DT for fixdt mode")
                        scr.echo("Current dt = "+str(sim.fixdt))
                    else:
                        dt_ = float(cmdargs[1])
                        sim.fixdt = abs(dt_)
    
#----------------------------------------------------------------------
# FIXDT: switch FIXDT mode on/off           
                elif cmd=="FIXDT":
                    if numargs<1:
                        scr.echo("FIXDT ON/OFF [,howmanyseconds]")
                        scr.echo("Current dt = "+str(sim.fixdt))
                        if sim.ffmode:  
                            scr.echo("FIXDT mode is ON")
                            if sim.ffstop>0.:
                                t_ = sim.ffstop-sim.t
                                scr.echo("for "+str(t_)+" more seconds")
                        else:
                            scr.echo("FIXDT mode is OFF")
                    else:
                        if cmdargs[1].upper()=="ON":
                            sim.ffmode = True
                            if numargs >=2:
                                try:
                                    tstop_ = float(cmdargs[2])
                                    sim.ffstop = abs(tstop_)+sim.t
                                except:
                                    sim.ffstop = -1.
                                    syntax = False # syntax is not ok
                            
                        elif cmdargs[1].upper()[:2]=="OF":
                            sim.ffmode = False
                            
#----------------------------------------------------------------------                        
# METRICS command: METRICS/METRICS OFF/0/1/2 [dt]  analyze traffic complexity metrics

                elif cmd[:6]=="METRIC":
                    if numargs < 1:
                        scr.echo("METRICS/METRICS OFF/0/1/2 [dt]")
                        
                        if traf.metricSwitch == 1:
                            scr.echo("")
                            scr.echo("Active: "+"("+str(traf.metric.metric_number+1)+") "+traf.metric.name[traf.metric.metric_number])
                            scr.echo("Current dt: "+str(traf.metric.dt)+" s")
                        if traf.metricSwitch == 0:
                            scr.echo("No metric active")

                    elif cmdargs[1] == "ON":  # arguments are strings
                        scr.echo("METRICS/METRICS OFF/0/1/2 [dt]")

                    elif cmdargs[1] == "OFF":  # arguments are strings
                        traf.metricSwitch = 0
                        scr.echo("Metric is off")

                    else:
                        metric_number = int(cmdargs[1])-1
                        if metric_number == -1:
                            traf.metricSwitch = 0
                            scr.echo("Metric is off")

                        elif metric_number <= len(traf.metric.name) and metric_number >= 0:
                            if traf.area == "Circle":
                                traf.metricSwitch = 1
                                scr.echo("("+str(traf.metric.metric_number+1)+") "+traf.metric.name[traf.metric.metric_number]+" activated")
                                try:
                                    metric_dt = float(cmdargs[2])
                                    if metric_dt > 0:
                                        traf.metric.dt = metric_dt
                                        scr.echo("with dt = "+str(metric_dt))
                                    else:
                                        scr.echo("No valid dt")  
                                except:
                                    scr.echo("with dt = "+str(traf.metric.dt))
                            else:
                                scr.echo("First define AREA FIR")
                        else:
                            scr.echo("No such metric")
                        
                   
#----------------------------------------------------------------------    
# AREA command: AREA lat0,lon0,lat1,lon1[,lowalt]  
#               AREA FIR fir radius [lowalt]
                elif cmd=="AREA":

                    if numargs == 0:
                        scr.echo("AREA lat0,lon0,lat1,lon1[,lowalt]")
                        scr.echo("or")
                        scr.echo("AREA fir,radius[,lowalt]")
                    elif numargs == 1 and cmdargs[1]!="OFF" and cmdargs[1]!="FIR":
                        scr.echo("AREA lat0,lon0,lat1,lon1[,lowalt]")
                        scr.echo("or")
                        scr.echo("AREA fir,radius[,lowalt]")
                    elif numargs==1:
                        if cmdargs[1]=="OFF":
                            traf.swarea = False
                            scr.redrawradbg = True
                            traf.area = ""
                        if cmdargs[1] == "FIR":
                            scr.echo("Specify FIR")

                    elif numargs > 1 and cmdargs[1][0].isdigit():
                        
                        lat0 = float(cmdargs[1])  # [deg]
                        lon0 = float(cmdargs[2])  # [deg]
                        lat1 = float(cmdargs[3])  # [deg]
                        lon1 = float(cmdargs[4])  # [deg]

                        traf.arealat0 = min(lat0,lat1)
                        traf.arealat1 = max(lat0,lat1)
                        traf.arealon0 = min(lon0,lon1)
                        traf.arealon1 = max(lon0,lon1)
                        
                        if numargs==5:
                            traf.areafloor = float(cmdargs[5])*ft
                        else:
                            traf.areafloor = -9999999.
                        
                        traf.area = "Square"
                        traf.swarea = True
                        scr.redrawradbg = True

# Avoid mass delete due to redefinition of area
                        traf.inside = traf.ntraf*[False]
                    
                    elif numargs > 2 and cmdargs[1] == "FIR":
                                              
                        for i in range(0,len(traf.navdb.fir)):
                            if cmdargs[2] == traf.navdb.fir[i][0]:
                                break
                        traf.metric.fir_number = i
                        if cmdargs[2] != traf.navdb.fir[i][0]:
                              scr.echo("Uknown FIR, try again")  
                        traf.metric.fir_circle_point = traf.metric.metric_Area.FIR_circle(traf.navdb,traf.metric.fir_number)                        
                        traf.metric.fir_circle_radius = float(cmdargs[3])
                        
                        if numargs==4:
                            traf.areafloor = float(cmdargs[4])*ft
                        else:
                            traf.areafloor = -9999999.
                        if numargs > 4:
                            scr.echo("AREA command unknown")
                            
                        traf.area = "Circle"
                        traf.swarea = True
                        scr.redrawradbg = True
                        traf.inside = traf.ntraf*[False]
                    else:
                        scr.echo("AREA command unknown")
                        scr.echo("AREA lat0,lon0,lat1,lon1[,lowalt]")
                        scr.echo("or")
                        scr.echo("AREA fir,radius[,lowalt]")

#----------------------------------------------------------------------    
# TAXI command: TAXI ON/OFF : if off, autodelete descending aircraft 
#                             below 1500 ft            
                elif cmd=="TAXI":
                    if numargs==0:
                        scr.echo("TAXI ON/OFF : OFF auto deletes traffic below 1500 ft")
                    else:
                        arg1 = cmdargs[1].upper()  # arguments are strings
                        traf.swtaxi = (arg1[:2]=="ON")
                        
#----------------------------------------------------------------------    
# SWRAD command: display switches of radar display
# SWRAD GEO / GRID / APT / VOR / WPT / LABEL (toggle on/off or cycle) 
# (for WPT,APT,LABEL value is optional)           

                elif cmd=="SWRAD" or cmd[:4]=="DISP":
                    if numargs==0:
                        scr.echo("SWRAD GEO / GRID / APT / VOR / " + \
                                 "WPT / LABEL / TRAIL [dt] / [value]")
                    else:
                        sw = cmdargs[1]
                        scr.redrawradbg = True
# Coastlines
                        if sw=="GEO":

                            scr.swgeo = not scr.swgeo
# FIR boundaries
                        elif sw=="TRAIL" or sw=="TRAILS":

                            traf.swtrails = not traf.swtrails
                            if numargs==2:
                                try:
                                    trdt = float(cmdargs[2])
                                    traf.trails.dt = trdt
                                except:
                                    scr.echo("TRAIL ON dt")
# FIR boundaries
                        elif sw=="FIR":

                            scr.swfir = not scr.swfir

# Airport: 0 = None, 1 = Large, 2= All
                        elif sw=="APT":

                            scr.apsw = (scr.apsw+1)%3
                            if numargs==2:
                                scr.apsw = int(cmdargs[2])
                            scr.navsel =[]

# Waypoint: 0 = None, 1 = VOR, 2 = also WPT, 3 = Also terminal area wpts

                        elif sw=="VOR" or sw=="WPT" or sw=="WP" or sw=="NAV":

                            scr.wpsw = (scr.wpsw+1)%4
                            if numargs==2:
                                scr.wpsw = int(cmdargs[2])
                            scr.navsel =[]
# Satellite image background on/off

                        elif sw=="SAT":
                            scr.swsat = not scr.swsat

# Traffic labels: cycle nr of lines 0,1,2,3

                        elif sw[:3]=="LAB": # Nr lines in label

                            scr.swlabel = (scr.swlabel+1)%4
                            if numargs==2:
                                scr.swlabel = int(cmdargs[2])

                        else:
                            scr.redrawradbg = False

#----------------------------------------------------------------------    
# TRAILS ON/OFF
                elif cmd[:5]=="TRAIL":
                    if numargs==0:
                        scr.echo("TRAILS ON/OFF [dt]")
                        if traf.swtrails:
                            scr.echo("Trails are currently ON")
                            scr.echo("Trails dt="+str(traf.trails.dt))
                        else:
                            scr.echo("Trails are currently OFF")
                    else:
                       if cmdargs[1]=="ON":
                           traf.swtrails = True
                           if numargs==2:
                               try:
                                   trdt = float(cmdargs[2])
                                   traf.trails.dt = trdt
                               except:
                                    scr.echo("TRAIL ON dt")

                       elif cmdargs[1]=="OFF" or cmdargs[1]=="OF":
                           traf.swtrails = False
                           traf.trails.clear()
                       else:
                           scr.echo('Syntax error')
                           scr.echo("TRAILS ON/OFF")
#----------------------------------------------------------------------    
# MCRE n, type/*, alt/*, spd/*, dest/* :Multiple create
                elif cmd[:4]=="MCRE":
                    if numargs==0:
                        scr.echo("Multiple CREate:")
                        scr.echo("MCRE n, type/*, alt/*, spd/*, dest/*")
                    else:
 # Currently only n,*,*,*,* supported (or MCRE n)
                        try:
                           n = int(cmdargs[1])
                           for i in range(n):

                               acid = "TUD"+str(randint(100,99999))
                               actype = "B747" # for now
                               aclat = random()*(scr.lat1 - scr.lat0)+scr.lat0
                               aclon = random()*(scr.lon1 - scr.lon0)+scr.lon0
                               achdg = float(randint(1,360))
                               acalt = float(randint(2000,39000))*ft
                               acspd = float(randint(250,450))
                               
                               traf.create(acid,actype,aclat,aclon,achdg,   \
                                           acalt,acspd)
                       
                        except:
                            scr.echo('Syntax error')
                            scr.echo("TRAILS ON/OFF")

#----------------------------------------------------------------------    
# DIST lat1,lon1,lat2,lon2 : calculate distance and direction from one pos to 2nd           
                elif cmd[:4]=="DIST":
                    if numargs==0:
                        scr.echo("DIST lat1,lon1,lat2,lon2")
                    else:
                        try:
                            lat0 = float(cmdargs[1])  # lat 1st pos
                            lon0 = float(cmdargs[2])  # lon 1st pos
                            lat1 = float(cmdargs[3])  # lat 2nd pos
                            lon1 = float(cmdargs[4])  # lon 2nd pos
                            qdr,d = qdrdist(lat0,lon0,lat1,lon1)
                            scr.echo("Dist = "+str(d)+" nm   QDR = " \
                                    +str(qdr)+" deg")
                        except:
                            scr.echo("DIST: Syntax error")
#----------------------------------------------------------------------    
# CALC  expression
                elif cmd[:4]=="CALC":
                    if numargs==0:
                        scr.echo("CALC expression")
                    else:
                        try:
                            x = eval(cmdline[5:].lower()) # lower for units!
                            scr.echo("Ans = "+str(x))
                        except:
                            scr.echo("CALC: Syntax error")

#----------------------------------------------------------------------    
# LNAV acid ON/OFF   Switch LNAV (HDG FMS navigation) on/off
                elif cmd=="LNAV":
                    if numargs==0:
                        scr.echo("LNAV acid, ON/OFF")
                    else:
                        idx = traf.id2idx(cmdargs[1])
                        if cmdargs[2].upper()=="ON":
                            traf.swlnav[idx] = True
                        elif cmdargs[2].upper()=="OFF":
                            traf.swlnav[idx] = False
#----------------------------------------------------------------------    
# VNAV acid ON/OFF  Switch VNAV (SPD+ALT FMS navigation)  on/off
                elif cmd=="VNAV":
                    if numargs==0:
                        scr.echo("VNAV acid, ON/OFF")
                    else:
                        idx = traf.id2idx(cmdargs[1])
                        if cmdargs[2].upper()=="ON":
                            traf.swvnav[idx] = True
                        elif cmdargs[2].upper()=="OFF":
                            traf.swvnav[idx] = False



#----------------------------------------------------------------------    
# Insert new command here: first three chars should be unique            
                elif cmd[:3]=="XXX":
                    if numargs==0:
                        scr.echo("cmd arg1, arg2")
                    else:
                        arg1 = cmdargs[1]  # arguments are strings
                        arg2 = cmdargs[2]  # arguments are strings
#----------------------------------------------------------------------    
# Insert new command here: first three chars should be unique            
                elif cmd[:3]=="XXX":
                    if numargs==0:
                        scr.echo("cmd arg1, arg2")
                    else:
                        arg1 = cmdargs[1]  # arguments are strings
                        arg2 = cmdargs[2]  # arguments are strings

#----------------------------------------------------------------------    
# Command not found
   
                else:
                    scr.echo("Unknown command: "+cmd)

#----------------------------------------------------------------------    
# End of command branches
#----------------------------------------------------------------------    
    
# Syntax not ok, => Default syntax error message:
                if not syntax:
                    print "Syntax error in command: ",cmdline
                    scr.echo("Syntax error in command:"+cmd)
                    scr.echo(cmdline)

# Error messages    
#            except:
#                scr.echo("Syntax error in command:"+cmd)
#                scr.echo(cmdline)
#
#                print "Error while processing:",cmd
#                print cmdline
#                print cmdargs


# End of for-loop of cmdstack
        self.cmdstack=[]
        return

