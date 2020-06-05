def dist(loc1, loc2):
    i, j = loc1
    x, y = loc2
    return (y-j)**2 + (x-i)**2


def center_dist(loc, size):
    center = (size[0]/2, size[1]/2)
    return dist(loc, center)


def h1(loc, rival, moves, rival_moves, size):
    return moves * center_dist(rival, size) - rival_moves * center_dist(loc, size)
