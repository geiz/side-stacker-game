from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"

def get_ai_move(board_state):
    prompt = f"You are playing Side-Stacking Connect 4 on a 7x7 board. You are 'O', the opponent is 'X'. Players place pieces in any row from the left (L) or right (R), shifting existing pieces. Win by aligning 4 in a row, column, or diagonal. Board state: {board_state} Your turn as 'O'. Choose the best move as (row, side), where row is 0-6 and side is 'L' or 'R'. Example response: (2, R). Do not write anything else."
    
    payload = {
        "model": "llama3.2",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)
    if response.status_code == 200:
        return response.json()["response"].strip()
    return "Error getting move"

@app.route("/move", methods=["POST"])
def get_move():
    data = request.json
    board_state = data.get("board", "")
    if not board_state:
        return jsonify({"error": "Board state required"}), 400

    ai_move = get_ai_move(board_state)
    return jsonify({"move": ai_move})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
