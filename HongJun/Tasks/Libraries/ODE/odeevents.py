import numpy as np

#Helper functions
from HongJun.Tasks.Libraries.ODE.odeget import odeget
from HongJun.Tasks.Libraries.ODE.feval import feval

def odeevents(t0,y0,options,extras):
    
    '''Event helper function for ode45.
        
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
    haveeventfun : bool
        True if event function contained in options, False otherwise.
    eventFcn : callable || None
        Event function if contained in the options, None otherwise.
    eventArgs : array_like, shape(k,) || None
        extras if event function contained in options, None otherwise.
    eventValue : array_like, shape(n,) || None
        Values of the event function for the initial values if event function contained in options,
        None otherwise.
    teout : ndarray, shape(0,)
        Empty numpy array to store events t values.
    yeout : ndarray, shape(0,)
        Empty numpy array to store events y values.
    ieout : ndarray, shape(0,)
        Empty numpy array to store events index values.
    '''
    
    haveeventfun = False
    eventArgs = None
    eventValue = None
    
    teout = np.array([])
    yeout = np.array([])
    ieout = np.array([])
    
    eventFcn=odeget(options,'Events',None)
    
    if eventFcn==None:
        #No event option
        return haveeventfun,eventFcn,eventArgs,eventValue,teout,yeout,ieout
    
    haveeventfun = True
    eventArgs = extras
    eventValue,_,_ = feval(eventFcn,t0,y0,eventArgs)
    
    return haveeventfun,eventFcn,eventArgs,eventValue,teout,yeout,ieout