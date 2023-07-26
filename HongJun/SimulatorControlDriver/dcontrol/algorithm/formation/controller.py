from typing import Any

import cvxpy as cvx
import numpy as np
from scipy.integrate import odeint, solve_ivp

LongDoubleNDarray = np.ndarray[Any, np.dtype[np.longdouble]]
ComplexNDarray = np.ndarray[Any, np.dtype[np.complex128]]


def calc_drone_new_state(
    t: float, state: LongDoubleNDarray, par: dict[str, Any]
) -> LongDoubleNDarray:
    print(f"calc {t}")
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
    _A: LongDoubleNDarray = par["A"]  # Control gain matrix
    n: int = par["n"]  # Number of agents
    omega_sat: tuple[np.longdouble, np.longdouble] = par[
        "omegaSat"
    ]  # Heading angle saturation
    v_sat: tuple[np.longdouble, np.longdouble] = par["vSat"]  # Speed saturation
    p_i: LongDoubleNDarray = par["p"]  # Desired direction of motion

    state = state.reshape((-1, 1))
    q: LongDoubleNDarray = state[: 2 * n]  # Position vector
    theta: LongDoubleNDarray = state[2 * n : 3 * n]  # Heading

    _H: LongDoubleNDarray = np.zeros((2 * n, n), dtype=np.longdouble)  # Heading matrix
    _H_p: LongDoubleNDarray = np.zeros(
        (2 * n, n), dtype=np.longdouble
    )  # Perpendicular heading matrix
    _R: LongDoubleNDarray = np.array(
        [[0, -1], [1, 0]], dtype=np.longdouble
    )  # 90 degree roation matrix

    # h: Float64NDarray = np.vstack([np.cos(theta).T, np.sin(theta).T])
    # h: Float64NDarray = h.reshape((-1,1)).flatten()
    # h = np.vstack([np.cos(theta), np.sin(theta)]).T.flatten()
    h = np.array([np.cos(theta), np.sin(theta)], dtype=np.longdouble).T
    h = h.reshape((-1, 1), order="F")
    # h = h.T.flatten().reshape((-1,1))

    for i in range(n):
        _H[2 * i : 2 * i + 2, i] = h[2 * i : 2 * i + 2].flatten()
        _H_p[2 * i : 2 * i + 2, i] = (_R @ h[2 * i : 2 * i + 2]).flatten()

    # Constant speed
    p: LongDoubleNDarray = np.mean(v_sat, dtype=np.longdouble) * np.tile(p_i, (n, 1))

    # Speed limiter
    # v_ctrl: Float64NDarray = (_H.T @ _A @ q).reshape((-1, 1))
    v_ctrl: LongDoubleNDarray = _H.T @ _A @ q
    v_sat_mean: np.longdouble = np.mean(v_sat, dtype=np.longdouble)
    v_min: LongDoubleNDarray = np.ones_like(v_ctrl, dtype=np.longdouble) * (
        v_sat[0] - v_sat_mean
    )
    v_max: LongDoubleNDarray = np.ones_like(v_ctrl, dtype=np.longdouble) * (
        v_sat[1] - v_sat_mean
    )
    v_ctrl: LongDoubleNDarray = np.maximum(v_ctrl, v_min, dtype=np.longdouble)
    v_ctrl: LongDoubleNDarray = np.minimum(v_ctrl, v_max, dtype=np.longdouble)

    # Heading angle rate of change limiter
    # omega_ctrl: Float64NDarray = (_H.T @ _A @ q).reshape((-1, 1))
    omega_ctrl: LongDoubleNDarray = _H.T @ _A @ q
    omega_min: LongDoubleNDarray = (
        np.ones_like(omega_ctrl, dtype=np.longdouble) * omega_sat[0]
    )
    omega_max: LongDoubleNDarray = (
        np.ones_like(omega_ctrl, dtype=np.longdouble) * omega_sat[1]
    )
    omega_ctrl: LongDoubleNDarray = np.maximum(
        omega_ctrl, omega_min, dtype=np.longdouble
    )
    omega_ctrl: LongDoubleNDarray = np.minimum(
        omega_ctrl, omega_max, dtype=np.longdouble
    )

    # Control
    v: LongDoubleNDarray = _H.T @ p + v_ctrl
    omega: LongDoubleNDarray = _H_p.T @ p + omega_ctrl

    # Speed limiter
    v_min: LongDoubleNDarray = np.ones_like(v, dtype=np.longdouble) * v_sat[0]
    v_max: LongDoubleNDarray = np.ones_like(v, dtype=np.longdouble) * v_sat[1]
    v: LongDoubleNDarray = np.maximum(v, v_min, dtype=np.longdouble)
    v: LongDoubleNDarray = np.minimum(v, v_max, dtype=np.longdouble)

    # Heading angle rate of change limiter
    omega_min: LongDoubleNDarray = (
        np.ones_like(omega, dtype=np.longdouble) * omega_sat[0]
    )
    omega_max: LongDoubleNDarray = (
        np.ones_like(omega, dtype=np.longdouble) * omega_sat[1]
    )
    omega: LongDoubleNDarray = np.maximum(omega, omega_min, dtype=np.longdouble)
    omega: LongDoubleNDarray = np.minimum(omega, omega_max, dtype=np.longdouble)

    # Derivative of state
    d_q = _H @ v
    d_theta = omega
    # d_state = np.concatenate([d_q, d_theta], axis=0)
    d_state = np.concatenate([d_q, d_theta], dtype=np.longdouble)
    # print(d_state)
    d_state = d_state.flatten()
    return d_state


def convert_complex_to_real(_A_c: ComplexNDarray) -> LongDoubleNDarray:
    """
    将一个复数矩阵转换为实数矩阵.
    :param _A_c: 维度为(n, n)的复数矩阵.
    :return: numpy.ndarray, 维度为(2n, 2n)的实数矩阵.
    """
    n = _A_c.shape[0]
    _A_r: LongDoubleNDarray = np.zeros((2 * n, 2 * n), dtype=np.longdouble)
    for i in range(n):
        for j in range(n):
            elem: np.longcomplex = _A_c[i, j]
            _A_r[2 * i : 2 * i + 2, 2 * j : 2 * j + 2] = np.array(
                [[elem.real, -elem.imag], [elem.imag, elem.real]], dtype=np.longdouble
            )
    return _A_r


def find_gains(qs: LongDoubleNDarray, adj: LongDoubleNDarray) -> LongDoubleNDarray:
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

    # Get orthogonal complement of [z ones(n,1)]
    _U, _, _ = np.linalg.svd(
        np.concatenate(
            (z.reshape(-1, 1), np.ones((n, 1), dtype=np.longdouble)),
            axis=1,
            dtype=np.complex128,
        )
    )
    _Q = _U[:, 2:n]

    # Subspace constraint for the given graph
    # _S = np.logical_not(adj)
    # np.fill_diagonal(_S, 0)
    _s = 1 - adj
    _S = _s - np.diag(np.diag(_s))

    # Solve via CVX
    _A = cvx.Variable((n, n), hermitian=True)
    objective = cvx.Maximize(cvx.lambda_min(_Q.T @ _A @ _Q))
    constraints: list[bool] = [
        _A
        @ np.concatenate(
            (z.reshape(-1, 1), np.ones((n, 1))), axis=1, dtype=np.complex128
        )
        == 0 + 1j * 0,
        # _A @ np.hstack([z[:, np.newaxis], np.ones((n, 1))]) == 0 + 1j * 0,
        cvx.norm(_A) <= 10,
        cvx.multiply(_A, _S) == 0,
    ]
    problem = cvx.Problem(objective, constraints)
    problem.solve()

    _A_c: ComplexNDarray = -_A.value  # Complex gain matrix
    _A_r = convert_complex_to_real(_A_c)  # Real represnetation of gain matrix

    return _A_r


# TODO: 矩阵依据n来生成
def control_formation(init_pos: LongDoubleNDarray, step: int) -> LongDoubleNDarray:
    """
    无人机编队控制函数.
    :param init_pos: 维度为(2, n), 包含了每个无人机初始坐标.
    :return: numpy.ndarray, 维度为(step, 3n), 共包含step步, 每一步包含n个无人机的xyz坐标.
    """
    # Desired formation coordinates
    # n = init_pos.shape[1]
    qs: LongDoubleNDarray = (
        np.array(
            [
                [0, -2, -2, -4, -4, -4, -6, -6, -6, -6], # 目标x
                [0, -1, 1, -2, 0, 2, -3, -1, 1, 3], # 目标y
            ],
            dtype=np.longdouble,
        )
        * np.sqrt(5)
        * 2
    )

    # Random initial positions
    q0 = init_pos

    # Random initial heading angles
    # theta0 = np.array([5.6645, 4.2256, 1.8902, 4.5136, 3.6334,
    #                     5.7688, 3.78, 4.25, 2.22, 1.37]).T
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
        ],
        dtype=np.longdouble,
    )

    # Parameters
    _T = np.array([0, 12], dtype=np.longdouble)  # Simulation time interval
    v_sat = np.array([3, 5], dtype=np.longdouble)  # Speed range
    omega_sat = np.array([-np.pi / 4.0, np.pi / 4.0], dtype=np.longdouble)  # Allowed heading angle rate of change
    p = np.array([[1], [0]], dtype=np.longdouble)  # Desired travel direction

    ## Computing formation control gains
    # Find stabilizing control gains (Needs CVX)
    _A = find_gains(qs.T.flatten().reshape((-1, 1)), adj)

    # If optimization failed, perturbe 'qs' slightly:
    # Simulate the model
    _T_vec = np.linspace(_T[0], _T[1], step, dtype=np.longdouble)
    # state0 = np.hstack((q0.T.flatten(), theta0))  # Initial state
    # state0 = np.hstack((q0.flatten().T, theta0))  # Initial state
    # state0 = np.concatenate([q0.flatten(), theta0])
    state0 = np.concatenate(
        [q0.T.flatten().reshape((-1, 1)), theta0.reshape((-1, 1))],
        axis=0,
        dtype=np.longdouble,
    )
    # Parameters passed down to the ODE solver
    par = {"n": n, "A": _A, "p": p, "vSat": v_sat, "omegaSat": omega_sat}

    # Simulate the dynamic system
    state_mat: LongDoubleNDarray = odeint(
        calc_drone_new_state,
        state0.flatten(),
        _T_vec,
        args=(par,),
        rtol=1e-6,
        atol=1e-6,
        tfirst=True,
    )
    # opt = {'rtol': 1e-6, 'atol': 1e-6}
    # sol = solve_ivp(fun=lambda t, y: calc_drone_new_state(t, y, par), t_span=(_T[0], _T[1]), y0=state0,
    #                 method='RK45', t_eval=_T_vec, rtol=opt['rtol'], atol=opt['atol'])
    # state_mat = sol.y.T
    return state_mat
