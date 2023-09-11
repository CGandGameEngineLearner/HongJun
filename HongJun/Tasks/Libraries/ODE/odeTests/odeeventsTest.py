import unittest, os, sys
import numpy as np

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from odeevents import odeevents

class Testodeevents(unittest.TestCase):
    
    def test_odeevents_noevents1(self):
        
        def f(t,y):
            return [t, 2*t]
        
        t0 = 1.2
        y0 = [1.4,7.6]
        options={}
        extra=[]
        haveEventFcn,eventFcn,eventArgs,valt,teout,yeout,ieout=odeevents(t0,y0,options,extra)
        
        self.assertEqual(haveEventFcn,False)
        self.assertEqual(eventFcn,None)
        self.assertEqual(eventArgs,None)
        self.assertEqual(valt,None)
        self.assertEqual(type(teout),np.ndarray)
        self.assertEqual(type(teout),np.ndarray)
        self.assertEqual(type(teout),np.ndarray)
        self.assertEqual(len(teout),0)
        self.assertEqual(len(yeout),0)
        self.assertEqual(len(ieout),0)
        
    def test_odeevents_noevents2(self):
        
        def f(t,y,c):
            return [t+c, 2*t]
        
        t0 = 1.2
        y0 = [1.4,7.6]
        options={}
        extra=[1]
        haveEventFcn,eventFcn,eventArgs,valt,teout,yeout,ieout=odeevents(t0,y0,options,extra)
        
        self.assertEqual(haveEventFcn,False)
        self.assertEqual(eventFcn,None)
        self.assertEqual(eventArgs,None)
        self.assertEqual(valt,None)
        self.assertEqual(type(teout),np.ndarray)
        self.assertEqual(type(teout),np.ndarray)
        self.assertEqual(type(teout),np.ndarray)
        self.assertEqual(len(teout),0)
        self.assertEqual(len(yeout),0)
        self.assertEqual(len(ieout),0)
    
    
    def test_odeevents_events1(self):
        
        def f(t,y):
            return [t, 2*t]
        
        def event(t,y):
            val = [3,1.2]
            terminal=[1,0]
            direction = [-1,1]
            return val,terminal,direction
        
        t0 = 1.2
        y0 = [1.4,7.6]
        options={'Events':event}
        extra=[]
        haveEventFcn,eventFcn,eventArgs,valt,teout,yeout,ieout=odeevents(t0,y0,options,extra)
        
        self.assertEqual(haveEventFcn,True)
        self.assertEqual(eventFcn,event)
        self.assertEqual(eventArgs,[])
        self.assertEqual(valt,[3,1.2])
        self.assertEqual(type(teout),np.ndarray)
        self.assertEqual(type(teout),np.ndarray)
        self.assertEqual(type(teout),np.ndarray)
        self.assertEqual(len(teout),0)
        self.assertEqual(len(yeout),0)
        self.assertEqual(len(ieout),0)
        
        
    def test_odeevents_events2(self):
        
        def f(t,y,c):
            return [t, 2*t]
        
        def event(t,y,c):
            val = [3,1.2]
            terminal=[1,0]
            direction = [-1,1]
            return val,terminal,direction
        
        t0 = 1.2
        y0 = [1.4,7.6]
        options={'Events':event}
        extra=[1]
        haveEventFcn,eventFcn,eventArgs,valt,teout,yeout,ieout=odeevents(t0,y0,options,extra)
        
        self.assertEqual(haveEventFcn,True)
        self.assertEqual(eventFcn,event)
        self.assertEqual(eventArgs,[1])
        self.assertEqual(valt,[3,1.2])
        self.assertEqual(type(teout),np.ndarray)
        self.assertEqual(type(teout),np.ndarray)
        self.assertEqual(type(teout),np.ndarray)
        self.assertEqual(len(teout),0)
        self.assertEqual(len(yeout),0)
        self.assertEqual(len(ieout),0)
    
if __name__ == "__main__":
    unittest.main()