import matplotlib.pyplot as plt
import numpy as np
import math
import scipy.integrate as integrate

from DroneMissions.ODE.ode import ode45


def simple_demo(width=8,height=6,font=12):
    
    plt.figure()
    fig = plt.gcf()
    fig.set_size_inches(width, height)
    plt.rcParams.update({'font.size': font})
    
    def dydt(t,y):
        return [np.cos(t)]
    
    tspan = [0,10]
    y0 = [1]
    
    r = ode45(dydt,tspan,y0)
    plt.plot(r.tout,r.yout[0])
    
    plt.title('Solution for y\'(t) = cos(t) with y(0) = 1 for t = {0,10}')
    plt.xlabel('t')
    plt.ylabel('y')



def backwards_tspan_demo(width=8,height=6,font=12):

    plt.figure()
    fig = plt.gcf()
    fig.set_size_inches(width, height)
    plt.rcParams.update({'font.size': font})
    
    def dydt(t,y):
        return [np.cos(t)]
    
    tspan = [10,0]
    y0 = [1]

    r = ode45(dydt,tspan,y0)
    plt.plot(r.tout,r.yout[0])
    
    plt.title('Solution for y\'(t) = cos(t) with y(0) = 1 for t = {10,0}')
    plt.xlabel('t')
    plt.ylabel('y')
   


def multiple_initial_conditions_demo(width=8,height=6,font=12):

    plt.figure()
    fig = plt.gcf()
    fig.set_size_inches(width, height)
    plt.rcParams.update({'font.size': font})
    
    def dydt(t,y):
        return [y[0]*math.cos(t),y[1]*math.cos(t),y[2]*math.cos(t),y[3]*math.cos(t),y[4]*math.cos(t)]
    
    tspan = [0,10]
    y0 = [1,2,3,4,5]
    
    r = ode45(dydt,tspan,y0)
    plt.plot(r.tout,r.yout[0])
    plt.plot(r.tout,r.yout[1])
    plt.plot(r.tout,r.yout[2])
    plt.plot(r.tout,r.yout[3])
    plt.plot(r.tout,r.yout[4])
    
    plt.title('Solution for y\'(t) = y * cos(t) with y(0) = 1,2,3,4,5 for t = {0,10}')
    plt.xlabel('t')
    plt.ylabel('y')



def bouncing_ball_demo(width=8,height=6,font=12):
    
    plt.figure()
    fig = plt.gcf()
    fig.set_size_inches(width, height)
    plt.rcParams.update({'font.size': font})
    
    def events(t,y):
        value = [y[0]]
        isterminal = [1]
        direction = [-1]
        return value,isterminal,direction
    
    options={'Events':events,'NormControl':'on','Refine':10}

    tspan=[0,30]
    tstart=0
    y0 = [0, 20]
    
    def dydt(t,y):
        return [y[1],-9.8]
    
    t=np.array([])
    y=np.array([])
    te=np.array([])
    ye=np.array([])
    
    for i in range(10):
        tspan=[tstart,30]
        r=ode45(dydt,tspan,y0,options)
        n=len(r.tout)
        y0[1]=0.9*y0[1]
        t=np.append(t,r.tout)
        y=np.append(y,r.yout[0])
        te=np.append(te,r.teout)
        ye=np.append(ye,r.yeout[0])
        tstart=r.tout[n-1]
    
    plt.plot(t,y)
    plt.scatter(te,ye,color='r')
    plt.title('Bouncing Ball Trajectory')
    plt.xlabel('Time (s)')
    plt.ylabel('Height (cm)')



def nonnegative_demo(width=8,height=6,font=12):
    
    plt.figure()
    fig = plt.gcf()
    fig.set_size_inches(width, height)
    plt.rcParams.update({'font.size': font})
    
    def dydt(t,y):
        return [-1,-t,-t*t]
    
    options={'NonNegative':[0,1,2]}
    tspan=[0,3]
    y0=[1,2,3]
    
    r=ode45(dydt,tspan,y0,options)
    plt.plot(r.tout,r.yout[0],label='y\'(t) = -1')
    plt.plot(r.tout,r.yout[1],label='y\'(t) = -t')
    plt.plot(r.tout,r.yout[2],label='y\'(t) = -t^2')
    
    
    plt.legend()
    plt.title('Non-Negative solutions')
    plt.xlabel('t')
    plt.ylabel('y')



def mass_demo(width=8,height=6,font=12):
    
    plt.figure()
    fig = plt.gcf()
    fig.set_size_inches(width, height)
    plt.rcParams.update({'font.size': font})
    
    
    def mass(t):
        return [[t+1,-1],[1,t+1]]
    
    def dydt(t,y):
        return [ math.cos(t),1]
    
    options={'Mass':mass,'MStateDependence':'none'}
    y0=[0,0] 
    tspan = [0,10]
    
    r = ode45(dydt,tspan,y0,options)
    plt.plot(r.tout,r.yout[0])
    plt.plot(r.tout,r.yout[1])

    plt.title('Mass demo')
    plt.xlabel('t')
    plt.ylabel('y')



def choosen_points_demo(width=8,height=6,font=12):
    
    plt.figure()
    fig = plt.gcf()
    fig.set_size_inches(width, height)
    plt.rcParams.update({'font.size': font})
    
    def dydt(t,y):
        return [y[0]*np.cos(t),y[1]*np.cos(t),y[2]*np.cos(t)]
    
    tspan = np.linspace(0,10,num=101)
    y0 = [1,2,3]
    
    r = ode45(dydt,tspan,y0)
    plt.plot(r.tout,r.yout[0])
    plt.plot(r.tout,r.yout[1])
    plt.plot(r.tout,r.yout[2])
    
    plt.title('Trigonometric functions with chosen points')
    plt.xlabel('t')
    plt.ylabel('y')
    
   
    
def absolute_tolerance_demo(width=8,height=6,font=12):
    
    plt.figure()
    fig = plt.gcf()
    fig.set_size_inches(width, height)
    plt.rcParams.update({'font.size': font})
    
    def dydt(t,y):
        return [math.cos(t),math.sin(t)]
    
    option={'AbsTol':[2.1e-6,4.5e-8]}
    r = ode45(dydt,[0,10],[1,0],option)
    plt.plot(r.tout,r.yout[0])
    plt.plot(r.tout,r.yout[1])



def refine_demo_1(width=8,height=6,font=12):
    
    plt.figure()
    fig = plt.gcf()
    fig.set_size_inches(width, height)
    plt.rcParams.update({'font.size': font})
    
    def dydt(t,y):
        return [np.cos(t),np.sin(t)]
    
    options={'Refine':20}
    r = ode45(dydt,[0,10],[1,0],options)
    plt.plot(r.tout,r.yout[0],'b',label = 'refine = 1')
    
    options={'Refine':1}
    r2 = ode45(dydt,[0,10],[1,0],options)
    plt.plot(r2.tout,r2.yout[0],'r',label='refine = 10')
    plt.plot(r.tout,r.yout[1],'b',label = 'refine = 1')
    plt.plot(r2.tout,r2.yout[1],'r',label='refine = 10')
    
    plt.title('Refinement demo')
    plt.xlabel('t')
    plt.ylabel('y')
    plt.legend(['refine = 20','refine = 1'])
    
    
    
def refine_demo_2(width=8,height=6,font=12):
    
    plt.figure()
    fig = plt.gcf()
    fig.set_size_inches(width, height)
    plt.rcParams.update({'font.size': font})
    
    def dydt(t,y):
        return [np.cos(t)]
    
    options={'Refine':4}
    
    r = ode45(dydt,[0,5],[1],options)
    plt.plot(r.tout[12:21],r.yout[0,12:21],'b')
    
    options={'Refine':1}
    r2 = ode45(dydt,[0,5],[1],options)
    
    plt.plot(r2.tout[3:6],r2.yout[0,3:6],'r')
   
    plt.vlines(x=1.2009509145207664,ymin=1.8,  ymax=1.9323832558773466, colors='r',linestyles='dashed', alpha=0.7)
    plt.vlines(x=1.3259509145207664,ymin=1.8,  ymax=1.970175241884764, colors='b',linestyles='dashed', alpha=0.5)
    plt.vlines(x=1.4509509145207664,ymin=1.8,  ymax=1.9928273192095607, colors='b',linestyles='dashed', alpha=0.5)
    plt.vlines(x=1.5759509145207664,ymin=1.8,  ymax=1.9999866178575545, colors='b',linestyles='dashed', alpha=0.5)
    plt.vlines(x=1.7009509145207664,ymin=1.8,  ymax=1.9915418852636042, colors='r',linestyles='dashed', alpha=0.7)
    plt.vlines(x=1.8259509145207664,ymin=1.8,  ymax=1.9676234949145097, colors='b',linestyles='dashed', alpha=0.5)
    plt.vlines(x=1.9509509145207664,ymin=1.8,  ymax=1.9286072692934104, colors='b',linestyles='dashed', alpha=0.5)
    plt.vlines(x=2.0759509145207664,ymin=1.8,  ymax=1.8751005881572886, colors='b',linestyles='dashed', alpha=0.5)
    plt.vlines(x=2.2009509145207664,ymin=1.8,  ymax=1.8079364922709038, colors='r',linestyles='dashed', alpha=0.7) 
    plt.xticks([1.2009509145207664,1.7009509145207664,2.2009509145207664])
    
    plt.title('Solution for y\'(t) = cos(t) for t = {0,5}')
    plt.xlabel('t')
    plt.ylabel('y')
    plt.legend(['refine = 4','refine = 1','Step','Interpolation'])
    


def orbit_demo(width=8,height=6,font=12):
    
    plt.figure()
    fig = plt.gcf()
    fig.set_size_inches(width, height)
    plt.rcParams.update({'font.size': font})
    
    def dydt(t,y):
        mu=1/82.45
        mustar=1-mu
                
        r13 = math.pow(((y[0]+mu)*(y[0]+mu) + y[1]*y[1]), 1.5)
        r23 = math.pow(((y[0]-mustar)*(y[0]-mustar) + y[1]*y[1]), 1.5)
        
        x1=y[2]
        x2=y[3]
        x3=2*y[3] + y[0] - mustar*((y[0]+mu)/r13) - mu*((y[0]-mustar)/r23)
        x4=-2*y[2] + y[1] - mustar*(y[1]/r13) - mu*(y[1]/r23)
        return [x1,x2,x3,x4]    
    
    def events(t,y):
        y0 = [1.2, 0, 0, -1.04935750983031990726]
        dDSQdt = 2*(((y[0]-y0[0])*y[2])+((y[1]-y0[1])*y[3]))
        value = [dDSQdt,dDSQdt]
        isterminal = [1,0]
        direction = [1,-1]
        return [value,isterminal,direction]
    
    y0 = [1.2,0,0,-1.04935750983031990726]
    tspan = [0,7]
    options = {'Events':events,'RelTol':1e-5,'AbsTol':1e-4}
    
    r = ode45(dydt,tspan,y0,options)
    plt.plot(r.yout[0],r.yout[1])
    plt.scatter(r.yeout[0],r.yeout[1],color='r')
    
    plt.title('Restricted three body problem')
    plt.xlabel('x')
    plt.ylabel('y')



def adaptive_step_demo(width,height,font):
    
    plt.figure()
    fig = plt.gcf()
    fig.set_size_inches(width, height)
    plt.rcParams.update({'font.size': font})
    
    options = {'Refine':1}
    def dydt(t,y):
        return [-1*y[0] + 10*np.exp(-1*(t-2)*(t-2)/0.002)]
    
    r = ode45(dydt,[1,4],[0.5],options)
    r2 = ode45(dydt,[1,4],[0.5])
    plt.plot(r2.tout,r2.yout[0])
    plt.vlines(r.tout,ymin=0,ymax=r.yout[0],colors='b',linestyles='dashed', alpha=0.5)
    
    plt.legend(['y(t)','Steps'])
    plt.title('Solution for y\'(t) = -y(t) + 10e^(-(t-2)^2/0.002) for t = {1,4}')
    plt.xlabel('t')
    plt.ylabel('y')



def solveivp_demo(width,height,font):
    
    plt.figure()
    fig = plt.gcf()
    fig.set_size_inches(width, height)
    plt.rcParams.update({'font.size': font})
    
    def dydt(t,y):
        return [-y[0]+np.cos(t)]
    
    tspan = np.linspace(0,15,100)
    res = integrate.solve_ivp(dydt,[0,15],[10],t_eval=tspan)
    plt.plot(res.t,res.y[0])
    
    plt.title('Solution of y\' = y + cos(t), y(0)=10 using solve_ivp')
    plt.xlabel('t')
    plt.ylabel('y')
        


def lorenz_demo():
    fig = plt.figure()
    fig.set_size_inches(15, 12)
    fig.patch.set_alpha(1)
    ax = fig.gca(projection='3d')
    
    sigma = 10.
    rho = 28.
    beta = 8./3.
    x0 = [0,1,2]
    dt=0.001
    
    def lorenz(t,y):
        A = np.array([[-1*beta,0,y[1]],[0,-1*sigma,sigma],[-1*y[1],rho,-1]])
        y=np.transpose(np.array([y]))
        return np.transpose(np.matmul(A,y))[0]
    
    tspan = np.linspace(dt,50,50000)
    options={'RelTol':1e-12,'AbsTol':1e-12}
    
    r = ode45(lorenz,tspan,x0,options)
    ax.plot(r.yout[0],r.yout[1],r.yout[2])
    
    ax.patch.set_facecolor('white')
    ax.grid(False)
    plt.show()


    
if __name__ == "__main__":
    
    width = 8
    height = 6
    font = 12
    
    #Series of demos to illustrate the use and options of ode45
    simple_demo(width,height,font)
    backwards_tspan_demo(width,height,font)
    multiple_initial_conditions_demo(width,height,font)
    bouncing_ball_demo(width,height,font)
    nonnegative_demo(width,height,font)
    mass_demo(width,height,font)
    choosen_points_demo(width,height,font)
    refine_demo_1(width,height,font)
    refine_demo_2(width,height,font)
    orbit_demo(width,height,font)
    adaptive_step_demo(width,height,font)
    solveivp_demo(width,height,font)
    lorenz_demo()
    
