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
    if dx > dy and dx > dz: rx = -(ry + rz)
    elif dy > dz: ry = -(rx + rz)
    else: rz = -(rx + ry)
    return int(rx), int(ry)

def draw_button(screen, rect, text, font, mouse_pos):
    color = (100, 100, 100) if rect.collidepoint(mouse_pos) else (60, 60, 60)
    pygame.draw.rect(screen, color, rect, border_radius=10)
    pygame.draw.rect(screen, (200, 200, 200), rect, 2, border_radius=10)
    txt_surf = font.render(text, True, (255, 255, 255))
    txt_rect = txt_surf.get_rect(center=rect.center)
    screen.blit(txt_surf, txt_rect)
    return rect.collidepoint(mouse_pos)

if __name__ == "__main__":
    pygame.init()
    W, H = 800, 600
    scr = pygame.display.set_mode((W, H))
    pygame.display.set_caption("TrapTheMouse")
    clock = pygame.time.Clock()
    
    font_title = pygame.font.SysFont("Arial", 50, bold=True)
    font_btn = pygame.font.SysFont("Arial", 30)
    font_small = pygame.font.SysFont("Arial", 20)

    state = "MENU_MAIN"
    
    selected_mode = ""
    selected_role = ""
    selected_diff = ""

    game = None
    SZ = 25
    CX, CY = W // 2, H // 2

    def center_rect_y(y, w=240, h=50):
        return pygame.Rect(W//2 - w//2, y, w, h)

    btn_vs_ai = center_rect_y(250)
    btn_vs_pvp = center_rect_y(320)

    btn_role_blocker = center_rect_y(250)
    btn_role_mouse = center_rect_y(320)
    
    btn_diff_easy = center_rect_y(250)
    btn_diff_med = center_rect_y(320)
    btn_diff_hard = center_rect_y(390)

    run = True
    while run:
        scr.fill((30, 30, 35))
        mx, my = pygame.mouse.get_pos()

        if state == "MENU_MAIN":
            title = font_title.render("TrapTheMouse", True, (255, 255, 255))
            scr.blit(title, title.get_rect(center=(W//2, 150)))

            draw_button(scr, btn_vs_ai, "VS Computer", font_btn, (mx, my))
            draw_button(scr, btn_vs_pvp, "VS Player (PVP)", font_btn, (mx, my))

        elif state == "MENU_ROLE":
            title = font_title.render("ALEGE ROLUL", True, (255, 255, 255))
            scr.blit(title, title.get_rect(center=(W//2, 150)))
            
            draw_button(scr, btn_role_blocker, "Joc ca ZIDAR", font_btn, (mx, my))
            draw_button(scr, btn_role_mouse, "Joc ca SOARECE", font_btn, (mx, my))
            
            back_txt = font_small.render("Apasa ESC pentru inapoi", True, (150, 150, 150))
            scr.blit(back_txt, back_txt.get_rect(center=(W//2, 500)))

        elif state == "MENU_DIFF":
            title = font_title.render("DIFICULTATE AI", True, (255, 255, 255))
            scr.blit(title, title.get_rect(center=(W//2, 150)))

            draw_button(scr, btn_diff_easy, "EAZY", font_btn, (mx, my))
            draw_button(scr, btn_diff_med, "MEDIUM", font_btn, (mx, my))
            draw_button(scr, btn_diff_hard, "HARD", font_btn, (mx, my))

            back_txt = font_small.render("Apasa ESC pentru inapoi", True, (150, 150, 150))
            scr.blit(back_txt, back_txt.get_rect(center=(W//2, 500)))

        elif state == "GAME":
            if not game.over:
                role_txt = "Zidar" if game.player_role == "BLOCKER" else "Soarece"
                diff_txt = f"Diff: {game.difficulty}" if game.mode == "AI" else "PVP"
                info = f"MOD: {game.mode} | Tu esti: {role_txt} | {diff_txt}"
                
                scr.blit(font_small.render(info, True, (200, 200, 200)), (20, 20))
                turn_info = "Randul tau" if (game.turn == 0 and game.player_role == "BLOCKER") or (game.turn == 1 and game.player_role == "MOUSE") else "Gandeste AI..."
                if game.mode == "PVP": turn_info = "Randul Zidarului" if game.turn == 0 else "Randul Soarecelui"
                
                scr.blit(font_small.render(turn_info, True, (100, 255, 100)), (20, 50))

            raw_q, raw_r = pixel_to_hex(mx, my, SZ, CX, CY)
            mid_r = game.h // 2
            mid_q = (game.w // 2) - (mid_r // 2)
            hq, hr = raw_q + mid_q, raw_r + mid_r

            for q, r in game.cells:
                color = (200, 200, 200)
                if (q, r) in game.walls: color = (60, 60, 60)
                if (q, r) == game.pos:   color = (255, 100, 100)
                
                if (q, r) == (hq, hr) and not game.over:
                    valid = False
                    is_neighbor = (q, r) in game.get_neighbors(*game.pos)
                    is_not_wall = (q, r) not in game.walls

                    if game.mode == "PVP":
                        if game.turn == 0:
                            if is_not_wall and (q,r) != game.pos: valid = True
                        else:
                            if is_neighbor and is_not_wall: valid = True
                    else:
                        if game.player_role == "BLOCKER":
                             if game.turn == 0 and is_not_wall and (q,r) != game.pos: valid = True
                        else:
                             if game.turn == 1 and is_neighbor and is_not_wall: valid = True

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
                
                if game.winner == "BLOCKER":
                    wtxt = "ZIDARUL A CASTIGAT!"
                    col = (100, 255, 100) if game.player_role == "BLOCKER" else (255, 100, 100)
                else:
                    wtxt = "SOARECELE A SCAPAT!"
                    col = (100, 255, 100) if game.player_role == "MOUSE" else (255, 100, 100)
                
                if game.mode == "PVP": col = (255, 215, 0)

                img = font_title.render(wtxt, True, col)
                scr.blit(img, img.get_rect(center=(W // 2, H // 2 - 20)))
                
                sub = font_small.render("R - Restart | ESC - Meniu Principal", True, (200, 200, 200))
                scr.blit(sub, sub.get_rect(center=(W // 2, H // 2 + 40)))

        for e in pygame.event.get():
            if e.type == pygame.QUIT: 
                run = False
            
            if state == "MENU_MAIN":
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if btn_vs_ai.collidepoint((mx, my)):
                        selected_mode = "AI"
                        state = "MENU_ROLE"
                    elif btn_vs_pvp.collidepoint((mx, my)):
                        selected_mode = "PVP"
                        game = Game(mode="PVP", player_role="BLOCKER")
                        state = "GAME"

            elif state == "MENU_ROLE":
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if btn_role_blocker.collidepoint((mx, my)):
                        selected_role = "BLOCKER"
                        state = "MENU_DIFF"
                    elif btn_role_mouse.collidepoint((mx, my)):
                        selected_role = "MOUSE"
                        state = "MENU_DIFF"
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    state = "MENU_MAIN"

            elif state == "MENU_DIFF":
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    ready = False
                    if btn_diff_easy.collidepoint((mx, my)):
                        selected_diff = "EASY"
                        ready = True
                    elif btn_diff_med.collidepoint((mx, my)):
                        selected_diff = "MEDIUM"
                        ready = True
                    elif btn_diff_hard.collidepoint((mx, my)):
                        selected_diff = "HARD"
                        ready = True
                    
                    if ready:
                        game = Game(mode="AI", difficulty=selected_diff, player_role=selected_role)
                        state = "GAME"

                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    state = "MENU_ROLE"

            elif state == "GAME":
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_r:
                        game.reset()
                    if e.key == pygame.K_ESCAPE:
                        state = "MENU_MAIN"
                
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    game.click_tile(hq, hr)

        pygame.display.flip()
        clock.tick(60)
        
    pygame.quit()