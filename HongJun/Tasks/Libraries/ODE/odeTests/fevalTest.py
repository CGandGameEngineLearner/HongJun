import unittest, os, sys

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from feval import feval

class Testfeval(unittest.TestCase):
    
    def test_feval_basic(self):
        
        def f1(t,y):
            return t*y[0]
        
        def f2(t):
            return 3*t
        
        def f3(t,y,c):
            return t*c*y[1]
        
        def f4(t,c):
            return t*c[0]
        
        try:
            self.assertEqual(feval(f1,1.5,[2,3],[]),3)
            self.assertEqual(feval(f1,1.5,[3],[]),4.5)
            self.assertEqual(feval(f2,1.5,None,[]),4.5)
            self.assertEqual(feval(f2,2,None,[]),6)
            self.assertEqual(feval(f3,2,[0,2],[3]),12)
            self.assertEqual(feval(f3,7,[0,1],[4]),28)
            self.assertEqual(feval(f4,2,None,[[4]]),8)
            self.assertEqual(feval(f4,5,None,[[2]]),10)
            
            self.assertRaises(Exception, feval, f1, 1.5, None ,[])
            self.assertRaises(Exception, feval, f1, 1.5, [1,2] ,[3])
            self.assertRaises(Exception, feval, f2, 1.5, [1,4] ,[])
            self.assertRaises(Exception, feval, f2, 1.5, None ,[3])
            self.assertRaises(Exception, feval, f3, 1.5, None ,[])
            self.assertRaises(Exception, feval, f3, 1.5, [1,2] ,[])
            self.assertRaises(Exception, feval, f4, 1.5, None ,[])
            self.assertRaises(Exception, feval, f4, 1.5, [1,2] ,[3])
        except:
            self.fail("feval correct test failed")

if __name__ == "__main__":
    unittest.main()