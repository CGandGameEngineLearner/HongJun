import numpy as np
import numbers as num
from inspect import signature
import warnings

#Helper functions
from HongJun.Tasks.Libraries.ODE.odeoptions import odeoptions
from HongJun.Tasks.Libraries.ODE.odeget import odeget
from HongJun.Tasks.Libraries.ODE.feval import feval


def odearguments(ode, tspan, y0, options, extras): 
    
    '''Function to verify the inputs of ode45 meet the specifications.
        
    Parameters
    ----------
    ode : callable
        ode function which will be evaluated.
    tspan : array_like, shape(2,) || shape(k,)
        Span over which the function should be evaluated, can be either be a pair [t_0,t_end] or an
        array of specific points.
    y0 : array_like, shape(n,)
        Initial values.
    options : dictionary
        Options, see ode45 sepifications for more information.
    extras : array_like, shape(k,)
        Extra arguments in the function evaluation, if no extra arguments are used then extra is empty. 
        
        
    Returns
    -------
    neq : integer
        Number of equations.
    tspan : array_like, shape(2,) || shape(k,)
        Span over which the function should be evaluated, can be either be a pair [t_0,t_end] or an
        array of specific points.
    ntspan : integer
        Size of tspan.
    nex : 2
        Used in main ode45
    t0 : scalar
        First time to be evaluated.
    tfinal : scalar
        Final time to be evaluated.
    tdir : scalar
        Whether tfinal is greater than t0, 1 if tfinal is greater and -1 otherwise.
    y0 : array_like, shape(n,)
        Initial values.
    f0 : array_like, shape(n,)
        Evaluation of ode for intial values y0.
    args : array_like, shape(k,)
        Extra arguments.
    odeFcn : callable
        ode function.
    options : dictionary.
        options dictionary.
    threshold : scalar || array_like, shape(n,)
        Difference between the absolute tolerance and relative tolerance, if the AbsTol option is a scalar
        then threshold is a scalar, and a array if AbsTol is an array.
    rtol : scalar
        Relative tolerance (RelTol option).
    normcontrol : Bool
        True if NormControl option is 'on', False otherwise.
    normy : scalar
        Norm of the intial values.
    hmax : scalar
        Maximum step size.
    htry : scalar
        Initial step size.
    htspan : scalar
        Difference between t_0 and t_end.
    dataType : numpy dtype
        float64.
    '''
    
    #Verify y0
    if not isinstance(y0,np.ndarray) and not isinstance(y0,list):
        raise TypeError('odearguments: y0: must be a list or ndarray')
    else:
        if len(y0)==0:
            raise ValueError('odearguments: y0: must have at least one initial value')
        for i in y0:
            if not isinstance(i,num.Number):
                raise TypeError('odearguments: y0: elements must be numbers')
        neq=len(y0)
    
    #Verify tspan
    if not isinstance(tspan,np.ndarray) and not isinstance(tspan,list):
        raise TypeError('odearguments: tspan: must be a list or ndarray')
    else:
        if len(tspan) < 2:
            raise ValueError('odearguments: tspan: must have at least two initial values')    
        for i in tspan:
            if not isinstance(i,num.Number):
                raise TypeError('odearguments: tspan: elements must be numbers')
    
    
    #Verify ode
    if not callable(ode):
        raise TypeError('odearguments: ode: ode function is not callable')
    else:
        sig = signature(ode)
        if len(sig.parameters) != 2 + len(extras):
            raise TypeError('odearguments: ode: ode function must have the correct number of arguments')
        else:
            result = feval (ode,tspan[0],y0,extras)
            if not isinstance(result,np.ndarray) and not isinstance(result,list):
                raise TypeError('odearguments: ode: ode function must return a list or ndarray type')
            else:
                if len(result) != len(y0):
                    raise ValueError('odearguments: ode: ode function must return a list or ndarray type of length equal to y0')
                for i in result:
                    if not isinstance(i,num.Number):
                        raise TypeError('odearguments: ode: elements must be numbers')
    
    #Check options
    odeoptions(options, tspan[0], y0, extras)
    
    htspan = abs(tspan[1]-tspan[0])
    ntspan = len(tspan)
    t0 = tspan[0]
    nex = 2
    tfinal = tspan[-1]
    args = extras
        
    #Verify tspan
    if t0 == tfinal:
        raise ValueError('odearguments: tspan: first value and final value must be different') 
    tdir = np.sign(tfinal-t0)
    if any(tdir*np.diff(tspan)<=0):
        raise ValueError('odearguments: tspan: must be monotonic')
    
    f0=feval(ode,t0,y0,extras)
    
    dataType='float64'
    
    #Relative tolerance
    rtol=odeget(options,'RelTol',1e-3)
    if rtol < 100 * np.finfo(dataType).eps:
        rtol = 100 * np.finfo(dataType).eps
        warnings.warn('odearguments: rtol: rtol was too small')
    
    #Absolute tolerance
    atol=odeget(options, 'AbsTol', 1e-6)
    normcontrol = (odeget(options, 'NormControl', 'off') == 'on')
    if normcontrol:
        normy=np.linalg.norm(y0)
    else:
        normy = 0
        
    if isinstance(atol,list):
        if normcontrol:
            raise ValueError('odearguments: NormControl: when \'on\' AbsTol must be a scalar')
        threshold = [tol/rtol for tol in atol]
    else:
        threshold=atol/rtol
    
    #Default max step is 1/10 size of the interval
    hmax=min(abs(tfinal-t0), abs(odeget(options, 'MaxStep', 0.1*(tfinal-t0))))
    htry=odeget(options,'InitialStep',0)
    
    odeFcn=ode
    
    
    return neq, tspan, ntspan, nex, t0, tfinal, tdir, y0, f0, args, odeFcn, options, threshold, rtol, normcontrol, normy, hmax, htry, htspan, dataType