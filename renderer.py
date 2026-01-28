import pygame
from settings import *

def draw_board(screen, board):
    """
    Renders the game board with a modern 3D aesthetic for locked pieces 
    and a minimalist grid for empty cells.
    """
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            rect = pygame.Rect(x*CELL, y*CELL, CELL, CELL)
            
            if board[y][x]:
                inner_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.w - 4, rect.h - 4)
                
                pygame.draw.rect(screen, ACCENT, rect, border_radius=3)
                
                center_color = tuple(min(255, c + 50) for c in ACCENT)
                pygame.draw.rect(screen, center_color, inner_rect, border_radius=2)
                
                highlight = pygame.Rect(rect.x + 3, rect.y + 3, rect.w - 6, rect.h // 3)
                highlight_color = tuple(min(255, c + 80) for c in ACCENT)
                highlight_surf = pygame.Surface((highlight.w, highlight.h), pygame.SRCALPHA)
                highlight_surf.fill((*highlight_color, 100))
                screen.blit(highlight_surf, (highlight.x, highlight.y))
                
                pygame.draw.rect(screen, (5, 34, 87, 180), rect, 2, border_radius=2)
            else:
                pygame.draw.rect(screen, GRID_COLOR, rect, 1)


def draw_piece(screen, shape, x, y, color):
    """
    Renders the active falling piece with layered effects including 
    shadows, highlights, and subtle shines.
    """
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                rect = pygame.Rect((x+j)*CELL, (y+i)*CELL, CELL, CELL)
                
                shadow_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.w, rect.h)
                shadow_surf = pygame.Surface((shadow_rect.w, shadow_rect.h), pygame.SRCALPHA)
                shadow_surf.fill((0, 0, 0, 50))
                screen.blit(shadow_surf, (shadow_rect.x, shadow_rect.y))
                
                pygame.draw.rect(screen, color, rect, border_radius=4)
                
                inner_rect = pygame.Rect(rect.x + 3, rect.y + 3, rect.w - 6, rect.h - 6)
                inner_color = tuple(min(255, c + 30) for c in color)
                pygame.draw.rect(screen, inner_color, inner_rect, border_radius=3)
                
                shine = pygame.Rect(rect.x + 5, rect.y + 5, rect.w - 10, rect.h // 4)
                shine_color = tuple(min(255, c + 50) for c in color)
                shine_surf = pygame.Surface((shine.w, shine.h), pygame.SRCALPHA)
                shine_surf.fill((*shine_color, 80))
                screen.blit(shine_surf, (shine.x, shine.y))
                
                bottom_shadow = pygame.Rect(rect.x + 5, rect.y + rect.h - rect.h // 5, rect.w - 10, rect.h // 5)
                dark_color = tuple(max(210, c - 25) for c in color)
                shadow_surf = pygame.Surface((bottom_shadow.w, bottom_shadow.h), pygame.SRCALPHA)
                shadow_surf.fill((*dark_color, 30))
                screen.blit(shadow_surf, (bottom_shadow.x, bottom_shadow.y))
                
                glow_color = tuple(min(255, c + 20) for c in color)
                pygame.draw.rect(screen, glow_color, rect, 1, border_radius=3)
                pygame.draw.rect(screen, (235, 227, 160), rect, 1, border_radius=3)