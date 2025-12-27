# This file lays out the functionality of the gallery screen.
# It shows previously capture images @ 320x240 with the ability to scroll left to right
# You can also zoom in and out of images. Zooming out far enough displays a grid of multiple images.
from utils.mountUSB import mount_usb
from screens.screen import Screen
from gpiozero import Button
from PIL import Image
import numpy as np

class GalleryScreen(Screen):
    def __init__(self, fb):
        # Once I have a function for it, do a check for USB mount
        # For now we can assume it is working
        self.right_button = Button(24, bounce_time=0.05)  # 24
        self.left_button = Button(23, bounce_time=0.05)  # 23
        # These locks are activated when button is pressed. They release when button is not pressed.
        # Prevents triggering an index increment every loop while button is held down (way too fast)
        self.right_button_lock = False
        self.left_button_lock = False
        self.gallery_path = mount_usb() / "gallery"
        self.images = []
        self.gallery_lock = False
        self.fb = fb
        self.index = 0

    def release_gallery_lock(self):
        self.gallery_lock = False

    def on_right_button_pressed(self):
        print("Right button pressed")
        self.right_button_lock = True
        self.release_gallery_lock()
        self.index += 1

    def on_left_button_pressed(self):
        print("Left button pressed")
        self.left_button_lock = True
        self.release_gallery_lock()
        self.index -= 1
    
    def on_right_button_released(self):
        self.right_button_lock = False
    
    def on_left_button_released(self):
        self.left_button_lock = False
        
    def load_gallery_images(self):
        for img_file in self.gallery_path.glob("*.jpg"):
            if img_file not in self.images:
                self.images.append(img_file)
        self.modulo = len(self.images)
        self.index = len(self.images) - 1  # Start at the most recent image

    def process(self):
        # print("Processing gallery frame")

        # If button is released, release the lock
        if self.right_button_lock and not self.right_button.is_pressed:
            self.on_right_button_released()
        if self.left_button_lock and not self.left_button.is_pressed:
            self.on_left_button_released()

        # If button is pressed and not locked, process the press
        if not self.right_button_lock and self.right_button.is_pressed:
            self.on_right_button_pressed()
        elif not self.left_button_lock and self.left_button.is_pressed:
            self.on_left_button_pressed()

        # Gallery lock prevents re-processing the same image multiple times
        # Is released by index increment
        if self.gallery_lock == False:
            self.gallery_lock = True

            if self.modulo == 0:
                print("No images in gallery.")
                return

            current_image_path = self.images[self.index % self.modulo]
            print(f"Displaying image: {current_image_path}")

            try:
                img = Image.open(current_image_path)
                img.convert("RGB")
                fb_frame = np.asarray(img, dtype=np.uint8)
                fb_frame = self.fb.letterbox(fb_frame)
                fb_bytes = self.fb.rgb24_to_rgb565(np.ascontiguousarray(fb_frame))
                self.fb.write_to_screen(fb_bytes)
            except Exception as e:
                print(f"Error loading image {current_image_path}: {e}")

    # Makes sure vars that are needed when screen is swapped to are available
    def load_screen(self):
        print("Loading gallery screen")
        self.load_gallery_images()
        self.release_gallery_lock()
