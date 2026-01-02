import random

class Game:
    def __init__(self, w=11, h=11, n_obs=10):
        self.w = w
        self.h = h
        self.cells = set()
        self.walls = set()
        self.pos = (0, 0) 
        self.over = False
        self.won = False
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
        if self.pos in opts: opts.remove(self.pos)
        current_walls = self.walls.copy()
        potential = [c for c in opts if c not in current_walls]
        
        if len(potential) < n: n = len(potential)
        new_walls = set(random.sample(potential, n))
        self.walls.update(new_walls)

    def get_neighbors(self, q, r):
        dirs = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
        return [(q+dq, r+dr) for dq, dr in dirs]

    def move_mouse(self, q, r):
        if self.over: return False

        if (q, r) not in self.get_neighbors(*self.pos):
            return False 

        if (q, r) not in self.cells:
            self.over = True
            self.won = True
            return True

        if (q, r) in self.walls:
            return False

        self.pos = (q, r)
        return True

    def reset(self):
        self.over = False
        self.won = False
        self.walls.clear()
        self.make_grid()
        self.add_walls(self.initial_obs)