import pygame
from settings import *
from copy import deepcopy

def draw_ghost_piece(screen, board, shape, x, color, valid_position):
    """
    Calculates and renders a transparent ghost piece at the bottom of the board 
    to indicate where the current piece will land.
    """
    # Calculate the lowest possible valid y-position for the ghost piece
    y = 0
    while valid_position(board, shape, x, y + 1):
        y += 1

    # Create a semi-transparent surface for the ghost effect
    ghost = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
    ghost.fill((*color, 60))

    # Draw the ghost piece blocks on the screen
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                screen.blit(ghost, ((x+j)*CELL, (y+i)*CELL))
