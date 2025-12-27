# This file lays out the functionality of the main camera screen
# It has a live feed of what the module sees + some light UI elements
# to use the touch screen to interact with the camera and its quick menu options
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
from picamera2 import Picamera2
from utils.rpiInfo import get_cpu_temp, get_fps
from utils.mountUSB import mount_usb
from gpiozero import Button
from screens.screen import Screen
from enum import Enum
import cv2

class FilterType(Enum):
    NONE = 0
    DEBUG = 1
    INVERT = 2
    GRAYSCALE = 3
    SEPIA = 4
    SOLARIZE = 5
    POSTERIZE = 6
    SCANLINES = 7
    NOISE = 8
    MIRROR = 9

class CameraScreen(Screen):
    FONT = ImageFont.load_default()
    
    def __init__(self, fb):
        self.picam2 = Picamera2()
        self.preview_config = self.picam2.create_preview_configuration(
            main={"size": (640, 480)}, # Has to be halved to fit display
            controls={
                "FrameDurationLimits": (40000, 40000)  # cap at 25 FPS, might help temps
            }
        )
        self.capture_config = self.picam2.create_still_configuration(main={"size": (2592, 1944)})
        self.fb = fb
        self.button = Button(26, bounce_time=0.05)  # small debounce
        self.button_locked = False  # lock flag

        self.debug_button = Button(4, bounce_time=0.05)  # GPIO4 for debug - prints temp + FPS
        self.debug_button_locked = False
        self.debug = False

        self.filter_types = list(FilterType)
        self.filter_index = 0
        self.current_filter = self.filter_types[self.filter_index]
        
        self.usb_path = mount_usb()
        if self.usb_path:
            self.gallery_path = self.usb_path / "gallery"
            self.gallery_path.mkdir(exist_ok=True)
        else:
            raise RuntimeError("No USB drive found. Cannot create gallery.")
        
        print("Initialized Camera Screen")

    def on_button_pressed(self):
        if not self.button_locked:
            self.button_locked = True
            self.capture_image()

    def on_button_released(self):
        self.button_locked = False


    def on_debug_button_pressed(self):
        if not self.debug_button_locked:
            self.debug_button_locked = True

            self.filter_index = (self.filter_index + 1) % len(self.filter_types) #Loops through filters
            self.current_filter = self.filter_types[self.filter_index]

            print(f"Filter changed to: {self.current_filter.name}")
    
    def on_debug_button_released(self):
        self.debug_button_locked = False

    def stop_camera(self):
        self.picam2.stop()
        
    def process(self):
        # If shutter is released, release the lock on further photos
        if self.button_locked and not self.button.is_pressed:
            self.on_button_released()
        # If button is pressed and not locked, take photo
        if self.button.is_pressed:
            self.on_button_pressed()
        
        # If debug button is released, release the lock
        if self.debug_button_locked and not self.debug_button.is_pressed:
            self.on_debug_button_released()
        # If debug button is pressed and not locked, toggle debug
        if self.debug_button.is_pressed:
            self.on_debug_button_pressed()
        
        frame = self.picam2.capture_array()
        fb_frame = self.fb.letterbox(frame)
        fb_frame = self.apply_filter(fb_frame)
        fb_bytes = self.fb.rgb24_to_rgb565(np.ascontiguousarray(fb_frame))
        self.fb.write_to_screen(fb_bytes)

    def draw_ui(self, frame):
        """Draws UI elements and returns the new frame"""
        # Convert to PIL for adding UI elements
        img = Image.fromarray(frame)
        # Create a transparent layer for text

        draw = ImageDraw.Draw(img)

        fps = get_fps()
        cpu_temp = get_cpu_temp()
        draw.text((5, 5), f"FPS: {fps:.1f}", font=self.FONT, fill=(255, 0, 0))
        draw.text((5, 25), f"CPU: {cpu_temp:.1f}C", font=self.FONT, fill=(255, 0, 0))

        # Convert back to numpy array for writing to screen
        return np.array(img)

    def capture_image(self):
        # Need to add a cache to start _1 from to stop counting from start very time
        file_name = "CAMFISA_0.jpg"
        path = self.gallery_path / file_name
        counter = 1
        while path.exists():
            file_name = f"CAMFISA_{counter}.jpg"
            path = self.gallery_path / file_name
            counter += 1

        print(f"Capturing image to {path}")
        self.picam2.switch_mode_and_capture_file(self.capture_config, path)
        # Account for sensor rotation
        image = Image.open(path)
        image = image.transpose(Image.ROTATE_90)
        if self.current_filter in (FilterType.POSTERIZE, FilterType.SCANLINES):
            # Convert to numpy
            arr = np.array(image)
            h, w = arr.shape[:2]

             # Determine scale for pixelation
            scale = 0.1 if self.current_filter == FilterType.POSTERIZE else 0.5

            # Downscale → Upscale
            small = cv2.resize(arr, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_NEAREST)
            arr = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)

            # Convert back to PIL
            image = Image.fromarray(arr)

        image = self.apply_filter_to_image(image)
        image.save(path)
    
    def load_screen(self):
        print("Loading camera screen")
        self.picam2.configure(self.preview_config)
        self.picam2.start()
    
    def apply_filter(self, frame: np.ndarray) -> np.ndarray:
        f = self.current_filter

        if f == FilterType.NONE:
            return frame

        elif f == FilterType.DEBUG:
            return self.draw_ui(frame)

        elif f == FilterType.INVERT:
            return 255 - frame

        elif f == FilterType.GRAYSCALE:
            gray = frame.mean(axis=2).astype(np.uint8)
            return np.stack([gray] * 3, axis=2)

        elif f == FilterType.SEPIA:
            sepia = frame.astype(np.float32)
            r, g, b = sepia[..., 0], sepia[..., 1], sepia[..., 2]
            sepia[..., 0] = 0.393*r + 0.769*g + 0.189*b
            sepia[..., 1] = 0.349*r + 0.686*g + 0.168*b
            sepia[..., 2] = 0.272*r + 0.534*g + 0.131*b
            return np.clip(sepia, 0, 255).astype(np.uint8)

        elif f == FilterType.SOLARIZE:
            return np.where(frame > 128, 255 - frame, frame)

        elif f == FilterType.POSTERIZE:
            return (frame // 64) * 64

        elif f == FilterType.SCANLINES:
            frame = frame.copy()
            frame[::2] = (frame[::2] * 0.6).astype(np.uint8)
            return frame

        elif f == FilterType.NOISE:
            noise = np.random.randint(0, 20, frame.shape, dtype=np.uint8)
            return np.clip(frame + noise, 0, 255)

        elif f == FilterType.MIRROR:
            return frame[:, ::-1]

        return frame

    def apply_filter_to_image(self, img: Image.Image) -> Image.Image:
        arr = np.array(img)
        filtered = self.apply_filter(arr)
        return Image.fromarray(filtered)