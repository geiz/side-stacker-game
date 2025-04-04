from stable_baselines3 import PPO
from connect4_env import SideStackingConnect4

env = SideStackingConnect4()
model = PPO.load("model/connect4_rl_model", env=env)

obs, _ = env.reset()
done = False
step_count = 0
max_steps = 70 

while not done and step_count < max_steps:
    action, _ = model.predict(obs)
    obs, reward, done, _, info = env.step(action)
    env.render()
    step_count += 1

print(f"Game ended in {step_count} steps with reward: {reward}")

if reward >= 100:
    winner_symbol = "X" if info["winner"] == 1 else "O"
    print(f"{winner_symbol} WON!")
elif reward == 0:
    print("Draw!")
elif reward < 0:
    loser_symbol = "X" if info["winner"] == 1 else "O"
    print(f"{loser_symbol} made bad moves!")
