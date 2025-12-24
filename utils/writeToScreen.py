# Functions for writing to the rpi screen
import numpy as np

def write_to_screen(fb, fb_bytes):
    """Write RGB565 bytes to the framebuffer"""
    fb.seek(0)
    fb.write(fb_bytes)

def rgb24_to_rgb565(frame):
    """Convert a (H,W,3) uint8 RGB array to RGB565 bytes"""
    r = (frame[:, :, 0] >> 3).astype(np.uint16)
    g = (frame[:, :, 1] >> 2).astype(np.uint16)
    b = (frame[:, :, 2] >> 3).astype(np.uint16)
    rgb565 = (r << 11) | (g << 5) | b
    return rgb565.tobytes()