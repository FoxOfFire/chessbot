from random import choice
from typing import Dict, List, Tuple

import chess


class Bot:

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

    def getval(self, board: chess.Board) -> int:

        val: int = 0
        for i in chess.SQUARES:
            piece = board.piece_at(i)
            if piece is None:
                continue
            frend = 1 if board.turn == piece.color else -1
            val += frend * self.pieceVals[piece.piece_type]

        return val

    def prev_mov(self, board: chess.Board) -> List[str]:
        return [str(s) for s in board.move_stack]

    def minimax(
        self,
        board: chess.Board,
        depth: int,
    ) -> Tuple[int, List[chess.Move]]:
        best: int = -10000000 if board.turn else 10000000
        legal_moves = board.generate_legal_moves()
        move: List[chess.Move] = []

        for current_move in legal_moves:
            mod = 0
            if board.is_capture(current_move):
                mod += self.TRADEMOD
            if board.is_into_check(current_move):
                mod -= self.CHECKMOD * 2

            board.push(current_move)
            if board.is_check():
                mod += self.CHECKMOD

            if depth < 1:
                val = self.getval(board)
            else:
                val = self.minimax(board, depth - 1)[0]

            board.pop()

            if board.is_checkmate():
                return -10000000, [current_move]
            if board.is_stalemate():
                return 0, [current_move]

            val *= 1 if board.turn else -1
            val += mod

            if best == val:
                move.append(current_move)
            elif best < val and board.turn or best > val and not board.turn:
                move = [current_move]
                best = val

            # print(prev_mov(board))

        return best, move

    def randombot(self, board: chess.Board, depth: int) -> chess.Board:

        moves: List[chess.Move] = self.minimax(board, depth)[1]
        board.push(choice(moves))
        return board
