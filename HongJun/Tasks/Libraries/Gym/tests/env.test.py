from HongJun.Tasks.Libraries.Gym.envs.drone_env import DroneEnv

def model():
    pass

env = DroneEnv()
observation = env.reset()
for _ in range(1000):
    action = model.predict(observation) # TODO
    observation, reward, done, info = env.step(action)
    if done:
        observation = env.reset()

env.close()
