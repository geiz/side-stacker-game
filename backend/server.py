from flask import Flask, request, jsonify
import numpy as np
import random
import logging
from flask_cors import CORS
from stable_baselines3 import PPO
from training.connect4_env import SideStackingConnect4  # Import Gym env

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)

# Load Trained RL Model
model = PPO.load("backend/model/connect4_rl_model")

BOARD_SIZE = 7  # 7x7 board

def get_ai_move(board_state, difficulty):
    """
    Uses RL to generate the best move.
    """
    observation = parse_board_state(board_state)

    for _ in range(10):  # Try up to 10 times
        if difficulty == "easy":
            move = get_random_move()
        elif difficulty == "medium":
            move = get_gen_ai_move(observation)
        else:
            move = get_rl_move(observation)

        row, side = move
        if is_valid_move(observation, row, side):
            return move

    # Fallback: pick any valid move directly if AI fails
    env = SideStackingConnect4()
    env.board = observation.copy()
    valid_actions = env.get_valid_actions()
    fallback_action = random.choice(valid_actions)
    return decode_action(fallback_action)
    
def is_valid_move(board, row, side):
    """
    Checks if a move is valid in the current board state using the game logic.
    """
    env = SideStackingConnect4()
    env.board = board.copy()
    valid_actions = env.get_valid_actions()
    
    action = row * 2 + (0 if side == "L" else 1)
    return action in valid_actions
    
def get_gen_ai_move(observation):
    """
    Placeholder for Gen AI logic (e.g., LLM-based decision).
    """
    # TODO: Add actual Gen AI logic
    # For now, mimic semi-smart logic
    valid_actions = SideStackingConnect4().get_valid_actions()
    return decode_action(random.choice(valid_actions))

def decode_action(action):
    row = action // 2
    side = "L" if action % 2 == 0 else "R"
    return [row, side]

def parse_board_state(board_state_str):
    """
    Converts board_state string into a numpy array.
    Expected format: "Row: 0: _ _ _ _ _ _ _ | Row: 1: _ _ _ _ _ _ _ | ..."
    """
    board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=np.int8)
    rows = board_state_str.split(",")
    for i, row in enumerate(rows):
        cells = row.split(":")[2].strip()  # Gets '_______' part
        board[i] = [0 if c == "_" else (1 if c == "O" else -1) for c in cells]
    return board

def get_random_move():
    """
    Selects a random valid move.
    """
    row = random.randint(0, BOARD_SIZE - 1)
    side = random.choice(["L", "R"])
    return [row, side]

def get_rl_move(observation):
    """
    Uses the trained RL model to predict the best move.
    """
    action, _ = model.predict(observation, deterministic=True)
    print("obs shape before predict:", observation.shape)

    row = action // 2
    side = "L" if action % 2 == 0 else "R"
    return [row, side]

@app.route("/move", methods=["POST"])
def get_move():
    data = request.json
    logging.info(f"Received move request: {data}")

    board_state = data.get("board", "")
    difficulty = data.get("difficulty", "hard")  # Default to hard

    if not board_state:
        return jsonify({"error": "Board state required"}), 400

    ai_move = get_ai_move(board_state, difficulty)
    row = int(ai_move[0])
    side = str(ai_move[1])

    return jsonify({"move": [row, side]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
