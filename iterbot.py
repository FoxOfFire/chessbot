from functools import reduce
from itertools import chain
from random import choice
from typing import Any, Dict, Iterator, List, Tuple

import chess

CHECKMOD = -700
TRADEMOD = 200

MAX_EVAL = 100000000
MIN_EVAL = -100000000


pieceValsCol: Dict[chess.PieceType, int] = {
    chess.PAWN: 1000,
    chess.KNIGHT: 3000,
    chess.BISHOP: 3000,
    chess.ROOK: 5000,
    chess.QUEEN: 9000,
    chess.KING: 200000,
}
pieceColMod: Dict[chess.Color, int] = {chess.WHITE: 1, chess.BLACK: -1}

pawnVals = [
    10 * i
    for i in [0, 0, 0, 0, 0, 0, 0, 0]
    + [50, 50, 50, 50, 50, 50, 50, 50]
    + [10, 10, 20, 30, 30, 20, 10, 10]
    + [5, 5, 10, 25, 25, 10, 5, 5]
    + [0, 0, 0, 20, 20, 0, 0, 0]
    + [5, -5, -10, 0, 0, -10, -5, 5]
    + [5, 10, 10, -20, -20, 10, 10, 5]
    + [0, 0, 0, 0, 0, 0, 0, 0]
]
pawnEndVals = [
    10 * i
    for i in [0, 0, 0, 0, 0, 0, 0, 0]
    + [80, 80, 80, 80, 80, 80, 80, 80]
    + [50, 50, 50, 50, 50, 50, 50, 50]
    + [30, 30, 30, 30, 30, 30, 30, 30]
    + [20, 20, 20, 20, 20, 20, 20, 20]
    + [10, 10, 10, 10, 10, 10, 10, 10]
    + [10, 10, 10, 10, 10, 10, 10, 10]
    + [0, 0, 0, 0, 0, 0, 0, 0]
]
knightVals = [
    10 * i
    for i in [-50, -40, -30, -30, -30, -30, -40, -50]
    + [-40, -20, 0, 0, 0, 0, -20, -40]
    + [-30, 0, 10, 15, 15, 10, 0, -30]
    + [-30, 5, 15, 20, 20, 15, 5, -30]
    + [-30, 0, 15, 20, 20, 15, 0, -30]
    + [-30, 5, 10, 15, 15, 10, 5, -30]
    + [-40, -20, 0, 5, 5, 0, -20, -40]
    + [-50, -40, -30, -30, -30, -30, -40, -50]
]
rookVals = [
    10 * i
    for i in [0, 0, 0, 0, 0, 0, 0, 0]
    + [5, 10, 10, 10, 10, 10, 10, 5]
    + [-5, 0, 0, 0, 0, 0, 0, -5]
    + [-5, 0, 0, 0, 0, 0, 0, -5]
    + [-5, 0, 0, 0, 0, 0, 0, -5]
    + [-5, 0, 0, 0, 0, 0, 0, -5]
    + [-5, 0, 0, 0, 0, 0, 0, -5]
    + [0, 0, 0, 5, 5, 0, 0, 0]
]
bishopVals = [
    10 * i
    for i in [-20, -10, -10, -10, -10, -10, -10, -20]
    + [-10, 0, 0, 0, 0, 0, 0, -10]
    + [-10, 0, 5, 10, 10, 5, 0, -10]
    + [-10, 5, 5, 10, 10, 5, 5, -10]
    + [-10, 0, 10, 10, 10, 10, 0, -10]
    + [-10, 10, 10, 10, 10, 10, 10, -10]
    + [-10, 5, 0, 0, 0, 0, 5, -10]
    + [-20, -10, -10, -10, -10, -10, -10, -20]
]
queenVals = [
    10 * i
    for i in [-20, -10, -10, -5, -5, -10, -10, -20]
    + [-10, 0, 0, 0, 0, 0, 0, -10]
    + [-10, 0, 5, 5, 5, 5, 0, -10]
    + [-5, 0, 5, 5, 5, 5, 0, -5]
    + [0, 0, 5, 5, 5, 5, 0, -5]
    + [-10, 5, 5, 5, 5, 5, 0, -10]
    + [-10, 0, 5, 0, 0, 0, 0, -10]
    + [-20, -10, -10, -5, -5, -10, -10, -20]
]
kingVals = [
    10 * i
    for i in [-80, -70, -70, -70, -70, -70, -70, -80]
    + [-60, -60, -60, -60, -60, -60, -60, -60]
    + [-40, -50, -50, -60, -60, -50, -50, -40]
    + [-30, -40, -40, -50, -50, -40, -40, -30]
    + [-20, -30, -30, -40, -40, -30, -30, -20]
    + [-10, -20, -20, -20, -20, -20, -20, -10]
    + [20, 20, -5, -5, -5, -5, 20, 20]
    + [20, 30, 10, 0, 0, 10, 30, 20]
]
kingEndVals = [
    10 * i
    for i in [-20, -10, -10, -10, -10, -10, -10, -20]
    + [-5, 0, 5, 5, 5, 5, 0, -5]
    + [-10, -5, 20, 30, 30, 20, -5, -10]
    + [-15, -10, 35, 45, 45, 35, -10, -15]
    + [-20, -15, 30, 40, 40, 30, -15, -20]
    + [-25, -20, 20, 25, 25, 20, -20, -25]
    + [-30, -25, 0, 0, 0, 0, -25, -30]
    + [-50, -30, -30, -30, -30, -30, -30, -50]
]

pieceTypeMod: Dict[chess.PieceType, List[int]] = {
    chess.PAWN: pawnVals,
    chess.KNIGHT: knightVals,
    chess.BISHOP: bishopVals,
    chess.ROOK: rookVals,
    chess.QUEEN: queenVals,
    chess.KING: kingVals,
}

pieceEndTypeMod: Dict[chess.PieceType, List[int]] = {
    chess.PAWN: pawnEndVals,
    chess.KNIGHT: knightVals,
    chess.BISHOP: bishopVals,
    chess.ROOK: rookVals,
    chess.QUEEN: queenVals,
    chess.KING: kingEndVals,
}


class Bot:
    def pvals(self, board: chess.Board) -> List[int]:
        ret = []
        typemod = pieceTypeMod if board.queens else pieceEndTypeMod
        for p, i in [(board.piece_at(i), i) for i in board.piece_map()]:
            assert p is not None
            t = p.piece_type
            c = p.color
            if board.turn:
                i = 63 - i
            ret.append((pieceValsCol[t] + typemod[t][i]) * pieceColMod[c])

        return ret

    def evaluate(self, board: chess.Board) -> int:
        flipper = 1 if board.turn else -1
        if board.is_stalemate() or board.can_claim_draw():
            return 0
        if board.is_checkmate():
            return flipper * MIN_EVAL

        val = reduce(lambda i, p: i + p, self.pvals(board), 0)
        val += reduce(lambda i, _: i + flipper * 100, board.legal_moves, 0)
        b = board.copy()
        b.apply_mirror()
        val -= reduce(lambda i, _: i + flipper * 100, b.legal_moves, 0)

        return val

    def check_eval(self, board: chess.Board) -> int:
        if board.is_stalemate() or board.can_claim_draw():
            return 0
        if board.is_checkmate():
            return MIN_EVAL if board.turn else MAX_EVAL

        moves = board.generate_legal_captures()
        best = self.evaluate(board)
        mm = max if board.turn else min

        for move in moves:
            board.push(move)
            best = mm(best, self.evaluate(board))
            board.pop()
        return best

    def sort_moves(
        self, moves: Dict[chess.Move, int], turn: chess.Color
    ) -> Dict[chess.Move, int]:
        return dict(
            sorted(
                moves.items(),
                key=lambda x: x[1],
                reverse=turn,
            )
        )

    def dict_stringify(self, d: Dict[Any, Any]) -> List[str]:
        return [(str(m[0]) + " " + str(m[1] / 1000)) for m in d.items()]

    def mitermax(
        self, board: chess.Board, depth: int, prev_moves: Dict[chess.Move, int]
    ) -> Dict[chess.Move, int]:
        accu = 0
        breaks = 0
        for move in prev_moves:

            board.push(move)

            alphas = [MIN_EVAL for _ in range(depth)]
            betas = [MAX_EVAL for _ in range(depth)]
            evals = [0 for i in range(depth + 1)]
            cdep = 0

            legal_moves = board.generate_legal_moves()
            moves = [legal_moves for _ in range(depth)]
            if depth == 0:
                prev_moves[move] = self.evaluate(board)
                board.pop()
                continue

            while cdep >= 0:

                try:
                    next = moves[cdep].__next__()
                    board.push(next)

                    cdep += 1
                    if cdep == depth:
                        evals[cdep] = self.evaluate(board)
                        accu += 1
                        raise StopIteration

                    moves[cdep] = chain(
                        board.generate_castling_moves(),
                        board.generate_legal_captures(),
                        board.generate_legal_moves(),
                    )

                    evals[cdep] = MIN_EVAL if board.turn else MAX_EVAL
                    betas[cdep] = betas[cdep - 1]
                    alphas[cdep] = alphas[cdep - 1]

                except StopIteration:
                    breaks -= 1
                    while True:
                        cdep -= 1
                        breaks += 1
                        board.pop()
                        val = evals[cdep + 1]

                        if board.turn:
                            evals[cdep] = max(val, evals[cdep])
                            alphas[cdep] = max(val, alphas[cdep])

                        else:
                            evals[cdep] = min(val, evals[cdep])
                            betas[cdep] = min(val, betas[cdep])

                        if betas[cdep] > alphas[cdep] or cdep < 0:
                            break

            prev_moves[move] = evals[0]
        print("checked:", accu, "cut:", breaks)
        return self.sort_moves(prev_moves, board.turn)

    def randombot(
        self,
        board: chess.Board,
        depth: int,
    ) -> Tuple[chess.Move, int]:
        print("Iterbot")

        WORST = MIN_EVAL if board.turn else MAX_EVAL
        moves = dict.fromkeys(board.generate_legal_moves(), WORST)
        assert len(moves) > 0
        for i in range(depth):
            res = self.mitermax(board, i, moves)
            assert type(res) is dict
            assert len(res) > 0

            moves = res
            val = list(moves.values())[0]
            print("depth:", i + 1, self.dict_stringify(moves)[0])
            if val == MAX_EVAL or val == MIN_EVAL:
                break
        mm = max if board.turn else min

        mov, best = mm(moves.items(), key=lambda m: m[1])
        best_moves = [move for (move, eval) in moves.items() if eval == best]
        ret = choice(best_moves)
        return ret, best
