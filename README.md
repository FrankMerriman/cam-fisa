# cam-fisa
Application to run a raspberry pi as a digital camera


Looks like LCD only supports bookworm

From raw os had to:
1. Get bookwork 64bit lite
2. 


Dependencies:
# for display
sudo apt install fbset fbcat

## test screen
sudo fbset -fb /dev/fb1
sudo cat /dev/urandom > /dev/fb1

## clear
sudo dd if=/dev/zero of=/dev/fb1

# For cam
sudo apt install libcamera-apps python3-pil python3-evdev  -y

# To enable:
sudo apt install raspi-config -y
then enable legacy cam stack

2592x1944


key1 = pin 7
key2 = pin 16
key3 = pin 18
key4 = pin 22



Project structure:
Main app handles button inputs and touch inputs? calls functions for screens? not sure exactly how to handle 

For encapsulation I ideally would have the code for shutter entirely within the camera screen