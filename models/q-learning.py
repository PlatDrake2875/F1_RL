import gymnasium as gym
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
import pickle


class QLearningAgent:
    def __init__(self, n_actions, gamma=0.9, alpha=0.1, epsilon_start=1.0, epsilon_end=0.01, epsilon_decay=0.995):
        self.n_actions = n_actions
        self.gamma = gamma
        self.alpha = alpha
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        self.q_table = defaultdict(lambda: np.zeros(n_actions))

    def select_action(self, state):
        if np.random.rand() < self.epsilon:
            return np.random.randint(self.n_actions)
        else:
            return np.argmax(self.q_table[state])

    def update_q_table(self, state, action, reward, next_state, done):
        next_max = np.max(self.q_table[next_state]) if not done else 0
        self.q_table[state][action] = self.q_table[state][action] + self.alpha * (
                reward + self.gamma * next_max - self.q_table[state][action])

    def update_epsilon(self):
        self.epsilon = max(self.epsilon * self.epsilon_decay, self.epsilon_end)


def train_agent(env, agent, episodes=5000):
    rewards = []
    for episode in range(episodes):
        state = env.reset()
        state = tuple(map(int, state['position']))  # Simplify state representation
        total_reward = 0
        done = False
        while not done:
            action = agent.select_action(state)
            next_state, reward, done, _ = env.step(action)
            next_state = tuple(map(int, next_state['position']))
            agent.update_q_table(state, action, reward, next_state, done)
            state = next_state
            total_reward += reward
            if done:
                agent.update_epsilon()
        rewards.append(total_reward)
        if episode % 100 == 0:
            print(f"Episode: {episode}, Total Reward: {total_reward}")

    # Optionally, save the trained Q-table for future use
    with open("q_table.pkl", "wb") as f:
        pickle.dump(dict(agent.q_table), f)

    plt.plot(rewards)
    plt.xlabel('Episode')
    plt.ylabel('Total Reward')
    plt.show()


if __name__ == "__main__":
    gym.envs.registration.register(
        id='F1Env-v0',
        entry_point='environments.car_env:F1_Env',
    )
    env = gym.make('F1Env-v0')
    n_actions = env.action_space.n
    agent = QLearningAgent(n_actions)
    train_agent(env, agent)
