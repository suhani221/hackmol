import numpy as np

class CliffWalkingEnv:
    def __init__(self, width=12, height=4):
        self.width = width
        self.height = height
        self.start_state = (0, 0)
        self.goal_state = (width-1, 0)
        self.current_state = self.start_state
        self.grid = np.zeros((height, width))
        self.grid[height-1, 1:width-1] = -100  # add cliff
        self.actions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
    def reset(self):
        self.current_state = self.start_state
        
    def step(self, action):
        x, y = self.current_state
        dx, dy = action
        x = min(max(x+dx, 0), self.width-1)
        y = min(max(y+dy, 0), self.height-1)
        reward = self.grid[y, x]
        done = (self.current_state == self.goal_state)
        self.current_state = (x, y)
        return self.current_state, reward, done
def q_learning(env, num_episodes=1000, alpha=0.5, epsilon=0.1, gamma=1.0):
    Q = np.zeros((env.height, env.width, len(env.actions)))
    for i in range(num_episodes):
        state = env.reset()
        done = False
        while not done:
            if np.random.random() < epsilon:
                action = np.random.randint(len(env.actions))
            else:
                action = np.argmax(Q[state])
            next_state, reward, done = env.step(env.actions[action])
            Q[state][action] += alpha * (reward + gamma * np.max(Q[next_state]) - Q[state][action])
            state = next_state
    return Q

def sarsa(env, num_episodes=1000, alpha=0.5, epsilon=0.1, gamma=1.0):
    Q = np.zeros((env.height, env.width, len(env.actions)))
    for i in range(num_episodes):
        state = env.reset()
        if np.random.random() < epsilon:
            action = np.random.randint(len(env.actions))
        else:
            action = np.argmax(Q[state])
        done = False
        while not done:
            next_state, reward, done = env.step(env.actions[action])
            if np.random.random() < epsilon:
                next_action = np.random.randint(len(env.actions))
            else:
                next_action = np.argmax(Q[next_state])
            Q[state][action] += alpha * (reward + gamma * Q[next_state][next_action] - Q[state][action])
            state = next_state
            action = next_action
    return Q
env = CliffWalkingEnv()
num_episodes = 5000
alpha = 0.5
epsilon = 0.1
gamma = 1.0

# Q-learning
Q_q_learning = q_learning(env, num_episodes=num_episodes, alpha=alpha, epsilon=epsilon, gamma=gamma)

# SARSA
Q_sarsa = sarsa(env, num_episodes=num_episodes, alpha=alpha, epsilon=epsilon, gamma=gamma)

# Evaluate policies
def evaluate_policy(Q, env, num_episodes=100):
    total_reward = 0
    for i in range(num_episodes):
        state = env.reset()
        done = False
        while not done:
            action = np.argmax(Q[state])
            next_state, reward, done = env.step(env.actions[action])
            total_reward += reward
            state = next_state
    return total_reward/num_episodes

print("Q-learning average reward:", evaluate_policy(Q_q_learning, env))
print("SARSA average reward:", evaluate_policy(Q_sarsa, env))
