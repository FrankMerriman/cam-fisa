import screens.cameraScreen as cameraScreen
import screens.galleryScreen as galleryScreen
import enum
from gpiozero import Button

class ScreenTypes(enum.Enum):
    PREVIEW = 1
    GALLERY = 2

class ScreenManager:
    def __init__(self, fb, cam_screen, gallery_screen):
        self.fb = fb
        self.screen_button = Button(25, bounce_time=0.05)
        self.screen_button_locked = False
        self.screen_button.when_pressed = self.on_screen_button_pressed
        self.screen_button.when_released = self.on_screen_button_released
        self.cam_screen = cam_screen
        self.gallery_screen = gallery_screen

        self.active_screen = cam_screen
        cam_screen.start_camera()
        
    def on_screen_button_pressed(self):
        if not self.screen_button_locked:
            self.screen_button_locked = True
            print("Screen button pressed, swapping screens")
            self.swap_screen()

    def on_screen_button_released(self):
        self.screen_button_locked = False

    def swap_screen(self):
        if self.active_screen == self.cam_screen:
            print("Switching to Gallery Screen")
            self.cam_screen.stop_camera()
            self.gallery_screen.load_gallery_images()
            self.active_screen = self.gallery_screen
        elif self.active_screen == self.gallery_screen:
            print("Switching to Camera Preview Screen")
            self.cam_screen.start_camera()
            self.active_screen = self.cam_screen

    def get_active_screen(self):
        return self.active_screen