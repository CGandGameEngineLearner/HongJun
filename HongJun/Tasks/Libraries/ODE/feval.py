import numpy as np

def feval(fun, t, y, extra):
    
    '''Helper function to evaluate a function.
        
    Parameters
    ----------
    fun : callable
        Function to be evaluated, must be in the form of fun(t, y, *extra) or fun(t, *extra).
    t : scalar
        Used in function evaluation,
    y : None || array_like, shape(n,)
        If y is None then the function will be called in the form fun(t, *extra), otherwise is will be
        called in the form fun(t, y, *extra).
    extra : array_like, shape(k,)
        Extra arguments in the function evaluation, if no extra arguments are used then extra is empty.    
    
    Returns
    -------
    result : array_like, shape(n,)
        Evaluated function result.
    '''
    
    if isinstance(y, np.ndarray):
        if y.ndim != 1:
            y = np.squeeze(y)  
            
    #fun has signature fun(t,*extra)
    if isinstance(y, type(None)):
        try:
            result = fun(t, *extra)
        except Exception as exception:
            raise Exception("ode45: feval: " + str(exception))
        return result
    
    #fun has signature fun(t,y,*extra)
    try:
        result = fun(t, y, *extra)
    except Exception as exception:
        raise Exception("ode45: feval: " + str(exception))
    return result
