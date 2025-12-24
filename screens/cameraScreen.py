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
from utils.rpiInfo import get_cpu_temp, get_fps
from evdev import InputDevice, categorize, ecodes
import select

class CameraScreen:
    FB_PATH = "/dev/fb1"
    FB_W, FB_H = 240, 320
    BUTTON_HEIGHT = 50
    FONT = ImageFont.load_default()

    def __init__(self):
        self.picam2 = Picamera2()
        self.preview_config = self.picam2.create_preview_configuration(main={"size": (640, 480)}) # Needs to be halved again to fit display, this is smallest available
        self.capture_config = self.picam2.create_still_configuration(main={"size": (2592, 1944)})
        self.video_config = self.picam2.create_video_configuration()
        self.fb = None
        self.touch_dev = InputDevice('/dev/input/event0')
    
    def start_camera(self):
        self.fb = open(self.FB_PATH, "r+b")
        self.picam2.configure(self.preview_config)
        # self.picam2.set_controls({"FrameDurationLimits": (66666, 66666)})
        self.picam2.start()

    def stop_camera(self):
        self.fb.close()
        self.picam2.stop()
        
    def preview_camera(self):
        frame = self.picam2.capture_array()
        fb_frame = self.letterbox(frame)
        fb_frame, top_area, bottom_area = self.draw_buttons(fb_frame)
        fb_bytes = rgb24_to_rgb565(np.ascontiguousarray(fb_frame))
        write_to_screen(self.fb, fb_bytes)
        r, _, _ = select.select([self.touch_dev], [], [], 0)
        if r:
            for event in self.touch_dev.read():
                print(event)

    def letterbox(self, frame):
        h, w = frame.shape[:2]
        scale = min(self.FB_W / w, self.FB_H / h)
        new_w, new_h = int(w * scale), int(h * scale)
        resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_NEAREST)
        fb_frame = np.zeros((self.FB_H, self.FB_W, 3), dtype=np.uint8)
        x_offset = (self.FB_W - new_w) // 2
        y_offset = (self.FB_H - new_h) // 2
        fb_frame[y_offset:y_offset+new_h, x_offset:x_offset+new_w, :] = resized[:, :, :3]
        return fb_frame
    
    def draw_buttons(self, frame):
        img = Image.fromarray(frame)
        draw = ImageDraw.Draw(img)
        top_button_area = (0, 0, self.FB_W // 2, self.BUTTON_HEIGHT)
        bottom_button_area = (self.FB_W // 2, self.FB_H - self.BUTTON_HEIGHT, self.FB_W, self.FB_H)
        draw.rectangle(top_button_area, fill=(0, 0, 255))
        draw.text((5, 5), "Top", fill=(255, 255, 255))
        draw.rectangle(bottom_button_area, fill=(255, 0, 0))
        draw.text((self.FB_W//2 + 5, self.FB_H - 45), "Bottom", fill=(255, 255, 255))
        return np.array(img), top_button_area, bottom_button_area

    # def draw_ui(self, frame):
    #     """Draws UI elements and returns the new frame"""
    #     # Convert to PIL for adding UI elements
    #     img = Image.fromarray(frame)
    #     draw = ImageDraw.Draw(img)

    #     fps = get_fps()
    #     cpu_temp = get_cpu_temp()
    #     draw.text((5, 5), f"FPS: {fps:.1f}", font=self.FONT, fill=(255, 0, 0))
    #     draw.text((5, 25), f"CPU: {cpu_temp:.1f}C", font=self.FONT, fill=(255, 0, 0))

    #     # Convert back to numpy array for writing to screen
    #     return np.array(img)

    # def capture_image(self):
    #     self.picam2.switch_mode_and_capture_file(self.capture_config, get_gallery_path() / "image.jpg")

    def capture_video():
        pass