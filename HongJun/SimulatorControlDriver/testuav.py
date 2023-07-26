import airsim

client = airsim.MultirotorClient()  # connect to the AirSim simulator



name = "UAV1"
client.enableApiControl(True, name)     # 获取控制权
client.armDisarm(True, name)    
client.takeoffAsync(vehicle_name=name).join()
client.moveToPositionAsync( 4500, 4500, -8, 5,vehicle_name = name).join()
client.moveToZAsync(-8, 1, vehicle_name=name)
print("hello")


