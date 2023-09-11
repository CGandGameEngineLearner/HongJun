import gymnasium as gym
from gym import spaces
import numpy as np
from HongJun.SimulatorControlDriver.SimulatorController import SimulatorController, name_drone

class MultiAgentDroneEnv(gym.Env):
    def __init__(self):
        super(MultiAgentDroneEnv, self).__init__()

        self.agents = ["agent0", "agent1"]
        self._agent_ids = set(self.agents)

        self.dones = set()

        self.simulator_controller = SimulatorController()

        self.action_space = spaces.Dict({agent: spaces.Discrete(3) for agent in self.agents})  # Define your action space here
        self.observation_space = spaces.Dict({agent: spaces.Box(low=np.array([-np.inf]*10), high=np.array([np.inf]*10)) for agent in self.agents})  # Define your observation space here

    def step(self, actions: dict):
        # Step each agent and gather results
        obs, rewards, dones, infos = {}, {}, {}, {}
        for agent_id, action in actions.items():
            obs[agent_id], rewards[agent_id], dones[agent_id], infos[agent_id] = self.simulator_controller.apply_action(agent_id, action)
            if dones[agent_id]:
                self.dones.add(agent_id)
        return obs, rewards, dones, infos

    def reset(self) -> dict:
        # Reset the environment to its initial state
        self.dones = set()
        self.simulator_controller = SimulatorController()
        obs = {agent: self.simulator_controller.get_initial_observation(agent) for agent in self.agents}
        return obs

    def render(self, mode='human'):
        # Render the environment to the screen
        pass
