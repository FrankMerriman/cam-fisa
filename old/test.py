import time
import os
import mmap
import numpy as np
from picamera2 import Picamera2
from PIL import Image, ImageDraw, ImageFont
from gpiozero import Button
from signal import pause

button = Button(26)  # BCM numbering

# --- Initialize camera ---
picam2 = Picamera2()
preview_config = picam2.create_preview_configuration(main={"size": (640, 480)}, transform=Picamera2.Transform(rotation=90))
capture_config = picam2.create_still_configuration(transform=Picamera2.Transform(rotation=90) )
picam2.configure(preview_config)
picam2.set_controls({"FrameDurationLimits": (66666, 66666)})
picam2.start()

# --- Framebuffer setup ---
FB_PATH = "/dev/fb1"
WIDTH, HEIGHT = 320, 240          # framebuffer resolution
FB_BYTES = WIDTH * HEIGHT * 2      # RGB565 = 2 bytes per pixel

fb_fd = os.open(FB_PATH, os.O_RDWR)
fb = mmap.mmap(fb_fd, FB_BYTES, mmap.MAP_SHARED, mmap.PROT_WRITE | mmap.PROT_READ)

def rgb24_to_rgb565(frame):
    """Convert a (H,W,3) uint8 RGB array to RGB565 bytes"""
    r = (frame[:, :, 0] >> 3).astype(np.uint16)
    g = (frame[:, :, 1] >> 2).astype(np.uint16)
    b = (frame[:, :, 2] >> 3).astype(np.uint16)
    rgb565 = (r << 11) | (g << 5) | b
    return rgb565.tobytes()

def get_cpu_temp():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp_milli = int(f.read())
    return temp_milli / 1000.0  # convert to °C

def shutter_pressed(channel):
    print("Capture button pressed!")
    capture_config = picam2.create_still_configuration(main={"size": (2592, 1944)})
    picam2.switch_mode_and_capture_file(capture_config, "image.jpg")

font = ImageFont.load_default()
prev_time = time.time()
fps = 0
button.when_pressed = shutter_pressed
try:
    while True:
        # Capture frame
        frame = picam2.capture_array()
        
        # Scale down to framebuffer size
        small_frame = frame[::2, ::2, :]  # 640x480 -> 320x240
        
        # Convert to PIL image for drawing
        img = Image.fromarray(small_frame)
        draw = ImageDraw.Draw(img)
        
        # Compute FPS
        now = time.time()
        fps = 1 / (now - prev_time)
        prev_time = now
        
        # Draw FPS and CPU temp
        cpu_temp = get_cpu_temp()
        draw.text((5, 5), f"FPS: {fps:.1f}", font=font, fill=(255, 0, 0))
        draw.text((5, 25), f"CPU: {cpu_temp:.1f}C", font=font, fill=(255, 0, 0))
        
        # Convert back to numpy array
        small_frame = np.array(img)
        
        # Convert to RGB565
        fb_bytes = rgb24_to_rgb565(small_frame)
        
        # Write to framebuffer
        fb.seek(0)
        fb.write(fb_bytes)
        # No sleep, continuous write
except KeyboardInterrupt:
    pass
finally:
    fb.close()
    os.close(fb_fd)
    picam2.stop()