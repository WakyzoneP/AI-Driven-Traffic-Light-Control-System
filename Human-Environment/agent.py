import torch
import random
import numpy as np
from collections import deque
from environment.environment import Environment
from model import Linear_QNet, QTrainer
from helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001


def convert_to_base_4(num):
    base_4 = [0, 0, 0]
    for i in range(3):
        base_4[i] = num % 4
        num //= 4
    return base_4


class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0.05
        self.gamma = 0.99
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(13, 256, 64)
        self.trainer = QTrainer(self.model, LR, self.gamma)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)  # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        # for state, action, reward, nexrt_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 400 - self.n_games
        final_move = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            for i in range(3):
                move = random.randint(0, 3)
                final_move[i] = move
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            print(f"Prediction: {prediction} Move: {move}")
            final_move = convert_to_base_4(move)

        return final_move


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    env = Environment()
    reward = -0.005
    while True:
        game_over, score = env.run()

        if env.can_make_step():
            old_state = env.generate_state()
            final_move = agent.get_action(old_state)

            reward, score = env.step(final_move)
            new_state = env.generate_state()
            print(f"Reward: {reward}")

            agent.train_short_memory(
                old_state, final_move, reward, new_state, game_over
            )

            agent.remember(old_state, final_move, reward, new_state, game_over)
        if game_over:
            print(f"Reward - end: {reward}")
            env.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            print(f"Game {agent.n_games} Score: {score}")
            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)
            
            reward = -0.005


if __name__ == "__main__":
    train()
