from random import choice
from typing import Dict, List, Tuple

import chess

board = chess.Board()

pieceVals: Dict[chess.PieceType, int] = {
    chess.PAWN: 1000,
    chess.KNIGHT: 3000,
    chess.BISHOP: 3100,
    chess.ROOK: 5000,
    chess.QUEEN: 9000,
    chess.KING: 10000000,
}
CHECKMOD = 500
TRADEMOD = 200


def getval(board: chess.Board) -> int:

    val: int = 0
    for i in chess.SQUARES:
        piece = board.piece_at(i)
        if piece is None:
            continue
        frend = 1 if board.turn == piece.color else -1
        val += frend * pieceVals[piece.piece_type]

    return val


def prev_mov(board: chess.Board) -> List[str]:
    return [str(s) for s in board.move_stack]


def minimax(board: chess.Board, depth: int) -> Tuple[int, List[chess.Move]]:
    best: int = -10000000 if board.turn else 10000000
    legal_moves = board.generate_legal_moves()
    move: List[chess.Move] = []

    for current_move in legal_moves:
        mod = 0
        if board.is_capture(current_move):
            mod += TRADEMOD
        if board.is_into_check(current_move):
            mod -= CHECKMOD * 2

        board.push(current_move)
        if board.is_check():
            mod += CHECKMOD

        if depth < 1:
            val = getval(board)
        else:
            val = minimax(board, depth - 1)[0]

        board.pop()

        if board.is_checkmate():
            return -10000000, [current_move]
        if board.is_stalemate():
            return 0, [current_move]

        val += mod
        val *= 1 if board.turn else -1

        if best == val:
            move.append(current_move)
        elif best < val and board.turn or best > val and not board.turn:
            move = [current_move]
            best = val

        # print(prev_mov(board))

    return best, move


def randombot(board: chess.Board) -> chess.Board:

    moves: List[chess.Move] = minimax(board, 2)[1]
    board.push(choice(moves))
    return board


i: int = 0
while not board.is_game_over() and not board.is_fifty_moves():

    i += 1

    board = randombot(board)
    print()
    print(board.unicode())
