from typing import Any

import cvxpy as cp
import numpy as np

from HongJun.Tasks.Libraries.ODE.ode import ode45

Float64NDarray = np.ndarray[Any, np.dtype[np.float32]]
ComplexNDarray = np.ndarray[Any, np.dtype[np.complex64]]
par = None
axi = 0

def PlaneSys_Ver3_2(
    _, state
):
    """
    该函数定义了一个平面上的多无人机系统模型, 该模型包含了多个无人机在平面上的运动模型, 并对每个无人机进行控制, 以使得无人机最终能够以预定的形态排列在平面上.
    :param t: 时间.
    :param state: 模型的状态向量, 长度为3n, 其中前2n个元素是每个无人机的二维位置坐标, 后n个元素是每个无人机的角度.
    :param par: 模型参数的字典.
        - n: int, 无人机的数量.
        - A: numpy.ndarray, 维度为(2n, 2n), 表示多无人机系统形态控制的增益矩阵.
        - p: numpy.ndarray, 维度为(2, 1) ,表示期望速度的方向.
        - vSat: numpy.ndarray, 维度为(1, 2), 表示速度的最大值和最小值.
        - omegaSat: numpy.ndarray, 维度为(1, 2), 表示角速度的最大值和最小值.

    :return: numpy.ndarray, 维度为(1, 3n), 前2n个元素是每个无人机的位置, 后n个元素是角度变化率.
    """
    _A = par["A"]  # Control gain matrix
    n = par["n"]  # Number of agents
    omega_sat = par[
        "omegaSat"
    ]  # Heading angle saturation
    v_sat = par["vSat"]  # Speed saturation
    p_i = par["p"]  # Desired direction of motion

    q = state[: 2 * n]  # Position vector
    theta = state[2 * n : 3 * n]  # Heading

    _H = np.zeros((2 * n, n), dtype=np.longdouble)  # Heading matrix
    _H_p = np.zeros((2 * n, n), dtype=np.longdouble)  # Perpendicular heading matrix
    _R = np.array([[0, -1], [1, 0]], dtype=np.longdouble)  # 90 degree roation matrix


    h = np.vstack((np.cos(theta), np.sin(theta))).T.flatten()

    for i in range(n):
        _H[2 * i : 2 * i + 2, i] = h[2 * i : 2 * i + 2]
        _H_p[2 * i : 2 * i + 2, i] = _R @ h[2 * i : 2 * i + 2]

    # Constant speed
    p = np.mean(v_sat) * np.tile(p_i, (n, 1))
    # print("_A",_A)
    
    # Speed limiter
    v_ctrl = (_H.T @ _A @ q).reshape((-1, 1))
    v_sat_mean = np.mean(v_sat)
    v_min = np.ones_like(v_ctrl, dtype=np.longdouble) * (v_sat[0] - v_sat_mean)
    v_max = np.ones_like(v_ctrl, dtype=np.longdouble) * (v_sat[1] - v_sat_mean)
    v_ctrl = np.maximum(v_ctrl, v_min)
    v_ctrl = np.minimum(v_ctrl, v_max)

    # print(v_ctrl.shape)

    # Heading angle rate of change limiter
    omega_ctrl = (_H_p.T @ _A @ q).reshape((-1, 1))
    omega_min = np.ones_like(omega_ctrl, dtype=np.longdouble) * omega_sat[0]
    omega_max = np.ones_like(omega_ctrl, dtype=np.longdouble) * omega_sat[1]
    omega_ctrl = np.maximum(omega_ctrl, omega_min)
    omega_ctrl = np.minimum(omega_ctrl, omega_max)

    # Control
    v: Float64NDarray = _H.T @ p + v_ctrl
    omega: Float64NDarray = _H_p.T @ p + omega_ctrl

    # Speed limiter
    v_min: Float64NDarray = np.ones_like(v, dtype=np.longdouble) * v_sat[0]
    v_max: Float64NDarray = np.ones_like(v, dtype=np.longdouble) * v_sat[1]
    v: Float64NDarray = np.maximum(v, v_min)
    v: Float64NDarray = np.minimum(v, v_max)

    # Heading angle rate of change limiter
    omega_min: Float64NDarray = np.ones_like(omega, dtype=np.longdouble) * omega_sat[0]
    omega_max: Float64NDarray = np.ones_like(omega, dtype=np.longdouble) * omega_sat[1]
    omega: Float64NDarray = np.maximum(omega, omega_min)
    omega: Float64NDarray = np.minimum(omega, omega_max)

    # Derivative of state
    d_q = _H @ v
    d_theta = omega
    d_state = np.concatenate([d_q, d_theta], axis=0, dtype=np.longdouble)

    # print('_H', _H)
    # print(d_state.flatten())

    global axi
    axi += 1
    # print(axi)

    return d_state.flatten()


def convert_complex_to_real(_A_c):
    """
    将一个复数矩阵转换为实数矩阵.
    :param _A_c: 维度为(n, n)的复数矩阵.
    :return: numpy.ndarray, 维度为(2n, 2n)的实数矩阵.
    """
    n = _A_c.shape[0]
    _A_r: Float64NDarray = np.zeros((2 * n, 2 * n), dtype=np.longdouble)
    for i in range(n):
        for j in range(n):
            elem: np.complex128 = _A_c[i, j]
            _A_r[2 * i : 2 * i + 2, 2 * j : 2 * j + 2] = np.array(
                [[elem.real, -elem.imag], [elem.imag, elem.real]]
                , dtype=np.longdouble
            )
    # print('A', _A_r)
    return _A_r

def find_gains(qs, adj):
    """
    计算多无人机系统形态控制的增益矩阵.
    :param qs: 维度为(1, 2n), 包含了每个无人机期望的形态坐标.
    :param adj: 维度为(n, n), 表示无人机之间的连接关系.
    :return: numpy.ndarray, 维度为(2n, 2n)的实数矩阵, 表示多无人机系统形态控制的增益矩阵.
    """
    # Number of agents
    n = adj.shape[0]

    # Complex representation of desired formation coordinates
    p = qs[0::2]
    q = qs[1::2]
    z = p + 1j * q

    z = np.array(z, dtype=np.clongdouble)

    # print(z)

    # Get orthogonal complement of [z ones(n,1)]
    _U, _, _ = np.linalg.svd(
        np.concatenate((z.reshape(-1, 1), np.ones((n, 1), dtype=np.longdouble)), axis=1)
    )
    _Q = _U[:, 2:n]
    # print("_Q",_Q)

    # Subspace constraint for the given graph
    # _S = np.logical_not(adj)
    # np.fill_diagonal(_S, 0)
    
    # S = not(adj);
    # S = S - diag(diag(S));
    _S = 1 - adj
    _S = _S - np.diag(np.diag(_S))
    
    #print("qs",qs)
    #print("p", p)
    #print("q", q)
    #print("z", z)
#    print("C", C)
    #print("_S",_S)
    #print("_Q",_Q)

    _A = cp.Variable((n,n), hermitian=True)
    objective = cp.Maximize(cp.lambda_min(_Q.conj().T@_A@_Q))
    constraints = [
        _A @ np.hstack([z[:, np.newaxis], np.ones((n, 1), dtype=np.longdouble)]) == 0+1j*0, 
        cp.norm(_A) <= 10, 
        cp.multiply(_A,_S) == 0
    ]
    problem = cp.Problem(objective, constraints)
    result = problem.solve()
    _A_c = -_A.value  # Complex gain matrix
    _A_r = convert_complex_to_real(_A_c)  # Real represnetation of gain matrix
    #print("A_c", _A_c)
    #print("A_r,===========", _A_r)
    return _A_r


# TODO: 矩阵依据n来生成
def control_formation(init_pos):
    """
    无人机编队控制函数.
    :param init_pos: 维度为(2, n), 包含了每个无人机初始坐标.
    :return: numpy.ndarray, 维度为(1, 3n), 前2n个元素是每个无人机的位置, 后n个元素是角度变化率.
    """
    # Desired formation coordinates
    qs =  np.array(
            [
                [0, 2, 2, 4, 4, 4, 6,6, 6, 6],
                [0, -1, 1, -2, 0, 2, -3, -1, 1, 3],
            ], dtype=np.longdouble
        )* np.sqrt(5) * 2

   # print("qsorigin",qs)
    # Random initial positions
    q0 = init_pos

    # Random initial heading angles
    # theta0 = np.array( [0  ,  0  ,  0 ,   0 ,   0 ,   0], dtype=np.longdouble).T
    theta0 = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.longdouble).T
    n = qs.shape[1]  # Number of agents

    # Graph adjacency matrix
    adj = np.array(
        [
            [0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 1, 1, 1, 0, 0, 0, 0, 0],
            [1, 1, 0, 0, 1, 1, 0, 0, 0, 0],
            [0, 1, 0, 0, 1, 0, 1, 1, 0, 0],
            [0, 1, 1, 1, 0, 1, 0, 1, 1, 0],
            [0, 0, 1, 0, 1, 0, 0, 0, 1, 1],
            [0, 0, 0, 1, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 1, 1, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 1, 1, 0, 1, 0, 1],
            [0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
        ],dtype=np.longdouble
    )

    # Parameters
    _T = [0., 12.]  # Simulation time interval
    v_sat = np.array([3., 5.], dtype=np.longdouble)  # Speed range
    omega_sat = np.array([-np.pi / 4., np.pi / 4.], dtype=np.longdouble)  # Allowed heading angle rate of change
    p = np.array([[-1.], [0.]], dtype=np.longdouble)  # Desired travel direction

    ## Computing formation control gains
    # Find stabilizing control gains (Needs CVX)
    # print("flatten",qs.T.flatten())
    _A = find_gains(qs.T.flatten(), adj)
    
    # If optimization failed, perturbe 'qs' slightly:
    # Simulate the model
    _T_vec = np.linspace(_T[0], _T[1], 50)
    state0 = np.hstack((q0.T.flatten(), theta0))  # Initial state


    _T_span = (_T[0], _T[1])

    # print("======_T_vec=========", _T_vec)
    # print("====state0========", state0)
    
    # Parameters passed down to the ODE solver
    global par

    par = {"n": n, "A": _A, "p": p, "vSat": v_sat, "omegaSat": omega_sat}


    # xxx = state0
    # for i in range(50):
    # 	yyy = PlaneSys_Ver3_2(None, xxx)
    # 	print('State ', i, yyy)
    # 	xxx = yyy

    # 1129
    
    # Simulate the dynamic system

    res = ode45(
        PlaneSys_Ver3_2,
        _T_vec,
        state0,
        options={'AbsTol':1e-6, 'RelTol':1e-6}
    )

    print("=====state_mat+++++", res.get_y().T)
    state_mat = res.get_y().T
    return state_mat

# control_formation()
