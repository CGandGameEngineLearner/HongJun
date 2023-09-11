from HongJun.Tasks.Libraries.ODE.feval import feval


def odenonnegative(ode,y0,threshold,idxNonNegative):
    
    '''Helper function to ensure non-negative solutions for ode45.
        
    Parameters
    ----------
    ode : callable
        Ode function.
    y0 : 
        Initial values.
    threshold : float || list
        Error threshold
    idxNonNegative : list
        List of solutions which should be non-negative.
        
        
    Returns
    -------
    odeFcn, : callable
        Overwriten odeFcn which will ensure that the indicated solution will be non-negative.
    thresholdNonNegative : array_like
        List of thresholds for the non-negative solutions.
    '''
    
    if any([True for i in idxNonNegative if i<0 or i>=len(y0)]):
        raise IndexError('odenonnegative: idxNonNegative: index outside of scope')
    
    if any([True for i in idxNonNegative if y0[i]<0]):
        raise ValueError('odenonnegative: y0: initial values were negative')
    
    if isinstance(threshold,list):
        thresholdNonNegative = [threshold[i] for i in idxNonNegative]
    else:
        thresholdNonNegative = [threshold] * len(idxNonNegative)
    
    #Wrapper function
    def local_odeFcn_nonnegative(t,y,*varargin):
        yp = feval(ode,t,y,varargin)
        ndx = [i for i in idxNonNegative if y[i]<=0]
        for i in ndx:
            yp[i] = max(yp[i],0)
        return yp

    odeFcn = local_odeFcn_nonnegative
        
    return odeFcn,thresholdNonNegative

