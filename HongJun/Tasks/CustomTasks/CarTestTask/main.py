# ready to run example: PythonClient/car/hello_car.py
import airsim
import time

# connect to the AirSim simulator
client = airsim.CarClient()
client.confirmConnection()
client.enableApiControl(True)
car_controls = airsim.CarControls()

while True:
    # get state of the car
    car_state = client.getCarState()
    print("Speed %d, Gear %d" % (car_state.speed, car_state.gear))

    # set the controls for car
    car_controls.throttle = 1
    car_controls.steering = 1
    client.setCarControls(car_controls)

    # let car drive a bit
    time.sleep(1)

    while (True):
        car_state = client.getCarState()

        if (car_state.speed < 5):
            car_controls.throttle = 1.0
        else:
            car_controls.throttle = 0.0



        client.setCarControls(car_controls)
