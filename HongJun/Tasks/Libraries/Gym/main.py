import gym
from gym import spaces
import numpy as np
import airsim

class CustomDroneEnv(gym.Env):
    def __init__(self):
        super(CustomDroneEnv, self).__init__()

        # Connect to the AirSim simulator 
        self.client = airsim.MultirotorClient()
        self.client.confirmConnection()
        self.client.enableApiControl(True)
        self.client.armDisarm(True)

        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions and Box observation space:
        self.action_space = spaces.Discrete(4)  # up, down, left, right
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(3,))  # x, y, z coordinates

    def step(self, action):
        # Execute one time step within the environment
        if action == 0:
            self.client.moveByVelocityZAsync(1, 0, 0, 1)  # move up
        elif action == 1:
            self.client.moveByVelocityZAsync(-1, 0, 0, 1)  # move down
        elif action == 2:
            self.client.moveByVelocityAsync(0, 1, 0, 1)  # move right
        elif action == 3:
            self.client.moveByVelocityAsync(0, -1, 0, 1)  # move left

        # Assume for now that the drone receives a reward of 1 for each step it takes
        reward = 1.0
        done = False

        # Get drone's position
        drone_state = self.client.getMultirotorState()
        position = drone_state.kinematics_estimated.position
        obs = np.array([position.x_val, position.y_val, position.z_val])

        return obs, reward, done, {}

    def reset(self):
        # Reset the state of the environment to an initial state
        self.client.reset()
        self.client.enableApiControl(True)
        self.client.armDisarm(True)

        # Get drone's position
        drone_state = self.client.getMultirotorState()
        position = drone_state.kinematics_estimated.position
        obs = np.array([position.x_val, position.y_val, position.z_val])

        return obs

    def render(self, mode='human'):
        # No rendering interface for AirSim, can consider using print for debugging
        pass

    def close(self):
        # Cleanup connection when done
        self.client.armDisarm(False)
        self.client.enableApiControl(False)
