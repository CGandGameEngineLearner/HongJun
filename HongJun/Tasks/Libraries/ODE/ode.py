import numpy as np
import math
import warnings

#Helper functions
from HongJun.Tasks.Libraries.ODE.ntrp45 import ntrp45
from HongJun.Tasks.Libraries.ODE.odearguments import odearguments
from HongJun.Tasks.Libraries.ODE.odeget import odeget
from HongJun.Tasks.Libraries.ODE.odeevents import odeevents
from HongJun.Tasks.Libraries.ODE.feval import feval
from HongJun.Tasks.Libraries.ODE.odezero import odezero
from HongJun.Tasks.Libraries.ODE.odemass import odemass
from HongJun.Tasks.Libraries.ODE.odemassexplicit import odemassexplicit
from HongJun.Tasks.Libraries.ODE.odenonnegative import odenonnegative
from HongJun.Tasks.Libraries.ODE.odefinalize import odefinalize


def ode45(odefun, tspan, y0, options = None, varargin = None):
    
    '''Function to solve non-stiff differential equations using the dormund prince method
        with adaptive step. The system of differential equations takes the form y' = f(t,y)
        with y(0) = y_0 for t = {t_0, t_end}.
            
    Parameters
    ----------
    odefun : callable
        Callable function which represents the system of differential equations to be
        solved. The function must take the form y' = f(t,y), eg:
            
            def dydt(t,y):
                return [math.cos(t), y[1] * math.sin(t)]
                
        Where t must be a float and y must be an array_like of size n, where n is the
        size of the system. The function must return an array_like with the same size
        of size n.
            
    tspan : array_like, shape(2,) || shape(k,)
        This array represents the span over which odefun will be evaluated. It can either
        be an array of size 2 which represents [t_0, t_end], or it can either be a larger
        array which would represent a series of chosen points. If tspan is a series of 
        chosen points, then the function will only be evaluated at those points.
    
    y0 : array_like, shape(n,)
        This array are the initial values for the odefun function. It must be the same size
        as the array returned by the odefun.
    
    options : dictionary
        This dictionary contains the user options, the keys are represented by the option
        name, and the values are the value of the options. If a default value is shown, then
        this is the value the option will be set to automatically. The possible options are:
            
            AbsTol : float || array_like, shape(n,)    (default : 1e-6)
                Absolute error tolerance, can be a positive float or an array of positive
                floats.
                
            RelTol : float    (default : 1e-3)
                Relative error tolerance.
                
            NormControl : 'on' || 'off'    (default : 'off')
                If 'off' then error at each step:
                    error[i] <= max(RelTol * y[i], AbsTol[i])
                If 'on' then error at each step:
                    |error| <= max(RelTol * |y|, |AbsTol|)
                If NormControl is 'on' then AbsTol must be a float and not an array_like.
            
            Stats : 'on' || 'off'    (default : 'off')
                If 'on' then the function will print a series of stats about the execution.
            
            InitialStep : float
                Size of the initial step, must be a positive float.
                
            MaxStep : float    (default : 0.1 * abs(t_0 - t_end))
                Size of the maximun step, must be a positive float.
            
            Refine : integer    (default : 4)
                Determines the refinement to be performed at each step. If refine is set to 
                one, then no refinement will be performed.
                
            NonNegative : array_like    (default : [])
                List solutions of the differential system which will be kept positive. The
                list must contain only integers representing the indices of the solutions.
            
            Events : callable
                Function which must return value, isterminal, direction, all of which are 
                array_like of the same size. When the value of any of the values is 0 then
                an event is triggered. The isterminal determines whether the event should stop
                the execution and can only take value of 0 or 1. The direction determines from
                which direction the event should be triggered, if -1 then the event triggers
                if coming from the negative direction, whereas 1 will trigger if coming from 
                the positive direction, and 0 will trigger when coming from any direction. E.g :
                    
                    def events(t,y):
                        value = [10 - t, y[1]]
                        isterminal = [0, 1]
                        direction = [1, 0]
                        return value, isterminal, direction
                
            Mass : callable || array_like, shape(n,n)
                The mass option can either be a constant mass matrix, a time dependent function
                or a state-time dependent function.
                
                    Mass Matrix : array_like, shape(n,n)
                        Will solve for y s.t. M y' = f(t,y), M must be a square matrix.
                    
                    Time Dependent Function : callable
                        Will solve for y s.t. M(t) y' = f(t,y), M(t) must be a function in the
                        which takes t as argument an return an array_like(n,n)
                    
                    State-Time Dependent Function : callable
                        Will solve for y s.t. M(t,y) y' = f(t,y), M(t,y) must be a function in the
                        which takes t and y as argument an return an array_like(n,n)
            
            MStateDependence : 'none' || 'weak'    (default : 'none')
                Must be set to 'weak' if the Mass option is a state-time dependent function, otherwise
                it must be set to 'none'.
                    
    varargin : array_like, shape(t,)
        These are extra arguments that can be passed to the odefun. For example:
            
            def dydt(t,y,a,b):
                return [math.cos(t) + a, y[1] * math.sin(t) + b]
            
            varagin = [a,b]
        Note that these extra argument will also be passed to any events or mass function.
            

    Returns
    -------
    _ : odefinalize
        The function will return an object of type odefinalize (see odefinalize).
    
    '''
    
    
    solver_name='ode45'

    nsteps = 0
    nfailed = 0
    nfevals = 0
    
    if isinstance(options,type(None)):
        options = {}
    
    if isinstance(varargin,type(None)):
        varargin = []
    
    #Handle solver arguments
    neq, tspan, ntspan, nex, t0, tfinal, tdir, y0, f0, odeArgs, odeFcn, options, threshold, rtol, normcontrol, normy, hmax, htry, htspan, dataType = odearguments(odefun, tspan, y0, options, varargin)
    nfevals = nfevals + 1
    
    
    refine=max(1,odeget(options,'Refine', 4))
    if len(tspan) > 2:
        outputAt = 'RequestedPoints'
    elif refine == 1:
        outputAt = 'SolverSteps'
    else:
        outputAt = 'RefinedSteps'
        s=np.array(range(1,refine))/refine
    
    
    printstats = (odeget(options,'Stats','off') == 'on')
    
    
    #Handle the event function 
    haveEventFcn,eventFcn,eventArgs,valt,teout,yeout,ieout=odeevents(t0,y0,options,varargin)
    
    
    #Handle the mass matrix
    Mtype, M, Mfun =  odemass(t0,y0,options,varargin)
    if Mtype > 0:
        odeFcn,odeArgs = odemassexplicit(Mtype,odeFcn,odeArgs,Mfun,M)
        f0 = feval(odeFcn,t0,y0,odeArgs)
        nfevals = nfevals + 1
    
     
    #Non-negative solution components
    idxNonNegative = odeget(options,'NonNegative',[])
    nonNegative = False
    if len(idxNonNegative) != 0:
        odeFcn,thresholdNonNegative = odenonnegative(odeFcn,y0,threshold,idxNonNegative)
        f0 = feval(odeFcn,t0,y0,odeArgs)
        nfevals = nfevals + 1
        nonNegative = True
    
    
    t=t0
    y=y0
    
    #Memory Allocation
    nout=1
    yout=np.array([],dtype=dataType)
    tout=np.array([],dtype=dataType)
    if ntspan > 2:
        tout = np.zeros((1,ntspan),dtype=dataType)
        yout = np.zeros((neq,ntspan),dtype=dataType)
    else:
        chunk = min(max(100,50*refine), refine+math.floor(math.pow(2,11)/neq))
        tout = np.zeros((1,chunk),dtype=dataType)
        yout = np.zeros((neq,chunk),dtype=dataType)
        
    nout = 1
    tout[nout-1] = t
    yout[:,nout-1] = y.copy()
    
    
    #Initialize method parameters
    stop=0
    power = 1/5
    A = np.array([1./5.,        3./10.,     4./5.,      8./9.,          1.,             1.              ],dtype=dataType)
    B = np.array([[1./5.,       3./40.,     44./45.,    19372./6561.,   9017./3168.,    35./384.        ],
                  [0.,          9./40.,     -56./15.,   -25360./2187.,  -355./33.,      0.              ],
                  [0.,          0.,         32./9.,     64448./6561.,   46732./5247.,   500./1113.      ],
                  [0.,          0.,         0.,         -212./729.,     49./176.,       125./192.       ],
                  [0.,          0.,         0.,         0.,             -5103./18656.,  -2187./6784.    ], 
                  [0.,          0.,         0.,         0.,             0.,             11./84.         ],
                  [0.,          0.,         0.,         0.,             0.,             0.              ]],dtype=dataType)
    
    
    E = np.array([[71./57600.], [0.], [-71./16695.], [71./1920.], [-17253./339200.], [22./525.], [-1./40.]],dtype=dataType)
    f=np.zeros((neq,7),dtype=dataType)
    hmin=16*np.spacing(float(t))
    np.set_printoptions(precision=16)    
    
    #Initial step
    if htry==0:
        absh = min(hmax, htspan)
        if normcontrol:
            rh=(np.linalg.norm(f0)/ max(normy, threshold))/ (0.8 * math.pow(rtol,power))
        else:
            if isinstance(threshold,list):
                rh=np.linalg.norm(f0 / np.maximum(np.abs(y),threshold),np.inf) / (0.8 * math.pow(rtol,power))
            else:
                rh=np.linalg.norm(f0 / np.maximum(np.abs(y),np.repeat(threshold,len(y))),np.inf) / (0.8 * math.pow(rtol,power))
        if (absh * rh) > 1:
            absh =1/rh
        absh = max(absh,hmin)
    else:
        absh=min(hmax,max(hmin,htry))
    
    f[:,0]=f0
    
    ynew=np.zeros(neq,dtype=dataType)
    
    #Main loop
    done=False
    while not done:
        hmin = 16*np.spacing(float(t))
        absh = min(hmax, max(hmin, absh))
        h = tdir * absh
                
        #If next step is within 10% of finish
        if 1.1*absh >= abs(tfinal - t):
            h = tfinal - t
            absh = abs(h)
            done = True
        
        #Advancing one step
        nofailed=True
        while True:
            hA = h * A
            hB = h * B
            f[:,1]=feval(odeFcn,t+hA[0],y+np.matmul(f,hB[:,0]),odeArgs)
            f[:,2]=feval(odeFcn,t+hA[1],y+np.matmul(f,hB[:,1]),odeArgs)
            f[:,3]=feval(odeFcn,t+hA[2],y+np.matmul(f,hB[:,2]),odeArgs)
            f[:,4]=feval(odeFcn,t+hA[3],y+np.matmul(f,hB[:,3]),odeArgs)
            f[:,5]=feval(odeFcn,t+hA[4],y+np.matmul(f,hB[:,4]),odeArgs)

            
            tnew = t + hA[5]
            if done:
                tnew = tfinal   #Hit end point exactly
            h = tnew - t
            
            
            ynew=y+np.matmul(f,hB[:,5])
            f[:,6]=feval(odeFcn,tnew,ynew,odeArgs)
            nfevals=nfevals+6

            #Estimation of the error
            NNrejectStep = False
            if normcontrol:
                normynew = np.linalg.norm(ynew)
                errwt = max(max(normy,normynew),threshold)
                err = absh * np.linalg.norm(np.matmul(f,E)[:,0])/errwt
                if nonNegative and err <= rtol and any([True for i in idxNonNegative if ynew[i] < 0]):
                    errNN = np.linalg.norm([max(0, -1*ynew[i]) for i in idxNonNegative]) / errwt
                    if errNN > rtol:
                        err = errNN
                        NNrejectStep = True
            else:
                denom=np.maximum(np.maximum(np.abs(y),np.abs(ynew)),threshold)
                err=absh*np.linalg.norm(np.divide(np.matmul(f,E)[:,0],denom),np.inf)
                if nonNegative and err <= rtol and any([True for i in idxNonNegative if ynew[i] < 0]):
                    errNN = np.linalg.norm(np.divide([max(0, -1*ynew[i]) for i in idxNonNegative],thresholdNonNegative), np.inf)
                    if errNN > rtol:
                        err = errNN
                        NNrejectStep =True


            #Error is outside the tolerance
            if err > rtol:
                nfailed = nfailed + 1
                if absh <= hmin:
                    warnings.warn("ode45: ode45: IntegrationTolNotMet "+str(t)+" "+str(hmin))
                    return odefinalize(solver_name,printstats,[nsteps,nfailed,nfevals],nout,tout,yout,haveEventFcn,teout,yeout,ieout)

                    
                if nofailed:
                    nofailed = False
                    if NNrejectStep:
                        absh = max(hmin, 0.5*absh)
                    else:
                        absh = max(hmin, absh * max(0.1, 0.8 * math.pow(rtol/err,power)))
                else:
                    absh = max(hmin, 0.5*absh)
                h= tdir * absh
                done = False
            else:   
                #Successful step
                NNreset_f7 = False
                if nonNegative and any([True for i in idxNonNegative if ynew[i]<0]):
                    for j in idxNonNegative:
                        ynew[j] = max(ynew[j],0)
                        
                    if normcontrol:
                        normynew = np.linalg.norm(ynew)
                    NNreset_f7=True
                
                break
            
            
        nsteps+=1
        
        if haveEventFcn:
            te,ye,ie,valt,stop=odezero([],eventFcn,eventArgs,valt,t,np.transpose(np.array([y])),tnew,np.transpose(np.array([ynew])),t0,h,f,idxNonNegative)
            if len(te)!=0:
                if len(teout)==0:
                    teout=np.copy(te)
                else:
                    teout=np.append(teout,te)
                    
                if len(yeout)==0:
                    yeout=np.copy(ye)
                else:
                    yeout=np.append(yeout,ye,axis=1)
                
                if len(ieout)==0:
                    ieout=np.copy(ie)
                else:
                    ieout=np.append(ieout,ie)
                    
                if stop:
                    #Terminal event
                    taux = t + (te[-1] - t)*A
                    _,f[:,1:7]=ntrp45(taux,t,np.transpose(np.array([y])),h,f,idxNonNegative)
                    tnew = te[-1]
                    ynew = ye[:,-1]
                    h = tnew - t
                    done = True
                    
        
        if outputAt == "SolverSteps":
            #Computed points, no refinement
            nout_new=1
            tout_new=np.array([tnew])
            yout_new=np.transpose(np.array([ynew]))
        elif outputAt == "RefinedSteps":
            #Computed points, with refinement
            tref=t+(tnew-t)*s
            nout_new=refine
            tout_new=tref.copy()
            tout_new=np.append(tout_new,tnew)
            yout_new,_=ntrp45(tref,t,np.transpose(np.array([y])),h,f,idxNonNegative)
            yout_new=np.append(yout_new,np.transpose(np.array([ynew])),axis=1)
        elif outputAt == "RequestedPoints":
            #Chosen points
            nout_new=0
            tout_new=np.array([])
            yout_new=np.array([])
            while nex <= ntspan:
                if tdir * (tnew - tspan[nex-1]) < 0:
                    if haveEventFcn and stop:
                        nout_new=nout_new+1
                        tout_new=np.append(tout_new,tnew)
                        if len(yout_new)==0:
                            yout_new=np.transpose(np.array([ynew]))
                        else:
                            yout_new=np.append(yout_new,np.transpose(np.array([ynew])),axis=1)
                    break
                
                nout_new = nout_new + 1
                tout_new = np.append(tout_new, tspan[nex-1])
                
                if tspan[nex-1] == tnew:
                    yout_temp = np.transpose(np.array([ynew]))    
                else:
                    yout_temp,_ = ntrp45(tspan[nex-1],t,y,h,f,idxNonNegative)
                
                if len(yout_new)==0:
                    yout_new=yout_temp
                else:
                    yout_new=np.append(yout_new,yout_temp,axis=1)
                nex = nex + 1
        
        
        #Extra memory allocation
        if nout_new > 0:
            oldnout=nout
            nout=nout+nout_new
            if nout>len(tout[0]):
                talloc=np.zeros((1,chunk),dtype=dataType)
                tout=np.array([np.append(tout,talloc)])
                yalloc=np.zeros((neq,chunk),dtype=dataType)
                yout=np.append(yout,yalloc,axis=1)
            for i in range(oldnout,nout):
                tout[0,i] = tout_new[i-oldnout]
                yout[:,i] = yout_new[:,i-oldnout]
            
        
        if done:
            break
        
        #No failures, compute new h
        if nofailed:
            temp = 1.25*math.pow((err/rtol),power)
            if temp > 0.2:
                absh=absh/temp
            else:
                absh=5.0*absh
                
        #Advance the integration by one step
        t=tnew
        y=ynew.copy()
        
        if normcontrol:
            normy=normynew
        
        if NNreset_f7:
            f[:,6]=feval(odeFcn,tnew,ynew,odeArgs)
            nfevals = nfevals+1
        f[:,0]=f[:,6]
        
    
    return odefinalize(solver_name,printstats,[nsteps,nfailed,nfevals],nout,tout,yout,haveEventFcn,teout,yeout,ieout)

