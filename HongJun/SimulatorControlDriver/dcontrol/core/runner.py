"""
运行器模块
"""

import asyncio
import random
from typing import Optional, Union

import airsim
from msgpackrpc.error import TransportError

from dcontrol.network.sender import BaseSender


class AirSimRunner:
    """
    运行器类
    """

    def __init__(
        self,
        cmd_list: list[tuple[int, float, float]],
        drone_dict: dict[Union[str, int], list[str]],
        sender: BaseSender[str],
    ):
        self.client: Optional[airsim.MultirotorClient] = None
        self.sender = sender
        self.drone_dict = drone_dict
        self.cmd_list = cmd_list
        self.red_side_names: set[int] = set()
        self.blue_side_names: set[int] = set()

    async def start(self):
        """
        启动运行器
        """
        self.client = airsim.MultirotorClient()
        while True:
            try:
                self.client.confirmConnection()
                break
            except TransportError:
                self.client = airsim.MultirotorClient()
                continue

        self.init_drones()
        await self.run()
        await self.stop()

    async def run(self):
        """
        运行器运行
        """
        if self.client is None:
            return

        name_list = self.get_vehicle_names()
        v_x = [0.0] * len(name_list)
        v_y = [0.0] * len(name_list)

        # 跑90s停下来
        for _ in range(180):
            # print(f"Runner> cmd list len: {len(self.cmd_list)}")
            while len(self.cmd_list) != 0:
                drone_id, v_x, v_y = self.cmd_list.pop()
                drone_name = "R0"
                if drone_id in self.red_side_names:
                    drone_name = "R" + str(drone_id)
                else:
                    drone_name = "B" + str(drone_id)
                self.client.moveByVelocityZAsync(
                    v_x, v_y, -3.0, 100, vehicle_name=drone_name
                )

            for _, drone_id in enumerate(name_list):
                drone_kstate = self.client.simGetGroundTruthKinematics(drone_id)
                is_destroyed, atkmisnum, defmisnum = tuple(
                    self.drone_dict.get(drone_id, "022")
                )

                drone_side = 0
                if drone_id[0] == "R":
                    drone_side = 1
                else:
                    drone_side = 0

                value = f"1234 {drone_id[1:]} {drone_kstate.position.x_val:.3f} {drone_kstate.position.y_val:.3f} {drone_side} {is_destroyed} {atkmisnum} {defmisnum}"

                await self.sender.put_data(value + "\n")

            await asyncio.sleep(1)

    def init_drones(self):
        """
        初始化无人机位置
        """
        if self.client is None:
            return

        name_list = self.get_vehicle_names()

        for name in name_list:
            if name[0] == "R":
                self.red_side_names.add(int(name[1:]))
            else:
                self.blue_side_names.add(int(name[1:]))

        for index, name in enumerate(name_list):
            drone_kstate = self.client.simGetGroundTruthKinematics(name)

            if int(name[1:]) in self.red_side_names:
                drone_kstate.position.x_val += (
                    random.random() - 0.5
                ) * 5 + 10  # 7.5~12.5m
                drone_kstate.position.y_val += (
                    random.random() - 0.5
                ) * 5 + 10  # 7.5~12.5
            else:
                drone_kstate.position.x_val += (
                    random.random() - 0.5
                ) * 5 - 10  # -12.5~-7.5
                drone_kstate.position.y_val += (
                    random.random() - 0.5
                ) * 5 - 10  # -12.5~-7.5

            self.client.simSetKinematics(drone_kstate, True, name)
            self.client.enableApiControl(True, name)
            self.client.armDisarm(True, name)

            if index != len(name_list) - 1:
                self.client.takeoffAsync(vehicle_name=name)
            else:
                self.client.takeoffAsync(vehicle_name=name_list[-1]).join()

    async def stop(self):
        """
        停止
        """
        stop_code: str = "9999"
        await self.sender.put_data(stop_code + "\n")

        if self.client is None:
            return

        name_list = self.get_vehicle_names()

        for index, name in enumerate(name_list):
            if index != len(name_list) - 1:
                self.client.landAsync(vehicle_name=name)
            else:
                self.client.landAsync(vehicle_name=name).join()

        for _, name in enumerate(name_list):
            self.client.armDisarm(False, vehicle_name=name)
            self.client.enableApiControl(False, vehicle_name=name)

    def get_vehicle_names(self) -> list[str]:
        """
        获得无人机名字列表
        """
        if self.client is None:
            return []

        return self.client.listVehicles()
