# Functions for writing to the rpi screen
import numpy as np
import cv2

class FBManager:
    """Framebuffer manager to handle opening and closing the framebuffer device"""
    def __init__(self, fb_path="/dev/fb0"):
        self.fb = open(fb_path, "r+b")
        self.width = 240
        self.height = 320

    def close(self):
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
    
    def letterbox(self, frame):
        h, w = frame.shape[:2]
        scale = min(self.width / w, self.height / h)
        new_w, new_h = int(w * scale), int(h * scale)
        resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_NEAREST)
        fb_frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        x_offset = (self.width - new_w) // 2
        y_offset = (self.height - new_h) // 2
        fb_frame[y_offset:y_offset+new_h, x_offset:x_offset+new_w, :] = resized[:, :, :3]
        return fb_frame