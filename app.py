import screens.cameraScreen as cameraScreen
import screens.galleryScreen as galleryScreen
from gpiozero import Button
import enum

class ScreenTypes(enum.Enum):
    PREVIEW = 1
    GALLERY = 2

def on_screen_button_pressed():
    global screen_button_locked
    if not screen_button_locked:
        screen_button_locked = True
        swap_screen()

def on_screen_button_released():
    global screen_button_locked
    screen_button_locked = False

def swap_screen():
    global current_screen
    if current_screen == ScreenTypes.PREVIEW:
        current_screen = ScreenTypes.GALLERY
    elif current_screen == ScreenTypes.GALLERY:
        current_screen = ScreenTypes.PREVIEW

screen_button = Button(25, bounce_time=0.05)
screen_button_locked = False

screen_button.when_pressed = on_screen_button_pressed
screen_button.when_released = on_screen_button_released

current_screen = ScreenTypes.PREVIEW # Default
cam_screen = cameraScreen.CameraScreen()
# gallery_screen = galleryScreen.GalleryScreen()

try:
    print(f"Starting Render Loop, current screen: {current_screen}")
    cam_screen.start_camera()
    while True:
            if current_screen == ScreenTypes.PREVIEW:
                cam_screen.preview_camera()
            elif current_screen == ScreenTypes.GALLERY:
                print("Switching to camera Gallery Screen")
                exit()
            
except KeyboardInterrupt:
    print("Exiting...")
finally:
    cam_screen.stop_camera()