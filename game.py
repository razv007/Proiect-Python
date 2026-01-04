import random
from collections import deque

class Game:
    def __init__(self, mode="AI", difficulty="MEDIUM", player_role="BLOCKER", w=11, h=11, n_obs=10):
        self.w = w
        self.h = h
        self.mode = mode
        self.difficulty = difficulty
        self.player_role = player_role
        self.cells = set()
        self.walls = set()
        self.pos = (0, 0)
        self.over = False
        self.winner = None
        self.turn = 0
        self.initial_obs = n_obs
        self.make_grid()
        self.add_walls(n_obs)

        if self.mode == "AI" and self.player_role == "MOUSE":
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
        if len(potential) < n: n = len(potential)
        self.walls.update(set(random.sample(potential, n)))

    def get_neighbors(self, q, r):
        dirs = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
        return [(q + dq, r + dr) for dq, dr in dirs]

    def has_valid_moves(self):
        for n in self.get_neighbors(*self.pos):
            if n not in self.walls:
                return True
        return False

    def get_shortest_path(self, start_pos):
        queue = deque([(start_pos, [])])
        visited = set([start_pos])

        while queue:
            current, path = queue.popleft()
            for neighbor in self.get_neighbors(*current):
                if neighbor not in self.cells:
                    if path: return path[0] 
                    else: return neighbor
                
                if neighbor not in self.walls and neighbor not in visited:
                    visited.add(neighbor)
                    new_path = path + [neighbor]
                    queue.append((neighbor, new_path))
        return None

    def click_tile(self, q, r):
        if self.over: return

        if self.player_role == "BLOCKER" or self.mode == "PVP":
            if self.turn == 0:
                if (q, r) == self.pos: return
                if (q, r) in self.walls: return
                if (q, r) not in self.cells: return

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

        elif self.player_role == "MOUSE" and self.mode == "AI":
            if self.turn == 1:
                moved = self.human_move_mouse(q, r)
                
                if moved and not self.over:
                    self.turn = 0
                    self.ai_move_blocker()

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
            move = self.get_shortest_path(self.pos)
            if not move or move not in valid_moves:
                move = random.choice(valid_moves)

        elif self.difficulty == "HARD":
            move = self.get_shortest_path(self.pos)
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
        if self.over: return
        
        path_node = self.get_shortest_path(self.pos)
        target_wall = None

        if self.difficulty == "EASY":
            opts = [c for c in self.cells if c not in self.walls and c != self.pos]
            if opts: target_wall = random.choice(opts)

        else:
            if path_node:
                if path_node not in self.walls and path_node != self.pos:
                    target_wall = path_node
            
            if not target_wall:
                neighbors = self.get_neighbors(*self.pos)
                opts = [n for n in neighbors if n not in self.walls]
                if opts: target_wall = random.choice(opts)

        if target_wall:
            self.walls.add(target_wall)
            self.turn = 1
            self.check_game_state_after_block()

    def reset(self):
        self.over = False
        self.winner = None
        self.turn = 0
        self.walls.clear()
        self.make_grid()
        self.add_walls(self.initial_obs)
        
        if self.mode == "AI" and self.player_role == "MOUSE":
            self.ai_move_blocker()