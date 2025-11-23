from pathlib import Path
from typing import Dict, Optional, Tuple

import chess
import pygame

from bot import Bot


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

    SPR_DIR = Path(".") / "sprites"

    surfs: Dict[chess.Color, Dict[chess.PieceType, pygame.Surface]] = {}

    for i in range(len(chess.COLOR_NAMES)):
        col, colname = (chess.COLORS[i], chess.COLOR_NAMES[i])
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
        x, y = (pos % 8, pos // 8)

        surf.blit(backs[(x + y) % 2 == 0], (x * size, y * size))

        if piece is not None:
            sprite = sprites[piece.color][piece.piece_type]
            size_x, size_y = sprite.size
            surf.blit(sprite, (x * size_x, y * size_y))

    pygame.transform.scale(surf, display.size, display)


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
        board = chess.Board()

        drawboard(board, 600, display)
        bot = Bot()
        while not board.is_game_over() and run:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
            board = bot.randombot(board, 2)
            print(board.move_stack[-1], clock.get_rawtime() / 1000)

            clock.tick(60)
            drawboard(board, 600, display)
            pygame.display.flip()

        for _ in range(600):
            clock.tick(60)
            if not run:
                break

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False


main()
pygame.quit()
