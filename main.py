import random

class Game:
    def __init__(self, w=11, h=11, n_obs=10):
        self.w = w
        self.h = h
        self.cells = set()
        self.walls = set()
        self.pos = (0, 0) 
        self.over = False
        self.make_grid()
        self.add_walls(n_obs)

    def make_grid(self):
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
        self.walls = set(random.sample(opts, n))

    def get_neighbors(self, q, r):
        dirs = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
        res = []
        for dq, dr in dirs:
            res.append((q + dq, r + dr))
        return res

    def move_mouse(self, q, r):

        if self.over:
            print("Blocat sau prea departe.") 
            return False

        if (q, r) not in self.get_neighbors(*self.pos):
            print("Blocat sau prea departe.")
            return False 

        if (q, r) not in self.cells:
            self.over = True
            print("Mutare reusita!")
            print("WIN: Soarecele a scapat!")
            return True

        if (q, r) not in self.walls:
            self.pos = (q, r)
            print("Mutare reusita!")
            return True
        print("Blocat sau prea departe.")
        return False
    
    def print_grid(self):
        print("\n--- Harta ---")
        print(self.w, self.h)
        print(self.walls)
        for r in range(self.h):
            indent = " " * (r % 2)
            line = ""
            for c in range(self.w):
                q = c - (r // 2)
                if (q, r) == self.pos:
                    char = "M"
                elif (q, r) in self.walls:
                    char = "#"
                else:
                    char = "."
                line += char + " "
            print(indent + line)

if __name__ == "__main__":
    game = Game(w=11, h=11, n_obs=10)

    print(f"Tabla: {game.w}x{game.h}")
    print(f"Soarece la: {game.pos}")
    print(f"Ziduri: {len(game.walls)}")
    q, r = game.pos
    target = (q+1,r)
    print(f"Target: {target}")
    game.move_mouse(q+1,r)
    game.move_mouse(q+2,r)
    game.print_grid()