# HongJun

## 介绍

鸿钧：一个基于虚幻引擎和 AirSim 的仿真系统，让用户以简单轻松的配置方式搭建定制化的无人机作战环境。
本项目是鸿钧的 python 控制器，其通过 Socket 协议与由基于虚幻引擎和 AirSim 的仿真系统——鸿钧建立通讯，并控制其中仿真的无人机，进行飞行和战斗任务。用户可以使用 Python 语言编写无人机的飞行任务程序，完成无人机的编队飞行、攻击战斗、集群对抗等任务。
本团队在 AirSim 的基础上拓展出了攻击、战斗系统，可以对无人机的作战环境进行模拟，本项目可作为集群智能的训练平台，适用于无人机集群对抗、轰炸敌方目标单位等任务的人工智能训练。

**该项目已被清华大学猛狮无人驾驶实验室和南京航空航天大学无人机实验室的研究生团队采用，并于人工智能仿真训练，并发表相关科研论文**
**本项目与HongJun的模拟器端项目是配套使用的,模拟器端项目链接：[HongJun模拟器](https://github.com/CGandGameEngineLearner/HongJunSimulator)**
# HongJun
## Introduction
HongJun: A simulation system based on Unreal Engine and AirSim, allowing users to easily configure customized drone combat environments. This project is the Python controller for HongJun, which communicates with the simulation system—HongJun, based on Unreal Engine and AirSim, through the Socket protocol and controls the simulated drones for flight and combat missions. Users can write drone flight mission programs in Python to complete tasks such as drone formation flight, attack combat, and swarm confrontation.

Our team has expanded the attack and combat system on the basis of AirSim, which can simulate the combat environment of drones. This project can be used as a training platform for swarm intelligence, suitable for artificial intelligence training in drone swarm confrontation and bombing enemy target units.

This project has been adopted by the graduate student team of the Tsinghua University Lion Unmanned Driving Laboratory and the Nanjing University of Aeronautics and Astronautics Drone Laboratory for artificial intelligence simulation training, and has published relevant scientific research papers.

This project is used in conjunction with the HongJun simulator end project. Link to the simulator end project: [HongJunSimulator](https://github.com/CGandGameEngineLearner/HongJunSimulator)

## 注意事项
本项目必须使用**Python 3.9.13**版本
配置开发环境前务必查看requirements.txt，并使用它来配置依赖库
把settings_无人机突防.json复制到User/Documents/AirSim目录下，并改名为settings.json覆盖原先的settings.json

**如果您在使用此项目时遇到困难，可以提`Issue`或编辑邮件并发送到`lifesize1@qq.com`进行咨询，如果你愿意向[联合国近东救济工程处](https://donate.unrwa.org/gaza/~my-donation)捐款，或者您本人已有了任何合法的国际慈善项目的捐款证明，我将免费帮您解决问题。**

## Notes
This project must use Python version 3.9.13.

Before configuring the development environment, be sure to check the requirements.txt and use it to configure the dependencies.

Copy settings_无人机突防.json to the User/Documents/AirSim directory and rename it to settings.json to overwrite the original settings.json.

**If you have difficulties using this project, you can file an 'Issue' or edit the email and send it to the 'lifesize1@qq.com' for consultation, and if you are willing to donate to [UNRWA](https://donate.unrwa.org/gaza/~my-donation), or if you have proof of donation to any legitimate international charity project, I will help you solve the problem free of charge.**
## 架构说明

![架构图](/illustration/ArchitectureDiagram.png)

## 训练任务案例和训练场景实机演示

### 携带导弹的无人机进行集群对抗 

![携带导弹的无人机进行集群对抗](/illustration/DroneWithMission.gif)

### 无人机海上突防

![无人机海上突防](/illustration/DroneBreakout.gif)

## 工程文件结构说明

### HongJun\SimulatorControlDriver

此目录为是负责无人机模拟器(即鸿钧无人机作战仿真模拟平台)进行连接和控制的驱动模块

### HongJun\Tasks\CustomTasks

此目录下存放了无人机飞行任务的程序，若用户需要自定义新的无人机飞行任务，那么请在此目录下新建 Python 软件包，并在其中编写 Python 程序控制无人机。每个飞行任务的 Python 软件包之间不要有相互依赖的关系，相互独立，互不影响。不要出现 TaskB import 了 Task A 的代码的情况。要共用的都放 Libraries 里面。

### HongJun\Tasks\Libraries

此目录下存放了所有飞行任务程序共用的库，如果您自定义的新飞行任务程序需要用某一第三方库或自己写的库，并且这个库会在多次飞行任务中用到，那么请尽量放在这里，一起共用。

### HongJun\SimulatorControlDriver\UClasses.py

在该py代码中定义的是服务端（控制器这端）的与客户端对应的UClass类的对象，以实现同步客户端对象到服务端的功能

### HongJun/SimulatorControlDriver/SimulatorController.py

此py文件实现的是处理模拟器（充当客户端）发来的事件和控制模拟器的逻辑

## 如何自定义飞行任务？

在 `HongJun\Tasks\CustomTasks` 目录下新建 Python 软件包作为你自定义的飞行任务的软件包，并在其中编写 Python 程序控制无人机。每个飞行任务的 Python 软件包之间不要有相互依赖的关系，相互独立，互不影响。不要出现 TaskB import 了 Task A 的代码的情况。要共用的都放 `HongJun/DroneTasks/Libraries` 里面。

每个飞行任务文件下至少需要以下文件：

-   **init.py**: Python software package initialization file
-   **Config.yml**: This is a configuration file. It is recommended to consolidate all the configuration information required for your custom flight mission programs here. It mainly stores the listening address of the Socket server. When creating a new flight mission, make sure to configure the listening address of the Socket server in this file. Each flight mission uses its corresponding Config.yml file in its respective directory for configuration information. They are independent and do not affect each other.
-   **main.py**: Your custom flight mission logic is primarily written here. To run it, execute this Python file.

例如，这里新建了一个 TestTask1
![新建了一个TestTask1](/illustration/TestTask1.png)

### Config.yml 文件的示例内容：

```
# The ConnectSystem in Unreal Engine is client.
# The SimulatorConnector in python is server.
# 在虚幻引擎中的ConnectSystem是客户端
# SimulatorConnector这边是服务端
server:
  host: 127.0.0.1
  port: 3000
```

### main.py 的示例内容(HongJun/Tasks/CustomTasks/TestTask1/main.py)：

```python
from HongJun.SimulatorControlDriver.SimulatorController import SimulatorController,name_drone
from HongJun.Tasks.Libraries.ODE.controller_3 import control_formation
import random
import time
import numpy as np
from loguru import logger
import airsim

def reverse(x: float) -> float:
    return -x

origin_x = [-24, -20, -16, -12, -8, -4, -0, 4, 8, 12]  # 无人机初始位置
origin_y = [0, 5, 0, 5, 0, 5, 0, 5, 0, 5]
num_agents = 10
enemy_num = 4
step = 50
velocity = 8
if __name__ == '__main__':
    simulator_controller = SimulatorController()
    client = simulator_controller.simulator_connector.airsim_client
    time.sleep(6)
    # simulator_controller.drones[0].moveToPositionAsync(-150.0, 10, -30, 15)
    # # asyncio.run(simulator_controller.simulator_connector.ws_server.sio.emit(event='attack', data='{"test":"ssssssssss"}',namespace='/'))
    # time.sleep(10)
    # simulator_controller.drones[0].attack(simulator_controller.drones[1])
    # # asyncio.run(simulator_controller.drones[1].attack(simulator_controller.drones[0]))
    # logger.info("已经发送完了开火指令")
    #
    # time.sleep(6)
    for i in range(num_agents + enemy_num):
        name = "UAV" + str(i + 1)
        simulator_controller.simulator_connector.airsim_client.enableApiControl(True, name)  # 获取控制权
        simulator_controller.simulator_connector.airsim_client.armDisarm(True, name)  # 解锁（螺旋桨开始转动）
        if i != num_agents - 1:  # 起飞
            simulator_controller.simulator_connector.airsim_client.takeoffAsync(vehicle_name=name)
        else:
            simulator_controller.simulator_connector.airsim_client.takeoffAsync(vehicle_name=name).join()

    for i in range(num_agents + enemy_num):  # 全部都飞到同一高度层
        name = "UAV" + str(i + 1)

        logger.info(i)
        if i != num_agents - 1:
            simulator_controller.simulator_connector.airsim_client.moveToZAsync(-8, 4, vehicle_name=name)
        else:
            simulator_controller.simulator_connector.airsim_client.moveToZAsync(-8, 4, vehicle_name=name).join()

    posalive = np.array([origin_x, origin_y, ], dtype=np.longdouble)

    stateMats = control_formation(posalive)

    path = [[0] * step for _ in range(num_agents)]
    j = 0
    for posinfo in stateMats:
        k = 0
        for i in range(num_agents):
            pos = airsim.Vector3r()
            pos.x_val = posinfo[k] - origin_x[i]
            pos.y_val = posinfo[k + 1] - origin_y[i]
            pos.z_val = -8
            print(i, pos)
            path[i][j] = pos
            k += 2
        j += 1

    for i in range(num_agents):
        name = "UAV" + str(i + 1)
        if i != num_agents - 1:
            simulator_controller.simulator_connector.airsim_client.moveOnPathAsync(path[i], velocity, vehicle_name=name)
        else:
            simulator_controller.simulator_connector.airsim_client.moveOnPathAsync(path[i], velocity,
                                                                                   vehicle_name=name).join()
    time.sleep(5)

    temppos = []
    for i in range(num_agents):
        path = []
        name = "UAV" + str(i + 1)
        pos = airsim.Vector3r()
        state_multirotor = client.getMultirotorState(name)
        x = state_multirotor.kinematics_estimated.position.x_val
        y = state_multirotor.kinematics_estimated.position.y_val
        pos.x_val = x
        pos.y_val = y
        temppos.append(pos)
        x = x - 100
        path.append(pos)

        if i != num_agents - 1:
            client.moveToPositionAsync(x, y, -8, velocity, vehicle_name=name)
        else:
            client.moveToPositionAsync(x, y, -8, velocity, vehicle_name=name).join()

    # simulator_controller.drones[1].attack(simulator_controller.drones[0])

    time.sleep(4)
    for i in range(1, 11):
        name = "UAV" + str(i)
        pos = airsim.Vector3r()
        state_multirotor = client.getMultirotorState(name)
        print(state_multirotor.kinematics_estimated.position.x_val + 20,
              state_multirotor.kinematics_estimated.position.y_val,
              state_multirotor.kinematics_estimated.position.z_val)

    # g1 = [2, 3]
    g1 = [1, 2, 3, 5]
    g2 = [4, 7, 8]
    g3 = [6, 9, 10]

    name_list = []
    done_list = []

    for i in simulator_controller.drones:
        name_list.append(i.name)
    index = list(range(num_agents + enemy_num))
    drone_zip = dict(zip(name_list, index))


    def MoveGroup1(move_x=-10):
        for i in g1:
            name = "UAV" + str(i)
            # pos_i = get_UAV_pos_enemy(client, vehicle_name=name_i)??????????????????????????????
            state_multirotor = client.getMultirotorState(name)
            x = state_multirotor.kinematics_estimated.position.x_val
            y = state_multirotor.kinematics_estimated.position.y_val
            client.moveOnPathAsync([airsim.Vector3r(x + move_x, y, -8)], velocity, vehicle_name=name)


    def MoveGroup2(move_x=-44, move_y=-35, move_z=0):
        print("g2 go...")
        for i in g2:
            name = "UAV" + str(i)
            # pos_i = get_UAV_pos(client, vehicle_name=name_i)
            state_multirotor = client.getMultirotorState(name)
            x = state_multirotor.kinematics_estimated.position.x_val
            y = state_multirotor.kinematics_estimated.position.y_val
            client.moveOnPathAsync([airsim.Vector3r(x, y - move_y, -8 + move_z),
                                    airsim.Vector3r(x + move_x, y - move_y, -8 + move_z)], velocity*2, vehicle_name=name)


    def MoveGroup3(move_x=-50, move_y=-35, move_z=0):
        print("g3 go...")
        for i in g3:
            name = "UAV" + str(i)
            # pos_i = get_UAV_pos(client, vehicle_name=name_i)
            state_multirotor = client.getMultirotorState(name)
            x = state_multirotor.kinematics_estimated.position.x_val
            y = state_multirotor.kinematics_estimated.position.y_val
            # if i == g4[-1]:
            #     client.moveOnPathAsync([airsim.Vector3r(x, y + move_y, -8 + move_z),
            #                             airsim.Vector3r(x + move_x, y + move_y, -8 + move_z)], velocity,
            #                            vehicle_name=name).join()
            # else:
            client.moveOnPathAsync([airsim.Vector3r(x, y + move_y, -8 + move_z),
                                    airsim.Vector3r(x + move_x, y + move_y, -8 + move_z)], velocity*2, vehicle_name=name)


    enemy_group = [11, 12, 13, 14]


    def MoveEnemy():
        for i in g1:
            name = "UAV" + str(i)
            if name_drone[name].is_destoried==0 and name_drone["UAV12"].is_destoried==0:
                simulator_controller.drones[drone_zip[name]].attack(simulator_controller.drones[drone_zip["UAV12"]])
            if name_drone[name].is_destoried==0 and name_drone["UAV13"].is_destoried==0:
                simulator_controller.drones[drone_zip[name]].attack(simulator_controller.drones[drone_zip["UAV13"]])
        for i in enemy_group:
            name = "UAV" + str(i)
            # pos_i = get_UAV_pos(client, vehicle_name=name_i)
            state_multirotor = client.getMultirotorState(name)
            x = state_multirotor.kinematics_estimated.position.x_val
            y = state_multirotor.kinematics_estimated.position.y_val
            z = state_multirotor.kinematics_estimated.position.z_val
            # if i == g4[-1]:
            #     client.moveOnPathAsync([airsim.Vector3r(x+40, y , z)], velocity//2,
            #                            vehicle_name=name).join()
            # else:
            client.moveOnPathAsync([airsim.Vector3r(x + 20, y, z)], velocity // 2,
                                   vehicle_name=name)



    MoveGroup2()
    MoveGroup3()
    MoveGroup1()
    MoveEnemy()



    # for i in range(num_agents):
    #     path = []
    #     name = "UAV" + str(i + 1)
    #     pos = airsim.Vector3r()
    #     state_multirotor = client.getMultirotorState(name)
    #     x = state_multirotor.kinematics_estimated.position.x_val
    #     y = state_multirotor.kinematics_estimated.position.y_val
    #     print(name, " arrive: ", x, y)





    def our_attack(t=False):

        for i in g1:
            name = "UAV" + str(i)
            if name_drone[name].is_destoried==0 and name_drone["UAV12"].is_destoried==0:
                simulator_controller.drones[drone_zip[name]].attack(simulator_controller.drones[drone_zip["UAV12"]])
            if name_drone[name].is_destoried==0 and name_drone["UAV13"].is_destoried==0:
                simulator_controller.drones[drone_zip[name]].attack(simulator_controller.drones[drone_zip["UAV13"]])
        if t:
            for i in g2:
                name = "UAV" + str(i)
                if name_drone[name].is_destoried==0 and name_drone["UAV11"].is_destoried==0:
                    simulator_controller.drones[drone_zip[name]].attack(simulator_controller.drones[drone_zip["UAV11"]])
            for i in g3:
                name = "UAV" + str(i)
                if name_drone[name].is_destoried==0 and name_drone["UAV14"].is_destoried==0:
                    simulator_controller.drones[drone_zip[name]].attack(simulator_controller.drones[drone_zip["UAV14"]])
    time.sleep(5)
    our_attack()
    time.sleep(1)
    # time.sleep(10)
    def Drone_move(i, x_, y_, z_, speed):
        logger.info(str(i)+" move...")
        name = "UAV" + str(i)
        logger.info(name)
        # pos_i = get_UAV_pos(client, vehicle_name=name_i)
        state_multirotor = client.getMultirotorState(vehicle_name =name)
        x = state_multirotor.kinematics_estimated.position.x_val
        y = state_multirotor.kinematics_estimated.position.y_val
        z = state_multirotor.kinematics_estimated.position.z_val
        client.moveToPositionAsync(x-x_, y-y_, z-z_, speed, vehicle_name=name)

    def forward():
        count = 1
        while name_drone["UAV11"].is_destoried==0 or name_drone["UAV12"].is_destoried==0 \
            or name_drone["UAV13"].is_destoried==0 or name_drone["UAV14"].is_destoried==0:
                for i in range(14):
                    name = "UAV" + str(i+1)
                    if name_drone[name].is_destoried == 0:
                            Drone_move(i + 1, 8, 0, 0, velocity//4)
                if count % 5==0:
                    name_drone["UAV11"].attack(name_drone["UAV1"])
                    name_drone["UAV12"].attack(name_drone["UAV2"])
                    name_drone["UAV13"].attack(name_drone["UAV3"])
                    name_drone["UAV14"].attack(name_drone["UAV4"])
                    our_attack(True)
                    time.sleep(1)
                    break
                count+=1
                time.sleep(2)

    forward()
    logger.info(" attack over")



    donedronenum = [1, 2,3,4,  10,11, 12, 13]
    donedronedit = {'1': [1, 2, 3, 4,  11, 12, 13,14],
                    '2': [2, 3, 4, 5,  11, 12, 13,14],
                    '3': [1, 2, 6, 9,  11, 12, 13,14],
                    '4': [5, 7, 8, 4,  11, 12, 13,14],
                    '5': [2, 3, 6,   11, 12, 13,14]}
    random.seed(time.perf_counter())
    order = random.randint(1, 5)
    donedronenum = donedronedit[str(order)]
    #donedronenum =[1, 2, 6, 9, 11, 12, 13,14]
    print("donedrone", donedronenum)
    lendonedrone = len(donedronenum)



    for i in donedronenum:
        name = "UAV" + str(i)
        logger.info("--"+name+" drop ")
        #if name_drone[name].is_destoried == 0:
            # client.moveToZAsync(0, velocity, timeout_sec=3e+38, vehicle_name=name)

    count = 0
    for i in range(num_agents):
        if i+1 not in donedronenum:
            name = "UAV" + str(i + 1)
            x = temppos[count].x_val + origin_x[count] - origin_x[i] - 150
            y = temppos[count].y_val + origin_y[count] - origin_y[i]
            try:
                if count !=  num_agents+4 - lendonedrone - 1 :
                    client.moveToPositionAsync(x, y, -8, velocity, vehicle_name=name)
                else:
                    client.moveToPositionAsync(x, y, -8, velocity, vehicle_name=name).join()
            except:
                logger.warning("有无人机被摧毁了，不能指挥其行动")
            count += 1

    count = 0
    time.sleep(5)
    for i in range(num_agents):
        if i+1 not in donedronenum:
            path = []
            name = "UAV" + str(i + 1)
            pos = airsim.Vector3r()
            state_multirotor = client.getMultirotorState(name)
            x = state_multirotor.kinematics_estimated.position.x_val
            y = state_multirotor.kinematics_estimated.position.y_val
            pos.x_val = x
            pos.y_val = y
            temppos.append(pos)
            x = x - 600
            path.append(pos)

            if count != 5:
                client.moveToPositionAsync(x, y, -15, 16, vehicle_name=name)
            else:
                client.moveToPositionAsync(x, y, -15, 16, vehicle_name=name).join()
            count += 1

```

这是无人机海上突防任务的代码，在打开相应模拟器环境的情况下，运行该HongJun/DroneTasks/TestTask1/main.py就可以看到对应的效果。

## 项目规范

### 命名规范

#### 文件名

尽量使用驼峰命名法，以减短文件路径长度,例如
![新建了一个TestTask1](/illustration/TestTask1.png)

#### 类名

尽量使用驼峰命名法，例如:

```
class SimulatorController:
```

#### 变量名

尽量使用下划线命名法

### DebugLog

建议使用 loguru 这个库来打印日志，因为它会标注 DebugLog 的代码位置，而且打印出来的字体和颜色看起来都很舒服！

```python
from loguru import logger
logger.info()
```

![DebugLog](/illustration/DebugLog.png)

