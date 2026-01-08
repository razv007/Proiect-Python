"""Core game logic and state management for Trap the Mouse.

This module contains the Game class which encapsulates all game rules,
state management, AI integration, and save/load functionality for the
Trap the Mouse game.
"""
import random
import pickle
import os
import math
from collections import deque
import ai_logic


class Game:
    """Represents a Trap the Mouse game instance.
    
    This class manages the hexagonal grid, mouse and wall positions,
    turn-based gameplay, AI opponents, undo/redo functionality, and
    persistent storage of game states.
    
    Attributes:
        w: Grid width in hexagons.
        h: Grid height in hexagons.
        mode: Game mode ("AI" or "PVP").
        difficulty: AI difficulty level ("EASY", "MEDIUM", "HARD").
        player_role: Player's role ("BLOCKER" or "MOUSE").
        cells: Set of all grid cell coordinates.
        walls: Set of wall/blocked cell coordinates.
        pos: Current mouse position as (q, r) tuple.
        over: Boolean indicating if game has ended.
        winner: Winning side ("BLOCKER" or "MOUSE"), None if ongoing.
        turn: Current turn (0 = blocker, 1 = mouse).
        history: List of previous game states for undo.
        redo_stack: Stack of undone states for redo.
        current_filename: Name of save file if game was loaded.
    """
    def __init__(self, mode="AI", difficulty="MEDIUM", player_role="BLOCKER", w=11, h=11, n_obs=10):
        """Initialize a new game instance.
        
        Args:
            mode: Game mode, "AI" or "PVP" (default "AI").
            difficulty: AI difficulty, "EASY"/"MEDIUM"/"HARD" (default "MEDIUM").
            player_role: Player's role, "BLOCKER" or "MOUSE" (default "BLOCKER").
            w: Grid width (default 11).
            h: Grid height (default 11).
            n_obs: Number of initial random obstacles (default 10).
        """
        self.w = w
        self.h = h
        self.mode = mode
        self.difficulty = difficulty
        self.player_role = player_role
        self.initial_obs = n_obs
        
        self.cells = set()
        self.walls = set()
        self.pos = (0, 0)
        self.over = False
        self.winner = None
        self.turn = 0
        
        self.history = []
        self.redo_stack = []
        self.current_filename = None

        self.make_grid()
        self.add_walls(n_obs)

        if self.mode == "AI" and self.player_role == "MOUSE":
            self.save_state()
            self.ai_move_blocker()

    def make_grid(self):
        """Generate hexagonal grid cells and initialize mouse position."""
        self.cells.clear()
        for r in range(self.h):
            for c in range(self.w):
                q = c - (r // 2)
                self.cells.add((q, r))
        
        cr = self.h // 2
        cc = self.w // 2
        self.pos = (cc - (cr // 2), cr)

    def add_walls(self, n):
        opts = list(self.cells)
        if self.pos in opts:
            opts.remove(self.pos)
        current_walls = self.walls.copy()
        potential = [c for c in opts if c not in current_walls]
        if len(potential) < n: 
            n = len(potential)
        self.walls.update(set(random.sample(potential, n)))

    def save_state(self):
        """Save current game state to history for undo functionality."""
        state = {
            'walls': self.walls.copy(),
            'pos': self.pos,
            'turn': self.turn,
            'over': self.over,
            'winner': self.winner
        }
        self.history.append(state)
        self.redo_stack.clear() 

    def undo(self):
        """Undo the last move, restoring previous game state."""
        if not self.history: return
        
        current_state = {
            'walls': self.walls.copy(),
            'pos': self.pos,
            'turn': self.turn,
            'over': self.over,
            'winner': self.winner
        }
        self.redo_stack.append(current_state)

        prev = self.history.pop()
        self.walls = prev['walls']
        self.pos = prev['pos']
        self.turn = prev['turn']
        self.over = prev['over']
        self.winner = prev['winner']

    def redo(self):
        """Redo a previously undone move."""
        if not self.redo_stack: return

        current_state = {
            'walls': self.walls.copy(),
            'pos': self.pos,
            'turn': self.turn,
            'over': self.over,
            'winner': self.winner
        }
        self.history.append(current_state)

        next_st = self.redo_stack.pop()
        self.walls = next_st['walls']
        self.pos = next_st['pos']
        self.turn = next_st['turn']
        self.over = next_st['over']
        self.winner = next_st['winner']

    def save_to_file(self, filename):
        """Save game state to a file using pickle.
        
        Args:
            filename: Name of save file.
        
        Returns:
            True if save succeeded, False otherwise.
        """
        try:
            folder = "saves"
            if not os.path.exists(folder):
                os.makedirs(folder)
            full_path = os.path.join(folder, filename)
            
            with open(full_path, "wb") as f:
                pickle.dump(self, f)
            
            self.current_filename = filename
            return True
        except:
            return False

    @staticmethod
    def load_from_file(filename):
        """Load a game instance from a save file.
        
        Args:
            filename: Name of save file to load.
        
        Returns:
            Game instance if successful, None otherwise.
        """
        try:
            folder = "saves"
            full_path = os.path.join(folder, filename)
            if not os.path.exists(full_path):
                return None
                
            with open(full_path, "rb") as f:
                game_obj = pickle.load(f)
                game_obj.current_filename = filename
                return game_obj
        except:
            return None

    def get_neighbors(self, q, r):
        dirs = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
        return [(q + dq, r + dr) for dq, dr in dirs]

    def has_valid_moves(self):
        for n in self.get_neighbors(*self.pos):
            if n not in self.cells:
                return True
            if n in self.cells and n not in self.walls:
                return True
        return False

    def final_hex(self, cell):
        if cell not in self.cells: 
            return False
        neighbors = self.get_neighbors(*cell)
        for n in neighbors:
            if n not in self.cells:
                return True
        return False

    def click_tile(self, q, r):
        """Handle mouse click on a hex tile.
        
        Args:
            q: Hexagon q coordinate.
            r: Hexagon r coordinate.
        """
        if self.over: return

        if self.player_role == "BLOCKER" or self.mode == "PVP":
            if self.turn == 0:
                if (q, r) == self.pos or (q, r) in self.walls or (q, r) not in self.cells:
                    return
                self.save_state()
                self.walls.add((q, r))
                self.check_game_state_after_block()
                
                if not self.over:
                    self.turn = 1
                    if self.mode == "AI":
                        self.ai_move_mouse()
            
            elif self.turn == 1 and self.mode == "PVP":
                self.save_state()
                moved = self.human_move_mouse(q, r)
                if moved: 
                    self.turn = 0
                else: 
                    self.undo()

        elif self.player_role == "MOUSE" and self.mode == "AI":
            if self.turn == 1:
                self.save_state()
                moved = self.human_move_mouse(q, r)
                if moved and not self.over:
                    self.turn = 0
                    self.ai_move_blocker()
                elif not moved:
                    self.undo()

    def human_move_mouse(self, q, r):
        if (q, r) not in self.get_neighbors(*self.pos): return False
        if (q, r) in self.walls: return False
        if (q, r) not in self.cells:
            self.over = True
            self.winner = "MOUSE"
            return True
        self.pos = (q, r)
        return True

    def check_game_state_after_block(self):
        if not self.has_valid_moves():
            self.over = True
            self.winner = "BLOCKER"

    def ai_move_mouse(self):
        """Execute AI-controlled mouse move based on difficulty level."""
        neighbors = self.get_neighbors(*self.pos)
        valid_moves = [n for n in neighbors if n not in self.walls]
        if not valid_moves:
            self.over = True
            self.winner = "BLOCKER"
            return
        
        move = None
        if self.difficulty == "EASY":
            move = random.choice(valid_moves)
        elif self.difficulty == "MEDIUM":
            move = ai_logic.get_shortest_path(self, self.pos)
            if not move or move not in valid_moves:
                move = random.choice(valid_moves)

        elif self.difficulty == "HARD":
             move = ai_logic.best_move_mouse(self, self.pos, self.walls)
             if not move or move not in valid_moves:
                 move = random.choice(valid_moves)

        if move not in self.cells:
            self.over = True
            self.winner = "MOUSE"
            return

        self.pos = move
        self.turn = 0
        self.check_game_state_after_block()

    def ai_move_blocker(self):
        """Execute AI-controlled blocker move to place an optimal wall."""
        if self.over: return
        target_wall = None
        
        if self.difficulty == "EASY":
            opts = [c for c in self.cells if c not in self.walls and c != self.pos]
            if opts: 
                target_wall = random.choice(opts)
        elif self.difficulty == "MEDIUM":
            move = ai_logic.get_shortest_path(self, self.pos)
            if move and move not in self.walls and move != self.pos:
                target_wall = move
            else:
                opts = [c for c in self.cells if c not in self.walls and c != self.pos]
                if opts: 
                    target_wall = random.choice(opts)
        elif self.difficulty == "HARD":
            target_wall = ai_logic.best_wall(self, self.pos, self.walls)

        if target_wall:
            self.walls.add(target_wall)
            self.turn = 1
            self.check_game_state_after_block()

    def reset(self):
        """Reset game to initial state with same configuration."""
        self.over = False
        self.winner = None
        self.turn = 0
        self.history.clear()
        self.redo_stack.clear()
        self.walls.clear()
        self.current_filename = None
        self.make_grid()
        self.add_walls(self.initial_obs)
        if self.mode == "AI" and self.player_role == "MOUSE":
            self.ai_move_blocker()
