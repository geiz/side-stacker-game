import gymnasium as gym
from stable_baselines3 import PPO
from connect4_env import SideStackingConnect4  # Import the Gym environment

# Create the environment
env = SideStackingConnect4()

# Train PPO Model
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=500000)  # Train longer for better results

# Save model
model.save("model/connect4_rl_model")
