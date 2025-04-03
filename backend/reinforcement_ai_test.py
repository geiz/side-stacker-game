from stable_baselines3 import PPO
from connect4_env import SideStackingConnect4

env = SideStackingConnect4()
model = PPO.load("model/connect4_rl_model", env=env)

obs, _ = env.reset()
done = False
step_count = 0
max_steps = 50 

current_player = 1  # Start with X, Y is -1

while not done and step_count < max_steps:
    action, _ = model.predict(obs)
    obs, reward, done, _, _ = env.step(action)
    env.render()
    step_count += 1
    current_player *= -1  # Flip after move

# Final move was made by the *previous* player (flip back)
last_player = -current_player
symbol = "X" if last_player == 1 else "O"

print(f"Game ended in {step_count} steps with reward: {reward}")
if reward >= 100:
    print(f"{symbol} WON!")
elif reward == 0:
    print("Draw!")
elif reward < 0:
    print(f"{symbol} made bad moves!")