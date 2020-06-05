import time
import heuristics
from random import shuffle


class AlphaBetaPlayer:
    def __init__(self):
        self.loc = None
        self.rival = None
        self.board = None
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]

        self.buffer = 10 # adjusts the time buffer - the algorithm folds up once there's less than buffer ms left
        self.time, self.start = 0, 0  # total time given for a run and start time, initialized in each call

    def set_game_params(self, board):
        self.board = board
        for i, row in enumerate(board):
            for j, val in enumerate(row):
                if val == 1:
                    self.loc = (i, j)
                elif val == 2:
                    self.rival = (i, j)

                # Getting both our location and rival's location for easier calculations
                if self.loc and self.rival:
                    break

    def get_moves(self, loc):
        i, j = loc
        moves = [(i + x, j + y) for x, y in self.directions if self.is_legal((i + x, j + y))]
        # shuffle(moves)
        return moves

    def is_legal(self, loc):
        i, j = loc
        h, w = self.board.shape
        # Check whether in the board's limits and free to use
        return 0 <= i < h and 0 <= j < w and self.board[loc] == 0

    def is_final(self, depth, turn):
        # A state is final for our run when we've reached max depth and when the current player is out of turns
        if depth == 0:
            return True
        if turn == 1 and not self.get_moves(self.loc):
            return True
        elif turn == 2 and not self.get_moves(self.rival):
            return True
        return False

    def score(self):
        moves = len(self.get_moves(self.loc))
        rival_moves = len(self.get_moves(self.rival))
        win, lose = float('inf'), float('-inf')

        if not rival_moves and moves:       # Rival is out of moves but we're not
            return win
        elif not moves and rival_moves:     # We're out of moves but rival isn't
            return lose

        # TODO: Figure out better heuristics, mine are shit :(
        return moves - rival_moves - heuristics.center_dist(self.loc, self.board.shape)

    def time_left(self):
        #   Compute time left for the run in milliseconds
        return (self.time - (time.time() - self.start)) * 1000

    def make_move(self, t):
        self.time, self.start = t, time.time()
        depth = 1
        best_move, best_score = None, float('-inf')
        while self.time_left() > self.buffer:  # At least #buffer ms left to run
            # print(self.time_left())
            # print(depth)
            best_move, best_score, leaves = self.RBMinimax(depth, 1, float('-inf'), float('inf'))
            depth += 1
        d = (best_move[0] - self.loc[0], best_move[1] - self.loc[1])
        # print(d)
        self.loc = best_move
        return d

    def set_rival_move(self, loc):
        self.board[loc] = 2
        self.board[self.rival] = -1
        self.rival = loc

    def RBMinimax(self, depth, agent, alpha, beta):
        # If we're out of time or the state is final, finish up
        if self.time_left() <= self.buffer or self.is_final(depth, agent):
            return self.loc, self.score(), 1

        best_move, leaves = None, 0

        # It's our turn - max node
        if agent == 1:
            curr_max = float('-inf')
            last_loc = self.loc
            moves = self.get_moves(last_loc)
            self.board[last_loc] = -1

            for d in moves:
                self.loc = d
                self.board[d] = 1
                loc, score, leaf = self.RBMinimax(depth - 1, 2, alpha, beta)
                if score >= curr_max:
                    curr_max = score
                    best_move = d

                leaves += leaf
                self.board[d] = 0

                alpha = max(curr_max, alpha)
                if curr_max >= beta:
                    curr_max = float('inf')
                    break

            self.loc = last_loc
            self.board[last_loc] = 1
            return best_move, curr_max, leaves

        # Opponent's turn - min node
        else:
            curr_min = float('inf')
            last_loc = self.rival
            moves = self.get_moves(last_loc)
            self.board[last_loc] = -1

            for d in moves:
                #   Edit state
                self.rival = d
                self.board[d] = 2
                loc, score, leaf = self.RBMinimax(depth - 1, 1, alpha, beta)
                if score <= curr_min:
                    curr_min = score
                    best_move = d
                leaves += leaf
                #   Revert map value
                self.board[d] = 0

                beta = min(curr_min, beta)
                if curr_min <= alpha:
                    curr_min = float('-inf')
                    break

            #   Revert to current state
            self.rival = last_loc
            self.board[last_loc] = 2
            return best_move, curr_min, leaves

    # Shitty heuristic stuff
    def future_moves(self, loc, depth):
        l, r = loc[1] - depth, loc[1] + depth
        u, d = loc[0] - depth, loc[0] + depth
        moves = self.get_moves(loc)
        visited = []
        count = 0
        while moves:
            m = moves.pop(0)
            if l <= m[1] <= r and u <= m[0] <= d and m not in visited:
                count += 1
                visited.append(m)
                moves += self.get_moves(m)
        return count

