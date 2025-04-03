from stable_baselines3 import PPO
from connect4_env import SideStackingConnect4

env = SideStackingConnect4()
model = PPO.load("model/connect4_rl_model", env=env)

obs, _ = env.reset()
done = False
step_count = 0
max_steps = 50 

while not done and step_count < max_steps:
    action, _ = model.predict(obs)
    obs, reward, done, _, _ = env.step(action)
    env.render()
    step_count += 1

print(f"Game ended in {step_count} steps with reward: {reward}")
print(f"Steps: {step_count}")
if reward >= 100:
    print("Agent WON!")
elif reward == 0:
    print("Draw!")
elif reward < 0:
    print("Agent made bad moves!")