"""Main game loop and UI rendering for Trap the Mouse.

This module contains the main entry point for the game, handling Pygame
initialization, event processing, state management, menu navigation, and
all rendering logic for the game interface.
"""
import pygame
import math
import os
from game import Game
import constants as C
import hex_math
import ui

if __name__ == "__main__":
    pygame.init()
    W, H = C.SCREEN_W, C.SCREEN_H
    scr = pygame.display.set_mode((W, H))
    pygame.display.set_caption("TrapTheMouse")
    clock = pygame.time.Clock()
    
    mouse_img_raw = None
    if os.path.exists("mouse.png"):
        mouse_img_raw = pygame.image.load("mouse.png")

    # Fonts
    font_title = pygame.font.SysFont("Arial", 50, bold=True)
    font_btn = pygame.font.SysFont("Arial", 28)
    font_small = pygame.font.SysFont("Arial", 18)

    state = "MENU_MAIN"

    selected_mode = ""
    selected_role = ""
    selected_diff = ""
    board_size = 11

    game = None
    SZ = 25
    CX, CY = W // 2, H // 2
    scaled_mouse_img = None

    # UI Elements Definition
    btn_vs_ai = ui.get_centered_rect_y(220, W)
    btn_vs_pvp = ui.get_centered_rect_y(280, W)
    btn_load_menu = ui.get_centered_rect_y(340, W) 
    
    btn_sz_11 = pygame.Rect(W//2 - 140, 450, 60, 40)
    btn_sz_13 = pygame.Rect(W//2 - 70, 450, 60, 40)
    btn_sz_15 = pygame.Rect(W//2, 450, 60, 40)
    btn_sz_17 = pygame.Rect(W//2 + 70, 450, 60, 40)

    btn_role_blocker = ui.get_centered_rect_y(250, W)
    btn_role_mouse = ui.get_centered_rect_y(310, W)
    
    btn_diff_easy = ui.get_centered_rect_y(220, W)
    btn_diff_med = ui.get_centered_rect_y(280, W)
    btn_diff_hard = ui.get_centered_rect_y(340, W)

    btn_undo = pygame.Rect(30, H - 60, 70, 40)
    btn_redo = pygame.Rect(110, H - 60, 70, 40)
    btn_save = pygame.Rect(200, H - 60, 70, 40)
    btn_load_ingame = pygame.Rect(280, H - 60, 70, 40)
    btn_menu = pygame.Rect(W - 110, H - 60, 80, 40)

    save_files = []
    save_file_rects = []
    delete_file_rects = []
    input_text = ""
    save_error_msg = ""
    
    msg_timer = 0
    msg_text = ""

    def refresh_save_list():
        save_files.clear()
        save_file_rects.clear()
        delete_file_rects.clear()
        
        folder = "saves"
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        files = [f for f in os.listdir(folder) if f.endswith(".sav")]
        files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)), reverse=True)
        
        display_files = files[:6]
        
        start_y = 200
        for i, f in enumerate(display_files):
            rect = ui.get_centered_rect_y(start_y + i * 60, W)
            del_rect = pygame.Rect(rect.right + 10, rect.y, 40, rect.height)
            
            save_files.append(f)
            save_file_rects.append(rect)
            delete_file_rects.append(del_rect)

    run = True
    while run:
        scr.fill(C.COLOR_BG)
        mx, my = pygame.mouse.get_pos()

        if state == "MENU_MAIN":
            title = font_title.render("TrapTheMouse", True, C.COLOR_WHITE)
            scr.blit(title, title.get_rect(center=(W//2, 120)))

            ui.draw_button(scr, btn_vs_ai, "VS Computer", font_btn, (mx, my))
            ui.draw_button(scr, btn_vs_pvp, "VS Player (PVP)", font_btn, (mx, my))
            ui.draw_button(scr, btn_load_menu, "Load Game", font_btn, (mx, my))

            lbl_sz = font_small.render("Board Size:", True, C.COLOR_TEXT_GRAY)
            scr.blit(lbl_sz, (W//2 - 140, 425))
            
            ui.draw_button(scr, btn_sz_11, "11", font_small, (mx, my), board_size==11)
            ui.draw_button(scr, btn_sz_13, "13", font_small, (mx, my), board_size==13)
            ui.draw_button(scr, btn_sz_15, "15", font_small, (mx, my), board_size==15)
            ui.draw_button(scr, btn_sz_17, "17", font_small, (mx, my), board_size==17)

        elif state == "MENU_SAVE":
            title = font_title.render("SAVE GAME AS", True, C.COLOR_WHITE)
            scr.blit(title, title.get_rect(center=(W//2, 200)))
           
            input_rect = pygame.Rect(W//2 - 150, 300, 300, 50)
            pygame.draw.rect(scr, (50, 50, 50), input_rect)
            pygame.draw.rect(scr, C.COLOR_TEXT_GRAY, input_rect, 2)
            
            txt_surf = font_btn.render(input_text, True, C.COLOR_WHITE)
            scr.blit(txt_surf, (input_rect.x + 10, input_rect.y + 10))
            
            if save_error_msg:
                err_surf = font_small.render(save_error_msg, True, C.COLOR_MSG_ERROR)
                scr.blit(err_surf, err_surf.get_rect(center=(W//2, 370)))

            info = font_small.render("Type name and press ENTER", True, C.COLOR_TEXT_DARK_GRAY)
            scr.blit(info, info.get_rect(center=(W//2, 500)))
            
            back_txt = font_small.render("ESC - Cancel", True, C.COLOR_TEXT_DARK_GRAY)
            scr.blit(back_txt, back_txt.get_rect(center=(W//2, 530)))

        elif state == "MENU_LOAD":
            title = font_title.render("SELECT SAVE", True, C.COLOR_WHITE)
            scr.blit(title, title.get_rect(center=(W//2, 100)))
            
            if not save_files:
                info = font_small.render("No save files found.", True, C.COLOR_TEXT_DARK_GRAY)
                scr.blit(info, info.get_rect(center=(W//2, 250)))
            
            for i, fname in enumerate(save_files):
                ui.draw_button(scr, save_file_rects[i], fname[:-4], font_small, (mx, my))
                ui.draw_button(scr, delete_file_rects[i], "X", font_small, (mx, my), bg_color=C.COLOR_BTN_DELETE)

            back_txt = font_small.render("ESC - Back", True, C.COLOR_TEXT_DARK_GRAY)
            scr.blit(back_txt, back_txt.get_rect(center=(W//2, 600)))

        elif state == "MENU_ROLE":
            title = font_title.render("ALEGE ROLUL", True, C.COLOR_WHITE)
            scr.blit(title, title.get_rect(center=(W//2, 150)))
            ui.draw_button(scr, btn_role_blocker, "Joc ca ZIDAR", font_btn, (mx, my))
            ui.draw_button(scr, btn_role_mouse, "Joc ca SOARECE", font_btn, (mx, my))
            back_txt = font_small.render("ESC - Back", True, C.COLOR_TEXT_DARK_GRAY)
            scr.blit(back_txt, back_txt.get_rect(center=(W//2, 500)))

        elif state == "MENU_DIFF":
            title = font_title.render("DIFICULTATE AI", True, C.COLOR_WHITE)
            scr.blit(title, title.get_rect(center=(W//2, 150)))
            ui.draw_button(scr, btn_diff_easy, "EAZY", font_btn, (mx, my))
            ui.draw_button(scr, btn_diff_med, "MEDIUM", font_btn, (mx, my))
            ui.draw_button(scr, btn_diff_hard, "HARD", font_btn, (mx, my))
            back_txt = font_small.render("ESC - Back", True, C.COLOR_TEXT_DARK_GRAY)
            scr.blit(back_txt, back_txt.get_rect(center=(W//2, 500)))

        elif state == "GAME":
            if game is None:
                state = "MENU_MAIN"
                continue
            
            SZ = hex_math.get_hex_size(game.w, game.h, W, H - 110)
            
            if mouse_img_raw:
                scaled_mouse_img = pygame.transform.scale(mouse_img_raw, (SZ * 1.5, SZ * 1.5))

            if not game.over:
                role_txt = "Zidar" if game.player_role == "BLOCKER" else "Soarece"
                diff_txt = f"{game.difficulty}" if game.mode == "AI" else "PVP"
                info = f"{game.mode} | {role_txt} | {diff_txt} | Size: {game.w}x{game.h}"
                scr.blit(font_small.render(info, True, C.COLOR_TEXT_GRAY), (20, 20))
                
                turn_label = "Randul tau" if (game.turn == 0 and game.player_role == "BLOCKER") or (game.turn == 1 and game.player_role == "MOUSE") else "Gandeste AI..."
                if game.mode == "PVP": turn_label = "Zidar" if game.turn == 0 else "Soarece"
                scr.blit(font_small.render(turn_label, True, C.COLOR_TURN_INDICATOR), (20, 45))

            raw_q, raw_r = hex_math.pixel_to_hex(mx, my, SZ, CX, CY)
            mid_r = game.h // 2
            mid_q = (game.w // 2) - (mid_r // 2)
            hq, hr = raw_q + mid_q, raw_r + mid_r

            for q, r in game.cells:
                color = C.COLOR_CELL_DEFAULT
                if (q, r) in game.walls: color = C.COLOR_WALL
                if (q, r) == game.pos:   color = C.COLOR_MOUSE_POS
                
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

                    color = C.COLOR_VALID_MOVE if valid else C.COLOR_INVALID_MOVE

                px, py = hex_math.hex_to_pixel(q - mid_q, r - mid_r, SZ, CX, CY)
                pts = []
                for i in range(6):
                    ang = math.radians(60 * i - 30)
                    pts.append((px + SZ * math.cos(ang), py + SZ * math.sin(ang)))
                pygame.draw.polygon(scr, color, pts)
                pygame.draw.polygon(scr, C.COLOR_BLACK, pts, 2)

                if (q, r) == game.pos and scaled_mouse_img:
                    r_img = scaled_mouse_img.get_rect(center=(px, py))
                    scr.blit(scaled_mouse_img, r_img)

            ui.draw_button(scr, btn_undo, "Undo", font_small, (mx, my))
            can_redo = len(game.redo_stack) > 0
            bg_redo = None if can_redo else (40, 40, 40)
            ui.draw_button(scr, btn_redo, "Redo", font_small, (mx, my), bg_color=bg_redo)
            ui.draw_button(scr, btn_save, "Save", font_small, (mx, my))
            ui.draw_button(scr, btn_load_ingame, "Load", font_small, (mx, my))
            ui.draw_button(scr, btn_menu, "Menu", font_small, (mx, my))

            if msg_timer > 0:
                msg_surf = font_small.render(msg_text, True, C.COLOR_MSG_INFO)
                scr.blit(msg_surf, (350, H - 50))
                msg_timer -= 1

            if game.over:
                overlay = pygame.Surface((W, H))
                overlay.fill((0, 0, 0))
                overlay.set_alpha(180)
                scr.blit(overlay, (0, 0))
                
                if game.winner == "BLOCKER":
                    wtxt = "ZIDARUL A CASTIGAT!"
                    col = C.COLOR_VALID_MOVE if game.player_role == "BLOCKER" else C.COLOR_MOUSE_POS
                else:
                    wtxt = "SOARECELE A SCAPAT!"
                    col = C.COLOR_VALID_MOVE if game.player_role == "MOUSE" else C.COLOR_MOUSE_POS
                
                if game.mode == "PVP": col = (255, 215, 0)

                img = font_title.render(wtxt, True, col)
                screen_center = img.get_rect(center=(W // 2, H // 2 - 20))
                scr.blit(img, screen_center)
                sub = font_small.render("R - Restart | ESC - Menu", True, C.COLOR_TEXT_GRAY)
                scr.blit(sub, sub.get_rect(center=(W // 2, H // 2 + 40)))

        for e in pygame.event.get():
            if e.type == pygame.QUIT: 
                run = False
            
            if state == "MENU_SAVE":
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        state = "GAME"
                        input_text = ""
                        save_error_msg = ""
                    elif e.key == pygame.K_RETURN:
                        if len(input_text) > 0:
                            fname = input_text + ".sav"
                            if os.path.exists(os.path.join("saves", fname)):
                                save_error_msg = "Name already exists!"
                            else:
                                if game.save_to_file(fname): 
                                    msg_text = "Game Saved!"
                                    msg_timer = 60
                                    state = "GAME"
                                    input_text = ""
                                    save_error_msg = ""
                    elif e.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                        save_error_msg = ""
                    else:
                        if len(input_text) < 15 and e.unicode.isalnum():
                            input_text += e.unicode
                            save_error_msg = ""

            elif state == "MENU_MAIN":
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if btn_vs_ai.collidepoint((mx, my)):
                        selected_mode = "AI"
                        state = "MENU_ROLE"
                    elif btn_vs_pvp.collidepoint((mx, my)):
                        selected_mode = "PVP"
                        game = Game(mode="PVP", player_role="BLOCKER", w=board_size, h=board_size)
                        state = "GAME"
                    elif btn_load_menu.collidepoint((mx, my)):
                        refresh_save_list()
                        state = "MENU_LOAD"
                    
                    if btn_sz_11.collidepoint((mx, my)): board_size = 11
                    if btn_sz_13.collidepoint((mx, my)): board_size = 13
                    if btn_sz_15.collidepoint((mx, my)): board_size = 15
                    if btn_sz_17.collidepoint((mx, my)): board_size = 17

            elif state == "MENU_LOAD":
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    for i, rect in enumerate(save_file_rects):
                        if rect.collidepoint((mx, my)):
                            loaded_game = Game.load_from_file(save_files[i])
                            if loaded_game:
                                game = loaded_game
                                state = "GAME"
                        
                        if delete_file_rects[i].collidepoint((mx, my)):
                            os.remove(os.path.join("saves", save_files[i]))
                            refresh_save_list()
                
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: state = "MENU_MAIN"

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
                        game = Game(mode="AI", difficulty=selected_diff, player_role=selected_role, w=board_size, h=board_size)
                        state = "GAME"
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    state = "MENU_ROLE"


            elif state == "GAME":
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_r: game.reset()
                    if e.key == pygame.K_ESCAPE: state = "MENU_MAIN"
                    if e.key == pygame.K_z: game.undo()
                    if e.key == pygame.K_y: game.redo()
                    if e.key == pygame.K_s: 
                        if game.current_filename:
                            if game.save_to_file(game.current_filename):
                                msg_text = "Game Saved!"; msg_timer = 60
                        else:
                            state = "MENU_SAVE"
                            input_text = ""
                            save_error_msg = ""
                
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if btn_undo.collidepoint((mx, my)): game.undo()
                    elif btn_redo.collidepoint((mx, my)): game.redo()
                    elif btn_save.collidepoint((mx, my)): 
                        if game.current_filename:
                            if game.save_to_file(game.current_filename):
                                msg_text = "Game Saved!"; msg_timer = 60
                        else:
                            state = "MENU_SAVE"
                            input_text = ""
                            save_error_msg = ""
                    elif btn_load_ingame.collidepoint((mx, my)):
                        refresh_save_list()
                        state = "MENU_LOAD"
                    elif btn_menu.collidepoint((mx, my)): state = "MENU_MAIN"
                    else:
                        game.click_tile(hq, hr)

        pygame.display.flip()
        clock.tick(60)
        
    pygame.quit()