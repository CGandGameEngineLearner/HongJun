import numpy as np
import os
import sys

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from ode import ode45

'''The This script is used to perform random testing for the ode45 function. This script
    works in conjunction with testScript.m, which generates the expected output for a series 
    of random inputs. This script will then read the inputs and expected outputs, pass the 
    inputs to the implemented ode45 function and check them against the expected output.
    Note: any functions which are added to the MATLAB script also have to be added to this 
    script.
'''

def solve_ode(inputs,result):
    sol=ode45(inputs.fun,inputs.tspan,inputs.y0,inputs.get_options(),inputs.varargin)
    result.compare_ty(sol.get_t(),sol.get_y())
    result.compare_stats(sol.get_stats())


def get_fun(val):
    #Add any ode function here
    f=None
    if val == 'cosbasic':
        def f(t,y):
            return [np.cos(t),2*np.cos(t)]
    if val == 'trigbasic':
        def f(t,y):
            return [y[0]*np.cos(t),y[1]*np.sin(t)]
    return f

def get_event_fun(val):
    #Add any event function here
    return val

def get_mass_fun(val):
    #Add any mass function here
    return val

class Inputs:
    def __init__(self):
        self.fun=None
        self.tspan=None
        self.y0=None
        self.varargin=[]
        self.reltol=None
        self.norm=None
        self.abstol=None
        self.refine=None
        self.stats=None
        self.nonnegative=None
        self.events=None
        self.maxstep=None
        self.initialstep=None
        self.mass=None
        self.massstate=None

    def __str__(self):
        if len(self.tspan)>2:
            strtspan=str(len(self.tspan))
        else:
            strtspan=str(self.tspan)
        return "Fun : "+str(self.fun)+"\nTspan : "+strtspan+"\nY0 : "+str(self.y0)+ \
        "\nVarargin : "+str(self.varargin)+"\nRelTol : "+str(self.reltol)+"\nAbsTol : "+str(self.abstol)+ \
        "\nNormControl : "+str(self.norm)+"\nRefine : "+str(self.refine)+"\nStats : "+str(self.stats)+ \
        "\nNonNegative : "+str(self.nonnegative)+"\nEvents : "+str(self.events)+"\nMaxStep : "+str(self.maxstep)+ \
        "\nInitialStep : "+str(self.initialstep)+"\nMass : "+str(self.mass)+"\nMStateDependence : "+str(self.massstate)+ "\n\n"

    def set_fun(self, val):
        self.fun=get_fun(val)
        
    def set_tspan(self, val):
        x = [0] * len(val)
        for i in range(len(val)):
            x[i]=float(val[i])
        self.tspan=x
    
    def set_y0(self, val):
        x = [0] * len(val)
        for i in range(len(val)):
            x[i]=float(val[i])
        self.y0=x
    
    def set_varargin(self, val):
        x = [0] * len(val)
        for i in range(len(val)):
            x[i]=float(val[i])
        self.varargin=x
    
    def set_reltol(self, val):
        self.reltol=float(val)
        
    def set_abstol(self, val):
        if len(val)==1:
            self.abstol=float(val[0])
        else:
            x = [0] * len(val)
            for i in range(len(val)):
                x[i]=float(val[i])
            self.abstol=x
        
    def set_norm(self, val):
        self.norm=val
        
    def set_refine(self, val):
        self.refine=int(val)
        
    def set_stats(self, val):
        self.stats=val
        
    def set_nonnegative(self, val):
        x = [0] * len(val)
        for i in range(len(val)):
            x[i]=int(val[i])-1
        self.nonnegative=x
        
    def set_events(self, val):
        self.events=get_event_fun(val)
        
    def set_maxstep(self, val):
        self.maxstep=float(val)
        
    def set_initialstep(self, val):
        self.initialstep=float(val)
    
    def set_mass_fun(self, val):
        self.mass=get_mass_fun(val)
    
    def set_mass_mat(self, val):
        l = int(np.sqrt(len(val)))
        x = np.zeros((l,l))
        for i in range(l):
            for j in range(l):
                x[i,j]=float(val[j*l + i])
        self.mass=x
    
    def set_massstate(self, val):
        self.massstate=val
    
    
    def get_options(self):
        opt ={}
        
        if self.reltol != None:
            opt["RelTol"] = self.reltol
        if self.abstol != None:
            opt["AbsTol"] = self.abstol
        if self.norm != None:
            opt["NormControl"] = self.norm
        if self.refine != None:
            opt["Refine"] = self.refine
        if self.stats != None:
            opt["Stats"] = self.stats
        if self.nonnegative != None:
            opt["NonNegative"] = self.nonnegative
        if self.events != None:
            opt["Events"] = self.events
        if self.maxstep != None:
            opt["MaxStep"] = self.maxstep
        if self.initialstep != None:
            opt["InitialStep"] = self.initialstep
        if not isinstance(self.mass,type(None)):
            opt["Mass"] = self.mass
        if self.massstate != None:
            opt["MStateDependence"] = self.massstate
        
        return opt

class Results:
    def __init__(self):
        self.tout=np.array([])
        self.yout=np.array([])
        self.nsteps=0
        self.nfailed=0
        self.nfevals=0
        self.teout=np.array([])
        self.yeout=np.array([])
        self.ieout=np.array([])
    
    
    def __str__(self):
        return "NStesps : "+str(self.nsteps)+"\nNFailed : "+str(self.nfailed)+"\nNFevals : "+str(self.nfevals)+ \
        "\nTout : "+str(self.tout)+"\nYout : "+str(self.yout)+"\nTeout : "+str(self.teout)+ \
        "\nYeout : "+str(self.yeout)+"\nIeout : "+str(self.ieout)+"\n\n"
    
    def compare_ty(self,tout,yout):
        errt = 0.0
        erry = 0.0
        
        t = self.tout
        y = self.yout
        
        print("Equal size : " + str(len(t)==len(tout) and len(y)==len(yout)*len(yout[0])) + " |t| = "+str(len(t))+" |y| = "+str(yout.shape))
        
        for i in range(len(t)):
            for j in range(len(yout)):
                if abs(yout[j][i]-y[j*len(t)+i])>erry:
                    erry = abs(yout[j][i]-y[j*len(t)+i])
            if abs(tout[i]-t[i])>errt:
                errt = abs(tout[i]-t[i])
        
        print("Error t : " + str(errt))
        print("Error y : " + str(erry))
        print()
    
    def compare_stats(self,statsvec):
        print("Nsteps Expected : "+str(self.nsteps)+" Actual : "+str(statsvec[0]))
        print("Nfailed Expected : "+str(self.nfailed)+" Actual : "+str(statsvec[1]))
        print("Nfevals Expected : "+str(self.nfevals)+" Actual : "+str(statsvec[2]))
        print()
        
    

        
    def compare_events(self,teout,yeout,ieout):
        te=self.teout
        ye=self.yeout
        ie=self.ieout
        
        
        print("Equal event size : " + str(len(self.teout)==len(teout)))
        print("Equal event size : " + str(len(self.teout)==len(teout)))
        print("Equal event size : " + str(len(self.teout)==len(teout)))
        self.assertEqual(len(te),len(teout))
        self.assertEqual(len(ye),len(yeout)*len(yeout[0]))
        self.assertEqual(len(ie),len(ieout))
        
        for i in range(len(te)):
            for j in range(len(yeout)):
                self.assertAlmostEqual(ye[j*len(te)+i],yeout[j][i])
            self.assertAlmostEqual(teout[i],te[i])
            self.assertEqual(ieout[i],ie[i]-1)
    
    
    def set_statvec(self, statsvec):
        self.nsteps=int(statsvec[0])
        self.nfailed=int(statsvec[1])
        self.nfevals=int(statsvec[2])
    
    def set_tout(self, tout):
        x = np.zeros((len(tout),))
        for i in range(len(tout)):
            x[i]=float(tout[i])
        self.tout=x
    
    def set_yout(self, yout):
        x = np.zeros((len(yout),))
        for i in range(len(yout)):
            x[i]=float(yout[i])
        self.yout=x
    
    def set_teout(self, teout):
        x = np.zeros((len(teout),))
        for i in range(len(teout)):
            x[i]=float(teout[i])
        self.teout=x
    
    def set_yeout(self, yeout):
        x = np.zeros((len(yeout),))
        for i in range(len(yeout)):
            x[i]=float(yeout[i])
        self.yeout=x

    def set_ieout(self, ieout):
        x = np.zeros((len(ieout),))
        for i in range(len(ieout)):
            x[i]=int(ieout[i])
        self.ieout=x
        
        
def read_tests(filename,names):
    f=open(filename,"r")
    results = []
    inputs = []
    for line in f:
        statsvec=[0,0,0]
        result = Results()
        inp = Inputs()
        sp = line.split(" ")
        for word in sp:
            key, values =word.split(":")
            if key == "Function":
                if not names:
                    inp.set_fun(values)
                else:
                    inp.fun=values
            elif key == "Tspan":
                val = values.split("#")
                val.pop()
                inp.set_tspan(val)         
            elif key == "Y0":
                val = values.split("#")
                val.pop()
                inp.set_y0(val) 
            elif key == "Varargin":
                val = values.split("#")
                val.pop()
                if val[0]!='':
                    inp.set_varargin(val)
            elif key == "RelTol":
                if values != '': 
                    inp.set_reltol(values)
            elif key == "AbsTol":
                val = values.split("#")
                val.pop()
                if val[0] != '': 
                    inp.set_abstol(val)
            elif key == "NormControl":
                if values != '': 
                    inp.set_norm(values)
            elif key == "Refine":
                if values != '': 
                    inp.set_refine(values)
            elif key == "Stats":
                if values != '': 
                    inp.set_stats(values)
            elif key == "NonNegative":
                val = values.split("#")
                val.pop()
                if val[0] != '':
                    inp.set_nonnegative(val)
            elif key == "Events":
                if values != '': 
                    if not names:
                        inp.set_events(values)
                    else:
                        inp.events=values
            elif key == "MaxStep":
                if values != '': 
                    inp.set_maxstep(values)
            elif key == "InitialStep":
                if values != '': 
                    inp.set_initialstep(values)
            elif key == "Mass":
                val = values.split("#")
                if len(val) == 1:
                    if not names:
                        inp.set_mass_fun(values)
                    else:
                        inp.mass=values
                else:
                    val.pop()
                    if val[0]!='':
                        inp.set_mass_mat(val)
            elif key == "MStateDependence":
                if values != '': 
                    inp.set_massstate(values)
            elif key == "Tout":
                val = values.split("#")
                val.pop()
                if len(val)>=1:
                    result.set_tout(val)
            elif key == "Yout":
                val = values.split("#")
                val.pop()
                if len(val)>=1:
                    result.set_yout(val)
            elif key == "Nsteps":
                statsvec[0]=values
            elif key == "Nfailed":
                statsvec[1]=values
            elif key == "Nfevals":
                statsvec[2]=values
            elif key == "Teout":
                val = values.split("#")
                val.pop()
                if len(val)>=1:
                    result.set_teout(val)
            elif key == "Yeout":
                val = values.split("#")
                val.pop()
                if len(val)>=1:
                    result.set_yeout(val)
            elif key == "Ieout":
                val = values.split("#")
                val.pop()
                if len(val)>=1:
                    result.set_ieout(val)
            else:
                print(key)
                raise Exception("Invalid key")
            
        result.set_statvec(statsvec)
        results.append(result)
        inputs.append(inp)
    return results,inputs

if __name__ == "__main__":
    results,inputs=read_tests("test.txt",False)
    for i in range(len(inputs)):
        solve_ode(inputs[i],results[i])

    