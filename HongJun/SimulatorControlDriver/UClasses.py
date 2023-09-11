import asyncio

from airsim.types import *
from loguru import logger

from HongJun.SimulatorControlDriver.SimulatorConnector import SimulatorConnector
import threading
import json

from panda3d.core import Vec3 as FVector # 所有三维向量用这个表示

# for python version<3.9
from typing import Dict as dict
from typing import List as list
# --------------------------------


class UObject:
    ObjectName:str=''
    Commponents = []


class UActorCommponent(UObject):
    FatherUObject: UObject

    def __init__(self, FatherUObject: UObject):
        self.FatherUObject = FatherUObject
        FatherUObject.Commponents.append(self)


class UMovementComponent(UActorCommponent):
    """
        提供Pawn类物体的移动功能的基础组件
    """
    _Velocity: FVector  # 该物体的运动速度矢量
    _FowardVector: FVector  # 该物体的向前向量
    _Speed: float  # 该物体的运动速率

    def setVelocity(self, velocity: FVector):
        self._Velocity = velocity
        self._Speed = np.linalg.norm(velocity)

    def getVelocity(self) -> FVector:
        return self._Velocity;

    def getSpeed(self):
        return self._Speed;

    def getFowardVector(self):
        return self._FowardVector




class USceneComponent(UActorCommponent):
    """
        场景组件用于记录相对和绝对的坐标、旋转、缩放
    """
    RelativeLocation: FVector
    RelativeRotation: FVector
    RelativeScale3D: FVector
    Parent:UObject
    def __init__(self,parent:UObject,relative_location: FVector,relative_rotation: FVector,relative_scale3D: FVector):
        self.RelativeLocation=relative_location
        self.RelativeRotation=relative_rotation
        self.RelativeScale3D=relative_scale3D
        self.Parent=parent

    def setTransform(self,relative_location: FVector,relative_rotation: FVector,relative_scale3D: FVector):
        self.RelativeLocation=relative_location
        self.RelativeRotation=relative_rotation
        self.RelativeScale3D=relative_scale3D
    def getRelativeLocation(self)->FVector:
        if isinstance(self.Parent,USceneComponent):
            location=self.RelativeLocation+self.Parent.getRelativeLocation();
            return location

        return self.RelativeLocation

    def getRelativeScale3D(self) -> FVector:
        if isinstance(self.Parent, USceneComponent):
            scale3D = self.RelativeScale3D*self.Parent.getRelativeScale3D();
            return scale3D
        return self.RelativeRotation

    def getRelativeRotation(self)->FVector:
        if isinstance(self.Parent,USceneComponent):
            rotaiton=self.RelativeRotation+self.Parent.getRelativeRotation();
            return rotaiton

        return self.RelativeLocation

class AActor(UObject):
    Tags: []  # Actor.tag列表

    def __init__(self, object_name:str, absolute_location: FVector, absolute_rotation: FVector, absolute_scale3D: FVector):
        self.ObjectName=object_name
        self.Commponents.append(USceneComponent(parent=self, relative_location=absolute_location, relative_rotation=absolute_rotation, relative_scale3D=absolute_scale3D))

    def setTransform(self,absolute_location: FVector,absolute_rotation: FVector,absolute_scale3D: FVector):
        assert isinstance(self.Commponents[0],USceneComponent)
        self.Commponents[0].setTransform(relative_location=absolute_location,relative_rotation=absolute_rotation,relative_scale3D=absolute_scale3D)



class UWorld(UObject):
    ObjectNameToActors={}

    def addActor(self,actor:AActor):

        self.ObjectNameToActors[actor.ObjectName]=actor

    def GetAllActorsOfClass(self,ClassType)->list[AActor]:
        result:list[AActor]
        for actor in self.ObjectNameToActors.values():
            if isinstance(actor,ClassType):
                result.append(actor)
        return result

    def updateActorTransform(self,object_name:str,absolute_location: FVector,absolute_rotation: FVector,absolute_scale3D: FVector):
        if object_name in self.ObjectNameToActors:
            self.ObjectNameToActors[object_name].setTransform(absolute_location=absolute_location,absolute_rotation=absolute_rotation,absolute_scale3D=absolute_scale3D)

    def updateActor(self,actor_name:str,absolute_location: FVector,absolute_rotation: FVector,absolute_scale3D: FVector):
        if actor_name in self.ObjectNameToActors:
            # print(type(self.ObjectNameToActors[actor_name]))
            self.ObjectNameToActors[actor_name].setTransform(absolute_location=absolute_location, absolute_rotation=absolute_rotation, absolute_scale3D=absolute_scale3D)
        else:
            self.ObjectNameToActors[actor_name]=AActor(object_name=actor_name, absolute_location=absolute_location, absolute_rotation=absolute_rotation, absolute_scale3D=absolute_scale3D)


class APawn(AActor):
    MovementComponent: UMovementComponent


class ADrone(APawn):
    # 为了让Drone更好用，很多属性都设置为了私有属性，但提供get和set方法，防止乱改出错。

    simulator_connector: SimulatorConnector
    name: str  # 每个无人机唯一的名称
    team: str  # 无人机所属阵营 红1蓝0

    is_destoried: int  # 无人机损毁状态 值为1表示活着 0是被摧毁了
    atk_msl_num: int  # 无人机攻击类导弹的剩余数量
    def_msl_num: int  # 无人机防御类导弹的剩余数量
    acc_mag: float  # 无人机加速度大小

    # 经度、纬度、海拔高度在模拟器中转换为x、y、z代替
    _lat: float  # 纬度（模拟器里面的世界是超平坦的，不是球体，但是可以看作它是墨卡托投影得到的世界地图）
    _lon: float  # 经度（模拟器中的x轴、y轴，在现实中会被经度和纬度代替，x轴坐标转化为经度，y轴坐标转化为纬度）
    _alt: float  # 海拔高度 （在现实中模拟器中的z轴坐标会转化为海拔高度）
    state_multirotor: MultirotorState  # airsim状态

    class AttackThread (threading.Thread):
        def __init__(self, my_drone, name:str, target_of_attack: AActor):
            threading.Thread.__init__(self)
            self.my_drone:ADrone=my_drone
            self.name = name

            self.target_of_attack=target_of_attack

        def run(self):
            asyncio.run(self.attack(self.target_of_attack))

        async def attack(self, target_of_attack: AActor):
            '''
            args:
                target_of_attack:Actor 该Drone需要攻击的Actor，当其值为None时(即未明确指定攻击对象时)，它会攻击它第一个遇到的敌人
            '''
            if self.my_drone.is_destoried == 1:
                logger.warning(self.name + "已经被摧毁")
                return
            if target_of_attack is None:
                logger.info(self.name + "的指定攻击目标为不存在，所以攻击它射程范围内第一个遇到的敌人")
                attack_command = {"drone_name": self.my_drone.name, "target_actor": "null"}
                command_json = json.dumps(attack_command)
                await self.my_drone.simulator_connector.ws_server.sio.emit(event='attack', data=command_json, namespace='/')
                logger.info("指令发送完毕")
            elif type(target_of_attack) == ADrone:
                logger.info(self.name + "的指定目标为Drone类对象"+target_of_attack.name)
                attack_command = {"drone_name": self.my_drone.name, "target_actor": target_of_attack.name}
                command_json = json.dumps(attack_command)
                await self.my_drone.simulator_connector.ws_server.sio.emit(event='attack', data=command_json, namespace='/')
                logger.info("指令发送完毕")
            else:
                logger.warning("暂时不支持除了Drone类对象和空对象以外的其他类型的对象，作为攻击目标")

    def __init__(self, simulator_connector: SimulatorConnector, name: str, id: int, state_multirotor: MultirotorState,
                 team: str, atk_msl_num: int, def_msl_num: int, absolute_location:FVector, absolute_rotation:FVector, absolute_scale3D:FVector):
        """初始化无人机实例
        args:
            id:int 无人机的唯一id
            tag:[] 无人机在虚幻引擎中的Actor.tag列表,由str组成的列表，其每一个元素都必须是str类型
            position:np.ndarray 表示无人机坐标的三维向量
            atk_msl_num:int # 无人机攻击类导弹的剩余数量
            def_msl_num:int # 无人机防御类导弹的剩余数量
        return:
            None
            :param absolute_scale3D:
        """
        super().__init__(object_name=name,absolute_location=absolute_location,absolute_rotation=absolute_rotation,absolute_scale3D=absolute_scale3D)
        self.simulator_connector = simulator_connector
        self._id = id
        self.name = name
        self.is_destoried = 0;
        self.team = team
        self.def_msl_num = def_msl_num
        self.atk_msl_num = atk_msl_num
        self.state_multirotor = state_multirotor

    def attack(self, target_of_attack: AActor):
        try:
            attack_thread=self.AttackThread(self,name=self.name+" attack_thread",target_of_attack=target_of_attack)
            attack_thread.start()
        except:
            logger.warning("攻击命令发送过程出现异常")

    def moveToPositionAsync(self, x, y, z, velocity, timeout_sec=3e+38, drivetrain=DrivetrainType.MaxDegreeOfFreedom,
                            yaw_mode=YawMode(),
                            lookahead=-1, adaptive_lookahead=1):
        logger.info(self.name+"开始飞行")
        self.simulator_connector.airsim_client.moveToPositionAsync(x, y, z, velocity, timeout_sec, drivetrain, yaw_mode, lookahead, adaptive_lookahead, vehicle_name=self.name)

    def landAsync(self,timeout_sec = 60):
        self.simulator_connector.airsim_client.landAsync(timeout_sec = timeout_sec, vehicle_name = self.name)

    def moveOnPathAsync(self,path, velocity, timeout_sec = 3e+38, drivetrain = DrivetrainType.MaxDegreeOfFreedom, yaw_mode = YawMode(),
        lookahead = -1, adaptive_lookahead = 1):
        self.simulator_connector.airsim_client.moveOnPathAsync(path, velocity, timeout_sec = timeout_sec, drivetrain = drivetrain, yaw_mode = yaw_mode,
                                                               lookahead = lookahead, adaptive_lookahead = adaptive_lookahead, vehicle_name = self.name)

    def moveToZAsync(self, z, velocity, timeout_sec = 3e+38, yaw_mode = YawMode(), lookahead = -1, adaptive_lookahead = 1):
        self.simulator_connector.airsim_client.moveToZAsync(z, velocity, timeout_sec = timeout_sec, yaw_mode = yaw_mode, lookahead = lookahead, adaptive_lookahead = adaptive_lookahead)

    def enableApiControl(self,is_enabled:bool):
        self.simulator_connector.airsim_client.enableApiControl(is_enabled, vehicle_name =self.name)

    def armDisarm(self,arm:bool):
        self.simulator_connector.airsim_client.armDisarm(arm, vehicle_name = self.name)


if __name__ == "__main__":
    pass