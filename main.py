import pygame
import math
from game import Game

def hex_to_pixel(q, r, sz, cx, cy):
    x = sz * (math.sqrt(3) * q + math.sqrt(3)/2 * r)
    y = sz * (3/2 * r)
    return (int(x + cx), int(y + cy))

def pixel_to_hex(x, y, sz, cx, cy):
    x, y = x - cx, y - cy
    q = (math.sqrt(3)/3 * x - 1/3 * y) / sz
    r = (2/3 * y) / sz
    return axial_round(q, r)

def axial_round(x, y):
    z = -(x + y)
    rx, ry, rz = round(x), round(y), round(z)
    dx, dy, dz = abs(rx - x), abs(ry - y), abs(rz - z)
    
    if dx > dy and dx > dz: 
        rx = -(ry + rz)
    elif dy > dz:           
        ry = -(rx + rz)
    else:                   
        rz = -(rx + ry)
    return int(rx), int(ry)

if __name__ == "__main__":
    pygame.init()
    W, H = 800, 600
    scr = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Hex Game - Phase 2")
    clock = pygame.time.Clock()
    
    game = Game(w=11, h=11, n_obs=15)
    
    SZ = 25
    CX, CY = W // 2, H // 2

    mid_r = game.h // 2
    mid_q = (game.w // 2) - (mid_r // 2)

    font_big = pygame.font.SysFont("Arial", 60, bold=True)
    font_small = pygame.font.SysFont("Arial", 30)
    overlay = pygame.Surface((W, H))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(180)
    
    run = True
    while run:
        scr.fill((30, 30, 35))
        mx, my = pygame.mouse.get_pos()
        raw_q, raw_r = pixel_to_hex(mx, my, SZ, CX, CY)
        hq, hr = raw_q + mid_q, raw_r + mid_r

        for q, r in game.cells:
            color = (200, 200, 200)
            if (q, r) in game.walls: 
                color = (60, 60, 60)
            if (q, r) == game.pos:   
                color = (255, 100, 100)
            
            if (q, r) == (hq, hr) and not game.over:
                is_neighbor = (q, r) in game.get_neighbors(*game.pos)
                if is_neighbor and (q, r) not in game.walls:
                    color = (100, 255, 100)
                elif is_neighbor and (q, r) in game.walls:
                    color = (100, 50, 50)
            
            px, py = hex_to_pixel(q - mid_q, r - mid_r, SZ, CX, CY)
            
            pts = []
            for i in range(6):
                ang = math.radians(60 * i - 30)
                pts.append((px + SZ * math.cos(ang), py + SZ * math.sin(ang)))
            
            pygame.draw.polygon(scr, color, pts)
            pygame.draw.polygon(scr, (0,0,0), pts, 2)

        if game.over:
            scr.blit(overlay, (0, 0))
            
            msg = "AI CASTIGAT!" if game.won else "E JOVER"
            c = (100, 255, 100) if game.won else (255, 100, 100)
            txt = font_big.render(msg, True, c)
            text_rect = txt.get_rect(center=(W//2, H//2 - 20))
            scr.blit(txt, text_rect)
            
            sub = font_small.render("Apasa R pentru Reset", True, (200,200,200))
            sub_rect = sub.get_rect(center=(W//2, H//2 + 40))
            scr.blit(sub, sub_rect)

        for e in pygame.event.get():
            if e.type == pygame.QUIT: run = False
            
            if e.type == pygame.KEYDOWN and e.key == pygame.K_r: 
                game.reset()
            
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                game.move_mouse(hq, hr)

        pygame.display.flip()
        clock.tick(60)
        
    pygame.quit()