import json
import torch
import random
import numpy as np
from collections import deque
from environment.constants import EnvType
from environment.environment import Environment
from model import Linear_QNet, QTrainer
from helper import plot, printProgressBar

MAX_MEMORY = 10_000_000
BATCH_SIZE = 100_000
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
    def __init__(self, config_file, device=torch.device("cpu")):
        self.config_file = config_file
        self._load_config()
        self.device = device
        self.n_games = 0
        self.epsilon = 0.05
        self.gamma = 0.99
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(
            self.number_of_intersections * 4,
            self.number_of_intersections * 4 * 12,
            4**self.number_of_intersections,
            device=device,
        )
        self.trainer = QTrainer(self.model, LR, self.gamma, device=device)

    def _load_config(self):
        file = open(self.config_file, "r")
        data = json.load(file)

        self.traffic_level = data["traffic_severity"]
        self.intersections = data["intersections"]
        self.number_of_intersections = len(self.intersections)

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
        self.epsilon = self.exploration_games - self.n_games % 100
        final_move = [0 for _ in range(64)]
        if random.randint(0, 100) < self.epsilon:
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

    def train(
        self,
        number_of_epos=120,
        show_ui=True,
        show_plot=True,
        exploration_games_ratio=0.1,
    ) -> Result:
        scores = []
        mean_scores = []
        total_score = 0
        record = 0
        epo_means = []
        epo_records = []
        self.exploration_games = 100 * exploration_games_ratio
        env = Environment(
            intersections_json=self.intersections,
            traffic_level=self.traffic_level,
            show_ui=show_ui,
        )
        for epo in range(1, number_of_epos + 1):
            epo_record = 0
            epo_total_score = 0
            while self.n_games < 100 * epo:

                old_state = env.generate_state()
                # print(f"old_state: {old_state}")
                final_move = self.get_training_action(old_state)

                move_index = np.argmax(final_move)

                reward, score, game_over = env.step(move_index)
                new_state = env.generate_state()
                # print(f"new_state: {new_state}")
                # print(f"Reward: {reward}\n Move: {move_index}\n")

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

                    epo_record = score if score > epo_record else epo_record
                    epo_total_score += score

                    # print(f"Game {agent.n_games} Score: {score}")
                    scores.append(score)
                    total_score += score
                    mean_score = total_score / self.n_games
                    mean_scores.append(mean_score)
                    if show_plot:
                        plot(scores, mean_scores)

                    if self.n_games % 100 == 0 and epo_total_score / 100 >= mean_score:
                        save_file = (
                            f"model-{self.config_file.split('/')[-1].split('.')[0]}.pth"
                        )
                        self.model.save(file_name=save_file)

                    if show_ui is False:
                        if self.n_games % 100 == 0:
                            epo_mean = epo_total_score / 100
                            epo_means.append(epo_mean)
                            epo_records.append(epo_record)
                            print(
                                f"Mean score: {mean_score} \nRecord: {record} \nEpo mean score: {epo_mean} \nEpo record: {epo_record}"
                            )
                        else:
                            printProgressBar(
                                self.n_games % 100 + 1,
                                100,
                                prefix=f"Epo {epo}:",
                                suffix="Complete",
                                length=50,
                            )

        result = Result()
        result.score.scores = scores
        result.score.mean_scores = mean_scores
        result.epos.epo_means = epo_means
        result.epos.epo_records = epo_records

        return result

    def simulate(self):
        env = Environment(
            intersections_json=self.intersections,
            show_ui=True,
            env_type=EnvType.SIMULATION,
        )
        load_file = f"model-{self.config_file.split('/')[-1].split('.')[0]}.pth"
        print(f"Loading model from {load_file}")
        self.model.load(file_name=load_file)
        while True:
            move = self.get_action(env.generate_state())
            move_index = np.argmax(move)
            print(f"Move: {move_index}")
            env.step(move_index)
            # env.step(0)


if __name__ == "__main__":
    agent = Agent("./config/config3.json")
    result = agent.train(
        number_of_epos=1, show_ui=False, show_plot=False, exploration_games_ratio=0.1
    )
    agent.simulate()
