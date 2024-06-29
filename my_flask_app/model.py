import cv2
import numpy as np
import mediapipe as mp
from collections import deque

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

cv2.namedWindow('Paint', cv2.WINDOW_AUTOSIZE)

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

def gesture_to_paint():
    global bpoints, gpoints, rpoints, ypoints, indices, paintWindow, is_dark_mode, colorIndex
    # Initialize webcam
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    while True:
        # Read each frame from the webcam
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Flip the frame vertically
        frame = cv2.flip(frame, 1)
        framergb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Set the color scheme based on the current mode
        colors = colors_dark if is_dark_mode else colors_light

        # Draw buttons on the frame
        draw_buttons(frame, colors)

        # Get hand landmark prediction
        result = hands.process(framergb)

        # Process the result
        if result.multi_hand_landmarks:
            landmarks = []
            for handslms in result.multi_hand_landmarks:
                for lm in handslms.landmark:
                    lmx = int(lm.x * 640)
                    lmy = int(lm.y * 480)
                    landmarks.append([lmx, lmy])

                # Draw landmarks on frame
                mpDraw.draw_landmarks(frame, handslms, mpHands.HAND_CONNECTIONS)

            fore_finger = (landmarks[8][0], landmarks[8][1])
            thumb = (landmarks[4][0], landmarks[4][1])
            cv2.circle(frame, fore_finger, 3, (0, 255, 0), -1)

            # Check for gestures to switch color or clear
            if thumb[1] - fore_finger[1] < 30:
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
                if colorIndex == 0:
                    bpoints[indices['blue']].appendleft(fore_finger)
                elif colorIndex == 1:
                    gpoints[indices['green']].appendleft(fore_finger)
                elif colorIndex == 2:
                    rpoints[indices['red']].appendleft(fore_finger)
                elif colorIndex == 3:
                    ypoints[indices['yellow']].appendleft(fore_finger)
        else:
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

        # Draw lines of all the colors on the canvas and frame
        points = [bpoints, gpoints, rpoints, ypoints]
        for i in range(len(points)):
            for j in range(len(points[i])):
                for k in range(1, len(points[i][j])):
                    if points[i][j][k - 1] is None or points[i][j][k] is None:
                        continue
                    cv2.line(frame, points[i][j][k - 1], points[i][j][k], colors[i], 2)
                    cv2.line(paintWindow, points[i][j][k - 1], points[i][j][k], colors[i], 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        key = cv2.waitKey(1)
        if key == ord('c'):
            break
        elif key == ord('t'):
            is_dark_mode = not is_dark_mode
            if is_dark_mode:
                paintWindow[:] = (0, 0, 0)  # Set paintWindow background to black for dark mode
            else:
                paintWindow[:] = (255, 255, 255)  # Set paintWindow background to white for light mode

    # Release the webcam and destroy all windows
    cap.release()
    cv2.destroyAllWindows()