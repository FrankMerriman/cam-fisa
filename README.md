# cam-fisa
Cannot remember if I followed OS setup for TFT display or if I used their bookworm image.
https://www.waveshare.com/wiki/2.8inch_RPi_LCD_(A)#For_Bullseye_32-bit_and_Buster_Systems

My module seems to have max of: 2592x1944


### WaveShare display
key 1 = pin 7 = gpio4

key 2 = pin 16 = gpio23

key 3 = pin 18 = gpio24

key 4 = pin 22 = gpio25

### To test display
1. `sudo apt install fbset fbcat`
2. `sudo fbset -fb /dev/fb0`
3. `sudo cat /dev/urandom > /dev/fb0`
4. `sudo dd if=/dev/zero of=/dev/fb0`

### For cam
sudo apt install libcamera-apps python3-pil python3-evdev  -y

### Fix for needing to run app as sudo due to dmaheap permissions
1. `sudo nano /etc/tmpfiles.d/dmaheap.conf`
2. Enter the following:
```
# Fix DMA heap permissions for libcamera
z /dev/dma_heap/system    0660 root video -
z /dev/dma_heap/linux,cma 0660 root video -
```
3. `sudo systemd-tmpfiles --create`
4. `sudo reboot`
5. `ls -l /dev/dma_heap/` and `group` -> Check group permissions exist for heap and user is in videos group

### Fix for raspberry Pi being stuck at login
1. `sudo mkdir -p /etc/systemd/system/getty@tty1.service.d`
2. `sudo nano /etc/systemd/system/getty@tty1.service.d/autologin.conf`
3. Add to file:
```
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin admin --noclear %I $TERM
```
4. `sudo reboot`



