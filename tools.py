""" 
Miscellaneous modules

Modules:
     txt2alt(txt): read altitude[ft] from txt (FL ot ft)
     txt2spd(spd,h): read CAS or Mach and convert to TAS for given altitude
     tim2txt(t)  : convert time[s] to HH:MM:SS.hh
     i2txt(i,n)  : convert integer to string of n chars with leading zeros

Created by  : Jacco M. Hoekstra
Date        : October 2013

Modifation  :
By          :
Date        :

"""

from time import strftime,gmtime
from aero import cas2tas,mach2tas,eas2tas,kts

#---------------------------------------------------------------------------

# Convert text to altitude in ft: FL300 => 30000 as float

def txt2alt(txt):  

# First check for FL otherwise feet
    if txt.upper()[:2]=='FL' and len(txt)>=4: # Syntax check Flxxx or Flxx 
        try:
            return 100.*int(txt[2:])
        except:
            return -999.
    else:
        try:
            return float(txt)
        except:
            return -999.
    return -999

#---------------------------------------------------------------------------


# Convert time to timestring: HH:MM:SS.hh

def tim2txt(t):
    return strftime("%H:%M:%S.",gmtime(t))+i2txt(int((t-int(t))*100.),2)
    
#---------------------------------------------------------------------------


# Convert integer to string with leading zeros to make it n chars long

def i2txt(i,n):
    itxt = str(i)
    return "0"*(n-len(itxt))+itxt

#---------------------------------------------------------------------------

# Convert text to speed (EAS [kts]/MACH[-] to TAS[m/s])

def txt2spd(txt,h):
    
    if len(txt)==0:
        return -1.
    try:    
        if txt[0]=='M':
            M_ = float(txt[1:])
            if M_>=20:   # Handle M95 notation as .95
                M_= M_*0.01
            acspd = mach2tas(M_,h) # m/s
            
        elif txt[0]=='.' or (len(txt)>=2 and txt[:2]=='0.'):
            spd_ = float(txt)
            acspd = mach2tas(spd_,h) # m/s
    
        else:
            spd_ = float(txt)*kts
            acspd = cas2tas(spd_,h) # m/s
    except:
        return -1.
        
    return acspd
    
