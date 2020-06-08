from NotAnimatedGameTest import *
from MapsGenerator import *
from ContestPlayer import ContestPlayer
from HeavyAlphaBetaPlayer import HeavyAlphaBetaPlayer
from sympy.stats import Bernoulli, sample_iter
import numpy
import random
import sys, os


def is_legal(board, loc):
    i, j = loc
    h, w = board.shape
    # Check whether in the board's limits and free to use
    return 0 <= i < h and 0 <= j < w and board[loc] == 0

def get_moves(board, loc):
    i, j = loc
    directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    moves = [(i + x, j + y) for x, y in directions if is_legal(board, (i + x, j + y))]
    return moves

def num_of_obsF(l):
    count = 0
    for x in l:
        if x == 'obs':
            count += 1
    return count


def get_random_simetric_map(m, n, obs_percent):
    board = numpy.zeros((m,n))
    # l = list(sample_iter(Bernoulli('X', obs_percent),m*n/2))
    num_of_obs = round(int(m*n/2)*obs_percent)
    l = random.choices(['obs','free'],[num_of_obs, int(m*n/2) - num_of_obs], k = int(m*n/2))
    num = num_of_obsF(l)
    while(num < num_of_obs):
        l = random.choices(['obs', 'free'], [num_of_obs, int(m * n / 2) - num_of_obs], k=int(m * n / 2))
        num = num_of_obsF(l)
    count =0
    i ,j  = 0, 0
    while i<m :
        while j< n/2:
            r = l[count]
            if r == "obs":
                board[i,j] = board[m-1-i, n-1-j] = -1
            j+= 1
            count += 1
        j = 0
        i+= 1
    found = False
    ii, jj = 0, 0
    while not found:
        ii, jj = random.randrange(m-1), random.randrange(n-1)
        if len(get_moves(board, (ii,jj))) > 0:
            found =True
    starts = [(ii, jj), (m-1-ii, n-1-jj)]
    size, blocks, _ = get_board_data(board)
    return [size, blocks, starts]

def comparison_players_blocks_ratio(player1, player2, move_time, m ,n ,rat):
    map = get_random_simetric_map(m,n, rat)
    real_rat = len(map[1])/(m*n)
    print('Starting Game')
    print(type(player1), 'VS', type(player2))
    print('Players (besides LivePlayer) have', move_time, 'seconds to make a move')
    game = NotAnimatedGameTest(map[0], map[1], map[2], player_1=player1, player_2=player2,
                    time_to_make_a_move=move_time, print_game_in_terminal=True)
    return real_rat, game.score


if __name__ == '__main__':
    heavy_player= HeavyAlphaBetaPlayer()
    contest_player = ContestPlayer()
    score = comparison_players_blocks_ratio(heavy_player, contest_player, 2, 6, 8, 0.1)
    print("BALASGASGLASDGKASLGASGL")
    # print("the score is ",score[1], ", the real ratio is ", score[0])