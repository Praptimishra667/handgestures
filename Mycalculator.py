import cv2
import numpy as np
import mediapipe as mp
import time
import math

# Mediapipe setup
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)
LEFT_IRIS = [468, 469, 470, 471]

# Button layout
buttons = [
    ["1", "2", "3", "+"],
    ["4", "5", "6", "-"],
    ["7", "8", "9", "="],
    ["C", "0", ".", "*"],
    ["←", "/", "(", ")"]
]
button_size = 60
button_margin = 10

# Calculator state
expression = ""
hover_start_time = None
hover_button = None
hover_threshold = 1.2  # seconds

# Colors and styles
bg_color = (30, 30, 40)
btn_color = (80, 80, 100)
hover_color = (0, 255, 0)
text_color = (255, 255, 255)
glass_color = (50, 50, 60, 0.4)  # RGBA-ish for blending

def draw_glass_panel(img, x1, y1, x2, y2, opacity=0.3):
    overlay = img.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), (80, 80, 100), -1)
    return cv2.addWeighted(overlay, opacity, img, 1 - opacity, 0)

def draw_buttons(frame):
    h, w = frame.shape[:2]
    x_offset = w - (button_size + button_margin) * 4 - 20
    y_offset = 120
    button_rects = []

    for i, row in enumerate(buttons):
        for j, char in enumerate(row):
            x1 = x_offset + j * (button_size + button_margin)
            y1 = y_offset + i * (button_size + button_margin)
            x2, y2 = x1 + button_size, y1 + button_size

            # Rounded button
            cv2.rectangle(frame, (x1, y1), (x2, y2), btn_color, -1, cv2.LINE_AA)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (120, 120, 130), 2, cv2.LINE_AA)
            cv2.putText(frame, char, (x1 + 15, y1 + 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, text_color, 2)
            button_rects.append((char, x1, y1, x2, y2))
    return button_rects

def get_iris_position(landmarks, width, height):
    iris = landmarks[LEFT_IRIS[0]]
    return int(iris.x * width), int(iris.y * height)

def safe_eval(expr):
    try:
        return str(round(eval(expr, {"__builtins__": None}, math.__dict__), 4))
    except:
        return "Err"

# Webcam
cap = cv2.VideoCapture(0)
prev_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    h, w = frame.shape[:2]

    # Background aesthetic
    blurred = cv2.GaussianBlur(frame, (41, 41), 0)
    frame = cv2.addWeighted(frame, 0.3, blurred, 0.7, 0)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0].landmark
        iris_x, iris_y = get_iris_position(landmarks, w, h)
        cv2.circle(frame, (iris_x, iris_y), 4, (0, 0, 255), -1)

        button_rects = draw_buttons(frame)
        now = time.time()
        found_hover = False

        for char, x1, y1, x2, y2 in button_rects:
            if x1 <= iris_x <= x2 and y1 <= iris_y <= y2:
                cv2.rectangle(frame, (x1, y1), (x2, y2), hover_color, 2, cv2.LINE_AA)
                if hover_button == char:
                    if now - hover_start_time >= hover_threshold:
                        if char == "C":
                            expression = ""
                        elif char == "=":
                            expression = safe_eval(expression)
                        elif char == "←":
                            expression = expression[:-1]
                        else:
                            expression += char
                        hover_start_time = None
                        hover_button = None
                else:
                    hover_button = char
                    hover_start_time = now
                found_hover = True
                break

        if not found_hover:
            hover_button = None
            hover_start_time = None
    else:
        draw_buttons(frame)

    # Glass panel expression background
    frame = draw_glass_panel(frame, 20, 10, w - 20, 100, 0.3)

    # Display expression & preview
    preview = safe_eval(expression) if expression and expression != "Err" else ""
    cv2.putText(frame, expression, (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.6, text_color, 3)
    if preview and preview != expression:
        cv2.putText(frame, f"= {preview}", (40, 95), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 180), 2)

    # FPS
    fps = int(1 / (time.time() - prev_time + 1e-5))
    prev_time = time.time()
    cv2.putText(frame, f'FPS: {fps}', (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)

    cv2.imshow("✨ Aesthetic Gaze Calculator", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
