# This file lays out the functionality of the gallery screen.
# It shows previously capture images @ 320x240 with the ability to scroll left to right
# You can also zoom in and out of images. Zooming out far enough displays a grid of multiple images.
from utils.mountUSB import mount_usb
from gpiozero import Button

class GalleryScreen:
    FB_PATH = "/dev/fb0"
    FB_W, FB_H = 240, 320

    def __init__(self):
        # Once I have a function for it, do a check for USB mount
        # For now we can assume it is working
        self.right_button = Button(24, bounce_time=0.05)  # small debounce
        self.left_button = Button(23, bounce_time=0.05)  # small debounce
        self.gallery_path = mount_usb() / "gallery"
        self.images = []
        
    def load_gallery_images(self):
        for img_file in self.gallery_path.glob("*.jpg"):
            if img_file not in self.images:
                self.images.append(img_file)

    def show_gallery(self):
        modulo = len(self.images)
        index = len(self.images) - 1  # Start at the most recent image
        while True:
            if modulo == 0:
                print("No images in gallery.")
                break

            current_image_path = self.images[index % modulo]
            print(f"Displaying image: {current_image_path}")
            # fb_bytes = rgb24_to_rgb565(np.ascontiguousarray(fb_frame))
            # write_to_screen(self.fb, fb_bytes)


            # Wait for button press to navigate
            if self.right_button.is_pressed:
                index += 1
            elif self.left_button.is_pressed:
                index -= 1