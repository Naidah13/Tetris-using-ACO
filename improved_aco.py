import random
import copy

class ThieryScherrerACO:
    """
    Implementation based on:
    'Applying Ant Colony Optimization to Tetris' (Thiery & Scherrer, 2009)
    
    Core concept: ACO learns WEIGHTS for board features, not direct positions.
    Each ant has its own weight set, and the best ant updates pheromone trails.
    This allows the algorithm to discover optimal heuristic weights through exploration.
    """
    
    def __init__(self, n_ants=40, lookahead=1):
        """
        Initialize ACO with ant colony parameters.
        
        Args:
            n_ants: Number of ants exploring solutions per iteration
            lookahead: Depth of future piece consideration (currently 1)
        """
        self.n_ants = n_ants
        self.lookahead = lookahead
        
        # Feature names based on Tetris board characteristics
        self.features = [
            'landing_height',    # Height where piece lands
            'eroded_cells',      # Cells cleared (reward)
            'row_transitions',   # Horizontal occupied/empty transitions
            'col_transitions',   # Vertical occupied/empty transitions
            'holes',            # Empty cells below occupied cells
            'wells',            # Deep column gaps
            'height_variance',  # Variance in column heights
            'max_height'        # Maximum column height
        ]
        
        # Pheromone trails: feature_name -> [(weight_value, pheromone_level), ...]
        self.pheromone_trails = {}
        for feature in self.features:
            self.pheromone_trails[feature] = self._init_weight_trail(feature)
        
        # MAX-MIN Ant System (MMAS) parameters
        self.tau_min = 0.1      # Minimum pheromone level
        self.tau_max = 4.0      # Maximum pheromone level
        self.rho = 0.1          # Evaporation rate (10% per iteration)
        self.alpha = 1.0        # Pheromone importance in selection
        self.beta = 2.0         # Exploration factor
        
        # Track best solution found so far
        self.best_weights = None
        self.best_score = float('-inf')
        self.iterations = 0
        
    def _init_weight_trail(self, feature):
        """
        Initialize discrete weight values with uniform pheromones.
        Creates ~21 possible weight values per feature.
        
        Args:
            feature: Feature name
            
        Returns:
            List of (weight_value, pheromone_level) tuples
        """
        if feature == 'eroded_cells':
            # Positive weights: reward line clearing
            weights = [i * 0.5 for i in range(0, 21)]  # [0.0, 0.5, 1.0, ..., 10.0]
        else:
            # Negative weights: penalize undesirable board states
            weights = [-i * 0.5 for i in range(0, 21)]  # [0.0, -0.5, -1.0, ..., -10.0]
        
        # Initialize all weights with equal pheromone (encourages exploration)
        initial_pheromone = 2.0
        return [(w, initial_pheromone) for w in weights]
    
    def extract_features(self, board, lines_cleared):
        """
        Extract all board features for evaluation.
        
        Args:
            board: Current board state
            lines_cleared: Number of lines just cleared
            
        Returns:
            Dictionary of feature_name -> feature_value
        """
        heights = self._column_heights(board)
        features = {}
        
        # Feature 1: Landing height (where piece landed)
        features['landing_height'] = max(heights) if heights else 0
        
        # Feature 2: Eroded cells (reward for clearing lines)
        features['eroded_cells'] = lines_cleared * 10
        
        # Feature 3: Row transitions (horizontal filled/empty changes)
        row_trans = 0
        for row in board:
            for i in range(len(row) - 1):
                if row[i] != row[i + 1]:
                    row_trans += 1
        features['row_transitions'] = row_trans
        
        # Feature 4: Column transitions (vertical filled/empty changes)
        col_trans = 0
        for col in zip(*board):
            for i in range(len(col) - 1):
                if col[i] != col[i + 1]:
                    col_trans += 1
        features['col_transitions'] = col_trans
        
        # Feature 5: Holes (critical metric - empty cells below filled cells)
        features['holes'] = self._count_holes(board)
        
        # Feature 6: Wells (deep vertical gaps between higher columns)
        wells = 0
        for i in range(len(heights)):
            left_height = heights[i-1] if i > 0 else 20
            right_height = heights[i+1] if i < len(heights)-1 else 20
            if heights[i] < left_height and heights[i] < right_height:
                wells += (min(left_height, right_height) - heights[i])
        features['wells'] = wells
        
        # Feature 7: Height variance (penalize uneven board)
        if heights:
            avg_height = sum(heights) / len(heights)
            features['height_variance'] = sum((h - avg_height) ** 2 for h in heights) / len(heights)
        else:
            features['height_variance'] = 0
        
        # Feature 8: Maximum height
        features['max_height'] = max(heights) if heights else 0
        
        return features
    
    def _column_heights(self, board):
        """Calculate height of each column."""
        heights = []
        for col in zip(*board):
            h = 0
            for cell in col:
                if cell:
                    break
                h += 1
            heights.append(len(col) - h)
        return heights
    
    def _count_holes(self, board):
        """Count holes (empty cells with filled cells above them)."""
        holes = 0
        for col in zip(*board):
            found_filled = False
            for cell in col:
                if cell:
                    found_filled = True
                elif found_filled:
                    holes += 1
        return holes
    
    def evaluate_with_weights(self, features, weights):
        """
        Evaluate board state using weighted sum of features.
        This is the core evaluation function that ants optimize.
        
        Args:
            features: Dictionary of feature values
            weights: Dictionary of feature weights
            
        Returns:
            Weighted score (higher is better)
        """
        score = 0
        for feature_name, feature_value in features.items():
            weight = weights.get(feature_name, 0)
            score += weight * feature_value
        return score
    
    def sample_ant_weights(self):
        """
        Sample weight configuration for one ant using pheromone-based probabilities.
        This is the CORE of ACO: probabilistic selection guided by pheromones.
        
        Higher pheromone levels → higher selection probability
        
        Returns:
            Dictionary of feature_name -> selected_weight
        """
        weights = {}
        
        for feature_name in self.features:
            trail = self.pheromone_trails[feature_name]
            
            # Calculate selection probabilities based on pheromone levels
            total_pheromone = sum(tau ** self.alpha for _, tau in trail)
            
            # Roulette wheel selection
            rand = random.uniform(0, total_pheromone)
            cumsum = 0
            
            for weight_val, tau in trail:
                cumsum += tau ** self.alpha
                if cumsum >= rand:
                    weights[feature_name] = weight_val
                    break
        
        return weights
    
    def generate_moves(self, shape, rotate_func, BOARD_WIDTH=10):
        """
        Generate all possible moves (rotation, x-position pairs).
        
        Returns:
            List of (rotation, x_position) tuples
        """
        moves = []
        current = shape
        
        for r in range(4):  # 4 possible rotations
            width = len(current[0])
            for x in range(BOARD_WIDTH - width + 1):
                moves.append((r, x))
            current = rotate_func(current)
        
        return moves
    
    def evaluate_move_with_weights(self, board, shape, move, weights,
                                   rotate_func, valid_pos_func, drop_func, clear_func):
        """
        Evaluate a single move using ant's learned weights.
        
        Returns:
            Score for this move (higher is better)
        """
        r, x = move
        
        # Apply rotation
        rotated = shape
        for _ in range(r):
            rotated = rotate_func(rotated)
        
        # Check validity
        if not valid_pos_func(board, rotated, x, 0):
            return float('-inf')
        
        # Simulate move
        new_board = drop_func(board, rotated, x)
        new_board, lines = clear_func(new_board)
        
        # Extract features and evaluate
        features = self.extract_features(new_board, lines)
        score = self.evaluate_with_weights(features, weights)
        
        return score
    
    def find_best_move(self, board, shape_name, shape, shape_queue=None,
                      rotate_func=None, valid_pos_func=None, 
                      drop_func=None, clear_func=None, evaluate_func=None):
        """
        Main ACO algorithm:
        1. Each ant samples weights from pheromone trails
        2. Each ant finds its best move using those weights
        3. Best-performing ant updates pheromone trails
        
        Returns:
            Tuple (rotation, x_position) for best move
        """
        moves = self.generate_moves(shape, rotate_func)
        ant_solutions = []
        
        # Each ant explores with its own weight configuration
        for ant_id in range(self.n_ants):
            ant_weights = self.sample_ant_weights()
            
            # Find best move for this ant's weights
            best_move = None
            best_score = float('-inf')
            
            for move in moves:
                score = self.evaluate_move_with_weights(
                    board, shape, move, ant_weights,
                    rotate_func, valid_pos_func, drop_func, clear_func
                )
                
                if score > best_score:
                    best_score = score
                    best_move = move
            
            if best_move:
                ant_solutions.append((best_move, best_score, ant_weights))
        
        if not ant_solutions:
            return (0, 5)  # Fallback: no rotation, center position
        
        # Select best ant solution
        best_move, best_score, best_weights = max(ant_solutions, key=lambda x: x[1])
        
        # Track global best across all iterations
        if best_score > self.best_score:
            self.best_score = best_score
            self.best_weights = best_weights
            print(f"[ACO] New best weights! Score: {best_score:.1f}")
        
        # Update pheromones based on best ant (MMAS reinforcement)
        self._update_pheromones(best_weights, best_score)
        
        self.iterations += 1
        return best_move
    
    def _update_pheromones(self, best_weights, score):
        """
        MAX-MIN Ant System (MMAS) pheromone update:
        - Evaporate all pheromones
        - Only best ant deposits new pheromones
        - Enforce min/max bounds to maintain exploration
        
        Args:
            best_weights: Weights used by best-performing ant
            score: Score achieved by best ant
        """
        # Step 1: Evaporation (decay all pheromones)
        for feature_name in self.features:
            trail = self.pheromone_trails[feature_name]
            for i in range(len(trail)):
                weight_val, tau = trail[i]
                trail[i] = (weight_val, tau * (1 - self.rho))
        
        # Step 2: Deposit pheromones from best ant
        if score > 0:
            # Scale deposit amount based on score quality
            deposit = min(2.0, abs(score) / 50.0)
            
            for feature_name, chosen_weight in best_weights.items():
                trail = self.pheromone_trails[feature_name]
                
                # Find and reinforce the chosen weight
                for i in range(len(trail)):
                    weight_val, tau = trail[i]
                    if abs(weight_val - chosen_weight) < 0.01:  # Float comparison tolerance
                        new_tau = tau + deposit
                        # Enforce MMAS bounds (prevents premature convergence)
                        new_tau = max(self.tau_min, min(self.tau_max, new_tau))
                        trail[i] = (weight_val, new_tau)
                        break


class ACOWrapper:
    """Wrapper class for compatibility with main game loop."""
    
    def __init__(self, n_ants=25):
        self.aco = ThieryScherrerACO(n_ants=n_ants, lookahead=1)
        self.pheromones = {}  # For UI display
        self.avg_pheromone_level = 0.0  # Average pheromone across all trails
    
    def find_best_move(self, board, shape_name, shape, shape_queue=None,
                      rotate_func=None, valid_pos_func=None, 
                      drop_func=None, clear_func=None, evaluate_func=None):
        """Forward call to ACO algorithm."""
        move = self.aco.find_best_move(
            board, shape_name, shape, shape_queue,
            rotate_func, valid_pos_func, drop_func, clear_func, evaluate_func
        )
        
        # Calculate average pheromone level across all features
        total_pheromone = 0
        total_weights = 0
        for feature, trail in self.aco.pheromone_trails.items():
            for _, tau in trail:
                total_pheromone += tau
                total_weights += 1
        
        self.avg_pheromone_level = total_pheromone / total_weights if total_weights > 0 else 0
        
        # Update pheromone display info for UI (top 5 features)
        self.pheromones = {
            feature: f"τ={sum(tau for _, tau in trail) / len(trail):.2f}"
            for feature, trail in list(self.aco.pheromone_trails.items())[:5]
        }
        
        return move