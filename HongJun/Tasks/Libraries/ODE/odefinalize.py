

class odefinalize:

    def __init__(self, solver, printstats, statsvec, nout, tout, yout, haveeventfun, teout, yeout, ieout):
    
        '''Class to create an object with the solutions of the ode45 integration.
            
        Parameters
        ----------
        solver : string
            Name of the solver used.
        printstats : boolean
            Boolean determining whether this function should print stats of the integration 
            process. These stats are the number of successful steps, the number of failed 
            steps, and the number of functions evaluated.
        statsvec : array_like, shape(3,)
            Array containing number of successful steps, the number of failed steps, and the
            number of functions evaluated.
        nout : integer
            Number of point evaluated during the integration process.
        tout : ndarray, shape(1,m)
            Array containing all the points t evaluated. This array is larger or equal to the
            number of points actually evaluated (m >= nout), the rest contains zeros.
        yout : ndarray, shape(n,m)
            Array containing all the results of the evaluation for the points in tout. This 
            array is larger or equal to the number of points actually evaluated (m >= nout),
            the rest contains zeros.
        haveeventfun : boolean
            Boolean determining whether there was an event function passed as option.
        teout : ndarray, shape(k,)
            Array containing the t points with an event.
        yeout : ndarray, shape(n,k)
            Array containing the evaluated values for all teout points with an event.
        ieout : ndarray, shape(k,)
            Array containing the indices of yeout values with an event.
    
        '''
        
        self.solver=solver
        self.nout=nout
        self.tout=tout[0,0:nout]
        self.yout=yout[:,0:nout]
        self.teout=teout
        self.yeout=yeout
        self.ieout=ieout
        
        if printstats:
            print("ode45:odefinalize:LogSuccessfulSteps      "+str(statsvec[0]))
            print("ode45:odefinalize:LogFailedAttempts       "+str(statsvec[1]))
            print("ode45:odefinalize:LogFunctionEvaluations  "+str(statsvec[2]))
        
        self.statsvec=statsvec
        self.haveeventfun=haveeventfun
    
    def get_solver(self):
        return self.solver
    
    def get_size(self):
        return self.nout
    
    def get_ty(self):
        return self.tout,self.yout
    
    def get_t(self):
        return self.tout
    
    def get_y(self):
        return self.yout
    
    def get_events(self):
        return self.teout, self.yeout, self.ieout
    
    def get_stats(self):
        return self.statsvec
    
    def has_events(self):
        return self.haveeventfun
    
    