from flask import Flask, request, jsonify
import numpy as np
import random
import logging
from flask_cors import CORS
from stable_baselines3 import PPO
from connect4_env import SideStackingConnect4  # Import Gym env

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)

# Load Trained RL Model
model = PPO.load("connect4_ai")

BOARD_SIZE = 7  # 7x7 board

def get_ai_move(board_state, difficulty):
    """
    Uses RL to generate the best move.
    """
    observation = parse_board_state(board_state)

    if difficulty == "easy":
        return get_random_move()
    elif difficulty == "medium":
        return get_mixed_move(observation)
    else:  # Hard difficulty uses trained RL model
        return get_rl_move(observation)

def parse_board_state(board_state):
    """
    Converts board_state string into a numpy array.
    """
    board_rows = board_state.split(" | ")
    board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=np.int8)

    for row_idx, row in enumerate(board_rows):
        board[row_idx] = [0 if cell == "_" else (1 if cell == "O" else -1) for cell in row]

    return board

def get_random_move():
    """
    Selects a random valid move.
    """
    row = random.randint(0, BOARD_SIZE - 1)
    side = random.choice(["L", "R"])
    return [row, side]

def get_mixed_move(observation):
    """
    50% chance to pick a random move, 50% chance to use RL.
    """
    if random.random() < 0.5:
        return get_random_move()
    return get_rl_move(observation)

def get_rl_move(observation):
    """
    Uses the trained RL model to predict the best move.
    """
    action, _ = model.predict(observation.flatten())
    row, side = divmod(action, 2)
    return [row, "L" if side == 0 else "R"]

@app.route("/move", methods=["POST"])
def get_move():
    data = request.json
    logging.info(f"Received move request: {data}")

    board_state = data.get("board", "")
    difficulty = data.get("difficulty", "hard")  # Default to hard

    if not board_state:
        return jsonify({"error": "Board state required"}), 400

    ai_move = get_ai_move(board_state, difficulty)
    return jsonify({"move": ai_move})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
