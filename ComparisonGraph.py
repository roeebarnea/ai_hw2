from MapsGenerator import ai_board
import numpy as np
from LiteAlphaBetaPlayer import LiteAlphaBetaPlayer
import matplotlib.pyplot as plt



if __name__ == '__main__':

    times = []
    depths = []
    for t in np.linspace(0.1, 3, 50):
        player = LiteAlphaBetaPlayer()
        player.set_game_params(ai_board.copy())
        d = player.make_move(t)
        times.append(t)
        depths.append(d)
    plt.scatter(times, depths)
    plt.show()