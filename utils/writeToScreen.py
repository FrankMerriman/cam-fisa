# Functions for writing to the rpi screen
import numpy as np

class writeToScreen:
    """Framebuffer manager to handle opening and closing the framebuffer device"""
    def __init__(self, fb_path="/dev/fb0"):
        self.fb_path = fb_path
        self.fb = None

    def __enter__(self):
        self.fb = open(self.fb_path, "wb")
        return self.fb

    def __exit__(self, exc_type, exc_value, traceback):
        if self.fb:
            self.fb.close()

    def write_to_screen(self, fb_bytes):
        """Write RGB565 bytes to the framebuffer"""
        self.fb.seek(0)
        self.fb.write(fb_bytes)

    def rgb24_to_rgb565(self, frame):
        """Convert a (H,W,3) uint8 RGB array to RGB565 bytes"""
        r = (frame[:, :, 0] >> 3).astype(np.uint16)
        g = (frame[:, :, 1] >> 2).astype(np.uint16)
        b = (frame[:, :, 2] >> 3).astype(np.uint16)
        rgb565 = (r << 11) | (g << 5) | b
        return rgb565.tobytes()