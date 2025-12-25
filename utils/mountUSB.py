import subprocess
from pathlib import Path

def mount_usb(self, mount_point="/mnt/usb"):
        """
        Detects a USB drive and mounts it.
        Returns Path to mount point if successful, else None.
        """
        Path(mount_point).mkdir(parents=True, exist_ok=True)

        # List block devices
        result = subprocess.run(["lsblk", "-o", "NAME,RM,TYPE,MOUNTPOINT"], capture_output=True, text=True)
        lines = result.stdout.splitlines()

        usb_device = None
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 3:
                name, rm, type_ = parts[:3]
                mountpoint = parts[3] if len(parts) > 3 else ""
                if rm == "1" and type_ == "part" and not mountpoint:
                    usb_device = f"/dev/{name}"
                    break

        if not usb_device:
            print("No unmounted USB drive detected.")
            return None

        # Mount the USB
        try:
            subprocess.run(["sudo", "mount", usb_device, mount_point], check=True)
            print(f"USB mounted at {mount_point}")
            return Path(mount_point)
        except subprocess.CalledProcessError as e:
            print(f"Failed to mount {usb_device}: {e}")
            return None