import cv2
import time
import scipy.spatial
import mediapipe as mp

import pyvirtualcam
from pyvirtualcam import PixelFormat

# Invert the feed
MIRROR_CAMERA = False

# If True, enables the cirtual camera.
# ! NOTE: Requires something like OBS virtualcam to be
# ! NOTE: on the system. 
OUTPUT_VIRTUAL = False
# Outputs the image to its own window. Handy for testing.
OUTPUT_LOCAL = True

# * Models we want to draw:
# Draws a stickman on the body
DO_STICKMAN = False
# Draws some face landmarks
DO_FACE = False
# Draws a lot of face landmarks. Also slow.
DO_ADVANCED_FACE = False
# Tracks your hand/fingers. Very cool, very slow.
# This is currently setup so you can "touch" a certain part
# of the image to do something.
DO_HAND = True

# * Mediapipe models we could toggle on/off
mp_pose = mp.solutions.pose
mp_face_detection = mp.solutions.face_detection
hands_module = mp.solutions.hands
distance_module = scipy.spatial.distance
mp_draw = mp.solutions.drawing_utils
face_mesh_module = mp.solutions.face_mesh
mp_drawing_styles = mp.solutions.drawing_styles

# * Init Models
pose = mp_pose.Pose()
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.8, model_selection=0)
hand_detection = hands_module.Hands(static_image_mode=False, min_detection_confidence=0.7, min_tracking_confidence=0.7, max_num_hands=1)
drawing_spec = mp_draw.DrawingSpec(thickness=1, circle_radius=1)
face_mesh_detection = face_mesh_module.FaceMesh(static_image_mode=False, max_num_faces=2,
                                    min_detection_confidence=0.8)

# Set frame size. More pixels means more processing.
pref_width = 1920
pref_height = 1080
pref_fps = 24
# Open video feed and configured preffered settings.
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Could not open video feed.")
cap.set(cv2.CAP_PROP_FRAME_WIDTH, pref_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, pref_height)
cap.set(cv2.CAP_PROP_FPS, pref_fps)

# Get the actual settings. Previous might not
# have been OK.
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

# ! Try to connect to the virtual camera output
try:
    if OUTPUT_VIRTUAL:
        cam = pyvirtualcam.Camera(width, height, fps, fmt=PixelFormat.BGR)
except Exception as e:
    print("Closing")
    cap.release()
    cv2.destroyAllWindows()
    raise e

previous_time = 0
frameWidth = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
frameHeight = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
 
circleCenter = (round(frameWidth/2), round(frameHeight/2))
circleRadius = 40

# * Now we are all set. Everything is either running,
# * or it raised an error. So we can start the fun stuff.

def process_image(img):
    """
        Processes all the models we want on this image.
    """
    ret = {}
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    if DO_STICKMAN:
        stickman_results = pose.process(imgRGB)
        ret["stickman_results"] = stickman_results
    if DO_FACE:
        face_results = face_detection.process(imgRGB)
        ret["face_results"] = face_results
    if DO_HAND:
        hand_results = hand_detection.process(imgRGB)
        ret["hand_results"] = hand_results
    if DO_ADVANCED_FACE:
        face_mesh_results = face_mesh_detection.process(imgRGB)
        ret["face_mesh_results"] = face_mesh_results

    ret["img"] = img
    return ret

while True:
    try:
        success, img = cap.read()
        if not success:
            # We could not get a frame for some reason.
            continue
        image_model_data = process_image(img)
        circleColor = (0, 0, 0)
        stickman_results = image_model_data.get("stickman_results", None)
        face_results = image_model_data.get("face_results", None)
        hand_results = image_model_data.get("hand_results", None)
        face_mesh_results = image_model_data.get("face_mesh_results", None)

        if DO_STICKMAN and stickman_results.pose_landmarks:
            # If we want to draw the stickman, AND there is one to draw:
            mp_draw.draw_landmarks(img, stickman_results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            for id, lm in enumerate(stickman_results.pose_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x*w), int(lm.y*h)
                cv2.circle(img, (cx, cy), 5, (255,0,0), cv2.FILLED)

        if DO_FACE and face_results.detections:
            # If we want to draw the basic face, AND there is one to draw:
            for detection in face_results.detections:
                # We could have multiple
                mp_draw.draw_detection(img, detection)

        if DO_HAND and (hand_results.multi_hand_landmarks != None):
            # If we want to do hand tracking, AND there is a hand.
            # * Basically this draws a point on the tip of your index finger, and if
            # * the tip is near the center of the screen, ie inside the drawn circle,
            # * we change the color of the circle.
            normalizedLandmark = hand_results.multi_hand_landmarks[0].landmark[hands_module.HandLandmark.INDEX_FINGER_TIP]
            pixelCoordinatesLandmark = mp_draw._normalized_to_pixel_coordinates(normalizedLandmark.x,
                                                                               normalizedLandmark.y,
                                                                               frameWidth,
                                                                               frameHeight)
            cv2.circle(img, pixelCoordinatesLandmark, 2, (255,0,0), -1)
            if distance_module.euclidean(pixelCoordinatesLandmark, circleCenter) < circleRadius:
                circleColor = (0,255,0)
            else:
                circleColor = (0,0,255)
            cv2.circle(img, circleCenter, circleRadius, circleColor, -1)

        if DO_ADVANCED_FACE and face_mesh_results.multi_face_landmarks:
            # If we want to draw the advanced face, AND there is one to draw:
            for face_landmarks in face_mesh_results.multi_face_landmarks:
                # Draw the facial landmarks on the output image with the face mesh tesselation
                # connections using default face mesh tesselation style.
                mp_draw.draw_landmarks(image=img, landmark_list=face_landmarks,
                                        connections=face_mesh_module.FACEMESH_TESSELATION,
                                        landmark_drawing_spec=None, 
                                        connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style())
                # Draw the facial landmarks on the output image with the face mesh contours
                # connections using default face mesh contours style.
                mp_draw.draw_landmarks(image=img, landmark_list=face_landmarks,
                                        connections=face_mesh_module.FACEMESH_CONTOURS,
                                        landmark_drawing_spec=None, 
                                        connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_contours_style())

        # Just some FPS calculation stuff. Draw the FPS on the image.
        current_time = time.time()
        fps = 1/(current_time-previous_time)
        previous_time = current_time
        cv2.putText(img, str(int(fps)), (50,50), cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0), 3)

        if MIRROR_CAMERA:
            # Flip the frame
            img = cv2.flip(img, 1)

        if OUTPUT_LOCAL:
            # Display in window.
            cv2.imshow('Frame', img)

        if OUTPUT_VIRTUAL:
            # Send to virtual camera
            cam.send(img)
            cam.sleep_until_next_frame()

        if cv2.waitKey(25) & 0xFF == ord('q'):
            # If we press `q`, close the program
            break    
    except KeyboardInterrupt:
        # We stopped this in console with Ctrl+C
        break
    except Exception as e:
        cap.release()
        cv2.destroyAllWindows()
        raise e

cap.release()
cv2.destroyAllWindows()