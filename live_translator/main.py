import cv2
import numpy as np
import pyvirtualcam
import speech_recognition as sr 
from pyvirtualcam import PixelFormat
from deep_translator import GoogleTranslator

# Invert the feed
MIRROR_CAMERA = False

# Available languages. [Code for audio recogniser, code for translator] 
LANG_AFRIKAANS = ['af', 'afrikaans']
LANG_ENG_SA = ['en-ZA', 'english']
LANG_SPANISH_MEX = ['es-MX', 'spanish']

# ! These are the languages we are using 
# The language to translate to
SCREEN_LANGUAGE = LANG_SPANISH_MEX
# The language to translate from
INPUT_LANGUAGE = LANG_ENG_SA

# If True, enables the virtual camera.
# ! NOTE: Requires something like OBS virtualcam to be
# ! NOTE: on the system. 
OUTPUT_VIRTUAL = True
# Outputs the image to its own window. Handy for testing.
OUTPUT_LOCAL = False

# this is called from the background thread
def callback(recognizer, audio):
    global screen_text
    # received audio data, now we'll recognize it using Google Speech Recognition
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        speech_text = recognizer.recognize_google(audio, language=INPUT_LANGUAGE[0])
        print("DETECTED: " + speech_text)
        translated_text = GoogleTranslator(source='auto', target=SCREEN_LANGUAGE[1]).translate(speech_text)
        screen_text = translated_text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

r = sr.Recognizer()
m = sr.Microphone()
screen_text = ""

with m as source:
    r.adjust_for_ambient_noise(source)  # we only need to calibrate once, before we start listening

# start listening in the background (note that we don't have to do this inside a `with` statement)
stop_listening = r.listen_in_background(m, callback)

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

        # Draw a black box onto the screen and overlay the text.
        # ! `screen_text` contains the last translated text, so just redraw that
        # ! each frame. The callback function will update it
        cv2.rectangle(frame, (0, 1080), (1920, 970), (0, 0, 0), -1)
        cv2.putText(frame, str(screen_text), 
                    (10, 1040), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    2,
                    (255,255,255),
                    3,
                    2)

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
        stop_listening(wait_for_stop=False)
        break
    except Exception as e:
        stop_listening(wait_for_stop=False)
        vc.release()
        cv2.destroyAllWindows()
        raise e

vc.release()
cv2.destroyAllWindows()

