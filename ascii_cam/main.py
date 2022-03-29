import cv2
import numpy as np
import pyvirtualcam
from pyvirtualcam import PixelFormat

# On the bottom of the screen we can leave a comment.
# If this is None it will be ignored
SCREEN_COMMENT = "NOTE: Virtual Victor does not understand work stuff."
# Invert the feed
MIRROR_CAMERA = False
# The character density map. From left to right each
# character fills more space, so appears more dense.
DENSITY = "@@#W$9876543210?!abc;:+=-,._ "
# If True, enables the cirtual camera.
# ! NOTE: Requires something like OBS virtualcam to be
# ! NOTE: on the system. 
OUTPUT_VIRTUAL = True
# Outputs the image to its own window. Handy for testing.
OUTPUT_LOCAL = False

# ! Settings to play with
# Manually increase brightness if needed
BRIGHTNESS_MULTIPLIER = 1.0
# Desaturates the red and blue pixel values, leaving
# a more matrix like feel (more green)
COLOR_DESAT = 0.8

# ! If you struggle with framerate, set this to True
SMOL_PC_WEAKLING_MODE = False



# Set frame size. More pixels means more processing.
pref_width = 1920
pref_height = 1080

if SMOL_PC_WEAKLING_MODE:
    pref_width = 1280
    pref_height = 720

# To get the characters, we downsize the image to the
# amount of characters we will output. Makes it faster.
scaled_width = 160 if not SMOL_PC_WEAKLING_MODE else 64
scaled_height = 90 if not SMOL_PC_WEAKLING_MODE else 36

# Set the desired FPS. 24 is the most cinematic
pref_fps = 24 if not SMOL_PC_WEAKLING_MODE else 15

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
scalar = width / scaled_width

# ! Try to connect to the virtual camera output
try:
    if OUTPUT_VIRTUAL:
        cam = pyvirtualcam.Camera(width, height, fps, fmt=PixelFormat.BGR)
except Exception as e:
    print("Closing")
    vc.release()
    cv2.destroyAllWindows()
    raise e

# * Now we are all set. Everything is either running,
# * or it raised an error. So we can start the fun stuff.

while True:
    try:
        # Get if there is a frame, and the frame itself
        success, frame = vc.read()
        if not success:
            # We could not get a frame for some reason.
            continue

        # Downscale to smaller frame to work with
        resized = cv2.resize(frame, (scaled_width, scaled_height))
        # Black out original frame. Now black canvas for us to put
        # characters on.
        cv2.rectangle(frame, (0, 0), (width, height), (0, 0, 0), -1)
                
        # Iterate through every one of these scaled pixels
        for col in range(scaled_height):
            for row in range(scaled_width):
                # Extract tje colors for that pixel
                red = min(255, resized[col, row, 2] * BRIGHTNESS_MULTIPLIER * COLOR_DESAT)
                green = min(255, resized[col, row, 1] * BRIGHTNESS_MULTIPLIER)
                blue = min(255, resized[col, row, 0] * BRIGHTNESS_MULTIPLIER * COLOR_DESAT)
                # We need to map the average color density onto our character density map.
                avg =  int((red + green + blue) / (255*3) * 255 )
                avg_percent = int(avg / 255 * (len(DENSITY)-1))
                text = str(DENSITY[avg_percent])
                # Now we have the character, lets put it on the frame
                cv2.putText(frame, text, 
                    (int(row*scalar), int(col*scalar)), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    0.5 if not SMOL_PC_WEAKLING_MODE else 0.75,
                    (int(blue), int(green), int(red)),
                    1 if not SMOL_PC_WEAKLING_MODE else 2,
                    1)

        if SCREEN_COMMENT:
            # We want to put a comment on the screen.
            # TODO: The position needs to be centered    
            cv2.rectangle(frame, (0, height), (width, int(950/1080*height)), (0, 0, 0), -1)
            cv2.putText(frame, SCREEN_COMMENT, 
                        (int(110/1920*width), int(1020/1080*height)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        2 if width == 1920 else 1,
                        (int(16), int(118), int(18)),
                        2 if width == 1920 else 1,
                        1)

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
            break

    except KeyboardInterrupt:
        # We stopped this in console with Ctrl+C
        break
    except Exception as e:
        vc.release()
        cv2.destroyAllWindows()
        raise e

vc.release()
cv2.destroyAllWindows()