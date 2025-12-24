import time

def get_cpu_temp():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp_milli = int(f.read())
    return temp_milli / 1000.0  # convert to °C

def get_fps():
    now = time.time()
    # ChatGPT told me about function attributes, not sure exactly how they work
    # Sort of like a class attribute maybe?
    if not hasattr(get_fps, "prev_time"):
        get_fps.prev_time = now
        return 0.0
    fps = 1.0 / (now - get_fps.prev_time)
    get_fps.prev_time = now
    return fps
