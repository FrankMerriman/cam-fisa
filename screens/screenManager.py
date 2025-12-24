# This file will be responsible for swapping between the different types of screen scenes
# on the camera UI such as the main camera preview, image review, settings menu, etc.
from enum import Enum

class Scenes(Enum):
    MAIN = 1
    PREVIEW = 2
    GALLERY = 3


# This function will switch the current scene to the specified scene name enum
def switch_to_scene(scene_name):
    pass