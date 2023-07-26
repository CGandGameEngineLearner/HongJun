import unittest, os, sys
import numpy as np

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from ntrp45 import ntrp45

class Testntrp45(unittest.TestCase):
    
    def test_ntrp45_basic1(self):
        tinterp = [0.0451129930831952,0.0902259861663904,0.135338979249586]
        t=0
        idx=[]
        h=0.180451972332781
        f=[[20,19.6463141342278,19.4694712013416,18.5852565369110,18.4280628187900,18.2315706711387,18.2315706711387],[-9.80000000000000,-9.80000000000000,-9.80000000000000,-9.80000000000000,-9.80000000000000,-9.80000000000000,-9.80000000000000]]
        y=[[0],[20]]
        yinterp, ypinterp = ntrp45(tinterp,t,y,h,f,idx)
        
        
        yinterpexp = np.array([[0.892287469153773,1.76463015328729,2.61702805240055],[19.5578926677847,19.1157853355694,18.6736780033541]])
        ypinterpexp = np.array([[19.5578926677847,19.1157853355694,18.6736780033540],[-9.80000000000000,-9.79999999999998,-9.79999999999996]])  
        
        self.assertEqual(yinterp.shape,yinterpexp.shape)
        
        for i in range(len(yinterp)):
            for j in range(len(yinterp[0])):
                self.assertAlmostEqual(yinterp[i][j],yinterpexp[i][j])
                self.assertAlmostEqual(ypinterp[i][j],ypinterpexp[i][j])
    
    
    
    def test_ntrp45_basic2(self):
        tinterp = [5.02377286301916e-05,0.000100475457260383,0.000150713185890575]
        t=0
        idx=[0,1]
        h=2.009509145207664e-04
        f=[[1,0.999999999192375,0.999999998182843,0.999999987077994,0.999999984046906,0.999999979809365,0.999999979809365],[0,-4.01901828933337e-05,-6.02852743197140e-05,-0.000160760730924163,-0.000178623034179707,-0.000200950913168324,-0.000200950913168324]]
        y=[[0],[1]]
        yinterp, ypinterp = ntrp45(tinterp,t,y,h,f,idx)
        
        yinterpexp = np.array([[5.02377286090597e-05,0.000100475457091328,0.000150713185320013],[0.999999998738085,0.999999994952341,0.999999988642768]])
        ypinterpexp = np.array([[0.99999999873808,0.999999994952341,0.999999988642766],[-5.02377286090597e-05,-0.000100475457091328,-0.000150713185320014]])  
        
        
        self.assertEqual(yinterp.shape,yinterpexp.shape)
        
        for i in range(len(yinterp)):
            for j in range(len(yinterp[0])):
                self.assertAlmostEqual(yinterp[i][j],yinterpexp[i][j])
                self.assertAlmostEqual(ypinterp[i][j],ypinterpexp[i][j])
                
    
    def test_ntrp45_basic3(self):
        tinterp = [1.57080778220098,1.57080945520405,1.57081112820712]
        t=1.570806109197909
        idx=[0,1]
        h=6.692012286313442e-06
        f=[[-9.78240301208668e-06,-1.11208054693206e-05,-1.17900066979302e-05,-1.51360128406711e-05,-1.57308583772059e-05,-1.64744152978109e-05,-1.64744152978109e-05],[-0.999999999952152,-0.999999999938164,-0.999999999930498,0,0,0,0]]
        y=[[1.00000002145106],[2.62606197117840e-06]]
        yinterp, ypinterp = ntrp45(tinterp,t,y,h,f,idx)
        
        np.set_printoptions(precision=16)  

        yinterpexp = np.array([[1.00000002143329,1.00000002141273,1.00000002138937],[7.52331655344854e-07,0,0]])
        ypinterpexp = np.array([[-1.14554060830435e-05,-1.31284091526923e-05,-1.48014122225256e-05],[-1.08841838995090,0,0]])  
        
        
        self.assertEqual(yinterp.shape,yinterpexp.shape)
        
        for i in range(len(yinterp)):
            for j in range(len(yinterp[0])):
                self.assertAlmostEqual(yinterp[i][j],yinterpexp[i][j])
                self.assertAlmostEqual(ypinterp[i][j],ypinterpexp[i][j]) 
    
    
if __name__ == "__main__":
    unittest.main()
