import time

import MinimaxPlayer
import numpy
from collections import deque
from Board import Board

def h1(loc, rival, moves, rival_moves, size):
    return moves * center_dist(rival, size) - rival_moves * center_dist(loc, size)


def h2(player):
    ploc, rloc = player.loc, player.rival
    moves = len(player.get_moves(ploc))
    rival = len(player.get_moves(rloc))
    size = player.board.shape
    return moves - rival - distance(ploc, rloc) - center_dist(ploc, size)


def dijkistra_matrix(player, board, loc):
    # start = time.time()
    visited = numpy.zeros(board.shape)
    dist = numpy.zeros(board.shape)
    dist[:] = numpy.inf
    dist[loc] = 0

    first_neighbours = get_moves(board, loc)
    for n in first_neighbours:
        dist[n] = 1

    que = deque(first_neighbours)

    while len(que) != 0:
        min_loc = que.popleft()
        for n in get_moves(board, min_loc):
            if dist[n] > dist[min_loc] + 1:
                dist[n] = dist[min_loc] + 1
            if visited[n] == 0:
                que.append(n)
                visited[n] = 1

    # elapsed = 1000*(time.time() - start)
    # update_time(elapsed, "Dijkstra Matrix")
    return dist


def dijkistra_max(player, board, loc):
    start = time.time()
    visited = numpy.zeros(board.shape)
    dist = numpy.zeros(board.shape)
    dist[:] = numpy.inf
    dist[loc] = 0

    max =0
    first_neighbours = get_moves(board, loc)
    for n in first_neighbours:
        dist[n] = 1

    que = deque(first_neighbours)

    while len(que) != 0:
        min_loc = que.popleft()
        for n in get_moves(board, min_loc):
            if dist[n] > dist[min_loc] + 1:
                dist[n] = dist[min_loc] + 1
                if dist[n] > max:
                    max = dist[n]
            if visited[n] == 0:
                que.append(n)
                visited[n] = 1

    elapsed = 1000 * (time.time() - start)
    update_time(elapsed, "Dijkstra Max")
    return max


def h3(player):
    start = time.time()
    dist1 = dijkistra_matrix(player, player.board, player.loc)
    dist2 = dijkistra_matrix(player, player.board, player.rival)
    count1, count2 = 0, 0
    for row in range(0, player.board.shape[0]):
        for col in range(0, player.board.shape[1]):
            if dist1[row, col] < dist2[row, col] and dist1[row, col] != numpy.inf:
                count1 += 1
            if dist2[row, col] < dist1[row, col] and dist2[row, col] != numpy.inf:
                count2 += 1
    elapsed = 1000*(time.time() - start)
    update_time(elapsed, "Double dijkstra")
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


def h5(player):
    p_dists = dijkistra_matrix(player, player.board, player.loc)
    if p_dists[player.rival] == numpy.inf:
        return h_future_moves(player, player.loc, 5)
    else:
        r_dists = dijkistra_matrix(player, player.board, player.rival)
        count1, count2 = 0, 0
        for row in range(0, player.board.shape[0]):
            for col in range(0, player.board.shape[1]):
                if p_dists[row, col] < r_dists[row, col] and p_dists[row, col] != numpy.inf:
                    count1 += 1
                if r_dists[row, col] < p_dists[row, col] and r_dists[row, col] != numpy.inf:
                    count2 += 1
        return count1 - count2

def max_free_direction(player):
    loc1 = player.loc
    max = 0
    for dir in player.directons:
        count = 0
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
    global max_time
    start = time.time()
    h, w = player.board.shape
    l, r = max(loc[1] - depth, 0), min(loc[1] + depth, w-1)
    u, d = max(0, loc[0] - depth), min(loc[0] + depth, h-1)
    moves = deque(player.get_moves(loc))
    visited = []
    count = 0
    while moves:
        m = moves.popleft()
        if distance(loc, m) <= depth and m not in visited:
            count += 1
            visited.append(m)
            moves += player.get_moves(m)

    update_time(1000*(time.time() - start), "Future moves")
    return count / depth


def dfs(player, loc):
    start = time.time()
    global max_time
    visited = numpy.zeros(player.board.shape)
    visited[loc] = 1
    moves = deque([loc])
    count = 0
    while moves:
        # print(moves)
        m = moves.popleft()
        for n in player.get_moves(m):
            if not visited[n]:
                count += 1
                visited[n] = count
                moves.append(n)

    max_time = max((time.time() - start)*1000, max_time)
    # print("DFS count: {}".format(count))
    # print(visited)
    # print()
    return count


def h_minimax(player):
    min_len = min(player.board.shape)
    v1 = h_future_moves(player, player.loc, min_len/4)
    v2 = h_manhattan_distance(player)/player.board.size
    v3 = h_next_move_options(player)/3
    return v1 - v2 + v3


def h_articulations(player):
    board = find_articulations(player)

    p_dists = dijkistra_matrix(player, board, player.loc)
    r_dists = dijkistra_matrix(player, board, player.rival)
    count1, count2 = 0, 0
    for row in range(0, player.board.shape[0]):
        for col in range(0, player.board.shape[1]):
            if p_dists[row, col] < r_dists[row, col] and p_dists[row, col] != numpy.inf:
                count1 += 1
            if r_dists[row, col] < p_dists[row, col] and r_dists[row, col] != numpy.inf:
                count2 += 1
    return count1 - count2

#
#
#   Components defined by articulation points
#
#

def h_components(player):
    start = time.time()
    p_dist = dijkistra_matrix(player, player.board, player.loc)
    r_dist = dijkistra_matrix(player, player.board, player.rival)

    player.board[player.loc], player.board[player.rival] = 0, 0
    arts1 = find_articulations(player)
    arts2 = find_articulations(player, True)

    visited = numpy.zeros(player.board.shape)

    c1, e1, _ = evaluate_components(p_dist, r_dist, player.board, arts1, visited, player.loc, player.time_up)
    c2, e2, _ = evaluate_components(r_dist, p_dist, player.board, arts2, visited, player.rival, player.time_up)

    player.board[player.loc], player.board[player.rival] = 1, 2
    elapsed = 1000 * (time.time() - start)
    update_time(elapsed, "Components")
    return (c1 - c2) + 3*(e1 - e2)


def evaluate_components(dists1, dists2, board, arts, visited, loc, timer):
    if timer():
        return -100, -100, False

    #   Explore the component that contains loc and is blocked by walls and articulation points
    cells, edges, pts, border = explore_component(dists1, dists2, board, arts, loc, visited, timer)

    best = [0, (cells, edges)]

    #   Recursively evaluate adjacent components
    for p in pts:
        c, e, b = evaluate_components(dists1, dists2, board, arts, visited, p, timer)
        # If the component includes 'border' cells (cells that are closer to the rival)
        # add the distance required to reach it; otherwise, merge components and try to maximize space
        size = c + cells if not b else c + dists1[p]

        if size > best[0]:
            best[0] = size
            best[1] = (c, e) if b else (cells + c, edges + e)

    return best[1][0], best[1][1], border


# def explore_component(dists1, dists2, board, arts, loc, visited, border=False):
#     if visited[loc]:
#         return 0, 0, [], border
#     cells, edges = 1, 0
#     cut_points = []
#     visited[loc] = 1
#
#     for n in get_moves(board, loc):
#         edges += 1
#         if not visited[n]:
#             if dists1[n] >= dists2[n]:
#                 border = True
#                 continue
#
#             if arts[n] == 3 or arts[loc] == 3:
#                 cut_points.append(n)
#                 continue
#
#             c, e, pts, border = explore_component(dists1, dists2, board, arts, n, visited, border)
#             cells += c
#             edges += e
#             cut_points += pts
#     return cells, edges, cut_points, border

def explore_component(dists1, dists2, board, arts, loc, visited, timer, border=False):
    cell_stack = deque([loc])
    cut_points = []

    cells, edges = 0, 0
    while cell_stack and not timer():
        # print(cell_stack)
        cell = cell_stack.pop()
        if visited[cell]:
            continue
        visited[cell] = 1
        cells += 1
        for n in get_moves(board, cell):
            if not visited[n]:
                edges += 1
                if dists1[n] >= dists2[n]:
                    border = True
                    continue

                if arts[n] == 3 or arts[cell] == 3:
                    cut_points.append(n)
                    continue

                # TODO: Check if this makes timeouts go away, maybe try play with the number (40)
                if distance(loc, n) >= 40:
                    continue

                cell_stack.append(n)

    return cells, edges, cut_points, border


"""
    Find articulation points in map
    https://www.geeksforgeeks.org/articulation-points-or-cut-vertices-in-a-graph/
"""
def find_articulations(player, rival=False):
    loc = player.loc if not rival else player.rival
    visited = numpy.zeros(player.board.shape)
    low = numpy.zeros(player.board.shape)
    low[:] = numpy.inf
    num = numpy.zeros(player.board.shape)
    num[:] = numpy.inf
    parent = numpy.zeros(player.board.shape)
    parent[loc] = -1
    board = numpy.copy(player.board)
    # print()
    # print(board)
    # print()
    art_util(board, visited, low, num, parent, 1, loc)

    # print(board)
    # exit()

    return board


def art_util(board, visited, low, num, parent, count, loc):
    if count == 800:    # Preventing recursion crash
        return
    visited[loc] = 1
    low[loc], num[loc], count = count, count, count + 1
    fwd_edges = 0
    for move in get_moves(board, loc):
        if not visited[move]:
            fwd_edges += 1
            parent[move] = board.shape[1] * loc[0] + loc[1]
            art_util(board, visited, low, num, parent, count, move)
            if low[move] >= num[loc] and board[loc] == 0:
                board[loc] = 3
            low[loc] = min(low[loc], low[move])
        else:
            if parent[loc] != board.shape[1] * move[0] + move[1]:
                low[loc] = min(low[loc], num[move])

    if parent[loc] == -1 and fwd_edges >= 2:
        board[loc] = 3

"""
    Timing utility functions
"""
max_time = 0
max_func = ""

def get_time():
    global max_time
    global max_func
    t = max_time
    # print("Longest function is {} with {} ms".format(max_func, max_time))
    max_time = 0
    return t


def update_time(t, func):
    global max_time
    global max_func
    if t > max_time:
        max_time = t
        max_func = func



"""
    Utility
"""


def get_moves(board, loc):
    i, j = loc
    moves = [(i + x, j + y) for x, y in [(1, 0), (0, 1), (-1, 0), (0, -1)] if is_legal(board, (i + x, j + y))]
    # shuffle(moves)
    return moves


def is_legal(board, loc):
    i, j = loc
    h, w = board.shape
    # Check whether in the board's limits and free to use
    return 0 <= i < h and 0 <= j < w and board[loc] == 0

def distance(loc1, loc2):
    i, j = loc1
    x, y = loc2
    return abs(y-j) + abs(x-i)


def center_dist(loc, size):
    center = (size[0]/2, size[1]/2)
    return distance(loc, center)

"""
    Start analysis
"""


def find_rival(player):
    start = time.time()
    player.board[player.rival] = 0
    visited = numpy.zeros(player.board.shape)
    q = deque([player.loc])

    while q and not visited[player.rival]:
        loc = q.popleft()
        dist = visited[loc] + 1
        for move in player.get_moves(loc):
            if not visited[move]:
                visited[move] = dist
                q.append(move)

    player.board[player.rival] = 2

    elapsed = 1000*(time.time() - start)
    update_time(elapsed, "Find rival")
    return visited[player.rival]

