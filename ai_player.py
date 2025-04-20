import random
import json
from tic_tac_toe import TicTacToe

class QLearningTicTacToe:
    def __init__(self, alpha=0.5, gamma=0.9, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.999):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.q_table = {}

    def get_state(self, board, player):
        """Compact state representation including player turn"""
        return "".join(board) + f"|{player}"

    def find_winning_move(self, game, player):
        """Returns a winning move if exists, otherwise None"""
        for move in game.available_moves():
            temp_game = TicTacToe()
            temp_game.board = game.board.copy()
            temp_game.make_move(move, player)
            if temp_game.current_winner:
                return move
        return None

    def update_q_table(self, old_state, action, reward, new_state):
        """Q-learning update rule"""
        old_q = self.q_table.get(f"{old_state}-{action}", 0)
        future_actions = [a for a in range(9) if new_state.split('|')[0][a] == " "]
        future_q = max([self.q_table.get(f"{new_state}-{a}", 0) for a in future_actions], default=0)
        self.q_table[f"{old_state}-{action}"] = old_q + self.alpha * (reward + self.gamma * future_q - old_q)

    def choose_action(self, board, player):
        """Epsilon-greedy action selection"""
        state = self.get_state(board, player)
        available_moves = [i for i in range(9) if board[i] == " "]

        if random.uniform(0, 1) < self.epsilon:
            return random.choice(available_moves)

        q_values = [self.q_table.get(f"{state}-{move}", 0) for move in available_moves]
        max_q = max(q_values)
        best_moves = [move for move, q in zip(available_moves, q_values) if q == max_q]
        return random.choice(best_moves)

    def save_q_table(self, filename="q_table.json"):
        """Save Q-table to file"""
        with open(filename, "w") as f:
            json.dump(self.q_table, f)

    def load_q_table(self, filename="q_table.json"):
        """Load Q-table from file"""
        try:
            with open(filename, "r") as f:
                self.q_table = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.q_table = {}

    def train(self, episodes=10000):
        """Training with occasional mistakes"""
        print(f"🏋️ Training {episodes} episodes (AI will make occasional 'mistakes')...")
        
        for episode in range(episodes):
            game = TicTacToe()
            current_player = "X" if episode % 2 == 0 else "O"
            
            while not game.current_winner and " " in game.board:
                state_before = self.get_state(game.board, current_player)
                
                if current_player == "O":
                    if random.random() < 0.1:
                        action = self.choose_action(game.board, "O")
                    else:
                        win_move = self.find_winning_move(game, "O")
                        if win_move:
                            action = win_move
                        else:
                            block_move = self.find_winning_move(game, "X")
                            action = block_move if block_move else self.choose_action(game.board, "O")
                else:
                    if random.random() < 0.3:
                        block_move = self.find_winning_move(game, "X")
                        action = block_move if block_move else random.choice(game.available_moves())
                    else:
                        action = random.choice(game.available_moves())
                
                game.make_move(action, current_player)
                state_after = self.get_state(game.board, "X" if current_player == "O" else "O")
                
                reward = 0
                if game.current_winner == "O":
                    reward = 5
                elif game.current_winner == "X":
                    reward = -3
                elif " " not in game.board:
                    reward = 1
                
                if action == 4: reward += 0.3
                elif action in [0, 2, 6, 8]: reward += 0.2
                
                if current_player == "O":
                    self.update_q_table(state_before, action, reward, state_after)
                
                current_player = "X" if current_player == "O" else "O"
            
            self.epsilon = max(self.epsilon * self.epsilon_decay, self.epsilon_min)
            
            if episode % 2000 == 0:
                print(f"   Episode {episode}: ε={self.epsilon:.3f}, Q-entries={len(self.q_table)}")
        
        self.save_q_table()
        print(f"✅ Training complete! Final Q-table size: {len(self.q_table)}")

    def play_ai_move(self, game, ai_player="O"):
        """Make a move with occasional human-like imperfections"""
        if random.random() < 0.15:
            action = self.choose_action(game.board, ai_player)
            game.make_move(action, ai_player)
            return
        
        opponent = "X" if ai_player == "O" else "O"
        
        win_move = self.find_winning_move(game, ai_player)
        if win_move:
            game.make_move(win_move, ai_player)
            return
        
        block_move = self.find_winning_move(game, opponent)
        if block_move:
            game.make_move(block_move, ai_player)
            return
        
        action = self.choose_action(game.board, ai_player)
        game.make_move(action, ai_player)
        
        state_before = self.get_state(game.board, ai_player)
        state_after = self.get_state(game.board, opponent)
        
        reward = 0
        if game.current_winner == ai_player:
            reward = 1
        elif game.current_winner:
            reward = -1
        elif " " not in game.board:
            reward = 0.3
        
        self.update_q_table(state_before, action, reward, state_after)
        self.epsilon = max(self.epsilon * self.epsilon_decay, self.epsilon_min)