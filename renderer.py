import pygame
from settings import *

def draw_board(screen, board):
    """Renderuje tablu sa modernim stilom"""
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            rect = pygame.Rect(x*CELL, y*CELL, CELL, CELL)
            
            if board[y][x]:
                # Locked piece - moderan 3D efekat
                # Inner glow efekat
                inner_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.w - 4, rect.h - 4)
                
                # Glavna boja
                pygame.draw.rect(screen, ACCENT, rect, border_radius=3)
                
                # Gradient efekat - svjetliji centar
                center_color = tuple(min(255, c + 50) for c in ACCENT)
                pygame.draw.rect(screen, center_color, inner_rect, border_radius=2)
                
                # Highlight na vrhu (3D efekat)
                highlight = pygame.Rect(rect.x + 3, rect.y + 3, rect.w - 6, rect.h // 3)
                highlight_color = tuple(min(255, c + 80) for c in ACCENT)
                highlight_surf = pygame.Surface((highlight.w, highlight.h), pygame.SRCALPHA)
                highlight_surf.fill((*highlight_color, 100))
                screen.blit(highlight_surf, (highlight.x, highlight.y))
                
                # Outer border - tanak tamni obrub
                pygame.draw.rect(screen, (0, 0, 0, 180), rect, 2, border_radius=3)
            else:
                # Prazno polje - minimalistički grid
                pygame.draw.rect(screen, GRID_COLOR, rect, 1)


def draw_piece(screen, shape, x, y, color):
    """Renderuje aktivnu kocku sa suptilnim 3D efektom"""
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                rect = pygame.Rect((x+j)*CELL, (y+i)*CELL, CELL, CELL)
                
                # Shadow effect - ispod kocke (suptilniji)
                shadow_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.w, rect.h)
                shadow_surf = pygame.Surface((shadow_rect.w, shadow_rect.h), pygame.SRCALPHA)
                shadow_surf.fill((0, 0, 0, 50))
                screen.blit(shadow_surf, (shadow_rect.x, shadow_rect.y))
                
                # Glavni dio kocke sa zaobljenim uglovima
                pygame.draw.rect(screen, color, rect, border_radius=4)
                
                # Inner highlight - malo svjetliji centar (smanjeno)
                inner_rect = pygame.Rect(rect.x + 3, rect.y + 3, rect.w - 6, rect.h - 6)
                inner_color = tuple(min(255, c + 30) for c in color)
                pygame.draw.rect(screen, inner_color, inner_rect, border_radius=3)
                
                # Top shine - suptilan odsjaj na vrhu (smanjen)
                shine = pygame.Rect(rect.x + 5, rect.y + 5, rect.w - 10, rect.h // 4)
                shine_color = tuple(min(255, c + 50) for c in color)
                shine_surf = pygame.Surface((shine.w, shine.h), pygame.SRCALPHA)
                shine_surf.fill((*shine_color, 80))
                screen.blit(shine_surf, (shine.x, shine.y))
                
                # Bottom shadow - blaga tamnija donja ivica
                bottom_shadow = pygame.Rect(rect.x + 5, rect.y + rect.h - rect.h // 5, rect.w - 10, rect.h // 5)
                dark_color = tuple(max(0, c - 25) for c in color)
                shadow_surf = pygame.Surface((bottom_shadow.w, bottom_shadow.h), pygame.SRCALPHA)
                shadow_surf.fill((*dark_color, 60))
                screen.blit(shadow_surf, (bottom_shadow.x, bottom_shadow.y))
                
                # Outer glow - suptilan svijetli obrub (tanak)
                glow_color = tuple(min(255, c + 20) for c in color)
                pygame.draw.rect(screen, glow_color, rect, 1, border_radius=4)
                
                # Crni outline - oštra definicija (tanak)
                pygame.draw.rect(screen, (0, 0, 0, 200), rect, 1, border_radius=4)