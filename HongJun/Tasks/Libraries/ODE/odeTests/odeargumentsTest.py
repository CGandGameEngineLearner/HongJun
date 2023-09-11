import unittest, os, sys
import numpy as np

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from odearguments import odearguments

class Testodearguments(unittest.TestCase):
    
    def test_odearguments_y0fail(self):
        
        def f(t,y):
            return [t]
            
        tspan = [0,10]
        extra = []
        opt = {}
        
        y = tuple((1,2))
        self.assertRaises(TypeError, odearguments, f, tspan, y, opt, extra)
        y = 1
        self.assertRaises(TypeError, odearguments, f, tspan, y, opt, extra)
        y = [[1,2]]
        self.assertRaises(TypeError, odearguments, f, tspan, y, opt, extra)
        y = ['1','2']
        self.assertRaises(TypeError, odearguments, f, tspan, y, opt, extra)
        y = []
        self.assertRaises(ValueError, odearguments, f, tspan, y, opt, extra)
    
    
    def test_odearguments_tspanfail(self):
        
        def f(t,y):
            return [t, 2*t]
        
        y = [0,10]
        extra = []
        opt = {}
        
        tspan = 1
        self.assertRaises(TypeError, odearguments, f, tspan, y, opt, extra)
        tspan = tuple((1,2))
        self.assertRaises(TypeError, odearguments, f, tspan, y, opt, extra)
        tspan = []
        self.assertRaises(ValueError, odearguments, f, tspan, y, opt, extra)
        tspan = [1]
        self.assertRaises(ValueError, odearguments, f, tspan, y, opt, extra)
        tspan = ['1', 2]
        self.assertRaises(TypeError, odearguments, f, tspan, y, opt, extra)
        tspan = [[1,2],[3,4]]
        self.assertRaises(TypeError, odearguments, f, tspan, y, opt, extra)
        tspan = [1,1]
        self.assertRaises(ValueError, odearguments, f, tspan, y, opt, extra)
        tspan = [1,3,2,4]
        self.assertRaises(ValueError, odearguments, f, tspan, y, opt, extra)
        
    
    def test_odearguments_odefail(self):
        
        tspan = [0,3]
        y = [0,10]
        extra = []
        opt = {}
        
        f = 1
        self.assertRaises(TypeError, odearguments, f, tspan, y, opt, extra)
        
        def f(t):
            return t
        
        self.assertRaises(TypeError, odearguments, f, tspan, y, opt, extra)
        
        def f(t,c):
            return t
        
        self.assertRaises(TypeError, odearguments, f, tspan, y, opt, [1])
        
        def f(t,y):
            return t
        
        self.assertRaises(TypeError, odearguments, f, tspan, y, opt, [1])
        
        def f(t,y):
            return t

        self.assertRaises(TypeError, odearguments, f, tspan, y, opt, extra)
        
        def f(t,y,c):
            return t

        self.assertRaises(TypeError, odearguments, f, tspan, y, opt, [1])
        
        def f(t,y):
            return [t]
        
        self.assertRaises(ValueError, odearguments, f, tspan, y, opt, extra)
        
        def f(t,y):
            return [t, '1']

        self.assertRaises(TypeError, odearguments, f, tspan, y, opt, extra)
        
        def f(t,y):
            return [t, y]

        self.assertRaises(TypeError, odearguments, f, tspan, y, opt, extra)
        
    
    def test_odearguments_optfail(self):
        
        def f(t,y):
            return [t, 2*t]
        
        y = [0,10]
        tspan = [0,1]
        extra = []
        opt = {'AbsTol':[3.4e-7,8.5e-6],'NormControl':'on'}
        self.assertRaises(ValueError, odearguments, f, tspan, y, opt, extra)
    
    def test_odearguments_nooptions1(self):
        opt = {}
        tspan = [0,10]
        y = [1,0]
        extra = []
        
        def f(t,y):
            return [np.cos(t),np.sin(t)]
        
        neq, tspan, ntspan, nex, t0, tfinal, tdir, y0, f0, odeArgs, odeFcn, options, threshold, rtol, normcontrol, normy, hmax, htry, htspan, dataType = odearguments(f, tspan, y, opt, extra)
        
        self.assertEqual(neq,2)
        self.assertEqual(tspan,[0,10])
        self.assertEqual(ntspan,2)
        self.assertEqual(nex,2)
        self.assertEqual(t0,0)
        self.assertEqual(tfinal,10)
        self.assertEqual(tdir,1)
        self.assertEqual(y0,[1,0])
        self.assertEqual(f0,[1,0])
        self.assertEqual(odeArgs,[])
        self.assertEqual(odeFcn,f)
        self.assertEqual(options,{})
        self.assertEqual(threshold,1e-3)
        self.assertEqual(rtol,1e-3)
        self.assertEqual(normcontrol,0)
        self.assertEqual(normy,0)
        self.assertEqual(hmax,1)
        self.assertEqual(htry,0)
        self.assertEqual(htspan,10)
        self.assertEqual(dataType,'float64')
        
    
    def test_odearguments_nooptions2(self):
        opt = {}
        tspan = [-1,0,1,2,3,4,5,6,7,8,9]
        y = [1,0,5]
        extra = [-1]
        
        def f(t,y,c):
            return [np.cos(t),np.sin(t),c]
        
        neq, tspan, ntspan, nex, t0, tfinal, tdir, y0, f0, odeArgs, odeFcn, options, threshold, rtol, normcontrol, normy, hmax, htry, htspan, dataType = odearguments(f, tspan, y, opt, extra)
        
        self.assertEqual(neq,3)
        self.assertEqual(tspan,[-1,0,1,2,3,4,5,6,7,8,9])
        self.assertEqual(ntspan,11)
        self.assertEqual(nex,2)
        self.assertEqual(t0,-1)
        self.assertEqual(tfinal,9)
        self.assertEqual(tdir,1)
        self.assertEqual(y0,[1,0,5])
        self.assertEqual(f0,[0.5403023058681398,-0.8414709848078965,-1])
        self.assertEqual(odeArgs,[-1])
        self.assertEqual(odeFcn,f)
        self.assertEqual(options,{})
        self.assertEqual(threshold,1e-3)
        self.assertEqual(rtol,1e-3)
        self.assertEqual(normcontrol,0)
        self.assertEqual(normy,0)
        self.assertEqual(hmax,1)
        self.assertEqual(htry,0)
        self.assertEqual(htspan,1)
        self.assertEqual(dataType,'float64')
        
    def test_odearguments_nooptions3(self):
        opt = {}
        tspan = [10,0]
        y = [1,0]
        extra = []
        
        def f(t,y):
            return [np.cos(t),np.sin(t)]
        
        neq, tspan, ntspan, nex, t0, tfinal, tdir, y0, f0, odeArgs, odeFcn, options, threshold, rtol, normcontrol, normy, hmax, htry, htspan, dataType = odearguments(f, tspan, y, opt, extra)
        
        self.assertEqual(neq,2)
        self.assertEqual(tspan,[10,0])
        self.assertEqual(ntspan,2)
        self.assertEqual(nex,2)
        self.assertEqual(t0,10)
        self.assertEqual(tfinal,0)
        self.assertEqual(tdir,-1)
        self.assertEqual(y0,[1,0])
        self.assertEqual(f0,[-0.8390715290764524,-0.5440211108893698])
        self.assertEqual(odeArgs,[])
        self.assertEqual(odeFcn,f)
        self.assertEqual(options,{})
        self.assertEqual(threshold,1e-3)
        self.assertEqual(rtol,1e-3)
        self.assertEqual(normcontrol,0)
        self.assertEqual(normy,0)
        self.assertEqual(hmax,1)
        self.assertEqual(htry,0)
        self.assertEqual(htspan,10)
        self.assertEqual(dataType,'float64')
        
        
    def test_odearguments_options1(self):
        opt = {'MaxStep':0.5,'InitialStep':1e-2,'RelTol':2.3e-4,'AbsTol':3.4e-7,'NormControl':'off'}
        tspan = [0,10]
        y = [1,0]
        extra = []
        
        def f(t,y):
            return [np.cos(t),np.sin(t)]
        
        neq, tspan, ntspan, nex, t0, tfinal, tdir, y0, f0, odeArgs, odeFcn, options, threshold, rtol, normcontrol, normy, hmax, htry, htspan, dataType = odearguments(f, tspan, y, opt, extra)
        
        self.assertEqual(neq,2)
        self.assertEqual(tspan,[0,10])
        self.assertEqual(ntspan,2)
        self.assertEqual(nex,2)
        self.assertEqual(t0,0)
        self.assertEqual(tfinal,10)
        self.assertEqual(tdir,1)
        self.assertEqual(y0,[1,0])
        self.assertEqual(f0,[1,0])
        self.assertEqual(odeArgs,[])
        self.assertEqual(odeFcn,f)
        self.assertEqual(options,{'MaxStep':0.5,'InitialStep':1e-2,'RelTol':2.3e-4,'AbsTol':3.4e-7,'NormControl':'off'})
        self.assertEqual(threshold,0.0014782608695652173)
        self.assertEqual(rtol,2.3e-4)
        self.assertEqual(normcontrol,0)
        self.assertEqual(normy,0)
        self.assertEqual(hmax,0.5)
        self.assertEqual(htry,0.01)
        self.assertEqual(htspan,10)
        self.assertEqual(dataType,'float64')
        
    
    def test_odearguments_options2(self):
        opt = {'MaxStep':15,'InitialStep':1e-2,'RelTol':2.3e-16,'AbsTol':[3.4e-7,8.5e-6],'NormControl':'off'}
        tspan = [0,10]
        y = [1,0]
        extra = []
        
        def f(t,y):
            return [np.cos(t),np.sin(t)]
        
        neq, tspan, ntspan, nex, t0, tfinal, tdir, y0, f0, odeArgs, odeFcn, options, threshold, rtol, normcontrol, normy, hmax, htry, htspan, dataType = odearguments(f, tspan, y, opt, extra)
        
        self.assertEqual(neq,2)
        self.assertEqual(tspan,[0,10])
        self.assertEqual(ntspan,2)
        self.assertEqual(nex,2)
        self.assertEqual(t0,0)
        self.assertEqual(tfinal,10)
        self.assertEqual(tdir,1)
        self.assertEqual(y0,[1,0])
        self.assertEqual(f0,[1,0])
        self.assertEqual(odeArgs,[])
        self.assertEqual(odeFcn,f)
        self.assertEqual(options,{'MaxStep':15,'InitialStep':1e-2,'RelTol':2.3e-16,'AbsTol':[3.4e-7,8.5e-6],'NormControl':'off'})
        self.assertEqual(threshold,[15312238.733059686,382805968.32649213])
        self.assertEqual(rtol,2.220446049250313e-14)
        self.assertEqual(normcontrol,0)
        self.assertEqual(normy,0)
        self.assertEqual(hmax,10)
        self.assertEqual(htry,0.01)
        self.assertEqual(htspan,10)
        self.assertEqual(dataType,'float64')
        
    
    def test_odearguments_options3(self):
        opt = {'MaxStep':15,'InitialStep':1e-2,'RelTol':2.3e-16,'AbsTol':3.4e-7,'NormControl':'on'}
        tspan = [0,10]
        y = [1.5,0.3]
        extra = []
        
        def f(t,y):
            return [np.cos(t),np.sin(t)]
        
        neq, tspan, ntspan, nex, t0, tfinal, tdir, y0, f0, odeArgs, odeFcn, options, threshold, rtol, normcontrol, normy, hmax, htry, htspan, dataType = odearguments(f, tspan, y, opt, extra)
        
        self.assertEqual(neq,2)
        self.assertEqual(tspan,[0,10])
        self.assertEqual(ntspan,2)
        self.assertEqual(nex,2)
        self.assertEqual(t0,0)
        self.assertEqual(tfinal,10)
        self.assertEqual(tdir,1)
        self.assertEqual(y0,[1.5,0.3])
        self.assertEqual(f0,[1,0])
        self.assertEqual(odeArgs,[])
        self.assertEqual(odeFcn,f)
        self.assertEqual(options,{'MaxStep':15,'InitialStep':1e-2,'RelTol':2.3e-16,'AbsTol':3.4e-7,'NormControl':'on'})
        self.assertEqual(threshold,15312238.733059686)
        self.assertEqual(rtol,2.220446049250313e-14)
        self.assertEqual(normcontrol,1)
        self.assertEqual(normy,1.5297058540778354)
        self.assertEqual(hmax,10)
        self.assertEqual(htry,0.01)
        self.assertEqual(htspan,10)
        self.assertEqual(dataType,'float64')
        
        
if __name__ == "__main__":
    unittest.main()