import pygame
import math
from game import Game

def hex_to_pixel(q, r, sz, cx, cy):
    x = sz * (math.sqrt(3) * q + math.sqrt(3) / 2 * r)
    y = sz * (3 / 2 * r)
    return (int(x + cx), int(y + cy))

def pixel_to_hex(x, y, sz, cx, cy):
    x, y = x - cx, y - cy
    q = (math.sqrt(3) / 3 * x - 1 / 3 * y) / sz
    r = (2 / 3 * y) / sz
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
    pygame.display.set_caption("Hex Game - Main Menu")
    clock = pygame.time.Clock()
    
    font_title = pygame.font.SysFont("Arial", 60, bold=True)
    font_btn = pygame.font.SysFont("Arial", 40)
    font_small = pygame.font.SysFont("Arial", 25)

    btn_ai = pygame.Rect(W // 2 - 120, 250, 240, 60)
    btn_pvp = pygame.Rect(W // 2 - 120, 350, 240, 60)
    
    state = "MENU"
    game = None
    SZ = 25
    CX, CY = W // 2, H // 2

    run = True
    while run:
        scr.fill((30, 30, 35))
        mx, my = pygame.mouse.get_pos()

        if state == "MENU":
            txt_title = font_title.render("HEX TRAP", True, (255, 255, 255))
            rt = txt_title.get_rect(center=(W // 2, 150))
            scr.blit(txt_title, rt)

            col_ai = (100, 100, 100) if btn_ai.collidepoint((mx, my)) else (60, 60, 60)
            pygame.draw.rect(scr, col_ai, btn_ai, border_radius=10)
            txt_ai = font_btn.render("VS Computer", True, (255, 255, 255))
            rai = txt_ai.get_rect(center=btn_ai.center)
            scr.blit(txt_ai, rai)

            col_pvp = (100, 100, 100) if btn_pvp.collidepoint((mx, my)) else (60, 60, 60)
            pygame.draw.rect(scr, col_pvp, btn_pvp, border_radius=10)
            txt_pvp = font_btn.render("VS Player", True, (255, 255, 255))
            rpvp = txt_pvp.get_rect(center=btn_pvp.center)
            scr.blit(txt_pvp, rpvp)

        elif state == "GAME":
            if not game.over:
                if game.mode == "AI":
                    info = "MOD: VS COMPUTER"
                else:
                    info = "MOD: PVP - Tura: " + ("Zidar" if game.turn == 0 else "Soarece")
                
                scr.blit(font_small.render(info, True, (200, 200, 200)), (20, 20))
                scr.blit(font_small.render("ESC - Meniu", True, (150, 150, 150)), (20, 50))

            raw_q, raw_r = pixel_to_hex(mx, my, SZ, CX, CY)
            mid_r = game.h // 2
            mid_q = (game.w // 2) - (mid_r // 2)
            hq, hr = raw_q + mid_q, raw_r + mid_r

            for q, r in game.cells:
                color = (200, 200, 200)
                if (q, r) in game.walls:
                    color = (60, 60, 60)
                if (q, r) == game.pos:
                    color = (255, 100, 100)
                
                if (q, r) == (hq, hr) and not game.over:
                    valid = False
                    if game.mode == "AI":
                        if (q, r) not in game.walls and (q, r) != game.pos:
                            valid = True
                    else:
                        if game.turn == 0:
                            if (q, r) not in game.walls and (q, r) != game.pos:
                                valid = True
                        else:
                            if (q, r) in game.get_neighbors(*game.pos) and (q, r) not in game.walls:
                                valid = True

                    color = (100, 255, 100) if valid else (255, 50, 50)

                px, py = hex_to_pixel(q - mid_q, r - mid_r, SZ, CX, CY)
                pts = []
                for i in range(6):
                    ang = math.radians(60 * i - 30)
                    pts.append((px + SZ * math.cos(ang), py + SZ * math.sin(ang)))
                
                pygame.draw.polygon(scr, color, pts)
                pygame.draw.polygon(scr, (0, 0, 0), pts, 2)

            if game.over:
                overlay = pygame.Surface((W, H))
                overlay.fill((0, 0, 0))
                overlay.set_alpha(180)
                scr.blit(overlay, (0, 0))
                
                wtxt = "ZIDARUL A CASTIGAT!" if game.winner == "BLOCKER" else "SOARECELE A SCAPAT!"
                wc = (100, 255, 100) if game.winner == "MOUSE" else (200, 200, 50)
                
                if game.mode == "AI" and game.winner == "MOUSE": 
                    wtxt = "AI PIERDUT!"
                    wc = (255, 100, 100)
                elif game.mode == "AI" and game.winner == "BLOCKER":
                    wtxt = "AI CASTIGAT!"
                    wc = (100, 255, 100)

                img = font_title.render(wtxt, True, wc)
                scr.blit(img, img.get_rect(center=(W // 2, H // 2 - 20)))
                
                sub = font_small.render("R - Restart | ESC - Meniu", True, (200, 200, 200))
                scr.blit(sub, sub.get_rect(center=(W // 2, H // 2 + 40)))

        for e in pygame.event.get():
            if e.type == pygame.QUIT: 
                run = False
            
            if state == "MENU":
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if btn_ai.collidepoint((mx, my)):
                        game = Game(mode="AI", w=11, h=11, n_obs=10)
                        state = "GAME"
                    elif btn_pvp.collidepoint((mx, my)):
                        game = Game(mode="PVP", w=11, h=11, n_obs=10)
                        state = "GAME"

            elif state == "GAME":
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_r:
                        game.reset()
                    if e.key == pygame.K_ESCAPE:
                        state = "MENU"
                
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    game.click_tile(hq, hr)

        pygame.display.flip()
        clock.tick(60)
        
    pygame.quit()