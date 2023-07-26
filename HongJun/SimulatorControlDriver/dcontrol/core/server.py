"""
服务器模块
"""

import asyncio
from json import loads
from time import time as get_time

from dcontrol.network.sender import BaseSender
from dcontrol.network.server import BaseServer

from .types import CmdList, DroneDict, IsStopped, MslMsgList ,DroneCommandJson


class AirSimInterServer(BaseServer):
    """
    中转服务器类
    """

    def __init__(self, host: str, port: int, cmd_list: CmdList):
        super().__init__(host, port, "AirSimInterServer")
        self.cmd_list = cmd_list

    async def handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        # class ChunkData:
        #     """
        #     序列里的数据快类型
        #     """

        #     def __init__(self, drone_id: int, v_x: float, v_y: float):
        #         self.drone_id = drone_id
        #         self.v_x = v_x
        #         self.v_y = v_y

        # fmt_code: str = "Iff"
        # chunk_size = calcsize(fmt_code)

        while True:
            raw_data = await reader.readline()
            # raw_data = raw_data.rstrip(b"\n")

            if not raw_data:
                break

            # print(f"{self.name}> Received data.")

            # chunk_num = len(raw_data) // chunk_size
            # fmt: str = fmt_code * chunk_num
            # print(f"unpack size: (fmt:{len(fmt)}, data: {len(raw_data)})")

            # if len(fmt) * 4 != len(raw_data):
            #     continue

            # unpacked_data = unpack(fmt, raw_data)
            # chunk_list = [
            #     ChunkData(*_chunk)
            #     for _chunk in zip(
            #         unpacked_data[::3], unpacked_data[1::3], unpacked_data[2::3]
            #     )
            # ]

            json_data:DroneCommandJson = loads(raw_data.decode().rstrip("\n"))

            for chunk in json_data["data"]:
                self.cmd_list.append((chunk["id"], chunk["v_x"], chunk["v_y"]))

        writer.close()


class UEInterServer(BaseServer):
    """
    中转服务器类
    """

    def __init__(
        self,
        host: str,
        port: int,
        drone_dict: DroneDict,
        msl_msg_list: MslMsgList,
        sender: BaseSender[str],
    ):
        super().__init__(host, port, "UEInterServer")
        self.drone_dict = drone_dict
        self.msl_msg_list = msl_msg_list
        self.sender = sender

    async def handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        while True:
            raw_data = await reader.readline()
            # raw_data = raw_data.rstrip(b"\n")

            if not raw_data:
                break

            # print(f"{self.name}> Received data.")
            decoded_data = raw_data.decode()
            msg_type_code, *message = decoded_data.split()
            # print(f"UEInterServer> code: {msg_type_code}")
            if msg_type_code == "1234":
                self.drone_dict[message[0]] = message[1:]
            elif msg_type_code == "7727":
                print(f"UEInterServer> 7727: {message}")
                self.msl_msg_list.append(message)
                # await self.sender.put_data(raw_data + b"\n")
                await self.sender.put_data(decoded_data + "\n")
            else:
                print(f"{self.name}> Unknown Message.")

        writer.close()


class ActorInterServer(BaseServer):
    """
    中转服务器类
    """

    def __init__(
        self,
        host: str,
        port: int,
        drone_dict: DroneDict,
        msl_msg_list: MslMsgList,
        is_stopped: IsStopped,
    ):
        super().__init__(host, port, "ActorInterServer")
        self.drone_dict = drone_dict
        self.msl_msg_list = msl_msg_list
        self.is_stopped = is_stopped
        self.start_time = get_time()

    async def handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        while True:
            raw_data = await reader.readline()
            # raw_data = raw_data.rstrip(b"\n")

            if not raw_data:
                break

            # print(f"{self.name}> Received data.")

            msg_type_code, *message = raw_data.decode().split()
            # print(f"ActorInterServer> code: {msg_type_code}")
            if msg_type_code == "1234":
                self.drone_dict[int(message[0])] = message[1:]
            elif msg_type_code == "7727":
                msg_time = get_time() - self.start_time
                print(f"ActorInterServer> 7727: {msg_time} {message}")
                self.msl_msg_list.append((msg_time, *message))
            elif msg_type_code == "9999":
                self.is_stopped["is_stopped"] = True

        writer.close()
