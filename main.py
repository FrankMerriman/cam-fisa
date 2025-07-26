from picamera2 import Picamera2, Preview
import time

picam2 = Picamera2()
camera_config = picam2.create_still_configuration()
print(camera_config)
picam2.configure(camera_config)
picam2.start()

while True:
    input("Press Enter to capture an image...")
    val = time.time()
    picam2.capture_file(f"{val}.jpg")