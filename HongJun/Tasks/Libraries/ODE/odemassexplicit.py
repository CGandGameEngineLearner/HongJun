from HongJun.Tasks.Libraries.ODE.feval import feval

import numpy as np
import scipy.linalg as lg
import scipy.sparse as sp
import scipy.sparse.linalg as spl


def odemassexplicit(massType,odeFcn,odeArgs,massFcn,massM):
    
    '''Event helper function for ode45.
        
    Parameters
    ----------
    massType : integer
        0 : If no mass option exists in options.
        1 : If mass option exists in options, and it matrix.
        2 : If mass option exists in options, and it is time-dependent function.
        2 : If mass option exists in options, and it is statetime-dependent function.
    odeFcn : callable
        Ode function.
    odeArgs : array_like
        Extra arguments for the ode function.
    massM : array_like, shape(n,n) || None
        Mass matrix if the mass option exists in options, and it is matrix. If mass option is a function
        then it is the evaluated mass function with the initial values. None otherwise.
    massFcn : callable || None
        Mass function if the mass option exists in options, and it is function. None otherwise.
        
    Returns
    -------
    odeFcn : callable
        Overwriten odeFcn which will solve M y' = f(t,y) for any evaluated points.
    odeArgs : array_like
        Overwriten odeArgs with all extra arguments needed to solve for M y' = f(t,y).
    '''
    
    if massType == 1:
        if type(massM)==type(sp.csr_matrix([])):
            superLU = spl.splu(massM)
            odeArgs = np.array([odeFcn, superLU, odeArgs])
            odeFcn = explicitSolverHandleMass1sparse
        else:
            PL, U = lg.lu(massM,permute_l = True)
            odeArgs = np.array([odeFcn, PL, U, odeArgs])
            odeFcn = explicitSolverHandleMass1
    elif massType==2:
        odeArgs = np.array([odeFcn, massFcn, odeArgs])
        odeFcn = explicitSolverHandleMass2
    else:
        odeArgs = np.array([odeFcn, massFcn, odeArgs])
        odeFcn = explicitSolverHandleMass3
    return odeFcn,odeArgs



def explicitSolverHandleMass1sparse(t,y,odeFcn,superLU,varargin):
    #Wrapper function for sparse mass matrix
    ode = feval(odeFcn,t,y,varargin)
    yp = superLU.solve(np.array(ode))
    return yp

def explicitSolverHandleMass1(t,y,odeFcn,PL,U,varargin):
    #Wrapper function for dense mass matrix
    ode = feval(odeFcn,t,y,varargin)
    xp = lg.lstsq(PL,ode)[0]
    yp = lg.lstsq(U,xp)[0]
    return yp

def explicitSolverHandleMass2(t,y,odeFcn,massFcn,varargin):
    #Wrapper function for time dependent function
    mass = feval(massFcn,t,None,varargin)
    ode = feval(odeFcn,t,y,varargin)
    yp = lg.lstsq(mass,ode)[0]
    return yp

def explicitSolverHandleMass3(t,y,odeFcn,massFcn,varargin):
    #Wrapper function for state-time dependent function
    mass = feval(massFcn,t,y,varargin)
    ode = feval(odeFcn,t,y,varargin)
    yp = lg.lstsq(mass,ode)[0]
    return yp


