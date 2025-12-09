from pathlib import Path
from typing import Dict, Optional, Tuple

import chess
import pygame

from bot import Bot as RecBot
from iterbot import Bot as ItBot

DEPTH = 4
INTERACT = True
STAY = True

SPR_DIR = Path(".") / "sprites"


def loadsprites() -> Tuple[
    Dict[
        chess.Color,
        Dict[
            chess.PieceType,
            pygame.Surface,
        ],
    ],
    Dict[chess.Color, pygame.Surface],
    int,
]:

    surfs: Dict[chess.Color, Dict[chess.PieceType, pygame.Surface]] = {}

    for i in range(len(chess.COLOR_NAMES)):
        col, colname = (not chess.COLORS[i], chess.COLOR_NAMES[i])
        p_dict: Dict[chess.PieceType, pygame.Surface] = {}

        for name in chess.PIECE_TYPES:

            p_path = SPR_DIR / (colname + "_" + chess.piece_name(name) + ".png")
            surf = pygame.image.load(p_path).convert_alpha()
            if surf is None:
                raise Exception("failed to load sprite")
            p_dict.update({name: surf})
            pass
        surfs.update({col: p_dict})

    dark = pygame.image.load(SPR_DIR / "dark.png").convert_alpha()
    light = pygame.image.load(SPR_DIR / "light.png").convert_alpha()

    backs = {chess.BLACK: dark, chess.WHITE: light}
    return surfs, backs, backs[chess.BLACK].size[0]


def drawboard(
    board: chess.Board,
    size: int,
    display: pygame.Surface,
    *,
    offset: Optional[Tuple[int, int]] = None
) -> None:
    sprites, backs, size = loadsprites()

    surf = pygame.Surface((size * 8, size * 8))
    for pos in chess.SQUARES:
        piece = board.piece_at(pos)
        x, y = (pos % 8, 7 - pos // 8)

        surf.blit(backs[(x + y) % 2 == 0], (x * size, y * size))

        if piece is not None:
            sprite = sprites[piece.color][piece.piece_type]
            size_x, size_y = sprite.size
            surf.blit(sprite, (x * size_x, y * size_y))

    pygame.transform.scale(surf, display.size, display)

    pygame.display.flip()


def p_move_gen(move: str) -> chess.Move:
    from_str = move[0:2]
    to_str = move[2:4]
    pars = chess.parse_square
    ret_move = chess.Move(pars(from_str), pars(to_str))

    return ret_move


def main() -> None:
    pygame.init()
    window_dimension = (600, 600)
    pygame.display.set_mode(
        size=window_dimension,
        flags=pygame.DOUBLEBUF,
    )
    clock = pygame.time.Clock()

    display = pygame.display.get_surface()

    assert display is not None

    run = True
    while run:
        # board = chess.Board(fen="8/4R3/6K1/3NB3/p5n1/1p2RNbk/8/8 w - - 0 1")
        board = chess.Board()

        drawboard(board, 600, display)
        botR = ItBot()
        botI = RecBot()
        while not board.is_game_over(claim_draw=True) and run:
            print("white" if board.turn else "black")
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            if not board.turn and INTERACT:
                p_move = p_move_gen("a1a1")
                while p_move not in board.generate_legal_moves():
                    p_move = p_move_gen(input("input a move"))

                board.push(p_move)
                clock.tick(60)
            else:
                print()
                if board.turn:
                    move, score = botI.randombot(board, DEPTH)
                else:
                    move, score = botR.randombot(board, DEPTH)
                print()
                clock.tick(2)
                print(
                    move,
                    score / 1000,
                    clock.get_time() / 1000,
                )
                assert move in board.generate_legal_moves()
                board.push(move)
            drawboard(board, 600, display)

        drawboard(board, 800, display)
        if STAY:
            input(("black" if board.turn else "white") + " won")
        else:
            print(("black" if board.turn else "white") + " won")
            for _ in range(600):
                clock.tick(60)
                if not run:
                    break

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False


main()
pygame.quit()
