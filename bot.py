from random import choice
from typing import Dict, List, Optional, Tuple

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

    def evaluate(self, board: chess.Board) -> int:
        val = self.getval(board)
        flipper = 1 if board.turn else -1
        if board.is_stalemate():
            return 0
        elif board.is_checkmate():
            return -10000000 * flipper
        elif board.can_claim_draw():
            return 0

        mod = 0
        for move in board.legal_moves:
            mod += self.TRADEMOD if board.is_capture(move) else 0
            mod += self.CHECKMOD if board.gives_check(move) else 0
        val += mod * flipper

        return val

    def minimax(
        self,
        board: chess.Board,
        depth: int,
        alpha: int = -10000000,
        beta: int = 10000000,
        save_moves: bool = False,
    ) -> Tuple[int, List[chess.Move]]:
        legal_moves = board.generate_legal_moves()
        moves: List[chess.Move] = []

        if depth < 1:
            return self.evaluate(board), moves

        best = 10000000
        if board.turn:
            best = -best

        for current_move in legal_moves:
            board.push(current_move)

            val, _ = self.minimax(board, depth - 1, alpha, beta)
            board.pop()

            pre_best = best
            if board.turn:
                best = max(val, best)
                alpha = max(val, alpha)
                if beta <= alpha:
                    break
            else:
                best = min(val, best)
                beta = min(val, beta)
                if beta <= alpha:
                    break
            if not save_moves:
                continue
            if best == val:
                moves.append(current_move)
            if best != pre_best:
                moves = [current_move]

        return best, moves

    def randombot(
        self,
        board: chess.Board,
        depth: int,
    ) -> Tuple[chess.Board, int]:

        eval, moves = self.minimax(board, depth, save_moves=True)
        board.push(choice(moves))
        return board, eval
