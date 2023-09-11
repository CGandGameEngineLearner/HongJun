"""
用于读取配置文件的类
"""

from typing import TypedDict


class ConfigDict(TypedDict):
    """
    承载配置文件数据的对象的类型声明
    """

    airsim_host: str
    airsim_port: int
    controller_host: str
    controller_port: int
    ue_host: str
    ue_port: int


class ConfigLoader:
    @staticmethod
    def load(file_name: str) -> ConfigDict:
        pass
