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
        # self.action_space = spaces.MultiDiscrete([7, 2])
        self.action_space = spaces.Discrete(14)


        # Observation Space: 7x7 matrix with -1 (O), 0 (empty), 1 (X)
        self.observation_space = spaces.Box(low=-1, high=1, shape=(7, 7), dtype=int)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.board = np.zeros((self.board_size, self.board_size), dtype=int)
        self.current_player = 1  # Reset to X (1)
        return self.board.copy(), {}

    def step(self, action):
        row = action // 2
        side = action % 2
        col = 0 if side == 0 else self.board_size - 1

        # Slide piece into available column
        original_col = col
        while 0 <= col < self.board_size and self.board[row, col] != 0:
            col += 1 if side == 0 else -1
            if col < 0 or col >= self.board_size:
                return self.board.copy(), -10, False, False, {"reason": "invalid_move"}

        # Apply move
        self.board[row, col] = self.current_player

        # Count player sequences
        reward = self.count_streak_reward(self.current_player)

        # Check for win or draw
        win_reward, terminated = self.check_win()
        if terminated and win_reward == 100:
            reward = 100  # override everything

        # Check if blocking opponent's 3-in-a-row
        if self.check_opponent_block(threshold=3):
            reward += 25

        # Ensure minimum reward per move (small penalty for wasting time)
        if reward == 0:
            reward = -0.1

        # Switch player
        self.current_player *= -1

        return self.board.copy(), reward, terminated, False, {}

    def count_streak_reward(self, player):
        reward = 0
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

        for r in range(self.board_size):
            for c in range(self.board_size):
                if self.board[r, c] != player:
                    continue
                for dr, dc in directions:
                    count = 1
                    for step in range(1, 4):
                        nr, nc = r + step * dr, c + step * dc
                        if 0 <= nr < self.board_size and 0 <= nc < self.board_size:
                            if self.board[nr, nc] == player:
                                count += 1
                            elif self.board[nr, nc] != 0:
                                break
                    if count == 2:
                        reward += 5
                    elif count == 3:
                        reward += 10
        return reward


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
                        return 100, True  # Winning move

        if not (self.board == 0).any():
            return 0, True  # Game ends in a draw
        
        # No win condition met
        return 0, False
    

    def check_opponent_block(self, threshold=3):
        opponent = -self.current_player
        for row in range(self.board_size):
            for side in [0, 1]:
                col = 0 if side == 0 else self.board_size - 1
                while 0 <= col < self.board_size and self.board[row, col] != 0:
                    col += 1 if side == 0 else -1
                    if col < 0 or col >= self.board_size:
                        break

                if 0 <= col < self.board_size and self.board[row, col] == 0:
                    self.board[row, col] = opponent
                    score = self.count_streak_reward(opponent)
                    self.board[row, col] = 0
                    if threshold == 3 and score >= 10:
                        return True
        return False


    def render(self):
        """Prints the board for debugging."""
        print("\n".join([" ".join(["X" if c == 1 else "O" if c == -1 else "." for c in row]) for row in self.board]))
        print()