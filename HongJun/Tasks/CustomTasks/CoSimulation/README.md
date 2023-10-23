# 运行环境要求：
Ubuntu20
Python3.8.10
ROS
# 快速开始

先把本项目的AirSim的setting.json放到~/Documents/AirSim/settings.json
```shell
sudo cp ./settings.json ~/Documents/AirSim/
```

打开模拟器端CoSimulation，然后开始运行

在本项目的CoSimulation目录下打开终端 输入以下命令启动ROS
```shell
roscore
rviz -d co_sim.rviz
```
再打开个终端，输入
```shell
python3 main.py
```
此时rviz内能显示图像即为成功
再打开个终端输入以下命令开始录制
```shell
rosbag record -a
```