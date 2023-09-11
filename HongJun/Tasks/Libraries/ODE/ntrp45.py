import numpy as np

def ntrp45(tinterp,t,y,h,f,idxNonNegative):
    
    '''Interpolation function for ode45.
        
    Parameters
    ----------
    tinterp : scalar || array_like, shape(k,)
        Time to approximate the solution.
    t : scalar
        Current time.
    y : array_like, shape(k,n) || shape(n,)
        Currently evaluated points.
    h : scalar
        Size of step.
    f : ndarray, shape(n,7)
        Evaluated derivative points.
    idxNonNegative : array_like, shape(m,)
        Non negative solutions.
        
        
    Returns
    -------
    yinterp : array_like
        Esitimation at tinterp.
    ypinterp : array_like
        Derivative points for tinterp.
    '''
    
    BI = np.array([
    [1,       -183/64,      37/12,       -145/128,  ],
    [0,          0,           0,            0,      ],
    [0,       1500/371,    -1000/159,    1000/371,  ],
    [0,       -125/32,       125/12,     -375/64,   ],
    [0,       9477/3392,   -729/106,    25515/6784, ],
    [0,        -11/7,        11/3,        -55/28,   ],
    [0,         3/2,         -4,            5/2,    ]])
    
    if not isinstance(tinterp,np.ndarray):
        if isinstance(tinterp,list):
            tinterp=np.array(tinterp)
        else:
            tinterp=np.array([tinterp])
    
    s = (tinterp - t)/h
    
    
    diff=np.matmul(np.matmul(f,h*BI),np.cumprod(np.tile(s,(4,1)),axis=0))
    if len(tinterp) == 1:
        if isinstance(y,np.ndarray):
            if y.ndim==2:
                tile = y
            else:
                tile = np.transpose(np.array([y]))
        else:
            tile = np.transpose(np.array([y]))
    else:
        tile=np.tile(y,(1,len(tinterp)))
        
    yinterp=tile+diff
    
    ncumprod=np.append(np.array([np.ones(len(s))]),np.cumprod([2*s,1.5*s,(4.0/3.0)*s],axis=0),axis=0)
    ypinterp=np.matmul(np.matmul(f,BI),ncumprod)
    
    #Non-negative option
    if len(idxNonNegative)!=0:
        idx=[(i,j) for i in idxNonNegative for j in range(len(yinterp[0])) if yinterp[i][j]<0]
        if len(idx) != 0:
            for i,j in idx:
                ypinterp[i][j]=0
                yinterp[i][j]=0

    return yinterp, ypinterp