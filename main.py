import pygame
import random
import copy
import sys
import json
from datetime import datetime
from settings import *
from renderer import draw_board, draw_piece
from ui import draw_panel, draw_button, draw_menu, draw_game_over, draw_winner
from effects import draw_ghost_piece
from improved_aco import ACOWrapper

# Automatic testing function
def run_auto_test(n_games=50, n_ants=40, max_pieces=500, save_results=True):
    """
    Executes a series of automated games to evaluate and track the ACO 
    algorithm's learning progress without visual rendering.
    """
    print(f"STARTING AUTOMATIC ACO TESTING - {n_games} GAMES")
    print(f"\nConfiguration: {n_games} games, {n_ants} ants, max {max_pieces} pieces per game")
    print("\n")
    
    # Persistent ACO instance allows learning to accumulate across games
    aco = ACOWrapper(n_ants=n_ants)
    results = []
    
    for game_num in range(n_games):
        game_start = datetime.now()
        game_state = GameState()
        
        max_height_reached = 0
        pieces_placed = 0
        
        # Initial piece spawn with ACO positioning
        game_state.spawn_next(1, aco)  

        while not game_state.game_over and pieces_placed < max_pieces:
            # Simulate instant drop for testing efficiency
            while valid_position(game_state.board, game_state.shape, game_state.x, game_state.y + 1):
                game_state.y += 1
            
            # Lock piece into the board array
            for i, row in enumerate(game_state.shape):
                for j, cell in enumerate(row):
                    if cell and game_state.y + i >= 0:
                        game_state.board[game_state.y + i][game_state.x + j] = 1
            
            pieces_placed += 1
            
            if any(game_state.board[0]):
                game_state.game_over = True
            else:
                game_state.board, cleared = clear_lines(game_state.board)
                if cleared > 0:
                    game_state.lines_total += cleared
                
                heights = column_heights(game_state.board)
                max_height_reached = max(max_height_reached, max(heights) if heights else 0)
                game_state.spawn_next(1, aco)
        
        game_duration = (datetime.now() - game_start).total_seconds()
        
        # Record game metrics for analysis
        game_result = {
            'game_number': game_num + 1,
            'lines_cleared': game_state.lines_total,
            'pieces_placed': pieces_placed,
            'max_height': max_height_reached,
            'duration_seconds': round(game_duration, 2),
            'aco_iterations': aco.aco.iterations
        }
        results.append(game_result)
        
        avg_lines = sum(r['lines_cleared'] for r in results) / len(results)
        best_game = max(results, key=lambda x: x['lines_cleared'])
        
        # Print progress
        print(f"Game {game_num + 1}/{n_games}: "
              f"{game_state.lines_total} lines | "
              f"{pieces_placed} pieces | "
              f"Max height: {max_height_reached} | "
              f"Time: {game_duration:.1f}s")
        print(f"  Running avg: {avg_lines:.1f} lines | Best so far: {best_game['lines_cleared']} lines (Game #{best_game['game_number']})")
        
        # Show improvement every 10 games
        if (game_num + 1) % 10 == 0:
            recent_10 = [r['lines_cleared'] for r in results[-10:]]
            print(f"\n  === Last 10 games avg: {sum(recent_10)/10:.1f} lines ===\n")
    
    # Final statistics
    print("TESTING COMPLETE - FINAL RESULTS")
    
    lines_list = [r['lines_cleared'] for r in results]
    print(f"Total games played: {n_games}")
    print(f"Average lines cleared: {sum(lines_list) / len(lines_list):.2f}")
    print(f"Best performance: {max(lines_list)} lines (Game #{results[lines_list.index(max(lines_list))]['game_number']})")
    print(f"Worst performance: {min(lines_list)} lines")
    print(f"Standard deviation: {(sum((x - sum(lines_list)/len(lines_list))**2 for x in lines_list) / len(lines_list))**0.5:.2f}")
    
    # Show learning trend (first 25% vs last 25%)
    quarter = n_games // 4
    if quarter > 0:
        early_avg = sum(lines_list[:quarter]) / quarter
        late_avg = sum(lines_list[-quarter:]) / quarter
        improvement = ((late_avg - early_avg) / early_avg * 100) if early_avg > 0 else 0
        print(f"\nLearning progress:")
        print(f"  First 25% games avg: {early_avg:.2f} lines")
        print(f"  Last 25% games avg: {late_avg:.2f} lines")
        print(f"  Improvement: {improvement:+.1f}%")
    
    # Show score distribution
    print(f"\nScore distribution:")
    ranges = [(0, 20), (20, 40), (40, 60), (60, 80), (80, 100), (100, float('inf'))]
    for low, high in ranges:
        count = sum(1 for x in lines_list if low <= x < high)
        if count > 0:
            bar = "█" * (count * 50 // n_games)
            label = f"{low}-{high-1}" if high != float('inf') else f"{low}+"
            print(f"  {label:>8} lines: {bar} ({count})")
     
    # Export results to JSON for external visualization/benchmarking
    if save_results:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"aco_test_results_{timestamp}.json"
        
        summary = {
            'timestamp': timestamp,
            'configuration': {
                'n_games': n_games,
                'n_ants': n_ants,
                'max_pieces': max_pieces
            },
            'summary_statistics': {
                'average_lines': sum(lines_list) / len(lines_list),
                'best_lines': max(lines_list),
                'worst_lines': min(lines_list),
                'std_dev': (sum((x - sum(lines_list)/len(lines_list))**2 for x in lines_list) / len(lines_list))**0.5,
                'early_avg': sum(lines_list[:quarter]) / quarter if quarter > 0 else 0,
                'late_avg': sum(lines_list[-quarter:]) / quarter if quarter > 0 else 0,
                'improvement_percent': improvement if quarter > 0 else 0
            },
            'games': results
        }
        
        with open(filename, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\nResults saved to: {filename}")
    
    return results

# Standard Tetris piece definitions
SHAPES = {
    "I": [[1, 1, 1, 1]],
    "O": [[1, 1],
          [1, 1]],
    "T": [[0, 1, 0],
          [1, 1, 1]],
    "S": [[0, 1, 1],
          [1, 1, 0]],
    "Z": [[1, 1, 0],
          [0, 1, 1]],
    "L": [[1, 0],
          [1, 0],
          [1, 1]],
    "J": [[0, 1],
          [0, 1],
          [1, 1]]
}

game_history = [] 

def rotate(shape):
    """Rotate the piece matrix 90 degrees clockwise."""
    return [list(row) for row in zip(*shape[::-1])]

def create_board():
    """Initialize an empty game board grid."""
    return [[0] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]

def valid_position(board, shape, x, y):
    """Verify if the piece's current coordinates are within bounds and unoccupied."""
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                if (x + j < 0 or x + j >= BOARD_WIDTH or 
                    y + i >= BOARD_HEIGHT or 
                    (y + i >= 0 and board[y + i][x + j])):
                    return False
                
    return True

def drop_piece(board, shape, x):
    """Simulate a hard drop on a temporary board to evaluate the outcome."""
    y = 0
    while valid_position(board, shape, x, y + 1):
        y += 1
        
    new_board = copy.deepcopy(board)
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                if y + i >= 0:
                    new_board[y + i][x + j] = 1
                    
    return new_board

def clear_lines(board):
    """Identify, remove full rows, and shift remaining rows down."""
    new_board = [row for row in board if 0 in row]
    cleared = BOARD_HEIGHT - len(new_board)
    for _ in range(cleared):
        new_board.insert(0, [0] * BOARD_WIDTH)
        
    return new_board, cleared

def column_heights(board):
    """Retrieve the height of each column for heuristic calculations."""
    heights = []
    for col in zip(*board):
        h = 0
        for cell in col:
            if cell:
                break
            h += 1
        heights.append(len(col) - h)
        
    return heights

def count_holes(board):
    """Count empty spaces that are trapped beneath locked blocks."""
    holes = 0
    for col in zip(*board):
        found = False
        for cell in col:
            if cell:
                found = True
            elif found:
                holes += 1
                
    return holes

def calculate_bumpiness(board):
    """Calculate column height differences."""
    heights = column_heights(board)
    
    return sum(abs(heights[i] - heights[i+1]) for i in range(len(heights)-1))

def evaluate_board(board, lines_cleared):
    """
    Standard heuristic evaluation using a weighted combination of 
    board features (Dellacherie-inspired).
    """
    heights = column_heights(board)
    
    # Extract structural features
    landing_height = max(heights) if heights else 0
    eroded_cells = lines_cleared * 10
    
    # Row transitions
    row_transitions = 0
    for row in board:
        for i in range(len(row) - 1):
            if row[i] != row[i + 1]:
                row_transitions += 1
    
    # Column transitions  
    col_transitions = 0
    for col in zip(*board):
        for i in range(len(col) - 1):
            if col[i] != col[i + 1]:
                col_transitions += 1
    
    # Holes 
    holes = count_holes(board)
    
    # Wells 
    wells = 0
    for i in range(len(heights)):
        left = heights[i-1] if i > 0 else 20
        right = heights[i+1] if i < len(heights)-1 else 20
        if heights[i] < left and heights[i] < right:
            wells += (min(left, right) - heights[i])
    
    # Height variance 
    if heights:
        avg_height = sum(heights) / len(heights)
        height_variance = sum((h - avg_height) ** 2 for h in heights) / len(heights)
    else:
        height_variance = 0
    
    # Max height difference
    max_height_diff = max(heights) - min(heights) if heights else 0
    
    # Aggregate height
    aggregate_height = sum(heights)
    
    # Dangerous tall columns
    dangerous_height = sum(1 for h in heights if h > 15)
    
    # Pierre Dellacherie weights and additional penalties
    score = (
        -4.500158825082766 * landing_height +
        +3.4181268101392694 * eroded_cells +
        -3.2178882868487753 * row_transitions +
        -9.348695305445199 * col_transitions +
        -7.899265427351652 * holes +
        -3.3855972247263626 * wells +
        -2.5 * height_variance +
        -1.8 * max_height_diff +
        -0.5 * aggregate_height +
        -15.0 * dangerous_height
    )
    
    # Line clear bonuses
    if lines_cleared == 1:
        score += 10
    elif lines_cleared == 2:
        score += 30
    elif lines_cleared == 3:
        score += 70
    elif lines_cleared == 4:
        score += 150  # Tetris!
    
    return score

class GameState:
    """Manages the lifecycle, progression, and internal data of a Tetris session."""
    def __init__(self):
        self.board = create_board()
        self.lines_total = 0
        self.score = 0
        self.level = 1
        self.game_over = False
        self.winner = False
        self.shape_queue = [get_new_piece() for _ in range(3)]
        self.shape_name, self.shape, self.x, self.y = None, None, None, None
        self.fall_counter = 0
        
    def spawn_next(self, mode, aco):
        """Prepares the next piece, using ACO logic if AI mode is active."""
        name, shp = self.shape_queue.pop(0)
        self.shape_queue.append(get_new_piece())
        
        if mode == 1:  # AI Mode: Consult ACO for optimal position
            move = aco.find_best_move(
                self.board, 
                name, 
                shp,
                shape_queue=self.shape_queue,
                rotate_func=rotate,
                valid_pos_func=valid_position,
                drop_func=drop_piece,
                clear_func=clear_lines,
                evaluate_func=evaluate_board
            )
            r, nx = move
            for _ in range(r):
                shp = rotate(shp)
            self.shape_name, self.shape, self.x, self.y = name, shp, nx, 0
        else:  # Manual Mode
            self.shape_name = name
            self.shape = shp
            self.x = BOARD_WIDTH // 2 - len(shp[0]) // 2
            self.y = 0
        
        if not valid_position(self.board, self.shape, self.x, self.y):
            self.game_over = True
            
    def reset(self):
        self.__init__()

def get_new_piece():
    """Pick a random tetromino shape from the library."""
    name = random.choice(list(SHAPES.keys()))
    
    return name, SHAPES[name]

# Uncomment the following block to run automatic testing
# if __name__ == "__main__":
#     run_auto_test(
#         n_games=50,        
#         n_ants=40,         
#         max_pieces=10000,   
#         save_results=True 
#    )
#    sys.exit()

# System Initialization
pygame.init()
screen = pygame.display.set_mode((BOARD_WIDTH * CELL + SIDEBAR, BOARD_HEIGHT * CELL))
pygame.display.set_caption("Tetris ACO")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 18, bold=True)
credit_font = pygame.font.SysFont("Arial", 14, italic=True)

# Application state
aco = ACOWrapper(n_ants=40)
game_state = GameState()
mode = None
show_menu = True

# UI layout definitions
mode_btn = pygame.Rect(BOARD_WIDTH * CELL + 30, 370, 130, 40)
restart_btn = pygame.Rect(BOARD_WIDTH * CELL // 2 - 65, BOARD_HEIGHT * CELL // 2 + 60, 130, 40)

# Primary Game Loop
while True:
    screen.fill(BG_COLOR)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if show_menu:
                # Calculate menu button collision bounds
                full_width = BOARD_WIDTH * CELL + SIDEBAR
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
                
                if manual_btn.collidepoint(event.pos):
                    mode = 0
                    show_menu = False
                    game_state.spawn_next(mode, aco)
                elif aco_btn.collidepoint(event.pos):
                    mode = 1
                    show_menu = False
                    game_state.spawn_next(mode, aco)
            
            elif mode_btn.collidepoint(event.pos) and not game_state.game_over:
                # Switch between Manual and ACO Mode
                mode = 1 - mode
                game_state.spawn_next(mode, aco)
            
            elif game_state.game_over and restart_btn.collidepoint(event.pos):
                # Restart game
                game_history.append(game_state.lines_total)
                print(f"Game {len(game_history)}: {game_state.lines_total} lines | "
                      f"Avg: {sum(game_history)/len(game_history):.1f} | "
                      f"Best: {max(game_history)}")
                game_state.reset()
                show_menu = True
                mode = None

        # Input handling for manual gameplay
        if not game_state.game_over and mode == 0 and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and valid_position(game_state.board, game_state.shape, game_state.x - 1, game_state.y):
                game_state.x -= 1
            if event.key == pygame.K_RIGHT and valid_position(game_state.board, game_state.shape, game_state.x + 1, game_state.y):
                game_state.x += 1
            if event.key == pygame.K_DOWN and valid_position(game_state.board, game_state.shape, game_state.x, game_state.y + 1):
                game_state.y += 1
            if event.key == pygame.K_UP:
                rs = rotate(game_state.shape)
                if valid_position(game_state.board, rs, game_state.x, game_state.y):
                    game_state.shape = rs
            if event.key == pygame.K_SPACE:
                # Hard drop
                while valid_position(game_state.board, game_state.shape, game_state.x, game_state.y + 1):
                    game_state.y += 1

    # Show menu
    if show_menu:
        draw_menu(screen, font)
   
        credits_surface = credit_font.render("© 2026 Hasovic N. & Malinov L.", True, (180, 180, 190))
        total_width = BOARD_WIDTH * CELL + SIDEBAR
        total_height = BOARD_HEIGHT * CELL
        credits_rect = credits_surface.get_rect(center=(total_width // 2, total_height - 20))
        screen.blit(credits_surface, credits_rect)

        pygame.display.flip()
        clock.tick(60)
        continue

    # Gravity and movement logic
    if not game_state.game_over:
        game_state.fall_counter += 1
        
        # Adjust fall speed based on mode
        if mode == 1:  # Fast in Aco Mode
            fall_threshold = 3
        else:  # Constant in Manual Mode
            fall_threshold = 30
        
        #else:  # Progressive speed in Manual Mode
        #    fall_threshold = max(7, 40 - game_state.level * 1.5)
        
        if game_state.fall_counter >= fall_threshold:
            game_state.fall_counter = 0
            
            if valid_position(game_state.board, game_state.shape, game_state.x, game_state.y + 1):
                game_state.y += 1
            else:
                for i, row in enumerate(game_state.shape):
                    for j, cell in enumerate(row):
                        if cell and game_state.y + i >= 0:
                            game_state.board[game_state.y + i][game_state.x + j] = 1
                
                if any(game_state.board[0]):
                    game_state.game_over = True
                else:
                    game_state.board, cleared = clear_lines(game_state.board)
                    
                    if cleared > 0:
                        game_state.score += {1: 100, 2: 300, 3: 500, 4: 800}.get(cleared, 0) * game_state.level
                        game_state.lines_total += cleared
                        game_state.level = game_state.lines_total // 10 + 1

                        if game_state.level >= 15:
                            game_state.winner = True
                            game_state.game_over = True
                            
                    game_state.spawn_next(mode, aco)

    # Rendering sequence
    draw_board(screen, game_state.board)
    if not game_state.game_over:
        draw_ghost_piece(screen, game_state.board, game_state.shape, game_state.x, 
                        SHAPE_COLORS[game_state.shape_name], valid_position)
        draw_piece(screen, game_state.shape, game_state.x, game_state.y, 
                  SHAPE_COLORS[game_state.shape_name])

    # Draw UI panel
    draw_panel(screen, font, mode, game_state.lines_total, game_state.score, game_state.level, 
               aco.aco.iterations, aco.avg_pheromone_level)
    draw_button(screen, mode_btn, "MANUAL" if mode == 0 else "ACO MODE", font, mode != 0)

    # Draw game over screen
    if game_state.game_over:
        if game_state.winner:
            draw_winner(screen, font, game_state.score, game_state.lines_total, restart_btn)
        else:
            draw_game_over(screen, font, game_state.score, game_state.lines_total, restart_btn)

    clock.tick(60)
    pygame.display.flip()