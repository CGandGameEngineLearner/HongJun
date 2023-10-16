#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import rospy

import airsim
from airsim.client import Pose

from geometry_msgs.msg import PoseStamped



import numpy as np

from geometry_msgs.msg import Point32
from sensor_msgs.msg import LaserScan, PointCloud2
from sensor_msgs.msg import PointField
from std_msgs.msg import Header
from sensor_msgs import point_cloud2

HOST = '172.24.240.1'
def pub_pointcloud(points):
    pc = PointCloud2()
    pc.header.stamp = rospy.Time.now()
    pc.header.frame_id = 'world'
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

def publishPose(pose_stamped_pub:rospy.Publisher,drone_pose:Pose):
    p_x=drone_pose.position.x_val
    p_y=drone_pose.position.y_val
    p_z=drone_pose.position.z_val


    o_x=drone_pose.orientation.x_val
    o_y=drone_pose.orientation.y_val
    o_z=drone_pose.orientation.z_val
    o_w=drone_pose.orientation.w_val

    pose_stamped = PoseStamped()
    pose_stamped.header.stamp = rospy.Time.now()
    pose_stamped.header.frame_id = "world"
    pose_stamped.pose.position.x = p_x
    pose_stamped.pose.position.y = p_y
    pose_stamped.pose.position.z = -p_z
    pose_stamped.pose.orientation.x = o_x
    pose_stamped.pose.orientation.y = o_y
    pose_stamped.pose.orientation.z = -o_z
    pose_stamped.pose.orientation.w = -o_w
    pose_stamped_pub.publish(pose_stamped)


def main():
    # connect the simulator
    client = airsim.MultirotorClient(ip=HOST)
    client.confirmConnection()
    # client.enableApiControl(True)
    client.armDisarm(True)

    pointcloud_pub = rospy.Publisher('/co_sim_drone_points', PointCloud2, queue_size=10)
    pointcloud_tank_pub = rospy.Publisher('/co_sim_tank_points', PointCloud2, queue_size=10)
    pose_stamped_pub = rospy.Publisher('/drone_pose', PoseStamped, queue_size=10)


    rate = rospy.Rate(25.0)

    while not rospy.is_shutdown():

        drone_pose=client.simGetVehiclePose(vehicle_name="drone_1")

        publishPose(pose_stamped_pub,drone_pose)
        # get the lidar data
        lidarData = client.getLidarData(lidar_name='LidarCustom',vehicle_name='drone_1')
        lidarDate_tank=client.getLidarData(lidar_name='LidarCustom',vehicle_name='tank')
        # print('lidar',lidarData)

        if len(lidarData.point_cloud) > 3:

            points = np.array(lidarData.point_cloud, dtype=np.dtype('f4'))
            points = np.reshape(points, (int(points.shape[0] / 3), 3))
            # points[:, 1] = -points[:, 1]
            points[:, 2] = -points[:, 2]
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
            print("No points received from Drone Lidar data")

        if len(lidarDate_tank.point_cloud) > 3 and False:

            points = np.array(lidarDate_tank.point_cloud, dtype=np.dtype('f4'))
            points = np.reshape(points, (int(points.shape[0] / 3), 3))
            # points[:, 1] = -points[:, 1]
            points[:, 0] = -points[:, 0]
            points[:, 1] = -points[:, 1]
            points[:, 2] = -points[:, 2]
            num_temp = np.shape(points)[0]
            # print(num_temp)
            numpy_temp = np.zeros(num_temp)
            numpy_temp1 = np.ones(num_temp)
            # print(numpy_temp)
            # points = np.c_[points,numpy_temp1,numpy_temp,numpy_temp]
            points = np.c_[points, numpy_temp1]

            # print('points:',points)
            pc = pub_pointcloud(points)

            pointcloud_tank_pub.publish(pc)
            rate.sleep()
        # else:
        #     print("No points received from Tank Lidar data")


if __name__ == "__main__":
    rospy.init_node('co_sim')
    main()