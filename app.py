import screens.cameraScreen as cameraScreen
import screens.galleryScreen as galleryScreen
import utils.writeToScreen as writeToScreen
from gpiozero import Button
import enum

class ScreenTypes(enum.Enum):
    PREVIEW = 1
    GALLERY = 2

def on_screen_button_pressed():
    global screen_button_locked
    if not screen_button_locked:
        screen_button_locked = True
        print("Screen button pressed, swapping screens")
        print(f"screen_button_locked: {screen_button_locked}")
        swap_screen()

def on_screen_button_released():
    global screen_button_locked
    screen_button_locked = False

def swap_screen():
    global current_screen
    global cam_screen
    global gallery_screen

    if current_screen == ScreenTypes.PREVIEW:
        print("Switching to Gallery Screen")
        cam_screen.stop_camera()
        gallery_screen.load_gallery_images()
        current_screen = ScreenTypes.GALLERY
    elif current_screen == ScreenTypes.GALLERY:
        print("Switching to Camera Preview Screen")
        cam_screen.start_camera()
        current_screen = ScreenTypes.PREVIEW

screen_button = Button(25, bounce_time=0.05)
screen_button_locked = False
screen_button.when_pressed = on_screen_button_pressed
screen_button.when_released = on_screen_button_released

fb = writeToScreen.writeToScreen() # Framebuffer manager, need to pass to screens
current_screen = ScreenTypes.PREVIEW # Default
cam_screen = cameraScreen.CameraScreen(fb)
gallery_screen = galleryScreen.GalleryScreen(fb)

try:
    print(f"Starting Render Loop, current screen: {current_screen}")
    cam_screen.start_camera()
    while True:
            if current_screen == ScreenTypes.PREVIEW:
                cam_screen.preview_camera()
            elif current_screen == ScreenTypes.GALLERY:
                gallery_screen.show_image()
            
except KeyboardInterrupt:
    print("Exiting...")
finally:
    fb.close()