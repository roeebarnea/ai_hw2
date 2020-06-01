import time

class MinimaxPlayer:
    def __init__(self):3
        self.loc = None
        self.board = None
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]

    def set_game_params(self, board):
        self.board = board
        for i, row in enumerate(board):
            for j, val in enumerate(row):
                if val == 1:
                    self.loc = (i, j)
                    break

    # return the position of player 1
    def position_of_1(board):
        for i, row in enumerate(board):
            for j, val in enumerate(row):
                if val == 1:
                    return i , j

    #return the position of player 2
    def position_of_2(board):
        for i, row in enumerate(board):
            for j, val in enumerate(row):
                if val == 2:
                    return i, j

    # check if the board is in final state
    def is_final_State(board):
        i1, j1 = position_of_1(board)
        i2, j2 = position_of_2(board)
        if i1+1 <= board.size() and board[i1+1,j1] == 0:
            return False
        if i1-1 >= 0 and board[i1-1,j1] == 0:
            return False
        if j1+1 <= board.size() and board[i1,j1+1] == 0:
            return False
        if j1-1 >= 0 and board[i1,j1-1] == 0:
            return False
        if i2+1 <= board.size() and board[i2+1,j2] == 0:
            return False
        if i2-1 >= 0 and board[i2-1,j2] == 0:
            return False
        if j2+1 <= board.size() and board[i2,j2+1] == 0:
            return False
        if j2-1 >= 0 and board[i2,j2-1] == 0:
            return False
        return True

    def state_score(self, board, loc):
        num_steps_available = 0
        for d in self.directions:
            i = loc[0] + d[0]
            j = loc[1] + d[1]
            if 0 <= i < len(board) and 0 <= j < len(board[0]) and board[i][j] == 0:  # then move is legal
                num_steps_available += 1

        if num_steps_available == 0:
            return -1
        else:
            return 4 - num_steps_available

    def count_ones(self, board):
        counter = 0
        for i, row in enumerate(board):
            for j, val in enumerate(row):
                if val == 1:
                    counter += 1
        return counter

    def h_num_of_moves(self, board, loc):
        num_steps_available = 0
        for d in self.directions:
            i = loc[0] + d[0]
            j = loc[1] + d[1]
            if 0 <= i < len(board) and 0 <= j < len(board[0]) and board[i][j] == 0:  # then move is legal
                num_steps_available += 1
        return  num_steps_available

    # function of the next iteration time limit estimation , it is not true! TODO
    def f(l, last_iteration_time):
        return 4*last_iteration_time*l

    def make_move(self, time):  # time parameter is not used, we assume we have enough time.
        ID_start_time = time()
        dd=1
        l=0
        i,j = position_of_1(self.board)
        move = RBMinimax(self,self.board,(i,j),1,dd,l)[2]
        last_iteration_time = time() - ID_start_time
        next_iteration_max_time = f(l,last_iteration_time)
        time_until_now = time() - ID_start_time
        while time_until_now + next_iteration_max_time < time:
            dd += 1
            l = 0
            iteration_start_time = time()
            move = RBMinimax(self, self.board, (i, j), 1, dd, l)[2]
            last_iteration_time = time() - iteration_start_time
            next_iteration_max_time = f(l, last_iteration_time)
            time_until_now = time() - ID_start_time
        return move

    def set_rival_move(self, loc):
        self.board[loc] = 2

    # RB-MiniMax as the presentation
    # self is only for the directions, board is actually the state - i hard copied it every new node
    # agent_loc is the location of the agent (which tell if its player 1 or 2)
    # dd is the depth is allowed, l number of leaves
    def RBMinimax(self, board, agent_loc, agent, dd, l):
        if is_final_State(board):
            l = l+1
            return h_num_of_moves(self, board, agent_loc), agent_loc
        if  dd==0:
            return h_num_of_moves(self, board, agent_loc), agent_loc
        if agent == 1:
            curr_max = float('-inf')
            last_loc = None
            for d in self.directions:
                i = agent_loc[0] + d[0]
                j = agent_loc[1] + d[1]
                if 0 <= i < len(board) and 0 <= j < len(board[0]) and board[i][j] == 0:  # then move is legal
                    new_board = board
                    board[agent_loc[0], agent_loc[1]] = -1
                    board[i,j] = agent
                    agent_loc= (i,j)
                    v = RBMinimax(self, new_board, agent_loc, 3-agent, dd-1, l)
                    if v[1] > curr_max:
                        curr_max = v[1]
                        last_loc = (i,j)
            return curr_max , last_loc
        else:
            curr_min = float('inf')
            last_loc = None
            for d in self.directions:
                i = agent_loc[0] + d[0]
                j = agent_loc[1] + d[1]
                if 0 <= i < len(board) and 0 <= j < len(board[0]) and board[i][j] == 0:  # then move is legal
                    new_board = board
                    board[agent_loc[0], agent_loc[1]] = -1
                    board[i, j] = agent
                    agent_loc = (i, j)
                    v = RBMinimax(self, new_board, agent_loc, 3 - agent, dd - 1, l)
                    if v[1] < curr_min:
                        curr_min = v[1]
                        last_loc = (i,j)
            return curr_min, last_loc