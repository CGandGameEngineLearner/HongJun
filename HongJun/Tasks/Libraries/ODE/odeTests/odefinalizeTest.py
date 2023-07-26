import unittest, os, sys
import numpy as np

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from odefinalize import odefinalize

class Testodefinalize(unittest.TestCase):
    
    def test_odefinalize_basic(self):
        solver='ode45'
        nout = 34
        statsvec = [12,34,1]
        printstats=True
        tout=np.ones((1,50))
        yout=np.ones((2,50))
        
        haveeventfun = True
        teout=np.ones((1,11))
        yeout=np.ones((2,11))
        ieout=np.ones((2,11))
        
        sol =odefinalize(solver, printstats, statsvec, nout, tout, yout, haveeventfun, teout, yeout, ieout)
        
        self.assertEqual(sol.get_t().shape,(34,))
        self.assertEqual(sol.get_y().shape,(2,34))
        
        te,ye,ie=sol.get_events()
        self.assertEqual(te.shape,(1,11))
        self.assertEqual(ye.shape,(2,11))
        self.assertEqual(ie.shape,(2,11))
        
        self.assertEqual(len(sol.get_stats()),3)
        self.assertEqual(sol.get_solver(),'ode45')
        self.assertEqual(sol.get_size(),34)
        self.assertEqual(sol.has_events(),True)
        
if __name__ == "__main__":
    unittest.main()