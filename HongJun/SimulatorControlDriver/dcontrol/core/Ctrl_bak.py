"""
FileName : Ctrl.py
Author : Huang Zhuofei
Date : 2023-1-29
Function : 1-接收DroneSim.py发来的无人机状态参数
           2-向DroneSim.py发送无人机的控制指令
           3-用户的集群算法应在这里实现
"""

import random
import socket
import struct
import threading
import time




# 描述无人机状态的类
class DroneState:
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

    # 接收用的Socket，需要绑定端口
    CtrlSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    CtrlSocket.bind((CtrlIP, CtrlPort))

    # 发送用的Socket，不用绑定
    CtrlSocket1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 定义全局字典，存放无人机状态
    droneDic = {}

    # 记录Ctrl启动时间
    startTime = time.time()

    # 将所有的打击消息按list存储
    mslList = []

    # 结束标志
    stoped = False

    # 接收数据的独立线程
    def recvdata():
        while 1:
            # 在CtrlPort端口阻塞式监听数据
            message, _ = CtrlSocket.recvfrom(2048)
            jiaoyan, *message = message.decode().split()
            if jiaoyan == "1234":
                droneDic[int(message[0])] = message[1:]
            elif jiaoyan == "7727":
                msgtime = time.time() - startTime
                mslList.append((msgtime, *message))
            elif jiaoyan == "9999":
                global stoped
                stoped = True
                # print('yyyyy')
                # mslDic[time.time()] = message
                # print(mslList[-1])
                # print()
            # # 取得的仿真数据
            # while data:
            #     ID, x, y, zhenying, alive, attmslnum, defmslnum, *data = data
            #     droneDic[ID] = (x, y, zhenying, alive, attmslnum, defmslnum)
            #     #print(ID, x, y, zhenying, alive, attmslnum, defmslnum)

    # 创建接收线程并启动
    RecvThread = threading.Thread(target=recvdata, args=())
    RecvThread.start()

    # 等待一秒钟，等droneDic充起来
    # time.sleep(1)
    # numOfDrones = len(droneDic)

    while 1:
        """↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓"""
        """        客户应在这里实现集群控制算法        """
        # 生成测试用的无人机指令
        OrderList = list()
        for i in range(len(droneDic)):
            # 所需的所有无人机信息均在droneDic中；key是ID，value是一个list，各个含义见DroneState的定义
            print(i, droneDic[i])
            # 打击消息存在于mslList中，数据组成为（时间、发射方、命中方）
            # 1.5, R0, B7 表示 第1.5s，R0无人机发射的攻击导弹击毁了B7无人机
            # 3.4, R3, -1 表示 第3.4s，R3无人机发射的攻击导弹被成功拦截
            # mslList

            neworder = Order()
            neworder.ID = i
            neworder.Vx = (random.random() - 0.5) * 3  # [-1.5,1.5] M/S
            neworder.Vy = (random.random() - 0.5) * 3  # [-1.5,1.5] M/S

            OrderList.append(neworder)

        for j in range(len(mslList)):
            print(mslList[j])

        # 打印仿真结束标识，当前运行90s后，存活的无人机会降落，此标识变为true
        print(stoped)
        """↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑"""
        print(
            "==============================================================================================="
        )
        mslList = []
        valueall = ()
        # 将OrderList中的所有数据打包，转换为字符串
        for each in OrderList:
            value = (each.ID, each.Vx, each.Vy)
            valueall = (*valueall, *value)
        s = struct.Struct("I2f" * len(OrderList))
        sendData = s.pack(*valueall)

        # 将数据发送到SimIP的SimPort
        CtrlSocket1.sendto(sendData, (SimIP, SimPort))

        # 发送周期客户指定是27s，测试时暂用5s
        time.sleep(5)
