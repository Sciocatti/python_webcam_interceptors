import cv2
import numpy as np
import pyvirtualcam
from pyvirtualcam import PixelFormat

# Invert the feed
MIRROR_CAMERA = False

# If True, enables the virtual camera.
# ! NOTE: Requires something like OBS virtualcam to be
# ! NOTE: on the system. 
OUTPUT_VIRTUAL = True
# Outputs the image to its own window. Handy for testing.
OUTPUT_LOCAL = False

# Set frame size. More pixels means more processing.
pref_width = 1920
pref_height = 1080
# Set the desired FPS. 24 is the most cinematic
pref_fps = 24

# Open video feed and configured preffered settings.
vc = cv2.VideoCapture(0)
if not vc.isOpened():
    raise RuntimeError("Could not open video feed.")

vc.set(cv2.CAP_PROP_FRAME_WIDTH, pref_width)
vc.set(cv2.CAP_PROP_FRAME_HEIGHT, pref_height)
vc.set(cv2.CAP_PROP_FPS, pref_fps)

# Get the actual settings. Previous might not
# have been OK.
width = int(vc.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = vc.get(cv2.CAP_PROP_FPS)

# ! Try to connect to the virtual camera output
try:
    if OUTPUT_VIRTUAL:
        cam = pyvirtualcam.Camera(width, height, fps, fmt=PixelFormat.BGR)
except Exception as e:
    print("Closing")
    vc.release()
    cv2.destroyAllWindows()
    raise e

while True:
    try:
        # Get if there is a frame, and the frame itself
        success, frame = vc.read()
        if not success:
            # We could not get a frame for some reason.
            continue

        # ! \/\/ Manipulate image here \/\/

        # ! /\/\ Manipulate image here /\/\

        if MIRROR_CAMERA:
            # Flip the frame
            frame = cv2.flip(frame, 1)

        if OUTPUT_LOCAL:
            # Display in window.
            cv2.imshow('Frame', frame)

        if OUTPUT_VIRTUAL:
            # Send to virtual camera
            cam.send(frame)
            cam.sleep_until_next_frame()    
        
        if cv2.waitKey(25) & 0xFF == ord('q'):
            # If we press `q`, close the program
            raise KeyboardInterrupt

    except KeyboardInterrupt:
        break
    except Exception as e:
        vc.release()
        cv2.destroyAllWindows()
        raise e

vc.release()
cv2.destroyAllWindows()