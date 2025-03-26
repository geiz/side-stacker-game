from flask import Flask, request, jsonify
import requests
import random
import logging
from flask_cors import CORS
import ast


logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)

OLLAMA_URL = "http://localhost:11434/api/generate"

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

def get_strategic_move(board_state):
    """
    Uses AI model to find the best move with an intention to win.
    """
    prompt = f"""
    You are playing Side-Stacking Connect 4 on a 7x7 board. You are 'O', the opponent is 'X'.
    Players place pieces in any row from the left (L) or right (R), shifting existing pieces.
    Win by aligning 4 in a row, column, or diagonal. If no winning move, choose a blocking move.
    
    Board state: {board_state} 

    Your turn as 'O'. Choose the best move as (row, side), where row is 0-6 and side is 'L' or 'R'.
    Example response: ['2', 'R']. Do not write anything else.
    """
    
    payload = {
        "model": "llama3.2",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)

    if response.status_code == 200:
        ai_response = response.json().get("response", "").strip()

        try:
            move_to_make = ast.literal_eval(ai_response)  # Convert "['2', 'R']" -> [2, "R"]
            if isinstance(move_to_make, list) and len(move_to_make) == 2:
                return move_to_make
            else:
                return "Invalid move format"
        except (SyntaxError, ValueError):
            return  "Error parsing move"

    return "Error getting move"

    ## Try 2
    # ai_response = requests.post(OLLAMA_URL, json=payload)
    # ai_response_parsed = ai_response.json()["response"].strip()

    # try:
    #     move_to_make = ast.literal_eval(ai_response_parsed) 
    #     return {"move": list(move_to_make)}  
    # except (SyntaxError, ValueError):
    #     return ValueError


    ## Try 1
    # response = requests.post(OLLAMA_URL, json=payload)

    # if response.status_code == 200:
    #     return response.json()["response"].strip()
    # return "Error getting move"

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