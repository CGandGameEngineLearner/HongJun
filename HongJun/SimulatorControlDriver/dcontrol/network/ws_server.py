"""
Websocket模块喵
"""

import asyncio
from typing import Optional, TypedDict

from aiohttp import web
from socketio.asyncio_server import AsyncServer
# from sender import  BaseSender

from dataclasses import dataclass

SIO:AsyncServer= AsyncServer(async_mode="aiohttp")


"""
定义一个字典类型，用于存储伤害信息
"""


class WebSocketServer(object):
    """
    Websocket类喵
    """

    def __init__(self, host: str, port: int, is_running):
        self.host = host
        self.port = port
        # self.sio = AsyncServer(async_mode="aiohttp")
        self.sio=SIO
        self.app = web.Application()
        self.sio.attach(self.app)
        # self.sender=BaseSender()
        # make one reference to event name so it can be easily renamed
        self.event_name = "ue"
        self.conn_history: list[str] = []  # track connected clients
        self.runner: Optional[web.AppRunner] = None
        self.site: Optional[web.TCPSite] = None
        self.is_running=is_running

        @self.sio.on("connect", namespace="/")
        async def handle_connect(sid: str, _):
            """
            When a client connects, bind each desired event to the client socket
            """
            # track connected clients via log
            self.conn_history.append(sid)
            # await self.sio.emit(self.event_name, "connected")
            await self.sio.emit(event='reply', room=sid, data="{\"token\": \"gugugaga\"}")
            client_conn_msg = f"Connected> {sid}, total: {len( self.conn_history)}"
            print(client_conn_msg)

        @self.sio.on("disconnect", namespace="/")
        async def handle_disconnect(sid: str):
            """
            track disconnected clients via log
            """
            self.conn_history.remove(sid)
            await self.sio.emit(self.event_name, "disconnected")
            client_disconn_msg = f"Disconnected> {sid}, total: {len(self.conn_history)}"
            print(client_disconn_msg)

        @self.sio.on(self.event_name, namespace="/")
        async def handle_message(sid: str, data: str):
            """
            multicast received mess
            age from client
            """
            import json
            json.loads(data)
            await self.sio.emit(self.event_name, "gugugaga")
            combinedMsg = f"{sid[:4]}: {data}"
            print(f"Multicast> {combinedMsg}")

        @self.sio.on("damage", namespace="/")
        async def damage_message(sid: str, data: str):
            """
            multicast received message from client
            """
            self.sender.push_data(data)




    async def start(self):
        """
        初始化函数喵
        """
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        print("~~")
        try:
            await self.site.start()
            self.is_running["is_running"] = True
            print("Server started!")
        except:
            print("eee")

    async def run(self):
        """
        运行函数喵
        """
        await self.start()

        while True:
            try:
                await asyncio.sleep(0.1)
            except KeyboardInterrupt:
                break

        if not self.runner is None:
            await self.runner.cleanup()
        if not self.site is None:
            await self.site.stop()
