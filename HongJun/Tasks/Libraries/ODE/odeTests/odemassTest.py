import unittest, os, sys
import numpy as np
import scipy.sparse as sp

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from odemass import odemass

class Testodemass(unittest.TestCase):
    
    def setUp(self):
        self.t0 = 1
        self.y0_int = [2]
        self.y0_vec = [1, 2]
        
        def ode_int(t,y):
            return [t*y]
        
        def ode_vec(t,y):
            return [y[1], 5]
        
        
        def mass_time_int(t):
            return [2*t]
        
        def mass_state_int(t,y):
            return [2*t*y[0]]
        
        def mass_time_vec(t):
            return [[t+1, 2*t+1],[2*t, 3*t]]
        
        def mass_state_vec(t,y):
            return [[t*y[0], 2*t*y[1]],[2*t, 3*t]]
        
        self.ode_int=ode_int
        self.ode_vec=ode_vec
        self.mass_time_int=mass_time_int
        self.mass_state_int=mass_state_int
        self.mass_time_vec=mass_time_vec
        self.mass_state_vec=mass_state_vec
   
     
    def test_odemass_int_nomass(self):
        opts = {}
        massType, massM, massFcn = odemass(self.t0,self.y0_int,opts,[])
        self.assertEqual(massType,0)
        self.assertEqual(massM[0,0],1)
        self.assertEqual(massFcn,None)
        
        
    def test_odemass_int_matrix(self):
        opts = {'Mass':[3]}
        massType, massM, massFcn = odemass(self.t0,self.y0_int,opts,[])
        self.assertEqual(massType,1)
        self.assertEqual(massM,[3])
        self.assertEqual(massFcn,None)
        
        
    def test_odemass_int_function_time(self):
        opts = {'Mass':self.mass_time_int,'MStateDependence':'none'}
        massType, massM, massFcn = odemass(self.t0,self.y0_int,opts,[])
        self.assertEqual(massType,2)
        self.assertEqual(massM,[2])
        self.assertEqual(massFcn,self.mass_time_int)

    
    def test_odemass_int_function_state_extra(self):
        opts = {'Mass':self.mass_state_int}
        massType, massM, massFcn = odemass(self.t0,self.y0_int,opts,[])
        self.assertEqual(massType,3)
        self.assertEqual(massM,[4])
        self.assertEqual(massFcn,self.mass_state_int)
        
        
    def test_odemass_int_function_state(self):
        opts = {'Mass':self.mass_state_int,'MStateDependence':'weak'}
        massType, massM, massFcn = odemass(self.t0,self.y0_int,opts,[])
        self.assertEqual(massType,3)
        self.assertEqual(massM,[4])
        self.assertEqual(massFcn,self.mass_state_int)
        
        
    def test_odemass_vec_nomass(self):
        opts = {}
        massType, massM, massFcn = odemass(self.t0,self.y0_vec,opts,[])
        self.assertEqual(massType,0)
        sparse = sp.eye(2)
        self.assertEqual((sparse - massM).nnz, 0)
        self.assertEqual(massFcn,None)
        
        
    def test_odemass_vec_matrix(self):
        opts = {'Mass':[[1, 2],[2, 3]]}
        massType, massM, massFcn = odemass(self.t0,self.y0_vec,opts,[])
        self.assertEqual(massType,1)
        self.assertEqual(massM,[[1, 2],[2, 3]])
        self.assertEqual(massFcn,None)
        
        
    def test_odemass_vec_function_time(self):
        opts = {'Mass':self.mass_time_vec,'MStateDependence':'none'}
        massType, massM, massFcn = odemass(self.t0,self.y0_vec,opts,[])
        self.assertEqual(massType,2)
        array = np.array([[2,3],[2,3]])
        for i in range(len(array)):
            for j in range(len(array[0])):
                self.assertEqual(massM[i][j],array[i][j])
        self.assertEqual(massFcn,self.mass_time_vec)
        
    
    def test_odemass_vec_function_state_extra(self):
        opts = {'Mass':self.mass_state_vec}
        massType, massM, massFcn = odemass(self.t0,self.y0_vec,opts,[])
        self.assertEqual(massType,3)
        array = np.array([[1,4],[2,3]])
        for i in range(len(array)):
            for j in range(len(array[0])):
                self.assertEqual(massM[i][j],array[i][j])
        self.assertEqual(massFcn,self.mass_state_vec)
        
        
    def test_odemass_vec_function_state(self):
        opts = {'Mass':self.mass_state_vec,'MStateDependence':'weak'}
        massType, massM, massFcn = odemass(self.t0,self.y0_vec,opts,[])
        self.assertEqual(massType,3)
        array = np.array([[1,4],[2,3]])
        for i in range(len(array)):
            for j in range(len(array[0])):
                self.assertEqual(massM[i][j],array[i][j])
        self.assertEqual(massFcn,self.mass_state_vec)
   
    

if __name__ == "__main__":
    unittest.main()
    
    
        
        