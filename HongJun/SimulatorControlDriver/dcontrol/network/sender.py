"""
异步发送器类
"""

import asyncio
from json import dumps
from typing import Generic, Optional

from .types import DataType


class BaseSender(Generic[DataType]):
    """
    基础发送器类
    """

    def __init__(self, host: str, port: int, owner: str = ""):
        self.owner = owner
        self.host = host
        self.port = port
        self.queue: asyncio.Queue[DataType] = asyncio.Queue()

    async def put_data(self, data: DataType):
        """
        将消息放入消息队列
        """

        await self.queue.put(data)

    async def send(self, writer: asyncio.StreamWriter):
        """
        发送数据的具体逻辑
        """
        while True:
            try:
                data = await self.queue.get()

                if isinstance(data, dict):
                    data = dumps(data)

                if isinstance(data, str):
                    data = data.encode()

                if isinstance(data, bytes):
                    writer.write(data)
                    await writer.drain()
                    # print(f"{self.owner}@Sender> Sent data to server.")
            except RuntimeError:
                continue

    async def start(self):
        """
        启动发送器，从消息队列取数据，并转发
        """
        writer: Optional[asyncio.StreamWriter] = None
        while True:
            try:
                _, writer = await asyncio.open_connection(self.host, self.port)
                break
            except ConnectionError:
                await asyncio.sleep(0.1)

        print(f"{self.owner}@Sender> Connected to server.")

        await self.send(writer)
