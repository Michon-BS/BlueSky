""" 
Standard Dialog modules, using Tkinter

Modules:
    fileopen()  : returns filename fo scenatriofile selected

Created by  : Jacco M. Hoekstra
Date        : October 2013

Modifation  :
By          :
Date        :

"""

from Tkinter import *
import tkFileDialog
import os


"""
Created on Fri Oct 11 13:50:49 2013

Windows dialogs

@author: jaccohoekstra
"""


def fileopen():

   os.chdir('scenario')

   master = Tk()
   master.withdraw() #hiding tkinter window
    
   file_path = tkFileDialog.askopenfilename(title="Open scenario file", \
                filetypes=[("Scenario files",".scn"),("All files",".*")])


# Close Tk, return to working directory    
   master.quit()
   
   os.chdir('..')

   return file_path