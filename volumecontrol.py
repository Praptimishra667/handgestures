import cv2
import mediapipe as mp
import numpy as np
import math

# MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Webcam
cap = cv2.VideoCapture(0)

def find_distance(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    volume = 0
    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

            lm = handLms.landmark
            thumb_tip = int(lm[4].x * w), int(lm[4].y * h)
            index_tip = int(lm[8].x * w), int(lm[8].y * h)

            # Draw circle and line
            cv2.circle(frame, thumb_tip, 10, (255, 0, 0), -1)
            cv2.circle(frame, index_tip, 10, (0, 255, 0), -1)
            cv2.line(frame, thumb_tip, index_tip, (255, 255, 255), 3)

            # Calculate distance and convert to volume %
            dist = find_distance(thumb_tip, index_tip)
            volume = np.interp(dist, [30, 200], [0, 100])
            
            # Draw Volume Bar
            cv2.rectangle(frame, (50, 150), (85, 400), (200, 200, 200), 2)
            bar_height = int(np.interp(volume, [0, 100], [400, 150]))
            cv2.rectangle(frame, (50, bar_height), (85, 400), (0, 255, 0), -1)
            cv2.putText(frame, f'{int(volume)} %', (40, 430), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Gesture Volume Control 🔊", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
