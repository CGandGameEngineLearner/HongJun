import unittest, os, sys
import numpy as np
import scipy.sparse as sp
import scipy.linalg as lg
import scipy.sparse.linalg as spl


currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from odemassexplicit import odemassexplicit,explicitSolverHandleMass1sparse,explicitSolverHandleMass1,explicitSolverHandleMass2,explicitSolverHandleMass3
from feval import feval

class Testodemassexplicit(unittest.TestCase):
    
    def setUp(self):
        self.t = 1
        self.y = [-1,2,5]
        self.extra = [1]
        
        def f(t,y,c):
            return [y[0]+c,y[1]+2*t,y[2]+3*t]
        
        self.f = f
        self.mass1 = [[1,1,-1],[6,2,-2],[-3,4,1]]
        
        def mass_time(t,c):
            return [[t, 2*t-1, -1],[6, 2*t, -2*t],[-3, 4, 1]]
        
        def mass_state(t,y,c):
            return [[t, 2*t-1, -1],[y[2]+1, y[1], -1*y[1]],[-3, 4, 1]]
        
        self.mass2 = mass_time
        self.mass3 = mass_state
        
    
    
    def test_odemassexplicit_mass1(self):
        odeFcn,odeArgs = odemassexplicit(1,self.f,self.extra,[],self.mass1)
        PL, U = lg.lu(self.mass1,permute_l = True)
        y = feval(odeFcn,self.t,self.y,odeArgs)
        result = np.array([1,2,3])
        
        self.assertEqual(odeFcn,explicitSolverHandleMass1)
        self.assertEqual(len(odeArgs),4)
        self.assertEqual(odeArgs[0],self.f)
        for i in range(len(PL)):
            self.assertAlmostEqual(y[i],result[i])
            for j in range(len(PL[0])):
                self.assertEqual(odeArgs[1][i,j],PL[i,j])
                self.assertEqual(odeArgs[2][i,j],U[i,j])
        self.assertEqual(odeArgs[3],[1])
        
        
        
    def test_odemassexplicit_mass1sparse(self):
        odeFcn,odeArgs = odemassexplicit(1,self.f,self.extra,[],sp.csr_matrix(self.mass1))
        superLU = spl.splu(sp.csr_matrix(self.mass1))
        y = feval(odeFcn,self.t,self.y,odeArgs)
        result = np.array([1,2,3])
        
        self.assertEqual(odeFcn,explicitSolverHandleMass1sparse)
        self.assertEqual(len(odeArgs),3)
        self.assertEqual(odeArgs[0],self.f)
        self.assertEqual((superLU.L-odeArgs[1].L).nnz,0)
        self.assertEqual((superLU.U-odeArgs[1].U).nnz,0)
        for i in range(len(result)):
            self.assertAlmostEqual(y[i],result[i])
        self.assertEqual(odeArgs[2],[1])
        
        
        
    def test_odemassexplicit_mass2(self):
        odeFcn,odeArgs = odemassexplicit(2,self.f,self.extra,self.mass2,[])
        
        y = feval(odeFcn,self.t,self.y,odeArgs)
        result = np.array([1,2,3])

        self.assertEqual(odeFcn,explicitSolverHandleMass2)
        self.assertEqual(len(odeArgs),3)
        self.assertEqual(odeArgs[0],self.f)
        self.assertEqual(odeArgs[1],self.mass2)
        for i in range(len(result)):
            self.assertAlmostEqual(y[i],result[i])
        self.assertEqual(odeArgs[2],[1])
        
        
        
    def test_odemassexplicit_mass3(self):
        odeFcn,odeArgs = odemassexplicit(3,self.f,self.extra,self.mass3,[])
        y = feval(odeFcn,self.t,self.y,odeArgs)
        result = np.array([1,2,3])
        
        self.assertEqual(odeFcn,explicitSolverHandleMass3)
        self.assertEqual(len(odeArgs),3)
        self.assertEqual(odeArgs[0],self.f)
        self.assertEqual(odeArgs[1],self.mass3)
        for i in range(len(result)):
            self.assertAlmostEqual(y[i],result[i])
        self.assertEqual(odeArgs[2],[1])
        
        

if __name__ == "__main__":
    unittest.main()