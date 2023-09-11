"""
类型模块
"""
from typing import Any, TypedDict, Union


class DroneState(TypedDict):
    """
    描述无人机状态的类
    """

    id: int  # 每个无人机唯一的ID号
    x: float  # 无人机的X坐标
    y: float  # 无人机的Y坐标
    side: int  # 无人机所属阵营 红1蓝0
    is_destroyed: int  # 无人机损毁状态
    atk_msl_num: int  # 无人机攻击类导弹的剩余数量
    def_msl_num: int  # 无人机防御类导弹的剩余数量


class DroneCommand(TypedDict):
    """
    无人机接收的指令
    """

    id: int  # 每个无人机唯一的ID号
    v_x: float  # 发给无人机的X方向速度指令
    v_y: float  # 发给无人机的Y方向速度指令


class DroneCommandJson(TypedDict):
    """
    Json
    """

    data: list[DroneCommand]


class IsStopped(TypedDict):
    """
    是否停止
    """

    is_stopped: bool


DroneDict = dict[Union[str, int], list[str]]
CmdList = list[tuple[int, float, float]]
MslMsgList = list[Union[list[str], tuple[Any, ...]]]
