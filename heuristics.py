import MinimaxPlayer
import numpy
from collections import deque
from Board import Board


def dist(loc1, loc2):
    i, j = loc1
    x, y = loc2
    return (y-j)**2 + (x-i)**2


def center_dist(loc, size):
    center = (size[0]/2, size[1]/2)
    return dist(loc, center)


def h1(loc, rival, moves, rival_moves, size):
    return moves * center_dist(rival, size) - rival_moves * center_dist(loc, size)


def h2(player):
    ploc, rloc = player.loc, player.rival
    moves = len(player.get_moves(ploc))
    rival = len(player.get_moves(rloc))
    size = player.board.shape
    return moves - rival - dist(ploc, rloc) - center_dist(ploc, size)

def get_neighbours(board, loc):
    neighbours = set()
    x, y = loc[0], loc[1]
    if x+1 <= board.size[0]-1:
        if board[x+1,y] == 0:
            neighbours.add((x+1,y))
    if y+1 <= board.size[1]-1:
        if board[x,y+1] == 0:
            neighbours.add((x,y+1))
    if x-1 >= 0:
        if board[x-1,y] == 0:
            neighbours.add((x-1,y))
    if y-1 >= 0:
        if board[x,y-1] == 0:
            neighbours.add((x,y-1))
    return neighbours


def dijkistra_matrix(board, loc):
    visited = numpy.zeros(board.size)
    dist = numpy.zeros(board.size)
    dist[:] = numpy.inf
    x, y = loc[0], loc[1]
    dist[x,y] = 0

    first_neighbours = get_neighbours(board, loc)
    for n in first_neighbours:
        x1,y1 = n[0],n[1]
        dist[x1,y1]= 1

    que = deque(first_neighbours)

    while len(que) != 0:
        min_loc = que.popleft()
        min_x, min_y = min_loc[0], min_loc[1]
        for n in get_neighbours(board,min_loc):
            x,y = n[0],n[1]
            if dist[x,y] > dist[min_x,min_y] + 1:
                dist[x,y] = dist[min_x,min_y] + 1
            if visited[x,y] == 0:
                que.append(n)
                visited[x,y] = 1

    return dist

def h3(player):
    loc1 = player.loc
    loc2 = player.rival
    board = player.board
    dist1 = dijkistra_matrix(board, loc1)
    dist2 = dijkistra_matrix(board, loc2)
    count1 = 0
    count2 = 0
    for row in range(0, board.size[0]):
        for col in range(0, board.size[1]):
            if dist1[row, col] == numpy.inf and dist2[row, col] == numpy.inf :
                continue
            if dist1[row, col] == numpy.inf:
                count2 += 1
                continue
            if dist2[row, col] == numpy.inf:
                count1 += 1
                continue
            if dist1[row, col] < dist2[row, col]:
                count1 += 1
                continue
            if dist1[row, col] < dist2[row, col]:
                count2 += 1
                continue
    return count1 - count2

def print_board_to_terminal(board):
    # print(board_to_print)
    print('_' * board.size[0] * 4)
    for row in range(0, board.size[0]):
        for col in range(0, board.size[1]):
            print(board[row,col],end= "  ", flush=True)
        print()


if __name__ == '__main__':
    board = Board((4,4), [],[(0,0),(3,3)])
    print_board_to_terminal(board)
    dist = dijkistra_matrix(board,(0,0))
    print(dist)
