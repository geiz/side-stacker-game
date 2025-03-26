from flask import Flask, request, jsonify
import requests
import random
import logging
from flask_cors import CORS
import ast
import re



logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)

OLLAMA_URL = "http://localhost:11434/api/generate"

# Chooses a move for the AI based on the difficulty level
def get_ai_move(board_state, difficulty):
    """
    Generates an AI move based on difficulty level.
    - Easy: Random move
    - Medium: 50% chance of strategic move, 50% random
    - Hard: Always chooses a winning move if available
    """
    if difficulty == "easy":
        return get_random_move(board_state)

    elif difficulty == "medium":
        if random.random() < 0.5:  # 50% chance
            return get_random_move(board_state)
        else:
            return get_strategic_move(board_state)

    else:  # Hard AI (default)
        return get_strategic_move(board_state)

# Easy difficulty and 50% of medium difficulty
def get_random_move(board_state):
    """
    Selects a random valid move from available rows and sides.
    """
    available_moves = []
    board_rows = board_state.split("\n")  # Convert string back to rows

    for row_index, row in enumerate(board_rows):
        if '_' in row:  # Check if row has an empty space
            available_moves.append((row_index, random.choice(['L', 'R'])))

    return random.choice(available_moves) if available_moves else "No Moves"

# Hard difficulty
def get_strategic_move(board_state):
    """
    Uses AI model to find the best move with an intention to win.
    """
    prompt = f"""
    You are playing Side-Stacking Connect 4 on a 7x7 board. You are 'O', the opponent is 'X'.
    Players place pieces in any row from the left 'L' or right 'R', shifting existing pieces.
    Win by aligning 4 x 'O' in a row, column, or diagonal. If no winning move, choose a blocking move.
    
    Board state: {board_state} 

    Your turn as 'O'. Choose the best move as [row, side, reason for move]. You want to win, and stop the 'X' from Winning. 
    Row is 0-6 and side is 'L' or 'R'. Good luck.
    Example response 1: ['2', 'R', 'Trying to connect 4 diagnonally between rows 2,3,4,5']. Do not write anything else.
    Example response 2: ['4', 'L', 'Trying to connect 4 vertically between rows 1,2,3,4']. Do not write anything else.
    Example response 3: ['5', 'R', 'Blocking a Vertical connect from X']. Do not write anything else.
    """
    
    payload = {
        "model": "llama3.2",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)

    if response.status_code == 200:
        ai_response = response.json().get("response", "").strip()
        return parse_ai_response(ai_response)

    return ["Error getting move"]

# AI sometimes give different formatted responses. This functions clears it up.
def parse_ai_response(ai_response):
    """
    Parses AI response to extract a valid move in the format [row, "L" or "R"].
    Handles multiple formats:
    - "[5, L]"
    - "['2', 'R']"
    - "[ 3 ,  'L' ]"
    - "(4, R)"
    """

    # Extract numbers and letters using regex
    match = re.findall(r"\d+|[LR]", ai_response)
    
    if len(match) == 2:
        try:
            row = int(match[0])  # Convert first part to an integer
            side = match[1] if match[1] in ['L', 'R'] else None  # Validate L/R
            if side:
                return [row, side, ai_response]  # Valid move format, with full response for debug
        except ValueError:
            pass

    return ["Error parsing move", ai_response]  # Default error response

# API to be called by Front-end
@app.route("/move", methods=["POST"])
def get_move():
    logging.info(f"Received Request: {request}")
    data = request.json
    logging.info(f"Received move request: {data}")

    board_state = data.get("board", "")
    difficulty = data.get("difficulty", "hard")  # Default to hard if not specified

    if not board_state:
        return jsonify({"error": "Board state required"}), 400

    ai_move = get_ai_move(board_state, difficulty)
    return jsonify({"move": ai_move})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)