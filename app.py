import screens.cameraScreen as cameraScreen

if __name__ == "__main__":
    cam_screen = cameraScreen.CameraScreen()
    cam_screen.start_camera()
    try:
        while True:
            cam_screen.preview_camera()
    except KeyboardInterrupt:
        cam_screen.stop_camera()