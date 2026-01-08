import random
import math
import collections

def bfs_dist(game, start, blocked):
    queue = collections.deque([(start, 0)])
    viz = {start: 0}
    while queue:
        nod, dist = queue.popleft()
        for n in game.get_neighbors(*nod):
            if n in game.cells and n not in blocked and n not in viz:
                viz[n] = dist + 1
                queue.append((n, dist + 1))
    return viz

def dp_IN_OUT(game, dist, blocked, start):
    edge_nodes = [n for n in dist if game.final_hex(n)]
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
        for v in game.get_neighbors(*u):
            if v in dist and v not in blocked and dist[v] == d_u + 1:
                IN[v] += IN[u]

    for ex in exits:
        OUT[ex] = 1 

    nods = sorted(dist.keys(), key=lambda x: -dist[x])
    for u in nods:
        if OUT[u] == 0 and u not in exits: continue
        d_u = dist[u]
        for v in game.get_neighbors(*u):
            if v in dist and v not in blocked and dist[v] == d_u - 1:
                OUT[v] += OUT[u]

    total = OUT[start]
    return IN, OUT, total

def build_dinic(game, start, blocked):
    dist = bfs_dist(game, start, blocked)
    edge_nodes = [n for n in dist if game.final_hex(n)]
    
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
        
        if game.final_hex(u) and dist[u] == min_dist:
            add_edge(f"{u}_out", T, INF)
        
        d_u = dist[u]
        for v in game.get_neighbors(*u):
            if v in dist and v not in blocked and dist[v] == d_u + 1:
                add_edge(f"{u}_out", f"{v}_in", INF)
                
    return graph, S, T

def dinic_bfs(s, t, graph, level):
    level.clear()
    level[s] = 0
    queue = collections.deque([s])
    
    while queue:
        u = queue.popleft()
        for v, cap, rev in graph[u]:
            if cap > 0 and v not in level:
                level[v] = level[u] + 1
                queue.append(v)
    
    return t in level

def dinic_dfs(u, t, flow, graph, level, ptr):
    if flow == 0 or u == t:
        return flow
    
    for i in range(ptr[u], len(graph[u])):
        ptr[u] = i 
        v, cap, rev = graph[u][i]
        
        if cap > 0 and v in level and level[v] == level[u] + 1:
            pushed = dinic_dfs(v, t, min(flow, cap), graph, level, ptr)
            if pushed > 0:
                graph[u][i][1] -= pushed
                graph[v][rev][1] += pushed
                return pushed
    
    return 0

def dinic(S, T, graph):
    max_flow = 0
    level = {}
    while dinic_bfs(S, T, graph, level):
        ptr = collections.defaultdict(int)
        while True:
            pushed = dinic_dfs(S, T, 10**9, graph, level, ptr)
            if pushed == 0: break
            max_flow += pushed
    return max_flow

def best_wall(game, mouse_pos, blocked):
    dist = bfs_dist(game, mouse_pos, blocked)
    if not dist: 
        opts = [c for c in game.cells if c not in blocked and c != mouse_pos]
        return random.choice(opts) if opts else None

    IN, OUT, total = dp_IN_OUT(game, dist, blocked, mouse_pos)
    
    if total == 0:
        opts = [c for c in game.cells if c not in blocked and c != mouse_pos]
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
            opts = [c for c in game.cells if c not in blocked and c != mouse_pos]
            return random.choice(opts) if opts else None

    candidates.sort(key=lambda x: x[1], reverse=True)
    top_k = candidates[:15]
    
    base_graph, S, T = build_dinic(game, mouse_pos, blocked)
    if not base_graph: 
        return top_k[0][0]
    
    base_cut = dinic(S, T, base_graph)
    
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
            
            temp_graph, tS, tT = build_dinic(game, mouse_pos,temp_blocked)
            if temp_graph:
                new_cut = dinic(tS, tT, temp_graph)
                marginal_cut = max(0, base_cut - new_cut)
        
        score = base_val + (alpha_cut * marginal_cut)
        
        if score > max_score:
            max_score = score
            best_hex = u

    return best_hex if best_hex else top_k[0][0]

def winning_hex(game, blocked):
    hexes = {}
    queue = collections.deque()
    for cell in game.cells:
        if cell not in blocked and game.final_hex(cell):
            hexes[cell] = 1
            queue.append(cell)
    
    while queue:
        u = queue.popleft()
        for v in game.get_neighbors(*u):
            if v not in game.cells or v in blocked or v in hexes:
                continue
            nod = -1
            mapp=collections.defaultdict(int)
            for nb in game.get_neighbors(*v):
                if nb in hexes:
                    if(hexes[nb]<=2):
                        mapp[hexes[nb]] += 1
                        if(mapp[hexes[nb]]==2):
                            nod=hexes[nb]
            if nod!=-1:
                hexes[v] = nod + 1
                queue.append(v)

    return hexes

def score_mouse(game, move, blocked, win_hexes):
    if move in win_hexes:
        return 10**9
        
    q = collections.deque([(move, 0)])
    viz = {move: 0}
    total = 0.0
    ok = False
    while q:
        curr, dist = q.popleft()
        
        if game.final_hex(curr):
            ok = True
            weight = 100.0 / math.pow(dist + 1.0, 2)
            total += weight
        
        for n in game.get_neighbors(*curr):
            if n in game.cells and n not in blocked and n not in viz:
                viz[n] = dist + 1
                q.append((n, dist + 1))
    if not ok:
        return -10**9
    return total

def best_move_mouse(game, mouse_pos, blocked):
    neighbors = game.get_neighbors(*mouse_pos)
    valid_moves = []
    
    for n in neighbors:
        if n not in game.cells:
            return n
        if n not in blocked:
            valid_moves.append(n)
    
    if not valid_moves:
        return None
        
    win_hexes = winning_hex(game, blocked)
    best_move = None
    best_score = -10**9
    
    for move in valid_moves:
        if game.final_hex(move):
            return move
            
        score = score_mouse(game, move, blocked, win_hexes)
        score += random.uniform(0, 0.1)
        
        if score > best_score:
            best_score = score
            best_move = move
    return best_move if best_move else random.choice(valid_moves)

def get_shortest_path(game, start_pos):
    queue = collections.deque([start_pos])
    prev = {start_pos: None}
    while queue:
        u = queue.popleft()
        if game.final_hex(u):
            cur = u
            while prev[cur] != start_pos:
                cur = prev[cur]
                if cur is None:
                    break
            return cur if cur is not None else u
        for nb in game.get_neighbors(*u):
            if nb not in game.cells:
                if prev.get(u) == start_pos:
                    return nb
            if nb not in game.walls and nb not in prev and nb in game.cells:
                prev[nb] = u
                queue.append(nb)
    return None
