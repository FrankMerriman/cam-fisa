# This file lays out the functionality of the main camera screen
# It has a live feed of what the module sees + some light UI elements
# to use the touch screen to interact with the camera and its quick menu options
import os
import mmap
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
from picamera2 import Picamera2
from utils.writeToScreen import write_to_screen, rgb24_to_rgb565
from utils.rpiInfo import get_cpu_temp, get_fps, get_gallery_path

class CameraScreen:
    FB_PATH = "/dev/fb1"
    WIDTH, HEIGHT = 320, 240          # framebuffer resolution
    FB_BYTES = WIDTH * HEIGHT * 2      # RGB565 = 2 bytes per pixel
    FONT = ImageFont.load_default()

    def __init__(self):
        self.picam2 = Picamera2()
        self.preview_config = self.picam2.create_preview_configuration(main={"size": (640, 480)}) # Needs to be halved again to fit display, this is smallest available
        self.capture_config = self.picam2.create_still_configuration(main={"size": (2592, 1944)})
        self.video_config = self.picam2.create_video_configuration()
    
    def start_camera(self):
        # Sets up frame buffer for drawing to screen, feel like this should go elesewhere
        self.fb_fd = os.open(self.FB_PATH, os.O_RDWR)
        self.fb = mmap.mmap(self.fb_fd, self.FB_BYTES, mmap.MAP_SHARED, mmap.PROT_WRITE | mmap.PROT_READ)

        self.picam2.configure(self.preview_config)
        self.picam2.set_controls({"FrameDurationLimits": (66666, 66666)})
        self.picam2.start()

    def stop_camera(self):
        self.fb.close()
        os.close(self.fb_fd)
        self.picam2.stop()
        
    def preview_camera(self):
        frame = self.picam2.capture_array()  # 640x480
        print(f"frame: {frame.shape}")

        # TFT size
        FB_W, FB_H = 240, 320

        # Choose one of these two (comment/uncomment to test)
        # crop_frame = self.crop_center(frame, FB_W, FB_H)
        crop_frame = self.letterbox(frame, FB_W, FB_H)
        
        print(f"processed frame: {crop_frame.shape}")

        small_frame = cv2.resize(crop_frame, (FB_W, FB_H), interpolation=cv2.INTER_NEAREST)
        print(f"small frame: {small_frame.shape}")

        fb_frame = np.ascontiguousarray(small_frame[:, :, :3])
        print(f"fb frame: {fb_frame.shape}")

        fb_bytes = rgb24_to_rgb565(fb_frame)
        write_to_screen(self.fb, fb_bytes)

    def crop_center(self, frame, target_w, target_h):
        h, w = frame.shape[:2]
        cam_ratio = w / h
        tft_ratio = target_w / target_h

        if cam_ratio > tft_ratio:
            # Camera is wider → crop left/right
            new_w = int(h * tft_ratio)
            x_start = (w - new_w) // 2
            return frame[:, x_start:x_start + new_w, :]
        else:
            # Camera is taller → crop top/bottom
            new_h = int(w / tft_ratio)
            y_start = (h - new_h) // 2
            return frame[y_start:y_start + new_h, :, :]

    def letterbox(self, frame, target_w, target_h):
        h, w = frame.shape[:2]

        scale_w = target_w / w
        scale_h = target_h / h
        scale = min(scale_w, scale_h)

        new_w = int(w * scale)
        new_h = int(h * scale)

        # Resize
        resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_NEAREST)

        # Black canvas
        fb_frame = np.zeros((target_h, target_w, 3), dtype=np.uint8)

        # Center the image
        x_offset = (target_w - new_w) // 2
        y_offset = (target_h - new_h) // 2
        fb_frame[y_offset:y_offset+new_h, x_offset:x_offset+new_w, :] = resized[:, :, :3]

        return fb_frame
    
    def draw_ui(self, frame):
        """Draws UI elements and returns the new frame"""
        # Convert to PIL for adding UI elements
        img = Image.fromarray(frame)
        draw = ImageDraw.Draw(img)

        fps = get_fps()
        cpu_temp = get_cpu_temp()
        draw.text((5, 5), f"FPS: {fps:.1f}", font=self.FONT, fill=(255, 0, 0))
        draw.text((5, 25), f"CPU: {cpu_temp:.1f}C", font=self.FONT, fill=(255, 0, 0))

        # Convert back to numpy array for writing to screen
        return np.array(img)

    def capture_image(self):
        self.picam2.switch_mode_and_capture_file(self.capture_config, get_gallery_path() / "image.jpg")

    def capture_video():
        pass