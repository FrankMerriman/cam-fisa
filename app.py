from utils.fbManager import FBManager
from screens.cameraScreen import CameraScreen
from screens.galleryScreen import GalleryScreen
from screens.screenManager import ScreenManager
from gpiozero import Button

right_button = Button(24, bounce_time=1)  # small debounce
left_button = Button(23, bounce_time=1)  # small debounce

# Create frame buffer interface class instance -> Want a single FB that is shared
fb = FBManager()
cam_screen = CameraScreen(fb)
gallery_screen = GalleryScreen(fb)
screen_manager = ScreenManager(fb, cam_screen, gallery_screen)

try:
    while True:
        active_screen = screen_manager.get_active_screen()
        active_screen.process()
        if right_button.is_pressed:
            print("Right")
        if left_button.is_pressed:
            print("Left")
except KeyboardInterrupt:
    print("Exiting...")
finally:
    fb.close()