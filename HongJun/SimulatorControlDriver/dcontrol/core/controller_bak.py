"""
FileName : DroneSim.py
Author : Huang Zhuofei
Date : 2023-1-29
Function : 1-接收Ctrl.py发来的无人机控制指令
           2-向Ctrl.py发送无人机的所有状态参数
           3-和UE端链接，将Ctrl.py的指令转换后发送至UE
           4-从UE端获取到无人机状态参数
"""

import random
import socket
import struct
import threading
import time

import airsim


class DroneState:
    """
    描述无人机状态的类
    """

    def __init__(self, id):
        self.ID = id  # 每个无人机唯一的ID号
        self.x = 0.0  # 无人机的X坐标
        self.y = 0.0  # 无人机的Y坐标
        self.ZhenYing = 0  # 无人机所属阵营 红1蓝0
        self.IsDestory = 0  # 无人机损毁状态
        self.AtkMslNum = 2  # 无人机攻击类导弹的剩余数量
        self.DefMslNum = 2  # 无人机防御类导弹的剩余数量


# 无人机接收的指令
class Order:
    def __init__(self):
        self.ID = 0  # 每个无人机唯一的ID号
        self.Vx = 0.0  # 发给无人机的X方向速度指令
        self.Vy = 0.0  # 发给无人机的Y方向速度指令

if __name__ == "__main__":
    # 定义控制端和仿真端的ip与端口
    SimIP = "127.0.0.1"
    SimPort = 54322
    CtrlIP = "127.0.0.1"
    CtrlPort = 54321

    UEIP = "127.0.0.1"
    UPPort = 54323

    # 接收用的Socket，需要绑定端口
    SimSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    SimSocket.bind((SimIP, SimPort))
    UESocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    UESocket.bind((UEIP, UPPort))

    # 发送用的Socket，不用绑定
    SimSocket1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 定义接受的数据，主线程也要读
    orderList = []

    # 接收指令数据的独立线程
    def recvdata0(ordL: list):
        fmt = "Iff"
        oneDataSize = struct.calcsize(fmt)
        while 1:
            # 在SimPort端口阻塞式监听数据
            message, _ = SimSocket.recvfrom(2048)
            numData = len(message) // oneDataSize
            data = struct.unpack(fmt * numData, message)
            while data:
                ID, Vx, Vy, *data = data
                # print('New Ctrl Order:')
                # print(ID, Vx, Vy)
                ordL.append((ID, Vx, Vy))

    # 创建接收指令数据的线程并启动
    RecvThread0 = threading.Thread(target=recvdata0, args=(orderList,))
    RecvThread0.start()

    dic = {}  # 以无人机名字为Key;生存状态、攻击导弹数量、防御导弹数量为Value的字典。如 R2:122
    mslMsgs = []

    def recvdata1():
        while 1:
            message0, _ = UESocket.recvfrom(2048)
            jiaoyan, *message = message0.decode().split()
            if jiaoyan == "1234":
                dic[message[0]] = message[1:]
            elif jiaoyan == "7727":
                mslMsgs.append(message)
                # print(message)
                SimSocket1.sendto(message0, (CtrlIP, CtrlPort))
            else:
                print("Unknown Message")
            # print(message.decode()[:-3],message.decode()[-3:])

    # 创建接收UE数据的线程并启动
    RecvThread1 = threading.Thread(target=recvdata1)
    RecvThread1.start()

    """
    这里需要写接收到指令之后，在AirSim中的处理
    并获取到UE返回的无人机数据
    """
    # 与AirSim建立连接，并返回句柄
    client = airsim.MultirotorClient()

    # 获取所有无人机的name列表
    NameList = client.listVehicles()

    # 区分出红蓝双方的名字
    RedIDList = set()
    BlueIDList = set()
    for each in NameList:
        if each[0] == "R":
            # RedNameList.append(each)
            RedIDList.add(int(each[1:]))
        else:
            # BlueNameList.append(each)
            BlueIDList.add(int(each[1:]))

    # 检查通信是否成功建立，会在命令行中有打印信息
    client.confirmConnection()

    for i in range(len(NameList)):
        tempName = NameList[i]
        # 位置随机部署
        state = client.simGetGroundTruthKinematics(tempName)

        # 红蓝方分拨初始化位置
        if int(tempName[1:]) in RedIDList:
            state.position.x_val += (random.random() - 0.5) * 5 + 10  # 7.5~12.5m
            state.position.y_val += (random.random() - 0.5) * 5 + 10  # 7.5~12.5
        else:
            state.position.x_val += (random.random() - 0.5) * 5 - 10  # -12.5~-7.5
            state.position.y_val += (random.random() - 0.5) * 5 - 10  # -12.5~-7.5

        client.simSetKinematics(state, True, tempName)

        # 开启API的控制权。遥控器的操作会抢夺API的控制权
        client.enableApiControl(True, tempName)

        # 解锁
        client.armDisarm(True, tempName)
        # 起飞
        if i != len(NameList) - 1:
            client.takeoffAsync(vehicle_name=tempName)
        else:
            client.takeoffAsync(vehicle_name=NameList[-1]).join()

    vx = [0.0] * len(NameList)
    vy = [0.0] * len(NameList)

    # 跑90s停下来
    for j in range(90):
        # ID, vx, vy = 0
        # ordToName = ''
        while orderList:
            ID, vx, vy = orderList.pop()
            if ID in RedIDList:
                ordToName = "R" + str(ID)
            else:
                ordToName = "B" + str(ID)
            # print(ID,"--",vx,'--',vy)
            client.moveByVelocityZAsync(vx, vy, -3, 100, vehicle_name=ordToName)

        for i in range(len(NameList)):
            tempName = NameList[i]
            state = client.simGetGroundTruthKinematics(tempName)
            # x = state.position.x_val
            # y = state.position.y_val
            # z = state.position.z_val
            # print(NameList[i], '---', (x, y, z))
            IsDestory, atkmisnum, defmisnum = tuple(dic.get(tempName, "022"))
            if tempName[0] == "R":
                zy = 1
            else:
                zy = 0

            value = (
                "1234"
                + " "
                + tempName[1:]
                + " "
                + state.position.x_val.__format__(".3f")
                + " "
                + state.position.y_val.__format__(".3f")
                + " "
                + str(zy)
                + " "
                + IsDestory
                + " "
                + atkmisnum
                + " "
                + defmisnum
            )

            SimSocket1.sendto(value.encode(), (CtrlIP, CtrlPort))

        time.sleep(1)

    stopMsg = "9999"
    SimSocket1.sendto(stopMsg.encode(), (CtrlIP, CtrlPort))
    # 进入降落锁机流程
    for i in range(len(NameList)):
        tempName = NameList[i]

        # 降落
        if i != len(NameList) - 1:
            client.landAsync(vehicle_name=tempName)
        else:
            client.landAsync(vehicle_name=NameList[-1]).join()

        # client.simDestroyObject(tempName)

    for i in range(len(NameList)):
        tempName = NameList[i]

        # lock
        client.armDisarm(False, vehicle_name=tempName)

        # release control
        client.enableApiControl(False, vehicle_name=tempName)
