import pygame
from constants import COLOR_BTN_NORMAL, COLOR_BTN_ACTIVE, COLOR_BTN_HOVER, COLOR_BTN_BORDER, COLOR_WHITE

def draw_button(screen, rect, text, font, mouse_pos, active=False, bg_color=None):
    if bg_color:
        color = bg_color
    else:
        base_col = COLOR_BTN_ACTIVE if active else COLOR_BTN_NORMAL
        color = COLOR_BTN_HOVER if rect.collidepoint(mouse_pos) else base_col
    
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, COLOR_BTN_BORDER, rect, 2, border_radius=8)
    txt_surf = font.render(text, True, COLOR_WHITE)
    txt_rect = txt_surf.get_rect(center=rect.center)
    screen.blit(txt_surf, txt_rect)
    return rect.collidepoint(mouse_pos)

def get_centered_rect_y(y, screen_w, w=260, h=45):
    return pygame.Rect(screen_w//2 - w//2, y, w, h)
