import json
import os
import torch
import random
import numpy as np
from collections import deque
from environment.constants import EnvType
from environment.environment import Environment
from model import Linear_QNet, QTrainer, ActivationFunction, Device
from helper import plot, printProgressBar
from pickle import dumps, loads
from typing import Literal

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001
SaveType = Literal["json", "binary"]

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

    class Encoder(json.JSONEncoder):
        def default(self, o):
            score_dict = o.score.__dict__
            epos_dict = o.epos.__dict__
            return {"score": score_dict, "epos": epos_dict}

    class Decoder(json.JSONDecoder):
        def decode(self, s):
            result = Result()
            result.score = Result.Score()
            result.epos = Result.Epos()

            result.score.scores = s["score"]["scores"]
            result.score.mean_scores = s["score"]["mean_scores"]
            result.epos.epo_means = s["epos"]["epo_means"]
            result.epos.epo_records = s["epos"]["epo_records"]

            return result

    def save(self, file_name, save_type: SaveType = "binary"):
        results_folder_path = "./results"
        if not os.path.exists(results_folder_path):
            os.makedirs(results_folder_path)
        file_name = os.path.join(results_folder_path, file_name)
        if save_type == "json":
            file_name = file_name + ".json"
            with open(file_name, "w") as file:
                json.dump(self, file, cls=Result.Encoder)
        elif save_type == "binary":
            file_name = file_name + ".bin"
            with open(file_name, "wb") as file:
                byte_data = dumps(self)
                file.write(byte_data)

    def load(self, file_name, save_type: SaveType = "binary"):
        results_folder_path = "./results"
        file_name = os.path.join(results_folder_path, file_name)
        if save_type == "json":
            file_name = file_name + ".json"
            with open(file_name, "r") as file:
                data = json.load(file)
                result = Result.Decoder().decode(data)
                self.__dict__ = result.__dict__
        elif save_type == "binary":
            file_name = file_name + ".bin"
            with open(file_name, "rb") as file:
                byte_data = file.read()
                result = loads(byte_data)
                self.__dict__ = result.__dict__


class Agent:
    def __init__(
        self,
        config_file,
        hidden_layers=0,
        activation_function: ActivationFunction = "relu",
        device: Device = "cpu",
    ):
        self.config_file = config_file
        self._load_config()
        self.device = device
        self.n_games = 0
        self.epsilon = 0.05
        self.gamma = 0.99
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(
            self.number_of_intersections * 4,
            self.number_of_intersections * 4 * 20,
            4**self.number_of_intersections,
            hidden_layers,
            activation_function,
            device,
        )
        self.trainer = QTrainer(self.model, LR, self.gamma, device=device)
        
    def transfer_model(self):
        file_name = f"model-{self.config_file.split('/')[-1].split('.')[0]}.pth"
        self.model.load(file_name)

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

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_training_action(self, state, show_ui=False):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = self.exploration_games - self.n_games % 100
        # self.epsilon = self.exploration_games - self.n_games
        final_move = [0 for _ in range(4**self.number_of_intersections)]
        
        if random.randint(0, 100) < self.epsilon:
            move = random.randint(0, 4**self.number_of_intersections - 1)
            final_move[move] = 1
            if show_ui:
                print("Random move " + str(move))
        else:
            state0 = torch.tensor(state, dtype=torch.float, device=self.device)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
            if show_ui:
                print("Predicted move " + str(move))
        return final_move

    def get_action(self, state):
        final_move = [0 for _ in range(4**self.number_of_intersections)]
        state0 = torch.tensor(state, dtype=torch.float, device=self.device)
        prediction = self.model(state0)
        move = torch.argmax(prediction).item()
        final_move[move] = 1
        return final_move

    def train(
        self,
        number_of_epos=1,
        show_ui=False,
        show_plot=False,
        exploration_games_ratio=0.1,
        save_results=True,
        save_type: SaveType="binary"
    ) -> Result:
        scores = []
        mean_scores = []
        total_score = 0
        record = 0
        epo_means = []
        epo_records = []
        self.exploration_games = 100 * exploration_games_ratio
        # exploration_games = 100 * number_of_epos * exploration_games_ratio
        # self.exploration_games = 80 if exploration_games < 80 else exploration_games
        print(f"Exploration games: {self.exploration_games}")
        env = Environment(
            intersections_json=self.intersections,
            show_ui=show_ui,
        )
        for epo in range(1, number_of_epos + 1):
            epo_record = 0
            epo_total_score = 0
            while self.n_games < 100 * epo:

                old_state = env.generate_state()
                final_move = self.get_training_action(old_state, show_ui=show_ui)

                move_index = np.argmax(final_move)

                reward, score, game_over = env.step(move_index)
                new_state = env.generate_state()
                
                if show_ui:
                    print("Old state: " + str(old_state))
                    print("Reward: " + str(reward))
                    print("Score: " + str(score))
                    print("New state: " + str(new_state))

                self.train_short_memory(
                    old_state, final_move, reward, new_state, game_over
                )

                self.remember(old_state, final_move, reward, new_state, game_over)
                game_over = True
                if game_over:
                    env.reset()
                    self.n_games += 1
                    self.train_long_memory()

                    if score > record:
                        record = score

                    epo_record = score if score > epo_record else epo_record
                    epo_total_score += score

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

        if save_results:
            result.save(
                f"result-{self.config_file.split('/')[-1].split('.')[0]}",
                save_type=save_type,
            )

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
    agent = Agent("./config/config4.json", hidden_layers=2, activation_function="relu")
    result = agent.train(
        number_of_epos=30,
        show_ui=True,
        show_plot=True,
        exploration_games_ratio=0.5,
        save_type="binary",
    )
    agent.simulate()
