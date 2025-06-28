import cv2
import mediapipe as mp

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=2)

# Function to detect gesture
def get_gesture(hand_landmarks):
    tips = [8, 12, 16, 20]  # Finger tips: Index, Middle, Ring, Pinky
    fingers = []
    for tip in tips:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    if fingers == [0, 0, 0, 0]:
        return "Rock"
    elif fingers == [1, 1, 1, 1]:
        return "Paper"
    elif fingers == [1, 0, 0, 0]:
        return "Scissors"
    else:
        return "Unknown"

# Start Webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    gestures = []

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            gestures.append(get_gesture(hand_landmarks))

    # If two hands are detected, compare their gestures
    if len(gestures) == 2:
        p1, p2 = gestures
        result_text = f"P1: {p1}  P2: {p2}"

        if p1 == p2:
            winner = "Draw"
        elif (p1 == "Scissors" and p2 == "Rock") or \
             (p1 == "Paper" and p2 == "Rock") or \
             (p1 == "Scissors" and p2 == "Paper"):
            winner = "Player 1 Wins!"
        else:
            winner = "Player 2 Wins!"

        # Display result on screen
        cv2.putText(frame, result_text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        cv2.putText(frame, winner, (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,0,255), 3)

    cv2.imshow("Rock Paper Scissors", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
import cv2
import mediapipe as mp

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=2)

# Function to detect gesture
def get_gesture(hand_landmarks):
    tips = [8, 12, 16, 20]  # Finger tips: Index, Middle, Ring, Pinky
    fingers = []
    for tip in tips:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    if fingers == [0, 0, 0, 0]:
        return "Rock"
    elif fingers == [1, 1, 1, 1]:
        return "Paper"
    elif fingers == [1, 0, 0, 0]:
        return "Scissors"
    else:
        return "Unknown"

# Start Webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    gestures = []

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            gestures.append(get_gesture(hand_landmarks))

    # If two hands are detected, compare their gestures
    if len(gestures) == 2:
        p1, p2 = gestures
        result_text = f"P1: {p1}  P2: {p2}"

        if p1 == p2:
            winner = "Draw"
        elif (p1 == "Rock" and p2 == "Scissors") or \
             (p1 == "Paper" and p2 == "Rock") or \
             (p1 == "Scissors" and p2 == "Paper"):
            winner = "Player 1 Wins!"
        else:
            winner = "Player 2 Wins!"

        # Display result on screen
        cv2.putText(frame, result_text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        cv2.putText(frame, winner, (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,0,255), 3)

    cv2.imshow("Rock Paper Scissors", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
