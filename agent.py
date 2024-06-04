import torch
import random
import numpy as np
from collections import deque
from environment.constants import EnvType
from environment.environment import Environment
from model import Linear_QNet, QTrainer
from helper import plot, printProgressBar

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Result:
    
    class Score:
        def __init__(self):
            self.scores = []
            self.mean_scores = []
            
    class Epos:
        def __init__(self):
            self.epo_means = []
            self.epo_records = []
    
    def __init__(self):
        self.score = Result.Score()
        self.epos = Result.Epos()


class Agent:
    def __init__(self, config_file = "config1.json", device = torch.device("cpu")):
        self.config_file = config_file
        self.device = device
        self.n_games = 0
        self.epsilon = 0.05
        self.gamma = 0.99
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(13, 256, 64, device=device)
        self.trainer = QTrainer(self.model, LR, self.gamma, device=device)

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

    def get_training_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = self.exploration_games - self.n_games
        final_move = [0 for _ in range(64)]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 63)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float, device=self.device)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            # print(f"Prediction: {prediction} \nMove: {move}")
            final_move[move] = 1
        return final_move
    
    def get_action(self, state):
        final_move = [0 for _ in range(64)]
        state0 = torch.tensor(state, dtype=torch.float, device=self.device)
        prediction = self.model(state0)
        move = torch.argmax(prediction).item()
        final_move[move] = 1
        return final_move
    
    def train(self, number_of_epos = 120, show_ui = True, show_plot = True, exploration_games_ratio = 0.1) -> Result:
        scores = []
        mean_scores = []
        total_score = 0
        record = 0
        epo_means = []
        epo_records = []
        exploration_games = number_of_epos * exploration_games_ratio
        self.exploration_games = 80 if exploration_games < 80 else exploration_games
        env = Environment(show_ui=show_ui)
        for epo in range(1, number_of_epos + 1):
            epo_record = 0
            epo_total_score = 0
            while self.n_games < 100 * epo:
            
                old_state = env.generate_state()
                final_move = self.get_training_action(old_state)

                move_index = np.argmax(final_move)

                reward, score, game_over = env.step(move_index)
                new_state = env.generate_state()
                # print(f"Reward: {reward}")

                self.train_short_memory(
                    old_state, final_move, reward, new_state, game_over
                )

                self.remember(old_state, final_move, reward, new_state, game_over)
                if game_over:
                    # print(f"Reward - end: {reward}")
                    env.reset()
                    self.n_games += 1
                    self.train_long_memory()

                    if score > record:
                        record = score
                        save_file = f"model-{self.config_file.split('.')[0]}.pth"
                        self.model.save(file_name=save_file)

                    epo_record = score if score > epo_record else epo_record
                    epo_total_score += score

                    # print(f"Game {agent.n_games} Score: {score}")
                    scores.append(score)
                    total_score += score
                    mean_score = total_score / self.n_games
                    mean_scores.append(mean_score)
                    if show_plot:
                        plot(scores, mean_scores)

                    if self.n_games % 100 == 0:
                        epo_mean = epo_total_score / 100
                        epo_means.append(epo_mean)
                        epo_records.append(epo_record)
                        print(f"Mean score: {mean_score} \nRecord: {record} \nEpo mean score: {epo_mean} \nEpo record: {epo_record}")

                    printProgressBar(self.n_games % 100 + 1, 100, prefix = f'Epo {epo}:', suffix = 'Complete', length = 50)

        result = Result()
        result.score.scores = scores
        result.score.mean_scores = mean_scores
        result.epos.epo_means = epo_means
        result.epos.epo_records = epo_records
    
        return result
    
    def simulate(self):
        env = Environment(show_ui=True, env_type=EnvType.SIMULATION)
        load_file = f"model-{self.config_file.split('.')[0]}.pth"
        self.model.load(file_name=load_file)
        while True:
            move = self.get_action(env.generate_state())
            move_index = np.argmax(move)
            
            env.step(move_index)


if __name__ == "__main__":
    agent = Agent()
    result = agent.train(number_of_epos=10, show_ui=True, show_plot=False, exploration_games_ratio=0.1)
    # agent.simulate()
