#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import copy

HOST = '172.24.240.1'
import math

import rospy
# import setup_path
import airsim
import airsim.client

import sys
import time
import argparse
import pprint

import numpy as np

from geometry_msgs.msg import Point32
from sensor_msgs.msg import LaserScan, PointCloud2
from sensor_msgs.msg import PointField
from std_msgs.msg import Header
from sensor_msgs import point_cloud2
import threading
import time

# 无人机飞行范围
range_x=[-200,200]
range_y=[-200,200]

# 无人机采样步长
step=10

# 无人机飞行高度
pos_z=0

#无人机与采到的第一个点的高度距离
delta_z=30

# 采到的第一个点的z轴值
point_z=pos_z
sample_points=[]

# 无人机飞行速度
velocity=3

yaw = 0 * np.pi/180
pitch = -90 * np.pi/180
roll = 0 * np.pi/180

drone1_name:str="drone_1"
# AirSim client
client:airsim.client.MultirotorClient
def generateSamplePoints()->[]:
    sample_points=[]
    current_position=np.array([0,0,pos_z])
    current_position[1] = range_y[0]
    while current_position[1]>=range_y[0] and current_position[1]<=range_y[1]:
        current_position[0]=range_x[0]
        while current_position[0]<=range_x[1]:
            sample_points.append(copy.deepcopy(current_position))
            current_position[0] = current_position[0] + step
        current_position[1]=current_position[1]+step
        while current_position[0] >= range_x[0]:
            sample_points.append(copy.deepcopy(current_position))
            current_position[0] = current_position[0] - step

    print('number of points is :{}'.format(len(sample_points)))
    return  sample_points



def pub_pointcloud(points):
    pc = PointCloud2()
    pc.header.stamp = rospy.Time.now()
    pc.header.frame_id = 'velodyne'
    pc.height = 1
    pc.width = len(points)

    # pc.fields = [
    # 		PointField('x', 0, PointField.FLOAT32, 1),
    # 		PointField('y', 4, PointField.FLOAT32, 1),
    # 		PointField('z', 8, PointField.FLOAT32, 1),
    # 		PointField('intensity', 16, PointField.FLOAT32, 1),
    # 		PointField('ring', 20, PointField.UINT16, 1)]

    # pc.fields = [
    # 		PointField('x', 0, PointField.FLOAT32, 1),
    # 		PointField('y', 4, PointField.FLOAT32, 1),
    # 		PointField('z', 8, PointField.FLOAT32, 1),
    # 		PointField('intensity', 12, PointField.FLOAT32, 1),
    # 		PointField('ring', 16, PointField.UINT16, 1),
    # 		PointField('time', 18, PointField.FLOAT32, 1)]

    pc.fields = [
        PointField('x', 0, PointField.FLOAT32, 1),
        PointField('y', 4, PointField.FLOAT32, 1),
        PointField('z', 8, PointField.FLOAT32, 1),
        PointField('intensity', 12, PointField.FLOAT32, 1)]

    pc.is_bigendian = False
    # pc.point_step = 18
    # pc.point_step = 22
    pc.point_step = 16
    pc.row_step = pc.point_step * points.shape[0]
    pc.is_dense = True

    pc.data = np.asarray(points, np.float32).tostring()

    return pc


def connectROS():

    pointcloud_pub = rospy.Publisher('/velodyne_points', PointCloud2, queue_size=10)
    rate = rospy.Rate(1.0)
    while not rospy.is_shutdown():



        lidarData = client.getLidarData()
        # print('lidar',lidarData)

        if len(lidarData.point_cloud) > 3:
            # print("点云的点数:{}".format(len(lidarData.point_cloud)))
            points = np.array(lidarData.point_cloud, dtype=np.dtype('f4'))
            points = np.reshape(points, (int(points.shape[0] / 3), 3))
            num_temp = np.shape(points)[0]
            # print(num_temp)
            numpy_temp = np.zeros(num_temp)
            numpy_temp1 = np.ones(num_temp)
            # print(numpy_temp)
            # points = np.c_[points,numpy_temp1,numpy_temp,numpy_temp]
            points = np.c_[points, numpy_temp1]

            # print('points:',points)
            pc = pub_pointcloud(points)

            pointcloud_pub.publish(pc)

            # rate.sleep()
        else:
            print("No points received from Lidar data")

def controlDrone(client:airsim.client.MultirotorClient)->None:
    sample_points = generateSamplePoints()
    print("目标采样点个数:{}".format(len(sample_points)))
    for i in range(0,len(sample_points)):
        target_point=sample_points[i]
        x = float(target_point[0])
        y = float(target_point[1])
        z = float(target_point[2])
        print('x=:{} y=:{} z=:{}'.format(x, y, z))
        client.moveToPositionAsync(x=x, y=y, z=z, velocity=velocity).join()




def connectAirSim()->airsim.client.MultirotorClient:
    client = airsim.MultirotorClient(ip=HOST)
    client.confirmConnection()
    # client.enableApiControl(True)
    # client.armDisarm(True)
    return client

class ConnectROSthread(threading.Thread):
    def run(self) -> None:
        print("开始对ROS发送数据")
        connectROS()

class controlDroneThread(threading.Thread):
    def __init__(self,name:str,client:airsim.client.MultirotorClient):
        threading.Thread.__init__(self)
        self.name=name
        self.client=client

    def run(self) -> None:
        controlDrone(self.client)



def checkArrivedTargetPoint(client:airsim.client.MultirotorClient,target_point:airsim.Vector3r,allowable_range_of_error:float)->bool:
    current_position = client.simGetVehiclePose(vehicle_name=drone1_name).position

    print("当前无人机位置x={},y={},z={}".format(current_position.x_val,current_position.y_val,current_position.z_val))
    cx=current_position.x_val
    cy=current_position.y_val
    cz=current_position.z_val

    tx=target_point.x_val
    ty=target_point.y_val
    tz=target_point.z_val

    distance2D:float=((tx-cx)**2+(ty-cy)**2)**0.5
    print("distance2D=:{}".format(distance2D))
    if(distance2D<=allowable_range_of_error):
        print("到达此目标点")
        return True
    return False

def getTargetPoint(sample_points,i):
    target_point = sample_points[i]
    x = float(target_point[0])
    y = float(target_point[1])
    z = float(target_point[2])

    return airsim.Vector3r(x,y,z)

def sendLidarDate(pointcloud_pub,rate):
    lidarData = client.getLidarData()
    print('lidar:{}'.format(len(lidarData.point_cloud)))


    if len(lidarData.point_cloud) > 3:
        # print("点云的点数:{}".format(len(lidarData.point_cloud)))
        print("第一个点的位置：")
        print(lidarData.point_cloud[0])
        point_z=lidarData.point_cloud[2]
        points = np.array(lidarData.point_cloud, dtype=np.dtype('f4'))
        points = np.reshape(points, (int(points.shape[0] / 3), 3))
        num_temp = np.shape(points)[0]
        # print(num_temp)
        numpy_temp = np.zeros(num_temp)
        numpy_temp1 = np.ones(num_temp)
        # print(numpy_temp)
        # points = np.c_[points,numpy_temp1,numpy_temp,numpy_temp]
        points = np.c_[points, numpy_temp1]

        # print('points:',points)
        pc = pub_pointcloud(points)

        pointcloud_pub.publish(pc)

        rate.sleep()
    else:
        print("No points received from Lidar data")
def mainLoop():
    b_loop_flag=True
    connectAirSim()
    sample_points = generateSamplePoints()
    print("目标采样点个数:{}".format(len(sample_points)))
    index_of_target_point=0

    pointcloud_pub = rospy.Publisher('/velodyne_points', PointCloud2, queue_size=10)

    target_point = getTargetPoint(sample_points, index_of_target_point)

    rate = rospy.Rate(25.0)
    sendLidarDate(pointcloud_pub, rate)
    # client.moveToPositionAsync(vehicle_name=drone1_name,x=target_point.x_val, y=target_point.y_val, z=point_z-delta_z, velocity=velocity)


    btakeoff=False

    while not rospy.is_shutdown():
        target_point=getTargetPoint(sample_points,index_of_target_point)
        if checkArrivedTargetPoint(client,target_point,100) or btakeoff==False:
            btakeoff=True
            index_of_target_point=index_of_target_point+1


            # client.moveToPositionAsync(x=target_point.x_val,y=target_point.y_val,z=point_z-delta_z,velocity=velocity)

        target_point = getTargetPoint(sample_points, index_of_target_point)
        x = float(target_point.x_val)
        y = float(target_point.y_val)
        z = float(target_point.z_val)
        print('target_point: x={} y={} z={}'.format(x, y, point_z - delta_z))

        sendLidarDate(pointcloud_pub,rate)








if __name__ == "__main__":
    rospy.init_node('UGV_lidar')

    client=connectAirSim()
    mainLoop()
