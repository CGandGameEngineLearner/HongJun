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
