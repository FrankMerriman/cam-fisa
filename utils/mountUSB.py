import subprocess
from pathlib import Path

def mount_usb():
        """
        Detects a USB drive and mounts it.
        Returns Path to mount point if successful, else None.
        """
        mount_point = Path("/home/admin/usb_mount")
        mount_point.mkdir(parents=True, exist_ok=True)

        usb_device = "/dev/sda1"

        # Mount
        subprocess.run(["sudo", "mount", "-o", "uid=1000,gid=1000", usb_device, str(mount_point)], check=True)
        print(f"USB mounted at {mount_point}")
        return mount_point