import cv2
import numpy as np
import mediapipe as mp
from collections import deque
import threading

# Initialize deque arrays to store points of different colors
bpoints = [deque(maxlen=1024)]
gpoints = [deque(maxlen=1024)]
rpoints = [deque(maxlen=1024)]
ypoints = [deque(maxlen=1024)]

# Initialize indices to keep track of points in respective color arrays
indices = {'blue': 0, 'green': 0, 'red': 0, 'yellow': 0}

# Kernel for image dilation
kernel = np.ones((5, 5), np.uint8)

# Color values in BGR format for light mode
colors_light = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]
colorIndex = 0

# Color values in BGR format for dark mode
colors_dark = [(255, 102, 102), (102, 255, 102), (102, 102, 255), (255, 255, 102)]

# Initialize the canvas
paintWindow = np.zeros((471, 636, 3), dtype=np.uint8)
paintWindow[:] = (0, 0, 0)  # Start with a black canvas for dark mode

# Define button positions and radius
button_radius = 30
buttons = {
    "CLEAR": (90, 33),
    "BLUE": (207, 33),
    "GREEN": (322, 33),
    "RED": (437, 33),
    "YELLOW": (552, 33)
}

# Mode toggle: True for dark mode, False for light mode
is_dark_mode = True  # Start with dark mode

def draw_buttons(frame, colors):
    for button in buttons:
        if button == "CLEAR":
            cv2.circle(frame, buttons[button], button_radius, (255, 255, 255), 2)
            text_size = cv2.getTextSize(button, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            text_x = buttons[button][0] - text_size[0] // 2
            text_y = buttons[button][1] + text_size[1] // 2
            cv2.putText(frame, button, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        else:
            color = colors[list(buttons.keys()).index(button) - 1]
            cv2.circle(frame, buttons[button], button_radius, color, -1)

# Initialize Mediapipe Hands
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mpDraw = mp.solutions.drawing_utils

# Function to process frames and detect gestures
def process_frame(frame):
    global bpoints, gpoints, rpoints, ypoints, indices, paintWindow, is_dark_mode, colorIndex

    frame = cv2.flip(frame, 1)
    framergb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    colors = colors_dark if is_dark_mode else colors_light
    draw_buttons(frame, colors)

    result = hands.process(framergb)

    if result.multi_hand_landmarks:
        landmarks = []
        for handslms in result.multi_hand_landmarks:
            for lm in handslms.landmark:
                lmx = int(lm.x * 640)
                lmy = int(lm.y * 480)
                landmarks.append([lmx, lmy])

            mpDraw.draw_landmarks(frame, handslms, mpHands.HAND_CONNECTIONS)

        fore_finger = (landmarks[8][0], landmarks[8][1])
        thumb = (landmarks[4][0], landmarks[4][1])
        cv2.circle(frame, fore_finger, 3, (0, 255, 0), -1)

        if abs(thumb[1] - fore_finger[1]) < 30:  # Ensure you are using absolute difference
            print("Switch gesture detected")  # Debug print
            for key in indices:
                indices[key] += 1
                if key == 'blue':
                    bpoints.append(deque(maxlen=512))
                elif key == 'green':
                    gpoints.append(deque(maxlen=512))
                elif key == 'red':
                    rpoints.append(deque(maxlen=512))
                elif key == 'yellow':
                    ypoints.append(deque(maxlen=512))
        elif fore_finger[1] <= 65:
            for button, position in buttons.items():
                if np.linalg.norm(np.array(fore_finger) - np.array(position)) <= button_radius:
                    print(f"Button {button} pressed")  # Debug print
                    if button == "CLEAR":
                        # Clear drawing points arrays
                        bpoints = [deque(maxlen=512)]
                        gpoints = [deque(maxlen=512)]
                        rpoints = [deque(maxlen=512)]
                        ypoints = [deque(maxlen=512)]
                        # Reset indices
                        indices = {key: 0 for key in indices}
                        # Clear the canvas (only clear the drawing, not the background)
                        paintWindow[:] = (0, 0, 0) if is_dark_mode else (255, 255, 255)
                    else:
                        colorIndex = list(buttons.keys()).index(button) - 1
        else:
            print(f"Drawing with color index {colorIndex}")  # Debug print
            if colorIndex == 0:
                bpoints[indices['blue']].appendleft(fore_finger)
            elif colorIndex == 1:
                gpoints[indices['green']].appendleft(fore_finger)
            elif colorIndex == 2:
                rpoints[indices['red']].appendleft(fore_finger)
            elif colorIndex == 3:
                ypoints[indices['yellow']].appendleft(fore_finger)

    points = [bpoints, gpoints, rpoints, ypoints]
    for i in range(len(points)):
        for j in range(len(points[i])):
            for k in range(1, len(points[i][j])):
                if points[i][j][k - 1] is None or points[i][j][k] is None:
                    continue
                cv2.line(frame, points[i][j][k - 1], points[i][j][k], colors[i], 2)
                cv2.line(paintWindow, points[i][j][k - 1], points[i][j][k], colors[i], 2)

    return frame

# Function to continuously process video feed
def process_video_feed():
    global is_dark_mode
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        processed_frame = process_frame(frame)

        cv2.imshow('Paint', paintWindow)
        ret, buffer = cv2.imencode('.jpg', processed_frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        

        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):
            break
        elif key == ord('t'):
            is_dark_mode = not is_dark_mode
            if is_dark_mode:
                paintWindow[:] = (0, 0, 0)
            else:
                paintWindow[:] = (255, 255, 255)
            print(f"Mode toggled to {'dark' if is_dark_mode else 'light'} mode")

    cap.release()
    cv2.destroyAllWindows()

# Start the thread for processing video feed
video_thread = threading.Thread(target=process_video_feed)
video_thread.daemon = True
video_thread.start()
