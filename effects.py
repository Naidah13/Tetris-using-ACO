import pygame
from settings import *
from copy import deepcopy

def draw_ghost_piece(screen, board, shape, x, color, valid_position):
    y = 0
    while valid_position(board, shape, x, y + 1):
        y += 1

    ghost = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
    ghost.fill((*color, 60))

    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                screen.blit(ghost, ((x+j)*CELL, (y+i)*CELL))
