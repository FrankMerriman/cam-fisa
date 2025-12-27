# This file lays out the functionality of the main camera screen
# It has a live feed of what the module sees + some light UI elements
# to use the touch screen to interact with the camera and its quick menu options
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from picamera2 import Picamera2
from utils.rpiInfo import get_cpu_temp, get_fps
from utils.mountUSB import mount_usb
from gpiozero import Button
from screens.screen import Screen

class CameraScreen(Screen):
    FONT = ImageFont.load_default()
    
    def __init__(self, fb):
        self.picam2 = Picamera2()
        self.preview_config = self.picam2.create_preview_configuration(
            main={"size": (640, 480)}, # Has to be halved to fit display
            controls={
                "FrameDurationLimits": (40000, 40000)  # cap at 25 FPS, might help temps
            }
        )
        self.capture_config = self.picam2.create_still_configuration(main={"size": (2592, 1944)})
        self.fb = fb
        self.button = Button(26, bounce_time=0.05)  # small debounce
        self.button_locked = False  # lock flag

        self.debug_button = Button(4, bounce_time=0.05)  # GPIO4 for debug - prints temp + FPS
        self.debug_button_locked = False
        self.debug = False
        
        self.usb_path = mount_usb()
        if self.usb_path:
            self.gallery_path = self.usb_path / "gallery"
            self.gallery_path.mkdir(exist_ok=True)
        else:
            raise RuntimeError("No USB drive found. Cannot create gallery.")
        
        print("Initialized Camera Screen")

    def on_button_pressed(self):
        if not self.button_locked:
            self.button_locked = True
            self.capture_image()

    def on_button_released(self):
        self.button_locked = False


    def on_debug_button_pressed(self):
        if not self.debug_button_locked:
            self.debug_button_locked = True
            self.debug = not self.debug # Swap state back and forth on each press
    
    def on_debug_button_released(self):
        self.debug_button_locked = False

    def stop_camera(self):
        self.picam2.stop()
        
    def process(self):
        # If shutter is released, release the lock on further photos
        if self.button_locked and not self.button.is_pressed:
            self.on_button_released()
        # If button is pressed and not locked, take photo
        if self.button.is_pressed:
            self.on_button_pressed()
        
        # If debug button is released, release the lock
        if self.debug_button_locked and not self.debug_button.is_pressed:
            self.on_debug_button_released()
        # If debug button is pressed and not locked, toggle debug
        if self.debug_button.is_pressed:
            self.on_debug_button_pressed()
        
        frame = self.picam2.capture_array()
        fb_frame = self.fb.letterbox(frame)
        if self.debug:
            fb_frame = self.draw_ui(fb_frame)
        fb_bytes = self.fb.rgb24_to_rgb565(np.ascontiguousarray(fb_frame))
        self.fb.write_to_screen(fb_bytes)

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
        # Need to add a cache to start _1 from to stop counting from start very time
        file_name = "CAMFISA_0.jpg"
        path = self.gallery_path / file_name
        counter = 1
        while path.exists():
            file_name = f"CAMFISA_{counter}.jpg"
            path = self.gallery_path / file_name
            counter += 1

        print(f"Capturing image to {path}")
        self.picam2.switch_mode_and_capture_file(self.capture_config, path)
        # Account for sensor rotation
        image = Image.open(path)
        image = image.transpose(Image.ROTATE_90)
        image.save(path)
    
    def load_screen(self):
        print("Loading camera screen")
        self.picam2.configure(self.preview_config)
        self.picam2.start()