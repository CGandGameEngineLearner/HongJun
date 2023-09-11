import json

import asyncio
import threading
import yaml
import socketio

"""
请看Socket.IO教程：
https://blog.csdn.net/qq_44484910/article/details/106319507
"""
# import eventlet
#
# eventlet.monkey_patch()
import eventlet.wsgi
import time

import airsim

from airsim import MultirotorClient, MultirotorState
from loguru import logger
from multiprocessing import Pool

with open('Config.yml', 'r', encoding='utf-8') as f:
    config = yaml.load(f.read(), Loader=yaml.SafeLoader)
host = config['server']['host']
port = config['server']['port']

sio_server: socketio.Server = socketio.Server(async_mode='eventlet')
# socketio_middleware: socketio.Middleware = socketio.Middleware(sio_server)
simulator_sid = None
is_running = {"is_running": False}

#
# @sio_server.on('connect')
# def on_connect(sid, environ):
#     """
#     与客户端建立连接后执行
#     本项目只是个用于在内网中训练人工智能的无人机仿真模拟器，并不是对外发行的客户端软件
#     客户端和服务端的通讯都在本地主机LocalHost完成
#     所以什么安全检验的暂时不做拉
#     """
#     is_running["is_running"] = True
#     logger.info("成功与客户端建立连接")
#     sendmsg = {'token': "You connected server successful."}
#     msg = json.dumps(sendmsg)
#     sio_server.emit(event='reply', room=sid, data=msg)
#     logger.info("发送回复")

from HongJun.SimulatorControlDriver.dcontrol.network.ws_server import WebSocketServer


class SimulatorConnector:
    host: str
    port: int
    airsim_client: MultirotorClient
    simulator_sid = None
    sio_server: socketio.Server
    ws_server: WebSocketServer = None

    # airsim没有的新功能需要操控这个副客户端(虚幻引擎)来完成

    def __init__(self):
        self.simulator_sid = simulator_sid
        self.sio_server = sio_server
        self.airsim_client = airsim.MultirotorClient()
        logger.info(self.airsim_client.listVehicles())
        #self.airsim_client.enableApiControl(True)
        #self.airsim_client.armDisarm(True)
        self.airsim_client.takeoffAsync().join()
        ws_server_thread = WSserverThead(1, "WS_server_thread", 1, self)
        ws_server_thread.start()

    async def startSocketIOserver(self):
        pass

    # def run(self):
    #     self.airsim_client.confirmConnection()
    #     self.airsim_client.enableApiControl(True)
    #     self.airsim_client.armDisarm(True)
    #     self.airsim_client.takeoffAsync().join()


async def testControl(simulator_connector):
    logger.info("waiting")
    while not is_running["is_running"]:
        logger.info(is_running["is_running"])
        await asyncio.sleep(2.0)

    logger.info(type(simulator_connector))
    logger.info(simulator_connector.airsim_client.listVehicles())

    simulator_connector.airsim_client.enableApiControl(True, vehicle_name='B0')
    simulator_connector.airsim_client.armDisarm(True, vehicle_name='B0')
    simulator_connector.airsim_client.takeoffAsync(vehicle_name='B0').join()
    simulator_connector.airsim_client.moveToPositionAsync(-150.0, 10, -80, 15, vehicle_name='B0').join()
    logger.info("test control end")


# async def startListen():
#     await asyncio.sleep(0.1)
#     eventlet.wsgi.server(eventlet.listen((host, port)), socketio_middleware)


# async def start_ws():
#     self_host: str = "localhost"
#     self_port: int = 3000
#     ws_server = WebSocketServer(self_host, self_port, is_running)
#     logger.info("ws run")
#     await ws_server.run()
#
# async def main():
#     await asyncio.gather(
#         control(), start_ws()
#     )
class WSserverThead(threading.Thread):

    def __init__(self, threadID, name, counter, simulator_connector: SimulatorConnector):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.simulator_connector = simulator_connector

    def run(self) -> None:
        logger.info('WSserver正在启动')
        asyncio.run(self.prepareInitWServer())

    async def initWSserver(self):
        self.simulator_connector.ws_server = WebSocketServer(host, port, is_running)
        logger.info("ws run")
        await self.simulator_connector.ws_server.run()

    async def prepareInitWServer(self):
        await asyncio.gather(self.initWSserver())


if __name__ == '__main__':
    simulator_connector = SimulatorConnector()
    logger.info("simulator_connector初始化中")
    asyncio.run(testControl(simulator_connector))
