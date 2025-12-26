from utils.fbManager import FBManager
from screens.cameraScreen import CameraScreen
from screens.galleryScreen import GalleryScreen
from screens.screenManager import ScreenManager

from gpiozero import Button
import subprocess

# Create frame buffer interface class instance -> Want a single FB that is shared
fb = FBManager()
cam_screen = CameraScreen(fb)
gallery_screen = GalleryScreen(fb)
screen_manager = ScreenManager(fb, cam_screen, gallery_screen)

shutdown_button = Button(4)

try:
    while True:
        active_screen = screen_manager.get_active_screen()
        active_screen.process()
        if shutdown_button.is_pressed:
            print("Shutdown button pressed, shutting down...")
            subprocess.run(["sudo", "shutdown"])
            exit()
except KeyboardInterrupt:
    print("Exiting...")
finally:
    fb.close()