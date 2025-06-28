import cv2
import numpy as np
import mediapipe as mp
import time
from collections import deque

# MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# Webcam setup
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
frame = cv2.flip(frame, 1)
h, w, _ = frame.shape

# Constants
box_size = 110
gap_x = 240
gap_y = 150
start_x = int(w * 0.2)
start_y = int(h * 0.15)
activation_delay = 1
colors_on = [(100, 255, 100), (180, 255, 150), (200, 255, 100)]
colors_off = [(100, 0, 0), (90, 0, 90), (60, 60, 180)]

# Messages
message_log = deque(maxlen=6)
hold_flags = [False] * 6
pulse_timer = 0
flash_timer = 0
start_time = time.time()
frame_counter = 0
fps_display_interval = 1  # seconds
fps = 0

# Switch boxes (1 page only)
switch_boxes = []
for row in range(3):
    for col in range(2):
        x = start_x + col * gap_x
        y = start_y + row * gap_y
        switch_boxes.append({
            "pos": (x, y),
            "state": False,
            "last_seen": 0,
            "hovering": False
        })

# Log function
def add_message(msg):
    timestamp = time.strftime('%H:%M:%S')
    message_log.appendleft(f"[{timestamp}] {msg}")

# Action per switch
def perform_action(i, state):
    global pulse_timer, flash_timer
    if i == 0:
        add_message("Light is {}".format("ON" if state else "OFF"))
        pulse_timer = time.time() + 0.5
    elif i == 1:
        add_message("Fan is {}".format("ON" if state else "OFF"))
        pulse_timer = time.time() + 0.5
    elif i == 2:
        add_message("Flash triggered!")
        flash_timer = time.time() + 0.6
    elif i == 3:
        add_message("Simulated action")
        pulse_timer = time.time() + 0.5
    elif i == 4:
        add_message("Pump is {}".format("ON" if state else "OFF"))
        pulse_timer = time.time() + 0.5
    elif i == 5:
        with open("log.txt", "a") as f:
            f.write(f"Switch 6 toggled to {state} at {time.strftime('%H:%M:%S')}\n")
        add_message("Log saved to file")
        pulse_timer = time.time() + 0.5

# Clock overlay
def draw_clock(frame):
    now = time.strftime('%H:%M:%S')
    cv2.putText(frame, now, (w - 140, 40), cv2.FONT_HERSHEY_DUPLEX, 0.9, (0, 255, 255), 2)

# FPS overlay
def draw_fps(frame, fps):
    cv2.putText(frame, f"FPS: {int(fps)}", (30, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

# Main loop
last_interaction_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)

    current_time = time.time()
    frame_counter += 1
    if current_time - start_time > fps_display_interval:
        fps = frame_counter / (current_time - start_time)
        start_time = current_time
        frame_counter = 0

    if current_time < flash_timer:
        overlay = frame.copy()
        overlay[:] = (255, 255, 255)
        frame = cv2.addWeighted(overlay, 0.5, frame, 0.5, 0)

    if pulse_timer > current_time:
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, h), (0, 255, 255), -1)
        frame = cv2.addWeighted(overlay, 0.2, frame, 0.8, 0)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    finger_pos = None
    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)
            x = int(handLms.landmark[8].x * w)
            y = int(handLms.landmark[8].y * h)
            finger_pos = (x, y)
            cv2.circle(frame, finger_pos, 12, (255, 0, 255), -1)
            last_interaction_time = current_time
            break

    if current_time - last_interaction_time > 10:
        cv2.putText(frame, "Idle Mode Activated", (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    on_count = 0

    for i, box in enumerate(switch_boxes):
        x, y = box["pos"]
        state = box["state"]
        hovering = box["hovering"]
        color = colors_on[i % 3] if state else colors_off[i % 3]

        if state:
            on_count += 1

        if finger_pos and x < finger_pos[0] < x + box_size and y < finger_pos[1] < y + box_size:
            if not hovering:
                box["hovering"] = True
                box["last_seen"] = current_time
            elif current_time - box["last_seen"] >= activation_delay:
                box["state"] = not state
                perform_action(i, box["state"])
                box["last_seen"] = current_time + 1
                box["hovering"] = False
                hold_flags[i] = False
            elif current_time - box["last_seen"] >= 3 and not hold_flags[i]:
                add_message(f"Switch {i+1} held for 3s")
                hold_flags[i] = True
        else:
            box["hovering"] = False
            hold_flags[i] = False

        glow_intensity = 3 if hovering else 1
        border_color = (0, 255, 255) if hovering else (255, 255, 255)
        cv2.rectangle(frame, (x - 4, y - 4), (x + box_size + 4, y + box_size + 4), border_color, glow_intensity)
        cv2.rectangle(frame, (x, y), (x + box_size, y + box_size), color, -1)
        cv2.putText(frame, f"Switch {i + 1}", (x + 10, y + 35), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, "ON" if box["state"] else "OFF", (x + 30, y + 85), cv2.FONT_HERSHEY_COMPLEX, 0.8,
                    (255, 255, 255), 2)

    if on_count == len(switch_boxes):
        frame[:] = (150, 255, 150)
    elif on_count == 0:
        frame[:] = (50, 50, 80)

    draw_clock(frame)
    draw_fps(frame, fps)

    # Header text
    cv2.putText(frame, "Hover your index finger for 1s to TOGGLE", (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)

    # Message box (bottom-left)
    box_w = 420
    box_h = 22 * len(message_log) + 20
    box_x = 30
    box_y = h - box_h - 20

    overlay = frame.copy()
    cv2.rectangle(overlay, (box_x, box_y), (box_x + box_w, box_y + box_h), (0, 0, 0), -1)
    frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)

    y_offset = box_y + 25
    for msg in message_log:
        if len(msg) > 40:
            msg1 = msg[:40]
            msg2 = msg[40:]
            cv2.putText(frame, msg1, (box_x + 10, y_offset), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 1)
            y_offset += 22
            cv2.putText(frame, msg2, (box_x + 10, y_offset), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 1)
            y_offset += 22
        else:
            cv2.putText(frame, msg, (box_x + 10, y_offset), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 1)
            y_offset += 22

    # Quit hint
    cv2.putText(frame, "Press 'q' to quit", (w - 200, h - 10), cv2.FONT_HERSHEY_PLAIN, 1.4, (200, 200, 200), 2)

    # Show window
    cv2.imshow("Smart Gesture Dashboard", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
