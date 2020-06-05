import time

import MinimaxPlayer
import numpy
from collections import deque
from Board import Board


def distance(loc1, loc2):
    i, j = loc1
    x, y = loc2
    return (y-j)**2 + (x-i)**2


def center_dist(loc, size):
    center = (size[0]/2, size[1]/2)
    return distance(loc, center)


def h1(loc, rival, moves, rival_moves, size):
    return moves * center_dist(rival, size) - rival_moves * center_dist(loc, size)


def h2(player):
    ploc, rloc = player.loc, player.rival
    moves = len(player.get_moves(ploc))
    rival = len(player.get_moves(rloc))
    size = player.board.shape
    return moves - rival - distance(ploc, rloc) - center_dist(ploc, size)


def dijkistra_matrix(player, board, loc):
    visited = numpy.zeros(board.shape)
    dist = numpy.zeros(board.shape)
    dist[:] = numpy.inf
    dist[loc] = 0

    first_neighbours = player.get_moves(loc)
    for n in first_neighbours:
        dist[n] = 1

    que = deque(first_neighbours)

    while len(que) != 0:
        min_loc = que.popleft()
        for n in player.get_moves(min_loc):
            if dist[n] > dist[min_loc] + 1:
                dist[n] = dist[min_loc] + 1
            if visited[n] == 0:
                que.append(n)
                visited[n] = 1

    return dist


def h3(player):
    dist1 = dijkistra_matrix(player, player.board, player.loc)
    dist2 = dijkistra_matrix(player, player.board, player.rival)
    count1, count2 = 0, 0
    for row in range(0, player.board.shape[0]):
        for col in range(0, player.board.shape[1]):
            if dist1[row, col] < dist2[row, col] and dist1[row, col] != numpy.inf:
                count1 += 1
            if dist2[row, col] < dist1[row, col] and dist2[row, col] != numpy.inf:
                count2 += 1
    return count1 - count2

def h_next_move_options(player):
    loc1 = player.loc
    loc2 = player.rival
    return len(player.get_moves(loc1)) - len(player.get_moves(loc2))

def h_manhattan_distance(player):
    loc1 = player.loc
    loc2 = player.rival
    return numpy.abs(loc1[0] - loc2[0]) + numpy.abs(loc1[1] - loc2[1])

def h4(player, moves, rival):
    return player.future_moves(player.loc, min(player.board.shape)) + (moves - rival) / 3.0 + \
           distance(player.loc, player.rival) / player.board.size

def max_free_direction(player):
    loc1 = player.loc
    max = 0
    for dir in player.directons:
        count =0
        curr = (loc1[0], loc1[1])
        curr[0] += dir[0]
        curr[1] += dir[1]
        while player.is_legal(curr):
            count += 1
            curr[0] += dir[0]
            curr[1] += dir[1]
        if count > max:
            max = count
    return max

def h_future_moves(player, loc, depth):
    l, r = loc[1] - depth, loc[1] + depth
    u, d = loc[0] - depth, loc[0] + depth
    moves = player.get_moves(loc)
    visited = []
    count = 0
    while moves:
        m = moves.pop(0)
        if l <= m[1] <= r and u <= m[0] <= d and m not in visited:
            count += 1
            visited.append(m)
            moves += player.get_moves(m)
    return count

def h_minimax(player):
    min_len = min(player.board.shape[0], player.board.shape[1])
    v1 =  h_future_moves(player, player.loc, min_len/4)/min_len
    v2 =  h_manhattan_distance(player)/player.board.size
    v3 = h_next_move_options(player)/3
    return v1+v2+v3