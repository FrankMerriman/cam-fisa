from utils.fbManager import FBManager
from screens.cameraScreen import CameraScreen
from screens.galleryScreen import GalleryScreen
from screens.screenManager import ScreenManager

# Create frame buffer interface class instance -> Want a single FB that is shared
fb = FBManager()

cam_screen = CameraScreen(fb)
gallery_screen = GalleryScreen(fb)
screen_manager = ScreenManager(fb, cam_screen, gallery_screen)


try:
    while True:
        active_screen = screen_manager.get_active_screen()
        active_screen.process()
except KeyboardInterrupt:
    print("Exiting...")
finally:
    fb.close()