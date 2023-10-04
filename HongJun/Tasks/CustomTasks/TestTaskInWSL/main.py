import airsim
import os
HOST = '172.24.240.1' # Standard loopback interface address (localhost)
from platform import uname
if 'linux' in uname().system.lower() and 'microsoft' in uname().release.lower(): # In WSL2
    if 'WSL_HOST_IP' in os.environ:
        HOST = os.environ['WSL_HOST_IP']
print("Using WSL2 Host IP address: ", HOST)

# 初始化，建立连接
client = airsim.MultirotorClient(ip=HOST)
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)
client.moveToPositionAsync(-100, 100, -1, 5).join()