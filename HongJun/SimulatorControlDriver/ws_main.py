"""
运行Websocket喵
"""
import asyncio

from dcontrol.network.ws_server import WebSocketServer


async def main():
    self_host: str = "localhost"
    self_port: int = 3000
    ws_server = WebSocketServer(self_host, self_port, {"is_running":False})
    await ws_server.run()


if __name__ == "__main__":
    asyncio.run(main())
