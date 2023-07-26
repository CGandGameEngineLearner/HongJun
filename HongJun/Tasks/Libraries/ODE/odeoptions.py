import numpy as np
import numbers as num
from inspect import signature


def odeoptions(options, t, y, varargin):
    
    '''Options helper function for ode45, verifies the options adhear to the sepcifications,
    otherwise an error is raised.
        
    Parameters
    ----------
    options : dictionary
        Options, see ode45 sepifications for more information.
    t : float
        Initial time.
    y : array_like, shape(n,)
        Initial values.
    varargin : array_like, shape(k,)
        Extra arguments for the ode function. 
    '''
    
    #Verify options is a dictionary
    if type(options) != type({}):
        raise TypeError("odeoptions: options is not a dictionary")
    
    #Iterate through all options      
    for (key,value) in options.items():
        
        #Verify RelTol, InitialStep, and MaxStep are positive numbers
        if key == 'RelTol' or key == 'InitialStep' or key == 'MaxStep':
            if isinstance(value,float) or isinstance(value,int):
                if value <= 0:
                    raise ValueError("odeoptions: " + str(key) + ": int/float must be positive")            
            else:
                raise TypeError('odeoptions: ' + str(key) + ': must be a positive int/float')


        #Verify AbsTol is a positive numbers or a list of positive number
        elif key == 'AbsTol':
            if isinstance(value,float) or isinstance(value,int):
                if value < 0:
                    raise ValueError('odeoptions: AbsTol: int/float must be positive')
            elif isinstance(value,list):
                if len(value) != len(y):
                    raise IndexError('odeoptions: AbsTol: list/ndarray must have the length as y0')
                else:
                    for i in value:
                        if isinstance(i,float) or isinstance(i,int):
                            if i < 0:
                                raise ValueError('odeoptions: AbsTol: list must have all elements be positive')
                        else:
                            raise TypeError('odeoptions: AbsTol: list must be have all elements be positive int/float')
            else:
                raise TypeError('odeoptions: AbsTol: must a int/float or list of int/float')
          
            
        #Verify NormControl and Stats are either 'on' or 'off'
        elif key == 'NormControl' or key == 'Stats':
            if value != 'on' and value != 'off':
                raise ValueError('odeoptions: ' + str(key) + ': must either be \'on\' or \'off\'')
        
        
        #Verify NonNegative is a list of indices
        elif key == 'NonNegative':
            if isinstance(value,list):
                for i in value:
                    if isinstance(i,int):
                        if i >= len(y) or i < 0:
                            raise IndexError('odeoptions: NonNegative: elements must be ints indicating an index of y')
                    else:
                        raise TypeError('odeoptions: NonNegative: list must only contain ints')   
            else:
                raise TypeError('odeoptions: NonNegative: must be a list')
                
        
        #Verify Refine is a positive integer       
        elif key == 'Refine':
            if isinstance(value,int):
                if value < 1:
                    raise ValueError('odeoptions: Refine: must be a positive integer')
            else:
                raise TypeError('odeoptions: Refine: must be a postive integer')
                    
        
        #Verify Events is an event function
        elif key == 'Events':
            if not callable(value):
                raise TypeError('odeoptions: Events: must be a function')
            else:
                vnew,isterminal,direction = value(t,y,*varargin)
                if not isinstance(vnew,list) or not isinstance(isterminal,list) or not isinstance(direction,list):
                    raise ValueError('odeoptions: Event: must output vnew,isterminal,direction of type list')
                else:
                    size = len(vnew)
                    if len(isterminal) != size or len(direction) != size:
                        raise ValueError('odeoptions: Event: must output vnew,isterminal,direction with same length as y')
                    for i in range(size):
                        if not isinstance(vnew[i],float) and not isinstance(vnew[i],int):
                            raise ValueError('odeoptions: Event: vnew must be int/float')
                        if isterminal[i] != 1 and isterminal[i] != 0:
                            raise ValueError('odeoptions: Event: isterminal must be either 1 or 0')
                        if direction[i] != 1 and direction[i] != 0 and direction[i] != -1:
                            raise ValueError('odeoptions: Event: direction must be either 0, 1 or -1')
                
        
        #Verify Mass is a mass function or square matrix
        elif key == 'Mass':
            if callable(value):
                sig = signature(value)
                if len(sig.parameters) == 2 + len(varargin):
                    mass = value(t,y,*varargin)   
                elif len(sig.parameters) == 1 + len(varargin):
                    mass = value(t,*varargin)
                else:
                    raise Exception('odeoptions: Mass: function must either be time dependent or state/time dependent')
            else:
                mass = value
            
            if isinstance(mass,list) or isinstance(mass,np.ndarray):
                if len(mass) == len(y):
                    for i in mass:
                        if not isinstance(i,list) and not isinstance(i,np.ndarray):
                            raise TypeError('odeoptions: Mass: function must return a square matrix of type list/ndarray')
                        if len(i) != len(y):
                            raise TypeError('odeoptions: Mass: function must return a square matrix with size same as length of y')
                        for j in i:
                            if not isinstance(j,num.Number):
                                raise ValueError('odeoptions: Mass: matrix must have elements of type int/float')
                            
                else:
                    raise TypeError('odeoptions: Mass: function must return a square matrix with size same as length of y')
            else:
                raise TypeError('odeoptions: Mass: function must return a square matrix of type list/ndarray')
                              
        
        #Verify MStateDependence 
        elif key == 'MStateDependence':
            if value != 'none' and value != 'weak':
                raise ValueError('odeoptions: MStateDependence: must either be \'none\' or \'weak\'')
                
            
        else:
            raise TypeError('odeoptions: ' + str(key) + ' is not a supported option')

        
        