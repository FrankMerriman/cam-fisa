from utils.fbManager import FBManager
from screens.cameraScreen import CameraScreen
from screens.galleryScreen import GalleryScreen
from screens.screenManager import ScreenManager

import subprocess
from PIL import Image, ImageDraw, ImageFont

# Create frame buffer interface class instance -> Want a single FB that is shared
fb = FBManager()

# Write welcome message
img = Image.new('RGB', (fb.width, fb.height), color=(0, 0, 0))
draw = ImageDraw.Draw(img)

# Load default font
font = ImageFont.load_default()

# Define text lines
lines = [
    "WELCOME TO CAMFISA",
    "MERRY CHRISTMAS",
    "ANFISA",
    "I LOVE YOU"
]

# Colors in RGB
BROWN = (94, 38, 0)
WHITE = (255, 255, 255)
YELLOW = (226, 226, 0)
RED = (205, 0, 0)
GREEN = (0, 255, 0)
CREAM = (230, 230, 210)

# Draw text (adjust positions as needed)
y = 5
for line in lines:
    draw.text((5, y), line, font=font, fill=WHITE)
    y += 15  # line spacing

# If you want, you can draw your ASCII art below in brown, red, etc.
ascii_art = [
    "┌φ╣╠╠╣╗              ╗▒╬╬╣φµ",
    "á╬╬╣▓▓╬╠╣▄φ▓▓▓▓▓▓▓▓Æ▄╬╣╣▓▓▒▒╠▌",
    "╠╣╣▓▓▓▓▓╣▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█▓▓╬╬╣",
    " ╙╠╣╬╬╬╣╬╣╣╬╣╣╣╣▓╣╣▓▓▓▓▓▓▓╬╬╩",
    "   ╞╬╬╬╬╬░╠▒╚╠╬╠╠╬╠╬╬╣▓▓▓▓▌"
]

y += 10
for line in ascii_art:
    draw.text((5, y), line, font=font, fill=BROWN)
    y += 12  # adjust spacing for art

# Convert to framebuffer bytes and write
fb_bytes = fb.rgb24_to_rgb565(img)
fb.write_to_screen(fb_bytes)


# Create screen instances
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