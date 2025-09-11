from picamera2 import Picamera2, Preview
import time
from pprint import pprint

picam2 = Picamera2()

camera_modes = picam2.sensor_modes
for i, mode in enumerate(camera_modes):
    print(f"Mode {i}: {mode}")

camera_config = picam2.create_still_configuration()
pprint(camera_config)
picam2.configure(camera_config)


picam2.start()

while True:
    input("Press Enter to capture an image...")
    # val = time.time()
    picam2.capture_file(f"sample.jpg") # So image path is the same for remote viewing / debug. Don't need more than 1 image saved rn.