"""
Main module of BlueSky Open ATM Simulator

Start this module to start the program

Created by  : Jacco M. Hoekstra (TU Delft)
Date        : September 2013

Modification:
By          :
Date        :

"""

# Only used for debugging>>>>
import time
import numpy as np
import pygame as pg   
# <<<< debugging

import CTraffic, CSimulation, CScreen, CKeyboard, CStack
import splash

#-----------------------------------------------------------------
# Show splash screen & version number in console

splash.show()
print " *** BlueSky Open Air Traffic simulator v0.6a ***"

# Initialize
print "Initializing Blue Sky objects...."

# Create objects for simulation, traffic, screen, keyboard & command stack
# To be used as global

sim  = CSimulation.Simulation() # contains time, simmode, etc.
traf = CTraffic.Traffic()       # contains data on aircraft
keyb = CKeyboard.Keyboard()     # processes input from keyboard & mouse 
scr  = CScreen.Screen(sim)      # screen output object
cmd  = CStack.Commandstack()    # list with strings with commands from file or user

# Start running the simulator (set sim mode)

sim.start()

# Main loop
while not sim.mode == sim.end :
    sim.update()                    # Update clock: t, dt

    keyb.update(sim,cmd,scr,traf)   # Check for keys & mouse
    
    cmd.checkfile(sim)              # Process input file

    cmd.process(sim,traf,scr)       # Process commands

    traf.update(sim,cmd)            # Traffic movements and controls
    
    scr.update(sim,traf)            # GUI update
    
# Restart traffic simulation:
    if sim.mode==sim.init:

# Reset Traffic database
        del traf
        traf = CTraffic.Traffic()
        sim.start()

# Clean up
print "Deleting Blue Sky objects..."

# Not now, leave them available for debugging purposes!


# Close metrics file explicitly for now
# needs to be moved to destructor traf.__del__  !

print "Closing Metrics file"
traf.metric.file.close()  

# When deleting of objects is commented out, the data is
# still accessible in shell for debugging after run

#del traf
#del sim
#del keyb
#del cmd
#del scr

# Quit pygame
pg.quit()      # Only for debugging, normally part of del scr

print "BlueSky ready."

