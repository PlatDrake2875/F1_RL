import gymnasium as gym
from gymnasium.envs.registration import register


gym.envs.registration.register(
    id='F1Env-v0',
    entry_point='environments.car_env:F1_Env',
)
env = gym.make('F1Env-v0', render_mode='human')

# Initialize the environment
observation = env.reset()

# Now you can render the environment
env.render()

# To keep the window open and render continuously, you might need a loop
# For example, a simple loop that runs for a few steps
for _ in range(10000):
    action = env.action_space.sample()  # Replace this with your action selection mechanism
    observation, reward, done, _, info = env.step(action)
    env.render()
    if done:
        env.reset()

# Remember to close the environment properly
env.close()
