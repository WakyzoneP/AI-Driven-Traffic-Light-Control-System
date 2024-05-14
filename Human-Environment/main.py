from environment.environment import Environment

env = Environment()
game_over = False
while game_over is False:
    game_over, _, _ = env.step()