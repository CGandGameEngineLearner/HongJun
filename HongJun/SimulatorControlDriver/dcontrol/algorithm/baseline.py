"""
基线算法模块
"""

import asyncio
import math
from abc import ABC, abstractmethod
from enum import Enum
from json import dumps
from math import sqrt
from random import random as get_random
from typing import Optional, TypedDict

from dcontrol.core.types import (
    DroneCommand,
    DroneDict,
    DroneState,
    IsStopped,
    MslMsgList,
)
from dcontrol.network.sender import BaseSender


class AbstractAlgorithm(ABC):
    """
    抽象类
    """

    @abstractmethod
    async def start(self) -> None:
        """
        运行算法
        """

        raise NotImplementedError


class DummyAlgorithm(AbstractAlgorithm):
    """
    算法执行类
    """

    def __init__(
        self,
        drone_dict: DroneDict,
        msl_msg_list: MslMsgList,
        is_stopped: IsStopped,
        sender: BaseSender[str],
    ):
        self.drone_dict = drone_dict
        self.msl_msg_list = msl_msg_list
        self.is_stopped = is_stopped
        self.sender = sender

    async def start(self):
        """
        运行算法
        """
        while True:
            cmd_list: list[DroneCommand] = []

            for i, (_, value) in enumerate(self.drone_dict.items()):
                # 所需的所有无人机信息均在droneDic中；key是ID，value是一个list，各个含义见DroneState的定义
                drone_state: DroneState = {
                    "id": i,
                    "x": float(value[0]),
                    "y": float(value[1]),
                    "side": int(value[2]),
                    "is_destroyed": int(value[3]),
                    "atk_msl_num": int(value[4]),
                    "def_msl_num": int(value[5]),
                }

                print(
                    f"{'R' if drone_state['side'] == 1 else 'B'}{drone_state['id']}\
                        ({'on' if drone_state['is_destroyed'] == 0 else 'off'}): \
                            ({drone_state['x']:.2f}, {drone_state['y']:.2f}), \
                                {drone_state['atk_msl_num']} atkmsl, \
                                    {drone_state['def_msl_num']} defmsl"
                )

                new_cmd: DroneCommand = {
                    "id": i,
                    "v_x": (get_random() - 0.5) * 3,  # [-1.5,1.5] M/S
                    "v_y": (get_random() - 0.5) * 3,  # [-1.5,1.5] M/S
                }
                cmd_list.append(new_cmd)

            # 打击消息存在于mslList中，数据组成为（时间、发射方、命中方）
            # 1.5, R0, B7 表示 第1.5s，R0无人机发射的攻击导弹击毁了B7无人机
            # 3.4, R3, -1 表示 第3.4s，R3无人机发射的攻击导弹被成功拦截

            for _, msl_msg in enumerate(self.msl_msg_list):
                print(msl_msg)

            # 打印仿真结束标识，当前运行90s后，存活的无人机会降落，此标识变为true
            print(f"DummyAlgo> is finnished: {self.is_stopped['is_stopped']}")
            print("==================")
            self.msl_msg_list.clear()
            # cmd_tuple = ()
            # for cmd in cmd_list:
            #     cmd_item = (cmd["id"], cmd["v_x"], cmd["v_y"])
            #     cmd_tuple = (*cmd_tuple, *cmd_item)

            json_data = {
                "data": list(
                    map(
                        lambda x: {"id": x["id"], "v_x": x["v_x"], "v_y": x["v_y"]},
                        cmd_list,
                    )
                )
            }

            if len(cmd_list) > 0:
                # struct_data = struct.Struct("I2f" * len(cmd_list)).pack(*cmd_tuple)
                # 将数据发送到SimIP的SimPort
                dumped_data = dumps(json_data) + "\n"
                await self.sender.put_data(dumped_data)

            # 发送周期客户指定是27s，测试时暂用5s
            await asyncio.sleep(2)


class DistanceDict(TypedDict):
    """
    傻逼py不能给lambda的参数做类型标注
    """

    id: int
    distance: float


class RunningStateEnum(Enum):
    """
    飞行状态枚举类喵
    """

    FLYING_TO_TARGET = 0


class DroneRunningSate(TypedDict):
    """
    记录飞行状态喵
    """

    id: int
    side: int
    state: RunningStateEnum


class DroneMachineMode(Enum):
    """
    状态机的状态喵
    """

    AVOID = 0
    ATTACK = 1
    FLEE = 2
    SINGLE_TRACE = 0


class DroneStateMachine:
    """
    执行状态机
    """

    def __init__(
        self,
        drone_state: DroneState,
        self_side_list: list[DroneState],
        opposite_side_list: list[DroneState],
    ):
        self.state = drone_state
        self.self_side_list = self_side_list
        self.opposite_side_list = opposite_side_list
        self.mode: DroneMachineMode = DroneMachineMode.ATTACK
        self.avoid_counter: int = 0
        self.attack_counter: int = 0
        self.avoid_range: float = 5.0  # 设置避障范围
        self.attack_range: float = 20.0  # 设置攻击范围
        self.flee_range: float = 2.0
        self.avoid_weight: float = 0.8  # 避障权重
        self.attack_weight: float = 0.8  # 攻击权重
        self.flee_weight: float = 0.8
        self.avoid_max_speed: float = 5.0
        self.attack_max_speed: float = 5.0
        self.flee_max_speed: float = 5.0

    def update_side_info(
        self, self_side_list: list[DroneState], opposite_side_list: list[DroneState]
    ):
        """
        更新下信息喵
        """
        self.self_side_list = self_side_list
        self.opposite_side_list = opposite_side_list

    def execute(self) -> DroneCommand:
        """
        状态机执行函数
        """
        # 先执行避障模式
        avoid_vx, avoid_vy = self.calc_avoid_velocity()
        cmd: DroneCommand = {
            "id": self.state["id"],
            "v_x": avoid_vx * self.avoid_weight,
            "v_y": avoid_vy * self.avoid_weight,
        }
        while True:
            if self.mode == DroneMachineMode.FLEE:
                self.avoid_counter += 1
                if self.avoid_counter > 10:
                    self.mode = DroneMachineMode.ATTACK
                    self.avoid_counter = 0
                else:
                    flee_cmd = self.flee()
                    cmd["v_x"] += flee_cmd["v_x"] * self.flee_weight
                    cmd["v_y"] += flee_cmd["v_y"] * self.flee_weight
                    break

            # 再执行攻击模式
            if self.mode == DroneMachineMode.ATTACK:
                self.attack_counter += 1
                if self.attack_counter > 100:
                    self.mode = DroneMachineMode.FLEE
                    self.attack_counter = 0
                else:
                    attack_cmd = self.attack()
                    cmd["v_x"] += attack_cmd["v_x"] * self.attack_weight
                    cmd["v_y"] += attack_cmd["v_y"] * self.attack_weight
                    break

        return cmd

    def calc_avoid_velocity(self) -> tuple[float, float]:
        """
        找出距离过近的其他无人机
        """
        drones = [*self.self_side_list, *self.opposite_side_list]
        near_drones = [
            d
            for d in drones
            if d["id"] != self.state["id"]
            and math.dist((d["x"], d["y"]), (self.state["x"], self.state["y"]))
            < self.avoid_range
        ]

        # 如果没有距离过近的无人机，则返回原速度
        if not near_drones:
            return 0.0, 0.0

        # 计算每个距离过近的无人机对当前无人机的斥力向量，并将所有斥力向量相加
        avoidance_vector = [0.0, 0.0]
        repulsion_force = 0.0

        for _d in near_drones:
            distance = math.dist((_d["x"], _d["y"]), (self.state["x"], self.state["y"]))
            repulsion_force = self.avoid_weight / (distance**2)
            angle = math.atan2(self.state["y"] - _d["y"], self.state["x"] - _d["x"])
            avoidance_vector[0] += repulsion_force * math.cos(angle)
            avoidance_vector[1] += repulsion_force * math.sin(angle)

        # 缩放避障向量到一定范围内的最大速度
        avoidance_speed = math.hypot(avoidance_vector[0], avoidance_vector[1])
        if avoidance_speed > self.avoid_max_speed:
            scale = self.avoid_max_speed / avoidance_speed
            avoidance_vector[0] *= scale
            avoidance_vector[1] *= scale

        return tuple(avoidance_vector)

    def calc_min_distance_enemy(self) -> tuple[float, Optional[DroneState]]:
        """
        计算最近的敌人喵
        """
        nearest_enemy = None
        min_distance = float("inf")
        for enemy in self.opposite_side_list:
            # 如果是同一方无人机，跳过
            if enemy["side"] == self.state["side"]:
                continue

            distance = (
                (enemy["x"] - self.state["x"]) ** 2
                + (enemy["y"] - self.state["y"]) ** 2
            ) ** 0.5
            if distance < min_distance:
                min_distance = distance
                nearest_enemy = enemy

        return min_distance, nearest_enemy

    def avoid(self) -> DroneCommand:
        """
        避障函数
        """
        # 获取当前状态中的所有无人机
        cmd: DroneCommand = {
            "id": self.state["id"],
            "v_x": 0.0,
            "v_y": 0.0,
        }

        # 计算避障速度
        avoid_vx, avoid_vy = self.calc_avoid_velocity()
        cmd["v_x"] = avoid_vx
        cmd["v_y"] = avoid_vy

        return cmd

    def attack(self) -> DroneCommand:
        """
        进攻
        """
        cmd: DroneCommand = {
            "id": self.state["id"],
            "v_x": 0.0,
            "v_y": 0.0,
        }
        # 查找距离当前无人机最近的敌机
        min_distance, nearest_enemy = self.calc_min_distance_enemy()

        # 如果没有敌机在阈值范围内，则返回
        if min_distance > self.attack_range:
            return cmd

        # 计算发射导弹的方向向量
        if nearest_enemy is None:
            return cmd

        v_x = nearest_enemy["x"] - self.state["x"]
        v_y = nearest_enemy["y"] - self.state["y"]
        norm = (v_x**2 + v_y**2) ** 0.5
        v_x /= norm
        v_y /= norm

        cmd["v_x"] = v_x * self.attack_max_speed
        cmd["v_y"] = v_y * self.attack_max_speed

        return cmd

    def flee(self) -> DroneCommand:
        """
        逃离策略的指令生成函数
        """
        cmd: DroneCommand = {
            "id": self.state["id"],
            "v_x": 0.0,
            "v_y": 0.0,
        }
        # 找到距离最近的敌方无人机
        min_distance, closest_enemy = self.calc_min_distance_enemy()
        if closest_enemy is None:
            return cmd

        # 如果最近的敌方无人机距离过近，则优先向远离敌方无人机的方向移动
        if min_distance < self.flee_range:
            direction_x = self.state["x"] - closest_enemy["x"]
            direction_y = self.state["y"] - closest_enemy["y"]
            distance = (direction_x**2 + direction_y**2) ** 0.5
            direction_x /= distance
            direction_y /= distance
            cmd["v_x"] = direction_x * self.flee_max_speed
            cmd["v_y"] = direction_y * self.flee_max_speed

        # 如果防御导弹数量足够，则释放防御导弹并逃跑
        # if self.state["def_msl_num"] > 0:
        #     return {"id": self.state["id"], "v_x": 0, "v_y": 0}

        return cmd


class CommonAlgorithm(AbstractAlgorithm):
    """
    算法执行类
    """

    def __init__(
        self,
        drone_dict: DroneDict,
        msl_msg_list: MslMsgList,
        is_stopped: IsStopped,
        sender: BaseSender[str],
    ):
        self.drone_dict = drone_dict
        self.msl_msg_list = msl_msg_list
        self.is_stopped = is_stopped
        self.sender = sender
        self.machine: dict[int, DroneStateMachine] = {}

    @staticmethod
    def calc_distance(_a: tuple[float, float], _b: tuple[float, float]) -> float:
        """
        计算距离喵
        """
        return sqrt((_a[0] - _b[0]) ** 2 + (_a[1] - _b[1]) ** 2)

    @staticmethod
    def get_drone_state_list(drone_dict: DroneDict) -> list[DroneState]:
        """
        转换列表无路喵
        """
        drone_state_list: list[DroneState] = []

        for i, (_, value) in enumerate(drone_dict.items()):
            drone_state: DroneState = {
                "id": i,
                "x": float(value[0]),
                "y": float(value[1]),
                "side": int(value[2]),
                "is_destroyed": int(value[3]),
                "atk_msl_num": int(value[4]),
                "def_msl_num": int(value[5]),
            }
            print(
                f"{'R' if drone_state['side'] == 1 else 'B'}{drone_state['id']}\
                    ({'on' if drone_state['is_destroyed'] == 0 else 'off'}): \
                        ({drone_state['x']:.2f}, {drone_state['y']:.2f}), \
                            {drone_state['atk_msl_num']} atkmsl, \
                                {drone_state['def_msl_num']} defmsl"
            )
            drone_state_list.append(drone_state)

        return drone_state_list

    async def start(self):
        """
        运行算法
        """

        while True:
            cmd_list: list[DroneCommand] = []
            drone_state_list: list[DroneState] = CommonAlgorithm.get_drone_state_list(
                self.drone_dict
            )

            for drone_state in drone_state_list:
                if drone_state["is_destroyed"] == 1:
                    continue

                self_side_list: list[DroneState] = []
                opposite_side_list: list[DroneState] = []

                for other_drone_stae in drone_state_list:
                    if (
                        other_drone_stae["is_destroyed"] == 0
                        and other_drone_stae["side"] == drone_state["side"]
                        and other_drone_stae["id"] != drone_state["id"]
                    ):
                        self_side_list.append(other_drone_stae)

                    if (
                        other_drone_stae["is_destroyed"] == 0
                        and other_drone_stae["side"] != drone_state["side"]
                        and other_drone_stae["id"] != drone_state["id"]
                    ):
                        opposite_side_list.append(other_drone_stae)

                if drone_state["id"] not in self.machine:
                    self.machine.setdefault(
                        drone_state["id"],
                        DroneStateMachine(
                            drone_state, self_side_list, opposite_side_list
                        ),
                    )

                drone_machine = self.machine.get(drone_state["id"])
                if not drone_machine is None:
                    drone_machine.update_side_info(self_side_list, opposite_side_list)
                    cmd_list.append(drone_machine.execute())

                # lambda的参数不给标注类型谔谔
                # def convert_state(
                #     _s: DroneState, _ds: DroneState = drone_state
                # ) -> DistanceDict:
                #     return {
                #         "id": _s["id"],
                #         "distance": CommonAlgorithm.calc_distance(
                #             (_ds["x"], _ds["y"]),
                #             (_s["x"], _s["y"]),
                #         ),
                #     }

                # distance_list: list[DistanceDict] = list(
                #     map(
                #         convert_state,
                #         opposite_side_list,
                #     )
                # )
                # min_distance_drone: DistanceDict = min(
                #     distance_list, key=lambda x: x["distance"]
                # )

                # if min_distance_drone["distance"] >= range_threshold:
                #     pass

            print(f"CommonAlgo> is finnished: {self.is_stopped['is_stopped']}")
            print("==========")
            self.msl_msg_list.clear()

            if len(cmd_list) > 0:
                cmd_str: str = "\n".join(
                    list(
                        map(
                            lambda a: f"{a['id']}: ({a['v_x']:.4f}, {a['v_y']:.4f})",
                            cmd_list,
                        )
                    )
                )
                print(f"CommonAlgo> cmd: \n {cmd_str}")
                json_data = {"data": cmd_list}
                dumped_data = dumps(json_data) + "\n"
                await self.sender.put_data(dumped_data)

            await asyncio.sleep(3)
