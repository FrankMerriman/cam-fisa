# This file lays out the functionality of the gallery screen.
# It shows previously capture images @ 320x240 with the ability to scroll left to right
# You can also zoom in and out of images. Zooming out far enough displays a grid of multiple images.
from utils.mountUSB import mount_usb
from screens.screen import Screen
from gpiozero import Button

class GalleryScreen(Screen):
    def __init__(self, fb):
        # Once I have a function for it, do a check for USB mount
        # For now we can assume it is working
        self.right_button = Button(24, bounce_time=1)  # 24
        self.left_button = Button(23, bounce_time=1)  # 23
        self.gallery_path = mount_usb() / "gallery"
        self.images = []
        self.gallery_lock = False
        self.fb = fb
        self.index = 0

    def on_right_button_pressed(self):
        print("Right button pressed")
        self.gallery_lock = False
        self.index += 1

    def on_left_button_pressed(self):
        print("Left button pressed")
        self.gallery_lock = False
        self.index -= 1
        
    def load_gallery_images(self):
        for img_file in self.gallery_path.glob("*.jpg"):
            if img_file not in self.images:
                self.images.append(img_file)
        self.modulo = len(self.images)
        self.index = len(self.images) - 1  # Start at the most recent image

    def process(self):
        print("Processing gallery frame")
        if self.right_button.is_pressed:
            self.on_right_button_pressed()
        elif self.left_button.is_pressed:
            self.on_left_button_pressed()

        
        if self.gallery_lock == False:
            self.gallery_lock = True

            if self.modulo == 0:
                print("No images in gallery.")
                return

            current_image_path = self.images[self.index % self.modulo]
            print(f"Displaying image: {current_image_path}")
        # fb_bytes = rgb24_to_rgb565(np.ascontiguousarray(fb_frame))
        # write_to_screen(self.fb, fb_bytes)
