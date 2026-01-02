import random

class Game:
    def __init__(self, mode="AI", w=11, h=11, n_obs=10):
        self.w = w
        self.h = h
        self.mode = mode
        self.cells = set()
        self.walls = set()
        self.pos = (0, 0)
        self.over = False
        self.winner = None
        self.turn = 0 
        self.initial_obs = n_obs
        self.make_grid()
        self.add_walls(n_obs)

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

    def get_neighbors(self, q, r):
        dirs = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
        return [(q + dq, r + dr) for dq, dr in dirs]

    def has_valid_moves(self):
        for n in self.get_neighbors(*self.pos):
            if n not in self.walls:
                return True
        return False

    def click_tile(self, q, r):
        if self.over:
            return

        if self.turn == 0:
            if (q, r) == self.pos:
                return
            if (q, r) in self.walls:
                return
            if (q, r) not in self.cells:
                return

            self.walls.add((q, r))
            
            if not self.has_valid_moves():
                self.over = True
                self.winner = "BLOCKER"
            else:
                self.turn = 1
                if self.mode == "AI":
                    self.ai_turn()

        elif self.turn == 1 and self.mode == "PVP":
            if (q, r) not in self.get_neighbors(*self.pos):
                return
            if (q, r) in self.walls:
                return

            if (q, r) not in self.cells:
                self.over = True
                self.winner = "MOUSE"
                return

            self.pos = (q, r)
            self.turn = 0

    def ai_turn(self):
        neighbors = self.get_neighbors(*self.pos)
        valid_moves = [n for n in neighbors if n not in self.walls]

        if not valid_moves:
            self.over = True
            self.winner = "BLOCKER"
            return

        move = random.choice(valid_moves)

        if move not in self.cells:
            self.over = True
            self.winner = "MOUSE"
            return

        self.pos = move
        self.turn = 0
        
        if not self.has_valid_moves():
            self.over = True
            self.winner = "BLOCKER"

    def reset(self):
        self.over = False
        self.winner = None
        self.turn = 0
        self.walls.clear()
        self.make_grid()
        self.add_walls(self.initial_obs)