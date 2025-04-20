class TicTacToe:
    def __init__(self):
        self.board = [" "] * 9  
        self.current_winner = None 

    def available_moves(self):
        return [i for i in range(9) if self.board[i] == " "]

    def make_move(self, position, player):
        if self.board[position] == " ":
            self.board[position] = player
            if self.check_winner(player):
                self.current_winner = player
            return True
        return False

    def check_winner(self, player):
        winning_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8], 
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6] 
        ]
        for combo in winning_combinations:
            if all(self.board[i] == player for i in combo):
                return True
        return False

    def reset(self):
        self.board = [" "] * 9
        self.current_winner = None