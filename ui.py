import pygame
from settings import *

def draw_panel(screen, font, mode, lines, score, level, aco_iterations, avg_pheromone):
    """
    Renders the sidebar panel containing game statistics, 
    current mode indicator, and ACO learning progress.
    """
    panel = pygame.Rect(BOARD_WIDTH * CELL, 0, SIDEBAR, BOARD_HEIGHT * CELL)
    pygame.draw.rect(screen, PANEL_COLOR, panel)

    # Render main title and algorithm subtitle
    title_font = pygame.font.SysFont("Arial", 22, bold=True)
    title = title_font.render("TETRIS", True, ACCENT)
    screen.blit(title, (panel.x + 40, 15))
    
    subtitle = pygame.font.SysFont("Arial", 14).render("ACO Algorithm", True, (150, 150, 160))
    screen.blit(subtitle, (panel.x + 45, 40))

    # Decorative separator line
    pygame.draw.line(screen, GRID_COLOR, (panel.x + 20, 65), (panel.x + SIDEBAR - 20, 65), 2)

    # Mode indicator (Manual vs ACO)
    mode_txt = "MANUAL" if mode == 0 else "ACO ACTIVE"
    mode_color = (255, 200, 0) if mode == 0 else (0, 255, 150)
    screen.blit(font.render("MODE:", True, TEXT_COLOR), (panel.x + 20, 80))
    screen.blit(font.render(mode_txt, True, mode_color), (panel.x + 20, 105))

    # General game statistics
    stats_y = 145
    screen.blit(font.render(f"LINES: {lines}", True, TEXT_COLOR),
                (panel.x + 20, stats_y))
    screen.blit(font.render(f"SCORE: {score}", True, TEXT_COLOR),
                (panel.x + 20, stats_y + 35))
    screen.blit(font.render(f"LEVEL: {level}", True, TEXT_COLOR),
                (panel.x + 20, stats_y + 70))
    
    # Render ACO telemetry only when AI mode is active
    if mode == 1:
        small_font = pygame.font.SysFont("Arial", 13)
        pygame.draw.line(screen, GRID_COLOR, (panel.x + 20, stats_y + 105), 
                         (panel.x + SIDEBAR - 20, stats_y + 105), 1)
        screen.blit(small_font.render("ACO LEARNING:", True, ACCENT), 
                    (panel.x + 20, stats_y + 115))
        screen.blit(small_font.render(f"Iterations: {aco_iterations}", True, (150, 150, 160)),
                    (panel.x + 20, stats_y + 140))
        screen.blit(small_font.render(f"Avg τ: {avg_pheromone:.2f}", True, (150, 150, 160)),
                    (panel.x + 20, stats_y + 165))

    # Control scheme guide for manual play
    if mode == 0:
        pygame.draw.line(screen, GRID_COLOR, (panel.x + 20, BOARD_HEIGHT * CELL - 180), 
                         (panel.x + SIDEBAR - 20, BOARD_HEIGHT * CELL - 180), 2)
        
        controls_font = pygame.font.SysFont("Arial", 11)
        controls_y = BOARD_HEIGHT * CELL - 160
        
        screen.blit(controls_font.render("CONTROLS:", True, ACCENT), (panel.x + 20, controls_y))
        screen.blit(controls_font.render("← → : Move", True, TEXT_COLOR), (panel.x + 20, controls_y + 18))
        screen.blit(controls_font.render("↑ : Rotate", True, TEXT_COLOR), (panel.x + 20, controls_y + 36))
        screen.blit(controls_font.render("↓ : Soft drop", True, TEXT_COLOR), (panel.x + 20, controls_y + 54))
        screen.blit(controls_font.render("SPACE: Hard drop", True, TEXT_COLOR), (panel.x + 20, controls_y + 72))

def draw_button(screen, rect, text, font, highlighted=False):
    color = ACCENT if highlighted else (50, 50, 60)
    border_color = ACCENT if highlighted else (70, 70, 80)
    
    shadow = pygame.Rect(rect.x + 2, rect.y + 2, rect.w, rect.h)
    pygame.draw.rect(screen, (10, 10, 15), shadow, border_radius=8)
    
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, border_color, rect, 2, border_radius=8)
    
    text_surf = font.render(text, True, TEXT_COLOR)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

def draw_menu(screen, font):
    """
    Renders the full-screen initial menu for game mode selection.
    """
    full_width = BOARD_WIDTH * CELL + SIDEBAR
    overlay = pygame.Surface((full_width, BOARD_HEIGHT * CELL))
    overlay.set_alpha(200)
    overlay.fill((10, 10, 15))
    screen.blit(overlay, (0, 0))
    
    title_font = pygame.font.SysFont("Arial", 48, bold=True)
    title = title_font.render("TETRIS ACO", True, ACCENT)
    title_rect = title.get_rect(center=(full_width // 2, BOARD_HEIGHT * CELL // 3))
    screen.blit(title, title_rect)
    
    subtitle_font = pygame.font.SysFont("Arial", 18)
    subtitle = subtitle_font.render("Ant Colony Optimization", True, (150, 150, 160))
    subtitle_rect = subtitle.get_rect(center=(full_width // 2, BOARD_HEIGHT * CELL // 3 + 50))
    screen.blit(subtitle, subtitle_rect)
    
    button_width = 180
    button_height = 55
    manual_btn = pygame.Rect(
        full_width // 2 - button_width - 15,
        BOARD_HEIGHT * CELL // 2,
        button_width,
        button_height
    )
    aco_btn = pygame.Rect(
        full_width // 2 + 15,
        BOARD_HEIGHT * CELL // 2,
        button_width,
        button_height
    )
    
    # Render Manual mode button
    pygame.draw.rect(screen, (70, 70, 80), manual_btn, border_radius=10)
    pygame.draw.rect(screen, (255, 200, 0), manual_btn, 3, border_radius=10)
    manual_text = pygame.font.SysFont("Arial", 22, bold=True).render("MANUAL", True, TEXT_COLOR)
    manual_rect = manual_text.get_rect(center=manual_btn.center)
    screen.blit(manual_text, manual_rect)
    
    # Render ACO mode button
    pygame.draw.rect(screen, (70, 70, 80), aco_btn, border_radius=10)
    pygame.draw.rect(screen, (0, 255, 150), aco_btn, 3, border_radius=10)
    aco_text = pygame.font.SysFont("Arial", 22, bold=True).render("ACO MODE", True, TEXT_COLOR)
    aco_rect = aco_text.get_rect(center=aco_btn.center)
    screen.blit(aco_text, aco_rect)
    
    # Footer info text
    info_font = pygame.font.SysFont("Arial", 14)
    info_text = info_font.render("Choose your gameplay mode", True, (120, 120, 130))
    info_rect = info_text.get_rect(center=(full_width // 2, BOARD_HEIGHT * CELL - 100))
    screen.blit(info_text, info_rect)

def draw_game_over(screen, font, score, lines, restart_btn):
    """
    Renders the game over overlay with final performance results.
    """
    overlay = pygame.Surface((BOARD_WIDTH * CELL, BOARD_HEIGHT * CELL))
    overlay.set_alpha(220)
    overlay.fill((15, 10, 10))
    screen.blit(overlay, (0, 0))
    
    over_font = pygame.font.SysFont("Arial", 48, bold=True)
    over_text = over_font.render("GAME OVER", True, (255, 80, 80))
    over_rect = over_text.get_rect(center=(BOARD_WIDTH * CELL // 2, BOARD_HEIGHT * CELL // 3))
    screen.blit(over_text, over_rect)
    
    # Performance summary
    stats_font = pygame.font.SysFont("Arial", 24)
    score_text = stats_font.render(f"Final Score: {score}", True, TEXT_COLOR)
    score_rect = score_text.get_rect(center=(BOARD_WIDTH * CELL // 2, BOARD_HEIGHT * CELL // 2 - 20))
    screen.blit(score_text, score_rect)
    
    lines_text = stats_font.render(f"Lines Cleared: {lines}", True, TEXT_COLOR)
    lines_rect = lines_text.get_rect(center=(BOARD_WIDTH * CELL // 2, BOARD_HEIGHT * CELL // 2 + 20))
    screen.blit(lines_text, lines_rect)
    
    # Restart interface
    pygame.draw.rect(screen, (70, 80, 70), restart_btn, border_radius=10)
    pygame.draw.rect(screen, (0, 255, 150), restart_btn, 3, border_radius=10)
    restart_text = pygame.font.SysFont("Arial", 20, bold=True).render("RESTART", True, TEXT_COLOR)
    restart_rect = restart_text.get_rect(center=restart_btn.center)
    screen.blit(restart_text, restart_rect)

def draw_winner(screen, font, score, lines, restart_btn):
    """
    Renders a celebratory overlay when the player reaches the target level.
    """
    overlay = pygame.Surface((BOARD_WIDTH * CELL, BOARD_HEIGHT * CELL))
    overlay.set_alpha(220)
    overlay.fill((20, 20, 10))
    screen.blit(overlay, (0, 0))
    
    # Victory headers
    winner_font = pygame.font.SysFont("Arial", 52, bold=True)
    winner_text = winner_font.render("YOU WIN!", True, (255, 215, 0)) 
    winner_rect = winner_text.get_rect(center=(BOARD_WIDTH * CELL // 2, BOARD_HEIGHT * CELL // 3))
    screen.blit(winner_text, winner_rect)
    
    # Subtitle
    subtitle_font = pygame.font.SysFont("Arial", 20)
    subtitle_text = subtitle_font.render("Level 15 Reached!", True, (255, 215, 0))
    subtitle_rect = subtitle_text.get_rect(center=(BOARD_WIDTH * CELL // 2, BOARD_HEIGHT * CELL // 3 + 50))
    screen.blit(subtitle_text, subtitle_rect)
    
    # Final results
    stats_font = pygame.font.SysFont("Arial", 24)
    score_text = stats_font.render(f"Final Score: {score}", True, TEXT_COLOR)
    score_rect = score_text.get_rect(center=(BOARD_WIDTH * CELL // 2, BOARD_HEIGHT * CELL // 2 - 10))
    screen.blit(score_text, score_rect)
    
    lines_text = stats_font.render(f"Lines Cleared: {lines}", True, TEXT_COLOR)
    lines_rect = lines_text.get_rect(center=(BOARD_WIDTH * CELL // 2, BOARD_HEIGHT * CELL // 2 + 30))
    screen.blit(lines_text, lines_rect)
    
    # Restart interface
    pygame.draw.rect(screen, (80, 80, 70), restart_btn, border_radius=10)
    pygame.draw.rect(screen, (255, 215, 0), restart_btn, 3, border_radius=10)
    restart_text = pygame.font.SysFont("Arial", 20, bold=True).render("RESTART", True, TEXT_COLOR)
    restart_rect = restart_text.get_rect(center=restart_btn.center)
    screen.blit(restart_text, restart_rect)