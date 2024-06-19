import torch
import torch.nn as nn
import torch.optim as optim
import os
from typing import Literal
import torch.nn.functional as F

Device = Literal["cpu", "mps"]
ActivationFunction = Literal["relu", "selu", "leaky_relu", "elu"]

def get_activation_function(activation_function: ActivationFunction):
    if activation_function == "relu":
        return F.relu
    elif activation_function == "selu":
        return F.selu
    elif activation_function == "leaky_relu":
        return F.leaky_relu
    elif activation_function == "elu":
        return F.elu
    else:
        raise ValueError("Invalid activation function")
    
def get_device(device: Device):
    if device == "cpu":
        return torch.device("cpu")
    elif device == "mps":
        return torch.device("mps")
    else:
        raise ValueError("Invalid device")

class Linear_QNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size, hidden_layers, activation_function: ActivationFunction, device: Device):
        super().__init__()
        self.device=get_device(device)
        self.activation_function = get_activation_function(activation_function)
        # init_model = nn.init.kaiming_normal_
        # self.linear_input = nn.Linear(input_size, hidden_size, device=self.device)
        # init_model(self.linear_input.weight, mode='fan_in', nonlinearity='leaky_relu')
        # self.linear_hidden_array = nn.ModuleList([nn.Linear(hidden_size, hidden_size, device=self.device) for _ in range(hidden_layers)])
        # for linear in self.linear_hidden_array:
            # init_model(linear.weight, mode='fan_in', nonlinearity='leaky_relu')
        # self.linear_output = nn.Linear(hidden_size, output_size, device=self.device)
        # init_model(self.linear_output.weight, mode='fan_in', nonlinearity='leaky_relu')
        
        # self.linear1 = nn.Linear(input_size, hidden_size, device=self.device)
        # self.linear2 = nn.Linear(hidden_size, output_size, device=self.device)
        
        # self.linear1 = nn.Linear(input_size, output_size, device=self.device)
        
        self.linear1 = nn.Linear(input_size, hidden_size, device=self.device)
        self.linear2 = nn.Linear(hidden_size, hidden_size, device=self.device)
        self.linear3 = nn.Linear(hidden_size, hidden_size, device=self.device)
        self.linear4 = nn.Linear(hidden_size, output_size, device=self.device)

    def forward(self, x):
        # x = self.activation_function(self.linear_input(x))
        # for linear in self.linear_hidden_array:
        #     x = self.activation_function(linear(x))
        #     x = linear(x)
        # x = self.linear_output(x)
        
        x = F.selu(self.linear1(x))
        x = self.linear2(x)
        x = F.selu(self.linear2(x))
        x = self.linear3(x)
        x = F.selu(self.linear3(x))
        x = self.linear4(x)
        
        return x

    def save(self, file_name='model.pth'):
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)
        
    def load(self, file_name='model.pth'):
        model_folder_path = './model'
        file_name = os.path.join(model_folder_path, file_name)
        self.load_state_dict(torch.load(file_name))

class QTrainer:
    def __init__(self, model, lr, gamma, device):
        self.device = device
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def train_step(self, state, action, reward, next_state, done):
        state = torch.tensor(state, dtype=torch.float, device=self.device)
        next_state = torch.tensor(next_state, dtype=torch.float, device=self.device)
        action = torch.tensor(action, dtype=torch.long, device=self.device)
        reward = torch.tensor(reward, dtype=torch.float, device=self.device)
        # (n, x)

        if len(state.shape) == 1:
            # (1, x)
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done, )

        pred = self.model(state)

        target = pred.clone()
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))

            target[idx][torch.argmax(action[idx]).item()] = Q_new
    
        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()

        self.optimizer.step()