import random
import pickle
import os
import math
from collections import deque
import ai_logic


class Game:
    def __init__(self, mode="AI", difficulty="MEDIUM", player_role="BLOCKER", w=11, h=11, n_obs=10):
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
        if self.over: return

        self.save_state()

        if self.player_role == "BLOCKER" or self.mode == "PVP":
            if self.turn == 0:
                if (q, r) == self.pos or (q, r) in self.walls or (q, r) not in self.cells:
                    self.undo()
                    return
                self.walls.add((q, r))
                self.check_game_state_after_block()
                
                if not self.over:
                    self.turn = 1
                    if self.mode == "AI":
                        self.ai_move_mouse()
            
            elif self.turn == 1 and self.mode == "PVP":
                moved = self.human_move_mouse(q, r)
                if moved: 
                    self.turn = 0
                else: 
                    self.undo()

        elif self.player_role == "MOUSE" and self.mode == "AI":
            if self.turn == 1:
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
        self.save_state()
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
