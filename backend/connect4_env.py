import gymnasium as gym
from gymnasium import spaces
import numpy as np

class SideStackingConnect4(gym.Env):
    def __init__(self):
        super(SideStackingConnect4, self).__init__()
        self.board_size = 7
        self.board = np.zeros((self.board_size, self.board_size), dtype=int)
        self.current_player = 1  # 1 = X, -1 = O

        # Action Space: 7 rows × 2 sides (left=0, right=1)
        self.action_space = spaces.MultiDiscrete([7, 2])

        # Observation Space: 7x7 matrix with -1 (O), 0 (empty), 1 (X)
        self.observation_space = spaces.Box(low=-1, high=1, shape=(7, 7), dtype=int)

    def reset(self, seed=None, options=None):
        self.board = np.zeros((self.board_size, self.board_size), dtype=int)
        self.current_player = 1  # Reset to X (1)
        return self.board.copy(), {}

    def step(self, action):
        """Takes a move, updates the board, and returns observation, reward, done."""
        row, side = action  # row = 0-6, side = 0 (Left) or 1 (Right)
        col = 0 if side == 0 else self.board_size - 1  # Choose column based on side


        # Check for valid move
        if self.board[row, col] != 0:
            return self.board.copy(), -10, True, False, {}  # Invalid move, heavy penalty

        # Place the piece in the correct column
        while 0 <= col < self.board_size and self.board[row, col] != 0:
            col += 1 if side == 0 else -1  # Move to next available column
            if col < 0 or col >= self.board_size:
                return self.board.copy(), -10, True, False, {}  # Invalid move penalty

        # Apply move
        self.board[row, col] = self.current_player

        # Check for a win or draw
        reward, done = self.check_win()

        # Reward for Blocking
        if self.check_opponent_block():
            reward += 3

        # Switch player
        self.current_player *= -1  # Toggle between 1 and -1

        return self.board.copy(), reward, done, False, {}

    def check_win(self):
        """Check if there is a winner."""
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for r in range(self.board_size):
            for c in range(self.board_size):
                if self.board[r, c] == 0:
                    continue
                for dr, dc in directions:
                    count = 1
                    for step in range(1, 4):
                        nr, nc = r + step * dr, c + step * dc
                        if 0 <= nr < self.board_size and 0 <= nc < self.board_size and self.board[nr, nc] == self.board[r, c]:
                            count += 1
                        else:
                            break
                    if count == 4:
                        return 10, True  # Winning move

        if not (self.board == 0).any():
            return 0, True  # Game ends in a draw
        
        # No win condition met
        return 0, False
    

    def check_opponent_block(self):
        """Checks if the move blocked an opponent's winning move."""
        opponent = -self.current_player
        temp_board = self.board.copy()
        for row in range(self.board_size):
            for side in [0, 1]:  # Left or Right
                col = 0 if side == 0 else self.board_size - 1
                while 0 <= col < self.board_size and temp_board[row, col] != 0:
                    col += 1 if side == 0 else -1
                    if col < 0 or col >= self.board_size:
                        break
                temp_board[row, col] = opponent  # Simulate opponent move
                reward, _ = self.check_win()
                temp_board[row, col] = 0  # Undo move
                if reward == 10:  # If opponent could have won
                    return True
        return False

    def render(self):
        """Prints the board for debugging."""
        print("\n".join([" ".join(["X" if c == 1 else "O" if c == -1 else "." for c in row]) for row in self.board]))
        print()