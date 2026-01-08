import random
import pickle
import os
import math
import collections
from collections import deque

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

    def bfs_dist(self, start, blocked):
        queue = deque([(start, 0)])
        viz = {start: 0}
        while queue:
            nod, dist = queue.popleft()
            for n in self.get_neighbors(*nod):
                if n in self.cells and n not in blocked and n not in viz:
                    viz[n] = dist + 1
                    queue.append((n, dist + 1))
        return viz

    def dp_IN_OUT(self, dist, blocked, start):
        edge_nodes = [n for n in dist if self.final_hex(n)]
        if not edge_nodes: return {}, {}, 0

        min_dist = min(dist[n] for n in edge_nodes)
        exits = [n for n in edge_nodes if dist[n] == min_dist]

        IN = collections.defaultdict(int)
        OUT = collections.defaultdict(int)

        nods = sorted(dist.keys(), key=lambda x: dist[x])
        IN[start] = 1

        for u in nods:
            if IN[u] == 0: continue
            d_u = dist[u]
            for v in self.get_neighbors(*u):
                if v in dist and v not in blocked and dist[v] == d_u + 1:
                    IN[v] += IN[u]

        for ex in exits:
            OUT[ex] = 1 

        nods = sorted(dist.keys(), key=lambda x: -dist[x])
        for u in nods:
            if OUT[u] == 0 and u not in exits: continue
            d_u = dist[u]
            for v in self.get_neighbors(*u):
                if v in dist and v not in blocked and dist[v] == d_u - 1:
                    OUT[v] += OUT[u]

        total = OUT[start]
        return IN, OUT, total

    def build_dinic(self, start, blocked):
        dist = self.bfs_dist(start, blocked)
        edge_nodes = [n for n in dist if self.final_hex(n)]
        
        if not edge_nodes: 
            return None, None, None
        
        min_dist = min(dist[n] for n in edge_nodes)
        
        graph = collections.defaultdict(list)
        S = "S"
        T = "T"
        INF = 10**9

        def add_edge(u, v, cap):
            graph[u].append([v, cap, len(graph[v])])
            graph[v].append([u, 0, len(graph[u]) - 1])

        add_edge(S, f"{start}_in", INF)

        for u in dist:
            cap_node = INF if u == start else 1
            add_edge(f"{u}_in", f"{u}_out", cap_node)
            
            if self.final_hex(u) and dist[u] == min_dist:
                add_edge(f"{u}_out", T, INF)
            
            d_u = dist[u]
            for v in self.get_neighbors(*u):
                if v in dist and v not in blocked and dist[v] == d_u + 1:
                    add_edge(f"{u}_out", f"{v}_in", INF)
                    
        return graph, S, T

    def dinic_bfs(self, s, t, graph, level):
        level.clear()
        level[s] = 0
        queue = deque([s])
        
        while queue:
            u = queue.popleft()
            for v, cap, rev in graph[u]:
                if cap > 0 and v not in level:
                    level[v] = level[u] + 1
                    queue.append(v)
        
        return t in level

    def dinic_dfs(self, u, t, flow, graph, level, ptr):
        if flow == 0 or u == t:
            return flow
        
        for i in range(ptr[u], len(graph[u])):
            ptr[u] = i 
            v, cap, rev = graph[u][i]
            
            if cap > 0 and v in level and level[v] == level[u] + 1:
                pushed = self.dinic_dfs(v, t, min(flow, cap), graph, level, ptr)
                if pushed > 0:
                    graph[u][i][1] -= pushed
                    graph[v][rev][1] += pushed
                    return pushed
        
        return 0

    def dinic(self, S, T, graph):
        max_flow = 0
        level = {}
        while self.dinic_bfs(S, T, graph, level):
            ptr = collections.defaultdict(int)
            while True:
                pushed = self.dinic_dfs(S, T, 10**9, graph, level, ptr)
                if pushed == 0: break
                max_flow += pushed
        return max_flow

    def best_wall(self, mouse_pos, blocked):
        dist = self.bfs_dist(mouse_pos, blocked)
        if not dist: 
            opts = [c for c in self.cells if c not in blocked and c != mouse_pos]
            return random.choice(opts) if opts else None

        IN, OUT, total = self.dp_IN_OUT(dist, blocked, mouse_pos)
        
        if total == 0:
            opts = [c for c in self.cells if c not in blocked and c != mouse_pos]
            return random.choice(opts) if opts else None

        candidates = []
        
        gamma = 0.4      
        w1 = 0.5          
        w2 = 0.5          
        
        level_sums = collections.defaultdict(int)
        for u in dist:
            if u == mouse_pos or u in blocked: continue
            if IN[u] > 0 and OUT[u] > 0:
                aux = IN[u] * OUT[u]
                d = dist[u]
                level_sums[d] += aux

        for u in dist:
            if u == mouse_pos or u in blocked: continue
            if IN[u] == 0 or OUT[u] == 0: continue
            
            aux = IN[u] * OUT[u]
            share = aux / total
            
            d = dist[u]
            level_total = level_sums[d]
            level_norm = (aux / level_total) if level_total > 0 else 0
            
            lead = max(0, d - 1)
            w_time = math.exp(gamma * lead)
            
            base_score = w_time * (w1 * share + w2 * level_norm)
            candidates.append((u, base_score))

        if not candidates:
             opts = [c for c in self.cells if c not in blocked and c != mouse_pos]
             return random.choice(opts) if opts else None

        candidates.sort(key=lambda x: x[1], reverse=True)
        top_k = candidates[:15]
        
        base_graph, S, T = self.build_dinic(mouse_pos, blocked)
        if not base_graph: 
            return top_k[0][0]
        
        base_cut = self.dinic(S, T, base_graph)
        
        best_hex = None
        max_score = -10**9
        alpha_cut = 3.0
        
        nodes_in_flow = set()
        for u in dist:
            if u == mouse_pos: 
                continue
            u_in = f"{u}_in"
            if u_in in base_graph:
                for v, cap, rev in base_graph[u_in]:
                    if v == f"{u}_out" and cap == 0:
                        nodes_in_flow.add(u)
                        break

        for u, base_val in top_k:
            marginal_cut = 0
            
            if u not in nodes_in_flow:
                marginal_cut = 0
            else:
                temp_blocked = blocked.copy()
                temp_blocked.add(u)
                
                temp_graph, tS, tT = self.build_dinic(mouse_pos,temp_blocked)
                if temp_graph:
                    new_cut = self.dinic(tS, tT, temp_graph)
                    marginal_cut = max(0, base_cut - new_cut)
            
            score = base_val + (alpha_cut * marginal_cut)
            
            if score > max_score:
                max_score = score
                best_hex = u

        return best_hex if best_hex else top_k[0][0]
    
    def winning_hex(self, blocked):
        hexes = {}
        queue = deque()
        for cell in self.cells:
            if cell not in blocked and self.final_hex(cell):
                hexes[cell] = 1
                queue.append(cell)
        
        while queue:
            u = queue.popleft()
            for v in self.get_neighbors(*u):
                if v not in self.cells or v in blocked or v in hexes:
                    continue
                nod = -1
                mapp=collections.defaultdict(int)
                for nb in self.get_neighbors(*v):
                    if nb in hexes:
                        if(hexes[nb]<=2):
                            mapp[hexes[nb]] += 1
                            if(mapp[hexes[nb]]==2):
                                nod=hexes[nb]
                if nod!=-1:
                    hexes[v] = nod + 1
                    queue.append(v)

        return hexes

    def score_mouse(self, move, blocked, win_hexes):
        if move in win_hexes:
            return 10**9
            
        q = deque([(move, 0)])
        viz = {move: 0}
        total = 0.0
        ok = False
        while q:
            curr, dist = q.popleft()
            
            if self.final_hex(curr):
                ok = True
                weight = 100.0 / math.pow(dist + 1.0, 2)
                total += weight
            
            for n in self.get_neighbors(*curr):
                if n in self.cells and n not in blocked and n not in viz:
                    viz[n] = dist + 1
                    q.append((n, dist + 1))
        if not ok:
            return -10**9
        return total

    def best_move_mouse(self, mouse_pos, blocked):
        neighbors = self.get_neighbors(*mouse_pos)
        valid_moves = []
        
        for n in neighbors:
            if n not in self.cells:
                return n
            if n not in blocked:
                valid_moves.append(n)
        
        if not valid_moves:
            return None
            
        win_hexes = self.winning_hex(blocked)
        best_move = None
        best_score = -10**9
        
        for move in valid_moves:
            if self.final_hex(move):
                return move
                
            score = self.score_mouse(move, blocked, win_hexes)
            score += random.uniform(0, 0.1)
            
            if score > best_score:
                best_score = score
                best_move = move
        return best_move if best_move else random.choice(valid_moves)
    
    def get_shortest_path(self, start_pos):
        queue = deque([start_pos])
        prev = {start_pos: None}
        while queue:
            u = queue.popleft()
            if self.final_hex(u):
                cur = u
                while prev[cur] != start_pos:
                    cur = prev[cur]
                    if cur is None:
                        break
                return cur if cur is not None else u
            for nb in self.get_neighbors(*u):
                if nb not in self.cells:
                    if prev.get(u) is None:
                        return nb
                if nb not in self.walls and nb not in prev and nb in self.cells:
                    prev[nb] = u
                    queue.append(nb)
        return None

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
            move = self.get_shortest_path(self.pos)
            if not move or move not in valid_moves:
                move = random.choice(valid_moves)

        elif self.difficulty == "HARD":
             move = self.best_move_mouse(self.pos, self.walls)
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
        target_wall = None
        
        if self.difficulty == "EASY":
            opts = [c for c in self.cells if c not in self.walls and c != self.pos]
            if opts: 
                target_wall = random.choice(opts)
        elif self.difficulty == "MEDIUM":
            move = self.get_shortest_path(self.pos)
            if move and move not in self.walls and move != self.pos:
                target_wall = move
            else:
                opts = [c for c in self.cells if c not in self.walls and c != self.pos]
                if opts: 
                    target_wall = random.choice(opts)
        elif self.difficulty == "HARD":
            target_wall = self.best_wall(self.pos, self.walls)

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