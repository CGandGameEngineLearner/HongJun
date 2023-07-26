import unittest, os, sys
import numpy as np
import math

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from odenonnegative import odenonnegative

class Testodenonnegative(unittest.TestCase):
    
    
    def setUp(self):
        
        
        def f_int(t,y):
            return [-1*t + y[0]]
        
        def f_vec(t,y,c):
            return [-1*t+c+y[0],-2*t+c]
        
        def f_trig(t,y):
            return [-1*math.sin(t),math.cos(t)]
            
        
        self.f_int = f_int
        self.f_vec = f_vec
        self.f_trig = f_trig
        
    
    
    def test_odenonnegative_indexfail(self):
        idxNonNegative=[1]
        threshold=1e-3
        self.assertRaises(IndexError,odenonnegative,self.f_int,[1],threshold,idxNonNegative)
        
        idxNonNegative=[-1]
        threshold=[1e-4,3e-5]
        self.assertRaises(IndexError,odenonnegative,self.f_vec,[1,3],threshold,idxNonNegative)
        
        idxNonNegative=[0,1]
        threshold=1e-4
        self.assertRaises(IndexError,odenonnegative,self.f_int,[1],threshold,idxNonNegative)
        
        idxNonNegative=[0,1,2]
        threshold=[1e-4,3e-5]
        self.assertRaises(IndexError,odenonnegative,self.f_trig,[1,2],threshold,idxNonNegative)
        
        
    
    def test_odenonnegative_y0fail(self):
        idxNonNegative=[0]
        threshold=1e-3
        self.assertRaises(ValueError,odenonnegative,self.f_int,[-1],threshold,idxNonNegative)
        
        idxNonNegative=[0]
        threshold=[1e-4,3e-5]
        self.assertRaises(ValueError,odenonnegative,self.f_vec,[-1,-1],threshold,idxNonNegative)
        
        idxNonNegative=[0,1]
        threshold=1e-4
        self.assertRaises(ValueError,odenonnegative,self.f_vec,[-1,1],threshold,idxNonNegative)
        
        idxNonNegative=[0,1]
        threshold=[1e-4,3e-5]
        self.assertRaises(ValueError,odenonnegative,self.f_trig,[0,-2],threshold,idxNonNegative)
    
    
    
    def test_odenonnegative_threshint(self):
        idxNonNegative=[0]
        threshold=1e-3
        y=[2]
        odeFcn,thresholdNonNegative=odenonnegative(self.f_int,y,threshold,idxNonNegative)
        t=np.linspace(0,4,num=9)
        for i in t:
            yp=odeFcn(i,y)
            ycomp=self.f_int(i,y)
            for j in range(len(yp)):
                if j in idxNonNegative:
                    self.assertEqual(yp[j],ycomp[j])
        
        self.assertEqual(len(thresholdNonNegative),1)
        self.assertEqual(thresholdNonNegative[0],1e-3)
        
        
        idxNonNegative=[1]
        threshold=1e-4
        y=[2,1]
        odeFcn,thresholdNonNegative=odenonnegative(self.f_vec,y,threshold,idxNonNegative)
        t=np.linspace(0,5,num=11)
        for i in t:
            yp=odeFcn(i,y,[1])
            ycomp=self.f_vec(i,y,[1])
            for j in range(len(yp)):
                if j in idxNonNegative:
                    self.assertEqual(yp[j],ycomp[j])
        
        self.assertEqual(len(thresholdNonNegative),1)
        self.assertEqual(thresholdNonNegative[0],1e-4)
        
        idxNonNegative=[0,1]
        threshold=1e-4
        y=[2,1]
        odeFcn,thresholdNonNegative=odenonnegative(self.f_vec,y,threshold,idxNonNegative)
        t=np.linspace(0,5,num=11)
        for i in t:
            yp=odeFcn(i,y,[1])
            ycomp=self.f_vec(i,y,[1])
            for j in range(len(yp)):
                if j in idxNonNegative:
                    self.assertEqual(yp[j],ycomp[j])
        
        self.assertEqual(len(thresholdNonNegative),2)
        self.assertEqual(thresholdNonNegative[0],1e-4)
        self.assertEqual(thresholdNonNegative[1],1e-4)
        
        idxNonNegative=[0]
        threshold=1e-4
        y=[0.5,1]
        odeFcn,thresholdNonNegative=odenonnegative(self.f_trig,y,threshold,idxNonNegative)
        t=np.linspace(0,19,num=100)
        for i in t:
            yp=odeFcn(i,y)
            ycomp=self.f_trig(i,y)
            for j in range(len(yp)):
                if j in idxNonNegative:
                    self.assertEqual(yp[j],ycomp[j])
        
        self.assertEqual(len(thresholdNonNegative),1)
        self.assertEqual(thresholdNonNegative[0],1e-4)
        
        
        idxNonNegative=[1,0]
        threshold=1e-4
        y=[0.5,1]
        odeFcn,thresholdNonNegative=odenonnegative(self.f_trig,y,threshold,idxNonNegative)
        t=np.linspace(0,19,num=100)
        for i in t:
            yp=odeFcn(i,y)
            ycomp=self.f_trig(i,y)
            for j in range(len(yp)):
                if j in idxNonNegative:
                    self.assertEqual(yp[j],ycomp[j])
        
        self.assertEqual(len(thresholdNonNegative),2)
        self.assertEqual(thresholdNonNegative[0],1e-4)
        self.assertEqual(thresholdNonNegative[1],1e-4)
        
        
    
    def test_odenonnegative_threshvec(self):
        idxNonNegative=[0]
        threshold=[1e-3]
        y=[2]
        odeFcn,thresholdNonNegative=odenonnegative(self.f_int,y,threshold,idxNonNegative)
        t=np.linspace(0,4,num=9)
        for i in t:
            yp=odeFcn(i,y)
            ycomp=self.f_int(i,y)
            for j in range(len(yp)):
                if j in idxNonNegative:
                    self.assertEqual(yp[j],ycomp[j])
        
        self.assertEqual(len(thresholdNonNegative),1)
        self.assertEqual(thresholdNonNegative[0],1e-3)
        
        
        idxNonNegative=[1]
        threshold=[1e-4,1e-3]
        y=[2,1]
        odeFcn,thresholdNonNegative=odenonnegative(self.f_vec,y,threshold,idxNonNegative)
        t=np.linspace(0,5,num=11)
        for i in t:
            yp=odeFcn(i,y,[1])
            ycomp=self.f_vec(i,y,[1])
            for j in range(len(yp)):
                if j in idxNonNegative:
                    self.assertEqual(yp[j],ycomp[j])
        
        self.assertEqual(len(thresholdNonNegative),1)
        self.assertEqual(thresholdNonNegative[0],1e-3)
        
        
        idxNonNegative=[0,1]
        threshold=[2e-4,1e-3]
        y=[0.5,1]
        odeFcn,thresholdNonNegative=odenonnegative(self.f_trig,y,threshold,idxNonNegative)
        t=np.linspace(0,19,num=100)
        for i in t:
            yp=odeFcn(i,y)
            ycomp=self.f_trig(i,y)
            for j in range(len(yp)):
                if j in idxNonNegative:
                    self.assertEqual(yp[j],ycomp[j])
        
        self.assertEqual(len(thresholdNonNegative),2)
        self.assertEqual(thresholdNonNegative[0],2e-4)
        self.assertEqual(thresholdNonNegative[1],1e-3)

if __name__ == "__main__":
    unittest.main()