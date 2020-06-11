from DijkistraAlphaBetaPlayer import DijkistraAlphaBetaPlayer
from LiteAlphaBetaPlayer import LiteAlphaBetaPlayer
from NotAnimatedGameTest import *
import LiveAnimatedGame
from MapsGenerator import *
from ContestPlayer import ContestPlayer
from HeavyAlphaBetaPlayer import HeavyAlphaBetaPlayer
from sympy.stats import Bernoulli, sample_iter
import numpy
import random
import sys, os
import matplotlib.pyplot as plt

from Game import Game
from LivePlayer import LivePlayer
from MapsGenerator import *
from SimplePlayer import SimplePlayer


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


def get_player(player_type, module):
    if player_type == 'LivePlayer':
        player = LivePlayer()
    elif player_type == 'SimplePlayer':
        player = SimplePlayer()
    elif player_type == 'MinimaxPlayer':
        player = module.MinimaxPlayer()
    elif player_type == 'AlphaBetaPlayer':
        player = module.AlphaBetaPlayer()
    elif player_type == 'OrderedAlphaBetaPlayer':
        player = module.OrderedAlphaBetaPlayer()
    elif player_type == 'HeavyAlphaBetaPlayer':
        player = module.HeavyAlphaBetaPlayer()
    elif player_type == 'LiteAlphaBetaPlayer':
        player = module.LiteAlphaBetaPlayer()
    elif player_type == 'ContestPlayer':
        player = module.ContestPlayer()
    elif player_type == 'DijkistraAlphaBetaPlayer':
        player = module.DijkistraAlphaBetaPlayer()
    else:
        print('bad input')
        exit(-1)
    return player


####################################################

def get_random_simetric_map(m, n, obs_percent):
    board = numpy.zeros((m, n))
    # l = list(sample_iter(Bernoulli('X', obs_percent),m*n/2))
    num_of_obs = round(int(m * n / 2) * obs_percent)
    l = random.choices(['obs', 'free'], [num_of_obs, int(m * n / 2) - num_of_obs], k=int(m * n / 2))
    num = num_of_obsF(l)
    while (num < num_of_obs):
        l = random.choices(['obs', 'free'], [num_of_obs, int(m * n / 2) - num_of_obs], k=int(m * n / 2))
        num = num_of_obsF(l)
    count = 0
    i, j = 0, 0
    while i < m:
        while j < n / 2:
            r = l[count]
            if r == "obs":
                board[i, j] = board[m - 1 - i, n - 1 - j] = -1
            j += 1
            count += 1
        j = 0
        i += 1
    found = False
    ii, jj = 0, 0
    while not found:
        ii, jj = random.randrange(m - 1), random.randrange(n - 1)
        if len(get_moves(board, (ii, jj))) > 0:
            found = True
    starts = [(ii, jj), (m - 1 - ii, n - 1 - jj)]
    size, blocks, _ = get_board_data(board)
    return [size, blocks, starts]


def comparison_players_blocks_ratio(player1, player2, move_time, m, n, rat, times):
    map = get_random_simetric_map(m, n, rat)
    sz, bl, st = map
    b = build_board(sz, bl, st)
    print("Board size: {}\nBlocks: {}\nStart points: {}".format(map[0], map[1], map[2]))
    print(b)
    real_rat = len(map[1]) / (m * n)
    print('Starting Game')
    print(player1, 'VS', "Dij")
    print('Players (besides LivePlayer) have', move_time, 'seconds to make a move')
    ties, win_1, win_2 = 0, 0, 0
    for x in range(times):
        heavy_player = LiteAlphaBetaPlayer()
        p = DijkistraAlphaBetaPlayer()
        contest_player = ContestPlayer()
        game = NotAnimatedGameTest(map[0], map[1], map[2], player_1=contest_player, player_2=p,
                                   time_to_make_a_move=move_time, print_game_in_terminal=False)
        sys.stdout = sys.__stdout__
        if game.score == 0:
            ties += 1
        elif game.score == 1:
            win_1 += 1
        elif game.score == 2:
            win_2 += 1

    return ties, win_1, win_2, real_rat


def comparison_players_blocks_ratio_tests(player1, player2, move_time, m, n, rat, num_of_maps_same_ratio,
                                          tests_per_map):
    ties, win_1, win_2 = 0, 0, 0
    for x in range(num_of_maps_same_ratio):
        ret = comparison_players_blocks_ratio(player1, player2, move_time, m, n, rat, tests_per_map)
        ties += ret[0]
        win_1 += ret[1]
        win_2 += ret[2]
    return ties, win_1, win_2


def test_2_players_different_ratios(player1, player2, move_time, m, n, num_of_maps_same_ratio, tests_per_map):
    rats, ties, players1, players2 = [], [], [], []
    total = num_of_maps_same_ratio * tests_per_map
    for x in range(1, 9, 1):
        rat = x / 10
        rats.append(rat)
        ret = comparison_players_blocks_ratio_tests(player1, player2, move_time, m, n, rat, num_of_maps_same_ratio,
                                                    tests_per_map)
        print("Player 1: {}\tPlayer 2:{}\tTies:{}".format(ret[1], ret[2], ret[0]))
        ties.append(ret[0] / total)
        players1.append(ret[1] / total)
        players2.append(ret[2] / total)
    plt.plot(rats, ties, 'bs', rats, players1, 'g^', rats, players2, 'r--')
    plt.show()


#######################################################


def get_random_simetric_map_with_border(m, n, p):
    board = numpy.zeros((m, n))
    if n % 2 == 0:
        for i in range(0, m, 1):
            for j in range(int(n / 2 - 1), int(n / 2 + 1), 1):
                board[i, j] = -1
        num_of_obs = round((m * n - 2 * m) / 2 * p)
        l = random.choices(['obs', 'free'], [num_of_obs, int((m * n - 2 * m) / 2 - num_of_obs)],
                           k=int((m * n - 2 * m) / 2))
        num = num_of_obsF(l)
        while (num < num_of_obs):
            l = random.choices(['obs', 'free'], [num_of_obs, int((m * n - 2 * m) / 2 - num_of_obs)],
                               k=int((m * n - 2 * m) / 2))
            num = num_of_obsF(l)
        count = 0
        for i in range(0, m, 1):
            for j in range(0, int(n / 2 - 1), 1):
                r = l[count]
                if r == "obs":
                    board[i, j] = board[i, n - 1 - j] = -1
                count += 1
    else:
        for i in range(0, m, 1):
            board[i, int((n - 1) / 2)] = -1
        num_of_obs = round((m * n - m) / 2 * p)
        l = random.choices(['obs', 'free'], [num_of_obs, int((m * n - m) / 2 - num_of_obs)], k=int((m * n - m) / 2))
        num = num_of_obsF(l)
        while (num < num_of_obs):
            num_of_obs = round((m * n - m) / 2 * p)
            l = random.choices(['obs', 'free'], [num_of_obs, int((m * n - m) / 2 - num_of_obs)], k=int((m * n - m) / 2))
        count = 0
        for i in range(0, m, 1):
            for j in range(0, int((n - 1) / 2), 1):
                r = l[count]
                if r == "obs":
                    board[i, j] = board[i, n - 1 - j] = -1
                count += 1

    found = False
    ii, jj = 0, 0
    while not found:
        ii, jj = random.randrange(m - 1), random.randrange(round((n - 1) / 2))
        if len(get_moves(board, (ii, jj))) > 0:
            found = True
    starts = [(ii, jj), (ii, n - 1 - jj)]
    size, blocks, _ = get_board_data(board)
    return [size, blocks, starts]


def play_with_border(player_1_type, player_2_type, m, n, p, num_of_plays, time_for_move):
    map = get_random_simetric_map_with_border(m, n, p)
    real_rat = len(map[1]) / (m * n)
    print()
    print('####################')
    print('Starting Game')
    print(player_1_type, 'VS', player_2_type)
    ties, win_1, win_2 = 0, 0, 0
    for i in range(num_of_plays):
        module_1 = __import__(player_1_type)
        module_2 = __import__(player_2_type)
        player_1 = get_player(player_1_type, module_1)
        player_2 = get_player(player_2_type, module_2)
        starts_copy = map[2].copy()
        game = NotAnimatedGameTest(map[0], map[1], starts_copy, player_1=player_1, player_2=player_2,
                                   time_to_make_a_move=time_for_move, print_game_in_terminal=False)
        sys.stdout = sys.__stdout__
        if game.score == 0:
            ties += 1
        elif game.score == 1:
            win_1 += 1
        elif game.score == 2:
            win_2 += 1

    print('number of ties in session', ties)
    print('number of wins of player 1 in session', win_1)
    print('number of wins of player 2 in session', win_2)
    return ties, win_1, win_2, real_rat


def test_border(player_1_type, player_2_type, m, n, p, num_of_plays, time_for_move, tests):
    ties, players1, players2 = 0, 0, 0
    total = num_of_plays * tests
    for x in range(tests):
        ret = play_with_border(player_1_type, player_2_type, m, n, p, num_of_plays, time_for_move)
        ties += ret[0]
        players1 += ret[1]
        players2 += ret[2]

    print()
    print('***----------TEST RESULTS----------***')
    print(player_1_type, 'VS', player_2_type)
    print('number of boards: ', tests)
    print('number of plays per board: ', num_of_plays)
    print('sum of overall plays', num_of_plays * tests)
    print()
    print('number of ties:', ties, 'precentage:', ties / total)
    print('number of player 1 wins:', players1, 'precentage:', players1 / total)
    print('number of player 2 wins:', players2, 'precentage:', players2 / total)
    print('***--------------------------------***')
    print()


if __name__ == '__main__':
    # test_border('ContestPlayer', 'DijkistraAlphaBetaPlayer', 12 ,12, 0.2, 10, 2, 5)
    # test_border('LiteAlphaBetaPlayer', 'DijkistraAlphaBetaPlayer', 12 ,12, 0.2, 10, 2, 5)
    # test_border('MinimaxPlayer', 'DijkistraAlphaBetaPlayer', 12 ,12, 0.2, 10, 2, 5)
    test_2_players_different_ratios('ContestPlayer', 'LiteAlphaBetaPlayer', move_time=1, m=40,
                                    n=40, num_of_maps_same_ratio=5, tests_per_map=5)
    test_2_players_different_ratios('ContestPlayer', 'HeavyAlphaBetaPlayer', move_time=1, m=44,
                                    n=50, num_of_maps_same_ratio=5, tests_per_map=5)
    test_2_players_different_ratios('ContestPlayer', 'AlphaBetaPlayer', move_time=1, m=40,
                                    n=60, num_of_maps_same_ratio=5, tests_per_map=5)
