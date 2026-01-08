import math

def get_hex_size(w, h, screen_w, screen_h):
    return min(screen_w // (w * 1.8), screen_h // (h * 1.6))

def hex_to_pixel(q, r, sz, cx, cy):
    x = sz * (math.sqrt(3) * q + math.sqrt(3) / 2 * r)
    y = sz * (3 / 2 * r)
    return (int(x + cx), int(y + cy))

def pixel_to_hex(x, y, sz, cx, cy):
    if sz == 0:
        return (0, 0)
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
