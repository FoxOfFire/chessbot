from enum import Enum, auto
from random import choice

import chess


class Modes(Enum):
    RANDOM = auto()


board = chess.Board()


def randombot(board: chess.Board) -> chess.Board:

    moves = board.generate_legal_moves()

    move_l = []
    for move in moves:
        move_l.append(move)

    board.push(choice(move_l))
    return board


while not board.is_game_over():
    board = randombot(board)
    print()
    print(board)
