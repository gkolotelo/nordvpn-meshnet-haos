#!/usr/bin/env python3
"""Generate professional-looking icon.png and logo.png for the NordVPN Meshnet HA add-on."""

import struct
import zlib
import math
import os

def create_png(width, height, draw_func, filename):
    """Create a PNG file from a draw function."""
    raw_data = b''
    for y in range(height):
        raw_data += b'\x00'  # filter byte
        for x in range(width):
            r, g, b = draw_func(x, y, width, height)
            raw_data += bytes([r, g, b])
    
    compressed = zlib.compress(raw_data)
    
    signature = b'\x89PNG\r\n\x1a\n'
    
    # IHDR chunk
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data)
    ihdr = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)
    
    # IDAT chunk
    idat_crc = zlib.crc32(b'IDAT' + compressed)
    idat = struct.pack('>I', len(compressed)) + b'IDAT' + compressed + struct.pack('>I', idat_crc)
    
    # IEND chunk
    iend_crc = zlib.crc32(b'IEND')
    iend = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)
    
    with open(filename, 'wb') as f:
        f.write(signature + ihdr + idat + iend)

def draw_circle(cx, cy, radius, x, y):
    """Draw a filled circle. Returns (r, g, b) if pixel is inside circle, else None."""
    dist = math.sqrt((x - cx)**2 + (y - cy)**2)
    if dist <= radius:
        return (78, 204, 163)  # meshnet green
    return None

def draw_line(x1, y1, x2, y2, x, y, thickness=2):
    """Draw a line. Returns (r, g, b) if pixel is on line, else None."""
    if x2 == x1:  # vertical line
        if abs(x - x1) <= thickness and y1 <= y <= y2:
            return (78, 204, 163)
        return None
    
    m = (y2 - y1) / (x2 - x1)
    y_on_line = y1 + m * (x - x1)
    
    if abs(y - y_on_line) <= thickness:
        return (78, 204, 163)
    return None

def meshnet_icon(x, y, w, h):
    """Create a shield-shaped icon with VPN symbol."""
    cx, cy = w/2, h/2
    r = w/2.5
    
    # Draw shield (circle)
    shield_color = draw_circle(cx, cy, r, x, y)
    if shield_color:
        # Draw VPN text/shield symbol inside
        # Draw a simple "shield" outline inside
        inner_r = r * 0.7
        
        # Shield shape (simplified as circle with triangle on top)
        # Draw "VPN" text as simple blocks
        # For simplicity, draw a simple "V" shape
        if y > cy - inner_r and y < cy + inner_r:
            # Draw "V" shape
            left_x = cx - inner_r * 0.6
            right_x = cx + inner_r * 0.6
            top_y = cy - inner_r * 0.5
            
            # Left arm of V
            if abs(x - (left_x + (cx - left_x) * (y - top_y) / (cy - top_y))) < 3:
                return (255, 255, 255)  # white V
            
            # Right arm of V
            if abs(x - (right_x - (right_x - cx) * (y - top_y) / (cy - top_y))) < 3:
                return (255, 255, 255)  # white V
        
        # Draw horizontal line (base of shield)
        if abs(y - (cy + inner_r * 0.3)) < 2:
            if cx - inner_r * 0.5 <= x <= cx + inner_r * 0.5:
                return (255, 255, 255)  # white base line
        
        return (78, 204, 163)  # meshnet green (shield fill)
    
    # Background (dark blue gradient)
    brightness = int(26 + (x / w) * 10)  # subtle gradient
    return (brightness, brightness + 16, brightness + 68)

def meshnet_logo(x, y, w, h):
    """Create a meshnet network diagram logo."""
    bg_r, bg_g, bg_b = 26, 42, 94
    
    # Define network nodes (central HA + 3 peers)
    nodes = [
        (w//2, h//2),      # HA (center)
        (w//4, h//4),      # Peer 1 (top-left)
        (3*w//4, h//4),    # Peer 2 (top-right)
        (w//2, 3*h//4),    # Peer 3 (bottom)
    ]
    
    # Draw connections (lines between nodes)
    for i, (x1, y1) in enumerate(nodes):
        for x2, y2 in nodes[i+1:]:
            # Draw line between nodes
            if x2 == x1:  # vertical line
                if abs(x - x1) <= 3 and min(y1, y2) <= y <= max(y1, y2):
                    return (78, 204, 163)  # meshnet green
            else:
                m = (y2 - y1) / (x2 - x1)
                y_on_line = y1 + m * (x - x1)
                if abs(y - y_on_line) <= 3 and min(x1, x2) <= x <= max(x1, x2):
                    return (78, 204, 163)  # meshnet green
    
    # Draw nodes (circles)
    for i, (nx, ny) in enumerate(nodes):
        dist = math.sqrt((x - nx)**2 + (y - ny)**2)
        if dist <= 30:  # node radius
            if i == 0:  # HA node (larger, white)
                return (255, 255, 255)
            else:  # Peer nodes (green)
                return (78, 204, 163)
    
    # Draw "HA" text in center (simplified as blocks)
    if 0.4*w < x < 0.6*w and 0.45*h < y < 0.55*h:
        return (255, 255, 255)  # white text
    
    # Draw "Meshnet" text at bottom (simplified)
    if 0.3*w < x < 0.7*w and 0.85*h < y < 0.9*h:
        return (78, 204, 163)  # green text
    
    return (bg_r, bg_g, bg_b)  # dark background

if __name__ == '__main__':
    project_path = '/home/gkolotelo/projects/nordvpn_hacs/meshnet'
    
    create_png(512, 512, meshnet_icon, os.path.join(project_path, 'icon.png'))
    create_png(512, 512, meshnet_logo, os.path.join(project_path, 'logo.png'))
    
    print("Generated icon.png and logo.png")
    
    # Verify files
    for f in ['icon.png', 'logo.png']:
        path = os.path.join(project_path, f)
        size = os.path.getsize(path)
        print(f"  {f}: {size} bytes")
