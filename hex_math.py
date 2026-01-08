"""Hexagonal grid mathematics and coordinate transformations.

This module provides utilities for converting between hexagonal grid
coordinates (axial system) and screen pixel coordinates, as well as
calculating appropriate hexagon sizes for rendering.
"""
import math

def get_hex_size(w, h, screen_w, screen_h):
    """Calculate the optimal hexagon size for fitting a grid on screen.
    
    Args:
        w: Grid width in hexagons.
        h: Grid height in hexagons.
        screen_w: Screen width in pixels.
        screen_h: Screen height in pixels.
    
    Returns:
        The maximum hexagon size (radius) that fits the grid on screen.
    """
    return min(screen_w // (w * 1.8), screen_h // (h * 1.6))

def hex_to_pixel(q, r, sz, cx, cy):
    """Convert axial hexagon coordinates to pixel coordinates.
    
    Args:
        q: Hexagon column coordinate (axial system).
        r: Hexagon row coordinate (axial system).
        sz: Hexagon size (radius).
        cx: Screen center X coordinate.
        cy: Screen center Y coordinate.
    
    Returns:
        Tuple of (x, y) pixel coordinates.
    """
    x = sz * (math.sqrt(3) * q + math.sqrt(3) / 2 * r)
    y = sz * (3 / 2 * r)
    return (int(x + cx), int(y + cy))

def pixel_to_hex(x, y, sz, cx, cy):
    """Convert pixel coordinates to axial hexagon coordinates.
    
    Args:
        x: Pixel X coordinate.
        y: Pixel Y coordinate.
        sz: Hexagon size (radius).
        cx: Screen center X coordinate.
        cy: Screen center Y coordinate.
    
    Returns:
        Tuple of (q, r) axial hexagon coordinates.
    """
    if sz == 0:
        return (0, 0)
    x, y = x - cx, y - cy
    q = (math.sqrt(3) / 3 * x - 1 / 3 * y) / sz
    r = (2 / 3 * y) / sz
    return axial_round(q, r)

def axial_round(x, y):
    """Round fractional axial coordinates to the nearest hexagon.
    
    Uses cube coordinate system internally to ensure the rounded
    coordinates represent a valid hexagon.
    
    Args:
        x: Fractional q coordinate.
        y: Fractional r coordinate.
    
    Returns:
        Tuple of (q, r) integer axial coordinates.
    """
    z = -(x + y)
    rx, ry, rz = round(x), round(y), round(z)
    dx, dy, dz = abs(rx - x), abs(ry - y), abs(rz - z)
    if dx > dy and dx > dz: rx = -(ry + rz)
    elif dy > dz: ry = -(rx + rz)
    else: rz = -(rx + ry)
    return int(rx), int(ry)
