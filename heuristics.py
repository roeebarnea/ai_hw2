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


def h4(player, moves, rival):
    return player.future_moves(player.loc, min(player.board.shape)) + (moves - rival) / 3.0 + \
           distance(player.loc, player.rival) / player.board.size
