# This file lays out the functionality of the gallery screen.
# It shows previously capture images @ 320x240 with the ability to scroll left to right
# You can also zoom in and out of images. Zooming out far enough displays a grid of multiple images.
from utils.mountUSB import mount_usb
from gpiozero import Button

class GalleryScreen:
    def __init__(self):
        self.usb_path = mount_usb()
        if self.usb_path:
            self.gallery_path = self.usb_path / "gallery"
            self.gallery_path.mkdir(exist_ok=True)
        else:
            raise RuntimeError("No USB drive found. Cannot create gallery.")
        
        self.right_button = Button(24, bounce_time=0.05)  # small debounce
        self.left_button = Button(23, bounce_time=0.05)  # small debounce
        