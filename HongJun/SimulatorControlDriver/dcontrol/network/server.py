"""
异步服务器类
"""

import asyncio
from typing import Optional

from .sender import BaseSender


class BaseServer:
    """
    基础服务器类
    """

    def __init__(self, host: str, port: int, name: str = "Server"):
        self.host = host
        self.port = port
        self.name = name
        self.server: Optional[asyncio.Server] = None

    async def handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        """
        接收客户端发来的信息，并处理
        """
        while True:
            raw_data = await reader.readline()
            raw_data = raw_data.rstrip(b"\n")
            if not raw_data:
                break
            print(f"{self.name}> Received data: {raw_data.decode()}")

        writer.close()

    async def start(self):
        """
        启动服务器
        """
        self.server = await asyncio.start_server(
            self.handle_client, self.host, self.port
        )
        print(f"{self.name}> Started.")

        async with self.server:
            await self.server.serve_forever()

    async def stop(self):
        """
        终止服务器
        """
        if self.server:
            self.server.close()
            await self.server.wait_closed()

class InterServer(BaseServer):
    """
    和互动的服务器类喵
    """

    def __init__(self, host: str, port: int, sender:BaseSender[str], name: str = "InterServer"):
        super().__init__(host, port, name)
        self.sender = sender
    
    async def handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        """
        接收客户端发来的信息，并处理
        """
        while True:
            raw_data = await reader.readline()
            raw_data= raw_data.rstrip(b"\n")
            if not raw_data:
                break
            print(f"{self.name}> Received data: {raw_data.decode()}")
            await self.sender.put_data("Gugugaga\n")

        writer.close()