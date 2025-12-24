# This file lays out the functionality of the main camera screen
# It has a live feed of what the module sees + some light UI elements
# to use the touch screen to interact with the camera and its quick menu options
import os
import mmap
import numpy as np
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
        frame = self.picam2.capture_array()
        small_frame = frame[::2, ::2, :]  # 640x480 -> 320x240
        rot_frame = np.rot90(small_frame, k=1)
        rot_frame = np.ascontiguousarray(rot_frame)
        rot_frame = rot_frame[:240, :320, :]

        ui_frame = self.draw_ui(rot_frame)
        
        print(ui_frame.shape, ui_frame.dtype, ui_frame.flags['C_CONTIGUOUS'])
        
        fb_bytes = rgb24_to_rgb565(ui_frame)
        write_to_screen(self.fb, fb_bytes)
    
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