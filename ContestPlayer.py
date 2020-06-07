import time
import heuristics
from random import shuffle


class ContestPlayer:
    def __init__(self):
        self.loc = None
        self.rival = None
        self.board = None
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.endgame = False

        self.buffer = 50 # adjusts the time buffer - the algorithm folds up once there's less than buffer ms left
        self.time, self.start = 0, 0  # total time given for a run and start time, initialized in each call

        # Minimax values of first level of sons for this run
        self.sons = [dict(), dict()]

        self.debug = False

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

    #####################
    #   Time utilities  #
    #####################

    def time_up(self):
        return self.time_left() <= self.buffer

    def time_left(self):
        #   Compute time left for the run in milliseconds
        return (self.time - (time.time() - self.start)) * 1000

    #####################
    #   Move utilities  #
    #####################

    def get_moves(self, loc):
        i, j = loc
        moves = [(i + x, j + y) for x, y in self.directions if self.is_legal((i + x, j + y))]
        shuffle(moves)
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

    def set_move(self, loc, curr):
        if not loc:
            print("loc is messed up, time left: {}".format(self.time_left()))
            self.debug = True
            return self.set_move(self.get_moves(curr)[0], curr)
        self.board[curr], self.board[loc] = -1, 1
        self.loc = loc
        return loc[0] - curr[0], loc[1] - curr[1]

    def set_rival_move(self, loc):
        self.board[loc] = 2
        self.board[self.rival] = -1
        self.rival = loc

    """
        Utility for son organization
    """
    def get_sons(self, agent=1):
        # Sons dict is cleared at the start of each make_move calll, so if it's empty we initialize it with the sons
        if not self.sons[0]:
            self.sons[0] = {move: 0 for move in self.get_moves(self.loc)}
            self.sons[1] = {move: 0 for move in self.get_moves(self.rival)}
            return
        # Otherwise, sons is already initialized with a previous iteration's values - return the possible moves sorted
        if agent == 1:
            return sorted(self.sons[agent - 1], key=self.sons[agent-1].get, reverse=True)
        else:
            return sorted(self.sons[agent - 1], key=self.sons[agent-1].get, reverse=False)

    ##########################
    #                        #
    #   Main move functions  #
    #                        #
    ##########################

    """
        Main move function - checks whether we're at endgame already an then uses minimax to find best move
    """
    def make_move(self, t):
        self.time, self.start = t, time.time()

        # self.endgame = True
        if self.endgame or not heuristics.find_rival(self):
            self.endgame = True

        best_move = self.minimax()
        return self.set_move(best_move, self.loc)

    """
        Iterative deepening with minimax
    """
    def minimax(self):
        best_move, best_score = None, float('-inf')
        limit = self.board.size
        depth = min(5, limit)
        self.sons[0].clear()
        self.sons[1].clear()
        self.get_sons(-1)

        while self.time_left() > self.buffer and depth <= limit:
            move, score, leaves = self.RBMinimax(depth, 1, float('-inf'), float('inf'), True)
            if score >= best_score:
                best_move = move
                best_score = score
            depth += 1
            # print("Minimax best: {}, {} [ Depth: {} ]".format(best_move, best_score, depth-1))
            if best_score == float('inf'):
                break

        # print("Minimax final best: {}, {} [ Depth: {} ]".format(best_move, best_score, depth-1))
        # print("Reached depth {} with score {}".format(depth-1, best_score))
        return best_move

    """
        Score functions: analyzes if we're at a final state or returns a heuristic value
        If at endgame, uses endgame heuristic to maximize space utilizations
        Otherwise, uses a more sophisticated heuristic
        If time is up, prunes the branch
    """
    def score(self, turn):
        moves = len(self.get_moves(self.loc))
        rival_moves = len(self.get_moves(self.rival))
        win, lose = float('inf'), float('-inf')

        if not rival_moves and not moves:
            return -100  # Tie penalty
        elif not rival_moves and turn == 2:  # Rival is out of moves but we're not
            return win
        elif not moves and turn == 1:  # We're out of moves but rival isn't
            return lose

        if self.endgame:
            return heuristics.dfs(self, self.loc) - moves
        if self.time_left() <= self.buffer:
            # print("timeout penalty")
            return lose if turn == 2 else win
        return heuristics.h_components(self)

    """
        RB minimax, with options for son sorting in the first two levels
    """
    def RBMinimax(self, depth, agent, alpha, beta, sons=False):
        # If we're out of time or the state is final, finish up
        if self.time_left() <= self.buffer or self.is_final(depth, agent):
            return self.loc, self.score(agent), 1

        best_move, leaves = None, 0

        # It's our turn - max node
        if agent == 1:
            curr_max = float('-inf')
            last_loc = self.loc
            moves = self.get_sons(1) if sons else self.get_moves(last_loc)
            # if sons:
            #     print("Depth 1 sons")
            #     print("Depth: [ {} ]".format(depth))
            #     print(self.sons)
            #     print(moves)
            #     print()
            self.board[last_loc] = -1

            for d in moves:
                self.loc = d
                self.board[d] = 1
                loc, score, leaf = self.RBMinimax(depth - 1, 2, alpha, beta, sons)
                if score >= curr_max:
                    curr_max = score
                    best_move = d

                leaves += leaf
                self.board[d] = 0
                if sons:
                    self.sons[0][d] = score

                alpha = max(curr_max, alpha)
                if curr_max >= beta:
                    curr_max = float('inf')
                    break

            if self.debug:
                print("Agent {}".format(agent))
                print("Just checked {} for depth {}".format(d, depth))
                print("Best so far: {} with {}".format(best_move, curr_max))
                print("Alpha[{}], Beta[{}]".format(alpha, beta))
                print()
            self.loc = last_loc
            self.board[last_loc] = 1
            return best_move, curr_max, leaves

        # Opponent's turn - min node
        else:
            curr_min = float('inf')
            last_loc = self.rival
            moves = self.get_sons(2) if sons else self.get_moves(last_loc)
            # if sons:
            #     print("Depth 2 sons")
            #     print("Depth: [ {} ]".format(depth))
            #     print(self.sons)
            #     print(moves)
            #     print()
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
                if sons:
                    self.sons[1][d] = score

                beta = min(curr_min, beta)
                if curr_min <= alpha:
                    curr_min = float('-inf')
                    break

            if self.debug:
                print("Agent {}".format(agent))
                print("Just checked {} for depth {}".format(d, depth))
                print("Best so far: {} with {}".format(best_move, curr_min))
                print()
            #   Revert to current state
            self.rival = last_loc
            self.board[last_loc] = 2
            return best_move, curr_min, leaves
