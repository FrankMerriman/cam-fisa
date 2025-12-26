import utils.writeToScreen as writeToScreen
import screens.cameraScreen as cameraScreen
import screens.galleryScreen as galleryScreen
from screens.screenManager import ScreenTypes, ScreenManager

# Create frame buffer interface class instance -> Want a single FB that is shared
fb = writeToScreen.writeToScreen()

cam_screen = cameraScreen.CameraScreen(fb)
gallery_screen = galleryScreen.GalleryScreen(fb)
screen_manager = ScreenManager.ScreenManager(fb, cam_screen, gallery_screen)

try:
    while True:
        active_screen = screen_manager.get_active_screen()
        active_screen.process()
except KeyboardInterrupt:
    print("Exiting...")
finally:
    fb.close()