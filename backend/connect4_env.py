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
        retry_limit = 5
        retries = 0

        while retries < retry_limit:
            row = action // 2
            side = action % 2
            col = 0 if side == 0 else self.board_size - 1

            # Slide piece into available column
            while 0 <= col < self.board_size and self.board[row, col] != 0:
                col += 1 if side == 0 else -1

            # Invalid move: no space in this direction
            if col < 0 or col >= self.board_size:
                retries += 1
                return self.board.copy(), -10, False, False, {
                    "reason": "invalid_move",
                    "retries": retries,
                    "action": (row, "L" if side == 0 else "R"),
                    "current_player": self.current_player,
                    "retry": True
                }

            # VALID move — break loop
            break

        # If all retries failed
        if retries >= retry_limit:
            return self.board.copy(), -50, True, False, {
                "reason": "max_retries_exceeded",
                "current_player": self.current_player,
                "retry": False
            }

        # Apply move
        self.board[row, col] = self.current_player

        # Count player sequences
        reward = self.count_streak_reward_from_move(self.current_player, row, col)

        # manual force big hint to AI if it's a winning move.
        if self.check_win_for_player(self.current_player):
            reward += 100 

        # Check for win or draw
        win_reward, terminated = self.check_win()

        if terminated:
            if win_reward == 100:
                reward += 100  # Win
            else:
                reward += 0    # Draw
        elif self.check_opponent_block():
            reward += 40
        elif self.detect_broken_4(-self.current_player):
            reward += 40
        elif reward == 0:
            reward += -0.1

        # Save winner before flipping
        winner = self.current_player
        self.current_player *= -1  # Flip turn

        return self.board.copy(), reward, terminated, False, {
            "winner": winner,
            "action": (row, col),
            "current_player": self.current_player,
            "retry": False
        }
    # Returns a list of valid moves to the AI
    def get_valid_actions(self):
        valid_actions = []
        for row in range(self.board_size):
            for side in [0, 1]:
                col = 0 if side == 0 else self.board_size - 1
                temp_col = col
                while 0 <= temp_col < self.board_size and self.board[row, temp_col] != 0:
                    temp_col += 1 if side == 0 else -1
                if 0 <= temp_col < self.board_size:
                    action = row * 2 + side
                    valid_actions.append(action)
        return valid_actions


    # Only Track the position of the latest move
    # Check in all directions from that point
    # Reward only based on the longest streak that move creates
    # No reward for 2 if it already triggered a 3 or 4
    def count_streak_reward_from_move(self, player, row, col):
        reward = 0
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

        max_streak = 1  # Always includes the move itself

        for dr, dc in directions:
            count = 1  # Start with the current move
            for step in range(1, 4):
                nr, nc = row + step * dr, col + step * dc
                if 0 <= nr < self.board_size and 0 <= nc < self.board_size:
                    if self.board[nr, nc] == player:
                        count += 1
                    else:
                        break

            for step in range(1, 4):
                nr, nc = row - step * dr, col - step * dc
                if 0 <= nr < self.board_size and 0 <= nc < self.board_size:
                    if self.board[nr, nc] == player:
                        count += 1
                    else:
                        break

            max_streak = max(max_streak, count)

        # Only reward based on the **longest streak** involving the new move
        if max_streak == 3:
            reward += 1
        elif max_streak >= 4:
            reward += 5  # fallback; win reward comes from check_win()

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
                    if count >= 4:
                        return 100, True  # Winning move

        if not (self.board == 0).any():
            return 0, True  # Game ends in a draw
        
        # No win condition met
        return 0, False
    
    # Checks if need to block an opponent
    def check_opponent_block(self, threshold=3):
        opponent = -self.current_player
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

        for row in range(self.board_size):
            for side in [0, 1]:
                col = self.simulate_stack(row, side)
                if col is None:
                    continue
                self.board[row, col] = opponent
                if self.is_winning_move(opponent, row, col, directions):
                    self.board[row, col] = 0
                    return True
                self.board[row, col] = 0

        return False
    
    # Helper functions
    def simulate_stack(self, row, side):
        col = 0 if side == 0 else self.board_size - 1
        while 0 <= col < self.board_size and self.board[row, col] != 0:
            col += 1 if side == 0 else -1
        if 0 <= col < self.board_size and self.board[row, col] == 0:
            return col
        return None
    
    # If there's a winning move, take it.
    def check_win_for_player(self, player):
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # V, H, D1, D2

        for row in range(self.board_size):
            for side in [0, 1]:
                col = 0 if side == 0 else self.board_size - 1
                temp_col = col
                while 0 <= temp_col < self.board_size and self.board[row, temp_col] != 0:
                    temp_col += 1 if side == 0 else -1
                    if temp_col < 0 or temp_col >= self.board_size:
                        break

                if 0 <= temp_col < self.board_size and self.board[row, temp_col] == 0:
                    self.board[row, temp_col] = player
                    if self.is_winning_move(player, row, temp_col, directions):
                        self.board[row, temp_col] = 0
                        return True
                    self.board[row, temp_col] = 0
                    
        return False
    
    # helper function for check_win_for_player
    def is_winning_move(self, player, row, col, directions):
        for dr, dc in directions:
            count = 1

            # Check backward
            for step in range(1, 4):
                r, c = row - dr * step, col - dc * step
                if 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r, c] == player:
                    count += 1
                else:
                    break

            # Check forward
            for step in range(1, 4):
                r, c = row + dr * step, col + dc * step
                if 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r, c] == player:
                    count += 1
                else:
                    break

            if count >= 4:
                return True
        return False
    
    # Detects a broken 4 in a row and apply block
    def detect_broken_4(self, player):
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        
        for r in range(self.board_size):
            for c in range(self.board_size):
                for dr, dc in directions:
                    positions = []
                    for step in range(5):  # Look at 5-cell segments to find broken 4s
                        nr, nc = r + step * dr, c + step * dc
                        if 0 <= nr < self.board_size and 0 <= nc < self.board_size:
                            positions.append((nr, nc))
                        else:
                            break
                    if len(positions) == 5:
                        vals = [self.board[nr, nc] for nr, nc in positions]
                        # Count how many are player's pieces and how many are empty
                        if vals.count(player) == 4 and vals.count(0) == 1:
                            empty_index = vals.index(0)
                            er, ec = positions[empty_index]
                            # Check if the empty spot is actually playable (not floating)
                            if er == self.board_size - 1 or self.board[er + 1, ec] != 0:
                                return True  # Threat detected
        return False


    def render(self):
        """Prints the board for debugging."""
        print("\n".join([" ".join(["X" if c == 1 else "O" if c == -1 else "." for c in row]) for row in self.board]))
        print()