"""User interface components and helpers.

This module provides reusable UI components for the game interface,
including button rendering and layout utilities.
"""
import pygame
from constants import COLOR_BTN_NORMAL, COLOR_BTN_ACTIVE, COLOR_BTN_HOVER, COLOR_BTN_BORDER, COLOR_WHITE

def draw_button(screen, rect, text, font, mouse_pos, active=False, bg_color=None):
    """Draw a button with hover and active state support.
    
    Args:
        screen: Pygame surface to draw on.
        rect: Pygame Rect defining button position and size.
        text: Button label text.
        font: Pygame font object for rendering text.
        mouse_pos: Tuple of (x, y) mouse coordinates.
        active: Whether the button is in active state (default False).
        bg_color: Optional custom background color (default None).
    
    Returns:
        True if mouse is over button, False otherwise.
    """
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
    """Create a horizontally centered rectangle at a given Y position.
    
    Args:
        y: Y coordinate for the rectangle.
        screen_w: Screen width used for centering.
        w: Rectangle width (default 260).
        h: Rectangle height (default 45).
    
    Returns:
        Pygame Rect centered horizontally at the given Y position.
    """
    return pygame.Rect(screen_w//2 - w//2, y, w, h)
