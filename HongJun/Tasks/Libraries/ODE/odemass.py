from HongJun.Tasks.Libraries.ODE.odeget import odeget
from HongJun.Tasks.Libraries.ODE.feval import feval

import scipy.sparse as sp


def odemass(t0, y0, options, extras):
    
    '''Mass helper function for ode45.
        
    Parameters
    ----------
    t0 : scalar
        Initial time to be evaluated.
    y0 : array_like, shape(n,)
        Initial values.
    options : dictionary
        Options, see ode45 sepifications for more information.
    extras : array_like, shape(k,)
        Extra arguments in the function evaluation, if no extra arguments are used then extra is empty. 
        
        
    Returns
    -------
    massType : integer
        0 : If no mass option exists in options.
        1 : If mass option exists in options, and it matrix.
        2 : If mass option exists in options, and it is time-dependent function.
        2 : If mass option exists in options, and it is statetime-dependent function.
    massM : array_like, shape(n,n) || None
        Mass matrix if the mass option exists in options, and it is matrix. If mass option is a function
        then it is the evaluated mass function with the initial values. None otherwise.
    massFcn : callable || None
        Mass function if the mass option exists in options, and it is function. None otherwise.
    '''
    
    #Initialize
    massType = 0
    massFcn = None
    massM = sp.eye(len(y0),format="csr")
    massArgs = None
    
    Moption = odeget(options,'Mass',None)
    if isinstance(Moption,type(None)):
        #No mass option
        return massType, massM, massFcn
    
    elif not callable(Moption):
        #Mass matrix
        massType = 1
        massM = Moption
        return massType, massM, massFcn
    
    else:
        #Mass function
        massFcn = Moption
        massArgs = extras
        Mstdep = odeget(options,'MStateDependence','weak')
        
        if Mstdep == 'none':
            massType = 2
        elif Mstdep == 'weak':
            massType = 3
        else:
            raise ValueError('odemass: MStateDependenceMass: Wrong type for MStateDependenceMass')
            
        if massType > 2:
            massM = feval(massFcn,t0,y0,massArgs)
        else:
            massM = feval(massFcn,t0,None,massArgs)
    
    return massType, massM, massFcn
