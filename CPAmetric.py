# -*- coding: utf-8 -*-
"""
Created on Mon Jan 06 13:56:50 2014

@author: Dennis Michon
"""

import numpy as np
import math as m
from aero_np import *
from collections import defaultdict as dd
from time import time as tt
import matplotlib.pyplot as plt
import csv
from itertools import izip


class CPAmetric():
    
    
    def __init__(self,area):
        
        self.initiallat = area[3][0]
        self.initiallon = area[3][1]
        self.dist_range = 5.0 #nm
       
        self.alt_range = 1000.0 #ft
        self.t_cpa = 0
        self.dist_cpa = 0
        self.spd = np.array([])
        self.lat = np.array([])
        self.lon = np.array([])
        self.pos = np.array([])
        self.trk = 0

        self.alt_dif = 0
        self.alt = 0
        self.id = []
        
        self.complexity = dd(lambda:dd(int))
        self.rel_trk = np.array([])
        self.step = -1
        self.id_previous = []
        self.headings = []
        self.headings_previous = np.array([])
        self.doubleconflict = 0
        self.ntraf = 0
        self.compl_ac = 0
        self.time_lookahead = 1800 #seconds
        


        return


    def applymetric(self,traf,sim):
        time1 = tt()
        sim.pause()
        self.doubleconflict = 0
        ##relative pos x and pos y   
        self.step = self.step + 1
        self.pos = np.array([])
        self.lat = np.array([])
        self.lon = np.array([])

        self.id = []
        self.alt_dif = 0

 

        [self.rel_trk, self.pos] = qdrdist_vector(self.initiallat,self.initiallon,np.mat(traf.lat),np.mat(traf.lon))
#        self.lat = np.append(self.lat,traf.lat)
#        self.lon = np.append(self.lon,traf.lon)
        self.id = traf.id
        
        #Position x and y wrt to initial position
        self.pos = np.mat(self.pos)
        #TRUE???
        anglex = np.cos(np.radians(90-self.rel_trk))
        angley = np.sin(np.radians(90-self.rel_trk))

        self.posx = np.mat(np.array(self.pos) * np.array(anglex)) #nm
        self.posy = np.mat(np.array(self.pos) * np.array(angley)) #nm
        
        self.lat = traf.lat
        self.lon = traf.lon

        self.alt = np.mat(traf.alt/ft)
        self.spd = traf.tas/nm #nm/s
        self.trk = traf.trk
        self.ntraf = traf.ntraf

        #Vectors CPA_dist and CPA_time
        #self.rel_vectors()
        

        print "NEW"
        
        #self.apply_heading_range()
        self.apply_twoCircleMethod()
        #self.saveData()
        time2 = tt()
        print (time2-time1)
        sim.play()
        return        
    
    

    def rel_vectors(self):
        
        self.alt_dif = self.alt-self.alt.T
 
        ## speeds

        hdgx = np.cos(np.radians(90-self.trk))
        hdgy = np.sin(np.radians(90-self.trk))

        spdu = np.mat(self.spd * hdgx.T).T #nm/s
        spdv = np.mat(self.spd * hdgy.T).T #nm/s 

        ## distances pos and spd
        distx = np.array(self.posx.T - self.posx) #nm
        disty = np.array(self.posy.T - self.posy) #nm
        distu = (np.array(spdu.T - spdu)) #nm/s
        distv = (np.array(spdv.T - spdv)) #nm/s


        ## predicted time to CPA
        self.t_cpa = -(distu*distx+distv*disty)/      \
         (distu*distu+distv*distv+np.array(np.eye(distu[:,0].size)))
         
        
        
        ## predicted distance to CPA
        relcpax = self.t_cpa*np.array(spdu.T)
        relcpay = self.t_cpa*np.array(spdv.T)        
        cpax = self.posx.T + relcpax 
        cpay = self.posy.T + relcpay
        distcpax = np.array(cpax-cpax.T)
        distcpay = np.array(cpay-cpay.T)
        self.dist_cpa = (distcpax**2+distcpay**2)**0.5
        
        return
        
        
    def apply_altfilter(self,S0):
        condition = abs(self.alt_dif)<self.alt_range
        #self.t_cpa = np.where(condition,self.t_cpa, np.nan)
        #self.dist_cpa = np.where(condition,self.dist_cpa, np.nan)
              
        S0 = np.where(condition,S0,np.nan)

        return S0         
        
    def apply_distfilter(self,H0):
        condition = self.dist_cpa<self.dist_range*3
        
        self.dist_cpa = np.where(condition,self.dist_cpa,np.nan)
        self.t_cpa = np.where(condition,self.t_cpa,np.nan)
        H0 = np.where(condition,H0,np.nan)

        return H0     
        
    def apply_timefilter(self):
        condition = self.t_cpa>0#(self.t_cpa<(self.time_range+20) * (self.t_cpa>0))
        self.t_cpa = np.where(condition,self.t_cpa,np.nan)
        self.dist_cpa = np.where(condition,self.dist_cpa,np.nan)


        return       

    def apply_before_filter(self,S0,Va):
        Vb = Va.T
        Va_Vb = np.add(np.abs(Va),np.abs(Vb))
        condition1 = S0>0
        condition2 = np.divide(S0,Va_Vb)>self.time_lookahead #seconds
        condition = np.multiply(condition1,condition2)
        condition = np.invert(condition)
        S0 = np.where(condition,S0,np.nan)      
                
        return S0


    def apply_twoCircleMethod(self):
        
        Va = np.mat(self.spd)
        Ha = np.radians(self.trk)
        
        

        Vb = np.add(Va,0.0000001)
        VaVa = np.multiply(Va,Va)
        
        Hb = Ha
        
        [H0,S0] = qdrdist_vector(np.mat(self.lat),np.mat(self.lon),np.mat(self.lat),np.mat(self.lon))
        S0 = np.where(S0 > 0, S0, np.nan)
        
        
        
        S0 = self.apply_before_filter(S0,Va)
        S0 = self.apply_altfilter(S0)
        
        
        H0 = np.radians(H0.T)
        
        
        R_S0 = np.divide(self.dist_range,S0)
        arcsin = np.arcsin(R_S0)
        
        ha_new11,ha_new21,ha_new12,ha_new22,t1d1,t1d2,t2d1,t2d2 = self.calc_angles(Vb,Hb,VaVa,H0,arcsin,S0)
        
        R_S0 = None
        arcsin = None
 

       
        ha_1 = np.degrees(ha_new11)        
        ha_3 = np.degrees(ha_new21)
        
        ha_2 = np.degrees(ha_new12)        
        ha_4 = np.degrees(ha_new22)
        

        t1 = t1d1
        t2 = t1d2
        t3 = t2d1
        t4 = t2d2
        
        ha_new11 = None
        ha_new21 = None
        ha_new12 = None
        ha_new22 = None
        t1d1 = None
        t1d2 = None
        t2d1 = None
        t2d2 = None

        ha_1,ha_2,ha_3,ha_4,t1,t2,t3,t4 = self.conditions(ha_1,ha_2,ha_3,ha_4,t1,t2,t3,t4,Va,Vb,Ha,Hb)
        
    

        
        ### MAKE COMPLEXITY SCORE
        diff_1_2 = np.subtract(ha_1,ha_2)
        diff_1_2 = np.abs((diff_1_2 + 180) % 360 - 180)

        
        diff_3_4 = np.subtract(ha_3,ha_4)
        diff_3_4 = np.abs((diff_3_4 + 180)  % 360 - 180)
        
        ## Condition where S0 < self.dist_range
        condition = np.multiply(S0<self.dist_range,S0>0)
        condition = np.invert(condition)
        diff_1_2 = np.where(condition,diff_1_2,180)
        diff_3_4 = np.where(condition,diff_3_4,180)
        
        
        ##now combine into 1 complexity score
        Compl_1 = np.divide(diff_1_2,360)
        Compl_2 = np.divide(diff_3_4,360)
        Compl_12ac = np.vstack((Compl_1,Compl_2))
        self.compl_ac = np.nansum(Compl_12ac, axis = 0)
        

        
        Compl_ac = np.nansum(self.compl_ac)
#        
        self.complexity[self.step][0] = Compl_ac #/ self.ntraf
        self.complexity[self.step][1] = Compl_ac / self.ntraf
        print Compl_ac
        print Compl_ac / self.ntraf
        #self.complexity_plot()
        #self.saveData()
        
        
        return


    def calc_angles(self,Vb,Hb,VaVa,H0,arcsin,S0):
        
        wx = np.multiply(Vb,np.sin(Hb))
        wy = np.multiply(Vb,np.cos(Hb))
        
        wxwx = np.multiply(wx,wx)
        wywy = np.multiply(wy,wy)
        wxwx_wywy = np.add(wxwx,wywy)

        
        a = np.subtract(wxwx_wywy.T,VaVa)
        
        
        H0_arcsin = np.subtract(H0,arcsin)
        xc1 = np.multiply(S0,np.sin(H0_arcsin))
        yc1 = np.multiply(S0,np.cos(H0_arcsin))

        xc1xc1 = np.multiply(xc1,xc1)
        yc1yc1 = np.multiply(yc1,yc1)
        
        a = np.where(a!=0,a,np.nan)
        a = np.add(a,0.00000000001)
        
        
        b1 = np.add(2*np.multiply(xc1,wx.T),2*np.multiply(yc1,wy.T))
        c1 = np.add(xc1xc1,yc1yc1)
        b1b1 = np.multiply(b1,b1)
        d1 = np.subtract(b1b1,4*np.multiply(a,c1))
        
        c1 = None
        b1b1 = None
        xc1xc1 = None
        yc1yc1 = None
        H0_arcsin = None

        
        a_2 = np.multiply(a,2)
        conditiond1 = d1<0
        conditiond1 = np.invert(conditiond1)
        d1 = np.where(conditiond1,d1,np.nan)
        t01d1 = np.divide(np.subtract(-b1,np.sqrt(d1)),a_2)
        t02d1 = np.divide(np.add(-b1,np.sqrt(d1)),a_2)
        

        
        t1d1 = np.minimum(t01d1,t02d1)
        t2d1 = np.maximum(t01d1,t02d1)
        
        xpt1d1 = np.add(xc1,np.multiply(wx.T,t1d1))
        xpt2d1 = np.add(xc1,np.multiply(wx.T,t2d1))
        
        ypt1d1 = np.add(yc1,np.multiply(wy.T,t1d1))
        ypt2d1 = np.add(yc1,np.multiply(wy.T,t2d1))

        xc1 = None
        yc1 = None
        
        H0_arcsin = np.add(H0,arcsin)
        xc2 = np.multiply(S0,np.sin(H0_arcsin))
        yc2 = np.multiply(S0,np.cos(H0_arcsin))

        xc2xc2 = np.multiply(xc2,xc2)
        yc2yc2 = np.multiply(yc2,yc2)
        
        wxT = wx.T
        wyT = wy.T
        xc2_wx = np.multiply(xc2,wxT)
        yc2_wy = np.multiply(yc2,wyT)
        xc2_wx2 = np.multiply(xc2_wx,2)
        yc2_wy2 = np.multiply(yc2_wy,2)
        b2 = np.add(xc2_wx2,yc2_wy2)
        c2 = np.add(xc2xc2,yc2yc2)
        b2b2 = np.multiply(b2,b2)
        d2 = np.subtract(b2b2,4*np.multiply(a,c2))
        
        
        c2 = None
        b2b2 = None
        xc2xc2 = None
        yc2yc2 = None
        H0_arcsin = None

        
        wxwx = None
        wywy = None
        wxwx_wywy = None
       
        conditiond2 = d2<0
        conditiond2 = np.invert(conditiond2)
        d2 = np.where(conditiond2,d2,np.nan)
        
        t01d2 = np.divide(np.subtract(-b2,np.sqrt(d2)),a_2)
        t02d2 = np.divide(np.add(-b2,np.sqrt(d2)),a_2)
        t1d2 = np.minimum(t01d2,t02d2)
        t2d2 = np.maximum(t01d2,t02d2)
        
        t01d1 = None
        t02d1 = None
        t01d2 = None
        t02d2 = None
        
        d1 = None
        d2 = None
        
        xpt1d2 = np.add(xc2,np.multiply(wx.T,t1d2))
        xpt2d2 = np.add(xc2,np.multiply(wx.T,t2d2))
        
        ypt1d2 = np.add(yc2,np.multiply(wy.T,t1d2))
        ypt2d2 = np.add(yc2,np.multiply(wy.T,t2d2))
        
        xc2 = None
        yc2 = None
        wx = None
        wy = None

        ha_new11 = np.arctan2(xpt1d1,ypt1d1)
        ha_new21 = np.arctan2(xpt2d1,ypt2d1)

        ha_new12 = np.arctan2(xpt1d2,ypt1d2)
        ha_new22 = np.arctan2(xpt2d2,ypt2d2)
        
        
        return ha_new11,ha_new21,ha_new12,ha_new22,t1d1,t1d2,t2d1,t2d2
    
    
    def conditions(self,ha_1,ha_2,ha_3,ha_4,t1,t2,t3,t4,Va,Vb,Ha,Hb):
        
        t1_nan = t1>0
        t2_nan = t2>0
        t3_nan = t3>0
        t4_nan = t4>0
        
        ha_1 = np.where(t1_nan,ha_1,np.nan)
        ha_2 = np.where(t2_nan,ha_2,np.nan)
        ha_3 = np.where(t3_nan,ha_3,np.nan)
        ha_4 = np.where(t4_nan,ha_4,np.nan)
        
        t1 = np.where(t1_nan,t1,np.nan)
        t2 = np.where(t2_nan,t2,np.nan)
        t3 = np.where(t3_nan,t3,np.nan)
        t4 = np.where(t4_nan,t4,np.nan)
        
        ##condition: Va < Vb and all + t's
        Va_Vb = Va < Vb
        t1_t2 = np.multiply(t1_nan,t2_nan)
        t3_t4 = np.multiply(t3_nan,t4_nan)
        t_allplus = np.multiply(t1_t2,t3_t4)
        condition = np.multiply(Va_Vb,t_allplus)
        condition = np.invert(condition)
        ha_3new = np.where(condition,ha_3,ha_4)
        t3new = np.where(condition,t3,t4)
        ha_4new = np.where(condition,ha_4,ha_3)
        t4new = np.where(condition,t4,t3)
        
        ##condition Va < Vb and t1,t3 negatif
        t1_neg = np.invert(t1_nan)
        t3_neg = np.invert(t3_nan)
        t1_t3_neg = np.multiply(t1_neg,t3_neg)
        condition = np.multiply(Va_Vb,t1_t3_neg)
        condition = np.invert(condition)
        ha_3 = np.where(condition,ha_3new,ha_4new)
        t3 = np.where(condition,t3new,t4new)
        ha_4 = np.where(condition,ha_4new,ha_2)
        t4 = np.where(condition,t4new,t2)
        
        ##condition Va < Vb and t2,t4 negatif
        t2_neg = np.invert(t2_nan)
        t4_neg = np.invert(t4_nan)
        t2_t4_neg = np.multiply(t2_neg,t4_neg)
        condition = np.multiply(Va_Vb,t2_t4_neg)
        condition = np.invert(condition)
        ha_2 = np.where(condition,ha_2,ha_3)
        t2 = np.where(condition,t2,t3)
        
        
        ## TBD More than 90-degree turns!
        Ha = np.degrees(Ha)
        Hb = np.degrees(Hb)        
        
        
        ## Lookahead time
        t1_lht = t1 > self.time_lookahead
        t2_lht = t2 > self.time_lookahead
        t1_t2_lht = np.multiply(t1_lht,t2_lht)
        t1_t2_lht = np.invert(t1_t2_lht)
        
        t3_lht = t3 > self.time_lookahead
        t4_lht = t4 > self.time_lookahead
        t3_t4_lht = np.multiply(t3_lht,t4_lht)
        t3_t4_lht = np.invert(t3_t4_lht)
        
        ha_1 = np.where(t1_t2_lht,ha_1,np.nan)
        ha_2 = np.where(t1_t2_lht,ha_2,np.nan)
        ha_3 = np.where(t3_t4_lht,ha_3,np.nan)
        ha_4 = np.where(t3_t4_lht,ha_4,np.nan)
        
        t1 = np.where(t1_t2_lht,t1,np.nan)
        t2 = np.where(t1_t2_lht,t2,np.nan)
        t3 = np.where(t3_t4_lht,t3,np.nan)
        t4 = np.where(t3_t4_lht,t4,np.nan)
        
        
        
        
        
        
        
        return ha_1,ha_2,ha_3,ha_4,t1,t2,t3,t4

    def saveData(self):
        
        acid = np.array(self.id).reshape(-1,).tolist()
        lat = np.array(self.lat).reshape(-1,).tolist()
        lon = np.array(self.lon).reshape(-1,).tolist()
        compl = np.array(self.compl_ac).reshape(-1,).tolist()
        alt =  np.array(self.alt).reshape(-1,).tolist()
        spd = np.array(self.spd).reshape(-1,).tolist()
        trk = np.array(self.trk).reshape(-1,).tolist()
        ntraf = np.repeat(np.array(self.ntraf),len(trk))
        ntraf = np.array(ntraf).reshape(-1,).tolist()

        data = izip(acid,lat,lon,alt,spd,trk,ntraf)
        
        step = str(self.step).zfill(3)
        fname = "./output/Hdg_Metric/"+step+"-BlueSky.csv"
        f = csv.writer(open(fname, "wb"))
        for row in data:
            
            f.writerow(row)
            
        
        
        
        
        
        return


    def complexity_plot(self):
        if self.step == 0:
            self.plot_complexity,= plt.plot([], [])
            self.plot_complexity2, = plt.plot([],[])
            plt.ion()
        
        t = int(self.step)
        self.plot_complexity.set_xdata(np.append(self.plot_complexity.get_xdata(), t))
        self.plot_complexity.set_ydata(np.append(self.plot_complexity.get_ydata(), self.complexity[self.step][0]))
        self.plot_complexity2.set_xdata(np.append(self.plot_complexity2.get_xdata(), t))
        self.plot_complexity2.set_ydata(np.append(self.plot_complexity2.get_ydata(), self.complexity[self.step][1]))
       
        plt.subplot(2,1,1)
        plt.plot(t,self.complexity[self.step][0],'b--o--')
        plt.subplot(2,1,2)
        plt.plot(t,self.complexity[self.step][1],'g--o--')
        plt.draw()
        #plt.plot(t,self.complexity[self.step][0,1],'g--o')
        #plt.legend(labels)
        #ax = plt.gca()        
        #ax.relim()
        #ax.autoscale_view()
        
        
        return

    
#    def heading_range(self,i,ac1_conflict,ac2_conflict,lat0_ac1,lon0_ac1,lat0_ac2,lon0_ac2):
#        
#        h_range = np.arange(int(self.trk[ac1_conflict[i]])-90,int(self.trk[ac1_conflict[i]])+90,1)
#        h_range = np.append(h_range,self.trk[ac2_conflict[i]])
#        
#
#        hdgx = np.cos(np.radians(90-h_range))
#        hdgy = np.sin(np.radians(90-h_range))
#        
#        spd = np.array([])
#        posy = np.array([])
#        posx = np.array([])
#        for l in range(0,len(h_range)-1):
#            posy = np.append(posy,self.posy[ac1_conflict[i]])
#            posx = np.append(posx,self.posx[ac1_conflict[i]])
#            spd = np.append(spd,self.spd[ac1_conflict[i]])
#        
#        spd = np.append(spd,self.spd[ac2_conflict[i]])
#        
#        spdu = np.mat(spd * hdgx).T #nm/s
#        spdv = np.mat(spd * hdgy).T #nm/s    
#        posy = np.append(posy,self.posy[ac2_conflict[i]])
#        posx = np.append(posx,self.posx[ac2_conflict[i]])
#        posx = np.mat(posx).T
#        posy = np.mat(posy).T
#
#        ## distances pos and spd
#        distx = np.array(posx - posx.T) #nm
#        disty = np.array(posy - posy.T) #nm
#        distu = (np.array(spdu - spdu.T)) #nm/s
#        distv = (np.array(spdv - spdv.T)) #nm/s
#
#        ## predicted time to CPA
#        t_heading = -(distu*distx+distv*disty)/      \
#         (distu*distu+distv*distv+np.array(np.eye(distu[:,0].size)))        
#        
#        t_heading = self.apply_timefilter(t_heading)
#        
#        relcpax = t_heading*np.array(spdu.T)
#        relcpay = t_heading*np.array(spdv.T)        
#        cpax = posx.T + relcpax 
#        cpay = posy.T + relcpay
#        distcpax = np.array(cpax-cpax.T)
#        distcpay = np.array(cpay-cpay.T)
#        distcpa = (distcpax**2+distcpay**2)**0.5
#        
#        n_headings = np.where(distcpa>self.dist_range)
#        headings = np.array([])
#        
#        for z in range(0,len(n_headings[0])/2):
#            headings = np.append(headings,h_range[n_headings[0][z]])
#            
#        
#
#        
#        #check if flightid is same, so multiple conflicts per id
#        if self.id[ac1_conflict[i]] == self.id_previous:
#            headings = np.intersect1d(self.headings_previous,headings)
#            n_fault_headings = len(h_range)-len(headings)    
#            ratio = float(float(n_fault_headings)/float(len(h_range)))
#            add_complexity = [self.id[ac1_conflict[i]],ratio,headings]
#            self.complexity[self.step][i-self.doubleconflict-1] = add_complexity
#            self.doubleconflict = self.doubleconflict + 1
#        else:
#            n_fault_headings = len(h_range)-len(headings)    
#            ratio = float(float(n_fault_headings)/float(len(h_range)))
#            add_complexity = [self.id[ac1_conflict[i]],ratio,headings]
#            self.complexity[self.step][i-self.doubleconflict] = add_complexity
#
#        
#        self.id_previous = self.id[ac1_conflict[i]]
#        self.headings_previous = headings
#    
#        return
#    
#    
#    
#    def apply_precisetime(self,range_t,delta_t,heading_range):        
#        
#        ac_conflict = np.where(self.t_cpa>0)
#        conflicts = np.size(ac_conflict)/2
#        
#        if conflicts > 0:
#            ac1_conflict = ac_conflict[0]
#            ac2_conflict = ac_conflict[1]
#    
#            
#            t_cpa_precise = np.array([])
#            plat_ac1 = np.array([])
#            plat_ac2 = np.array([])
#            plon_ac1 = np.array([])
#            plon_ac2 = np.array([])
#            
#            for i in range(0,conflicts):
#                lat0_ac1 = self.lat[ac1_conflict[i]]
#                lat0_ac2 = self.lat[ac2_conflict[i]]
#                lon0_ac1 = self.lon[ac1_conflict[i]]
#                lon0_ac2 = self.lon[ac2_conflict[i]]
#                
#                # DETAILED CPA
##                t_cpa_ac1ac2 = self.t_cpa[ac1_conflict[i]][ac2_conflict[i]]
##                t_cpa_range = np.arange(t_cpa_ac1ac2-range_t,t_cpa_ac1ac2+range_t,delta_t)
##                dist_ac1 = t_cpa_precise*self.spd[ac1_conflict[i]]*nm
##                dist_ac2 = t_cpa_precise*self.spd[ac2_conflict[i]]*nm
##                
##                
##                plat_ac1 = np.append(plat_ac1,lat0_ac1 + \
##                             np.degrees(dist_ac1*np.cos(np.radians(self.trk[ac1_conflict[i]]))/Rearth))            
##                plat_ac2 = np.append(plat_ac2,lat0_ac2 + \
##                             np.degrees(dist_ac2*np.cos(np.radians(self.trk[ac2_conflict[i]]))/Rearth)) 
##                plon_ac1 = np.append(plon_ac1,lon0_ac1 + \
##                                   np.degrees(dist_ac1*np.sin(np.radians(self.trk[ac1_conflict[i]])) \
##                                     /np.cos(np.radians(lat0_ac1))/Rearth)) 
##                plon_ac2 = np.append(plon_ac2,lon0_ac2 + \
##                                   np.degrees(dist_ac2*np.sin(np.radians(self.trk[ac2_conflict[i]])) \
##                                       /np.cos(np.radians(lat0_ac2))/Rearth)) 
##                
##                dist_ac1ac2 = np.array([])
##                for j in range(0,np.size(t_cpa_range)):
##                    dist_ac1ac2 = np.append(dist_ac1ac2,(latlondist(plat_ac1[j],plon_ac1[j],plat_ac2[j],plon_ac2[j]))/nm)
##                
##                index_new_t_cpa = np.argmin(dist_ac1ac2)
##                self.dist_cpa[ac1_conflict[i]][ac2_conflict[i]] = dist_ac1ac2[index_new_t_cpa]
##    
##                self.t_cpa[ac1_conflict[i]][ac2_conflict[i]] = t_cpa_precise[index_new_t_cpa]
#                               
#                if heading_range == 1:
#                    self.heading_range(i,ac1_conflict,ac2_conflict,lat0_ac1,lon0_ac1,lat0_ac2,lon0_ac2)
#            
#        return

    def apply_heading_range(self):
        

        
        Va = np.mat(self.spd)
        Ha = np.radians(self.trk)
        Ha_len = len(Ha)
        Ha = np.repeat(Ha,Ha_len)

        Ha = Ha.reshape(Ha_len,Ha_len)

        Vb = Va
        Hb = Ha

        
        R = self.dist_range
        
        [H0,S0] = qdrdist_vector(np.mat(self.lat),np.mat(self.lon),np.mat(self.lat),np.mat(self.lon))
      
        #H0 = self.apply_distfilter(H0)
        #H0 = self.apply_altfilter(H0)
        S0 = self.apply_before_filter(S0,Va)
        
        H0 = np.radians(H0.T)
        R_S0 = np.divide(R,S0)
        arcsin = np.arcsin(R_S0) 
        Hr_new1 = H0 - arcsin
        Hr_new2 = H0 + arcsin
        Vb_Va = np.divide(Vb.T,Va)
        Hb_Hr_sin1 = np.sin(Hr_new1 - Hb)
        mp1 = np.multiply(Vb_Va,Hb_Hr_sin1)
        mp1 = (mp1 + 1)%2 - 1
        Hb_Hr_sin2 = np.sin(Hr_new2 - Hb)
        mp2 = np.multiply(Vb_Va,Hb_Hr_sin2)
        mp2 = (mp2 + 1)%2 - 1
        
        Ha_new11 = Hr_new1 - np.arcsin(mp1)
        Ha_new12 = Hr_new1 - np.arcsin(np.pi-mp1)
        Ha_new21 = Hr_new2 - np.arcsin(mp2)
        Ha_new22 = Hr_new2 - np.arcsin(np.pi-mp2)

        Ha_new11 = np.degrees(Ha_new11)
        Ha_new12 = np.degrees(Ha_new12)
        Ha_new21 = np.degrees(Ha_new21)
        Ha_new22 = np.degrees(Ha_new22)
        
        Ha_new11 = (Ha_new11+180)%360-180
        Ha_new12 = (Ha_new12+180)%360-180
        Ha_new21 = (Ha_new21+180)%360-180
        Ha_new22 = (Ha_new22+180)%360-180

        ## Check for more than 90-degree headings, TBD
        Hdeg = np.degrees(Ha.T)
        Heading_1 = np.subtract(Hdeg,90)
        Heading_2 = np.add(Hdeg,90)

        #Heading_1 = (Heading_1+180)%360-180
        #Heading_2 = (Heading_2+180)%360-180

        #Heading_new11
        condition11a = Ha_new11 < Heading_1
        condition11b = S0>0
        condition11 = np.multiply(condition11a,condition11b)
        condition11 = np.invert(condition11)
        Ha_new11 = np.where(condition11,Ha_new11,Heading_1)
                
        #Heading_new21
        condition21a = Ha_new21 > Heading_2
        condition21 = np.multiply(condition21a,condition11b)
        condition21 = np.invert(condition21)
        Ha_new21 = np.where(condition21,Ha_new21,Heading_2)
    
        #Condition where Va>Vb and angle_rel does not include in H0_limits
        va_sxa = np.multiply(Va,np.sin(Ha))
        vb_sxb = va_sxa
        va_cxa = np.multiply(Va,np.cos(Ha))
        vb_cxb = va_cxa
        angle_rel = np.arctan2(np.subtract(va_sxa.T,vb_sxb),np.subtract(va_cxa.T,vb_cxb))
        angle_rel = np.degrees(angle_rel)
        angle_rel = (angle_rel+180)%360-180
        
        
        condition1 = Va.T > Vb
        H0_lim1 = np.degrees(H0) - 90
        H0_lim2 = np.degrees(H0) + 90
        H0_lim1 = (H0_lim1+180)%360-180
        H0_lim2 = (H0_lim2+180)%360-180
        condition2a = angle_rel < H0_lim1
        condition2b = angle_rel > H0_lim2
        
        condition2 = np.multiply(condition2a,condition2b)
        condition = np.multiply(condition1,condition2)
        condition = np.invert(condition)

        Ha_new11 = np.where(condition,Ha_new11,np.nan)
        Ha_new12 = np.where(condition,Ha_new12,np.nan)
        Ha_new21 = np.where(condition,Ha_new21,np.nan)
        Ha_new22 = np.where(condition,Ha_new22,np.nan)



#        S0_S0 = np.multiply(S0,S0)
#        d_sep = self.dist_range**2
#        aaa = np.multiply(2,np.multiply(S0,self.dist_range))        
#        d_min = H0        
#        condition = np.abs(np.subtract(H0,x_rel)) < np.radians(90)
#        d_min = np.where(condition,d_min,np.multiply(H0,np.sin(np.subtract(H0,x_rel))))
#        cos_b = np.arcsin(np.divide(d_min,self.dist_range)) - np.abs(np.subtract(H0,x_rel))
#        mp = np.multiply(aaa,cos_b)
#        upper = np.sqrt(S0_S0 + d_sep - mp)
#        Va_Va = np.multiply(Va,Va)
#        Vb_Vb = np.multiply(Vb,Vb)
#        va_vb = np.multiply(Va,Vb)
#        a_va_vb = np.multiply(2,va_vb)
#        mult = np.multiply(a_va_vb,np.cos(np.subtract(Ha.T,Hb)))
#        Va_Va_Vb_Vb = np.add(Va_Va,Vb_Vb)
#
#
#        v_rel = np.sqrt(np.subtract(Va_Va_Vb_Vb,mult))
#        print v_rel
#        t_fls = np.divide(upper,v_rel)
#        
#        print t_fls        
        

        
        diff_11_21 = np.subtract(Ha_new11,Ha_new21)
        diff_11_21 = np.abs((diff_11_21 + 180) % 360 - 180)

        
        diff_12_22 = np.subtract(Ha_new12,Ha_new22)
        diff_12_22 = np.abs((diff_12_22 + 180)  % 360 - 180)
        
        
        ##now combine into 1 complexity score
        Compl_1 = np.divide(diff_11_21,360)
        Compl_2 = np.divide(diff_12_22,360)
        Compl_12ac = np.vstack((Compl_1,Compl_2))
        Compl_ac = np.nansum(Compl_12ac, axis = 0)
       
        #Condition where S0 < self.dist_range
#        condition = np.multiply(S0<self.dist_range,S0>0)
#        condition = np.invert(condition)
#        Compl_ac = np.where(condition,Compl_ac,0.5)
        
        
        
        Compl_ac = np.nansum(Compl_ac)
        
        self.complexity[self.step][0] = Compl_ac #/ self.ntraf
        self.complexity[self.step][1] = Compl_ac / self.ntraf
        
        self.complexity_plot()
        
        return



