from itertools import chain
from random import choice
from typing import Dict, List, Optional, Tuple

import chess

pieceVals: Dict[chess.PieceType, int] = {
    chess.PAWN: 1000,
    chess.KNIGHT: 3000,
    chess.BISHOP: 3100,
    chess.ROOK: 5000,
    chess.QUEEN: 9000,
    chess.KING: 10000000,
}
CHECKMOD = 700
TRADEMOD = 200

MAX_EVAL = 100000000
MIN_EVAL = -100000000


class Bot:
    def evaluate(self, board: chess.Board) -> int:
        flipper = 1 if board.turn else -1
        if board.is_stalemate() or board.can_claim_draw():
            return 0
        if board.is_checkmate():
            return MIN_EVAL * flipper

        val = 0
        if board.is_check():
            val -= flipper * CHECKMOD

        for piece in [board.piece_at(i) for i in board.piece_map()]:
            assert piece is not None
            flipper = 1 if piece.color else -1
            val += flipper * pieceVals[piece.piece_type]

        return val

    def minimax(
        self,
        board: chess.Board,
        depth: int,
        alpha: int = MIN_EVAL,
        beta: int = MAX_EVAL,
        prev_moves: Dict[chess.Move, int] = {},
    ) -> Dict[chess.Move, int] | int:
        save_moves = len(prev_moves) != 0
        WORST = MIN_EVAL if board.turn else MAX_EVAL
        best = WORST

        legal_moves: Dict[chess.Move, int]
        if save_moves:
            legal_moves = prev_moves
            assert len(legal_moves) == len(
                list(board.generate_legal_moves()),
            )

        else:
            legal_moves = dict.fromkeys(
                list(
                    chain(
                        board.generate_castling_moves(),
                        board.generate_legal_captures(),
                        board.generate_legal_moves(),
                    )
                ),
                WORST,
            )

        if len(legal_moves) < 1 or depth < 1:
            return self.evaluate(board)

        for current_move in legal_moves:
            board.push(current_move)
            val = self.minimax(board, depth - 1, alpha, beta)
            assert isinstance(val, int)
            board.pop()

            if board.turn:
                best = max(val, best)
                alpha = max(val, alpha)
            else:
                best = min(val, best)
                beta = min(val, beta)

            if save_moves:
                legal_moves.update({current_move: val})
            if beta <= alpha:
                break

        if save_moves:
            dict(
                sorted(
                    legal_moves.items(),
                    key=lambda x: x[1],
                    reverse=board.turn,
                )
            )
            return legal_moves
        return best

    def randombot(
        self,
        board: chess.Board,
        depth: int,
    ) -> Tuple[chess.Board, int]:

        moves = dict.fromkeys(board.generate_legal_moves(), 0)
        assert len(moves) > 0
        print("white" if board.turn else "black")
        for i in range(1, depth):
            res = self.minimax(
                board,
                i,
                prev_moves=moves,
            )
            assert type(res) is dict
            assert len(res) > 0

            moves = res
            print("depth:", i + 1)
            val = list(moves.values())[0]
            if val == MAX_EVAL or val == MIN_EVAL:
                break
        mm = max if board.turn else min

        mov, best = mm(moves.items(), key=lambda m: m[1])
        best_moves = [move for (move, eval) in moves.items() if eval == best]
        ret = choice(best_moves)
        print(str(ret))
        board.push(ret)
        return board, best
