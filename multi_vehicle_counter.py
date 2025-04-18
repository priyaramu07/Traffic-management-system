import cv2
import numpy as np
import time
import mysql.connector

# Database connection
db = mysql.connector.connect(
    host="host name",
    user="user name",
    password="your password",
    database="multi_vehicle_data"
)
cursor = db.cursor()

# Load separate videos for each lane
video_paths = ["lane2.mp4", "lane1.mp4", "lane3.mp4", "lane4.mp4"]
videos = [cv2.VideoCapture(path) for path in video_paths]

# Parameters
MIN_WIDTH_RECT = 80
MIN_HEIGHT_RECT = 80
COUNT_LINE_POSITION = 550
OFFSET = 6

# Background subtractors
bg_subtractors = [cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=40) for _ in range(4)]

# Trackers
vehicles_list = [{} for _ in range(4)]
vehicle_ids = [0] * 4

# Counters
forward_counters = [0] * 4
backward_counters = [0] * 4
last_forward_counts = [0] * 4
last_backward_counts = [0] * 4
start_times = [time.time()] * 4

# Get center of bounding box
def get_center(x, y, w, h):
    return x + int(w / 2), y + int(h / 2)

# Start main loop
while True:
    frames = []
    for i in range(4):
        ret, frame = videos[i].read()
        if not ret:
            frames.append(np.zeros((640, 480, 3), dtype=np.uint8))  # Black frame if video ends
            continue

        # Preprocessing
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (3, 3), 5)
        img_sub = bg_subtractors[i].apply(blur)
        dilated = cv2.dilate(img_sub, np.ones((5, 5)))
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        processed = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel)
        processed = cv2.morphologyEx(processed, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(processed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cv2.line(frame, (25, COUNT_LINE_POSITION), (1200, COUNT_LINE_POSITION), (255, 127, 0), 3)

        new_detections = []
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            if w >= MIN_WIDTH_RECT and h >= MIN_HEIGHT_RECT:
                center = get_center(x, y, w, h)
                new_detections.append(center)

        updated_vehicles = {}
        for center in new_detections:
            matched = False
            for v_id, v_pos in vehicles_list[i].items():
                if abs(center[0] - v_pos[0]) < 50 and abs(center[1] - v_pos[1]) < 50:
                    updated_vehicles[v_id] = center
                    matched = True

                    if v_pos[1] > center[1]:  # Moving up (forward)
                        color = (0, 0, 255)
                        if COUNT_LINE_POSITION - OFFSET < center[1] < COUNT_LINE_POSITION + OFFSET:
                            forward_counters[i] += 1
                    elif v_pos[1] < center[1]:  # Moving down (backward)
                        color = (255, 0, 0)
                        if COUNT_LINE_POSITION - OFFSET < center[1] < COUNT_LINE_POSITION + OFFSET:
                            backward_counters[i] += 1

                    cv2.rectangle(frame, (center[0] - 40, center[1] - 40), (center[0] + 40, center[1] + 40), color, 2)
                    cv2.circle(frame, center, 4, color, -1)
                    break

            if not matched:
                updated_vehicles[vehicle_ids[i]] = center
                vehicle_ids[i] += 1

        vehicles_list[i] = updated_vehicles

        # Display counts
        cv2.putText(frame, f"Lane {i+1}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 4)
        cv2.putText(frame, f"FWD: {forward_counters[i]}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        cv2.putText(frame, f"BWD: {backward_counters[i]}", (50, 140), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

        # Display each lane in its own window
        cv2.imshow(f"Lane {i+1} - Vehicle Detection", frame)

    # Insert data into DB every 10 seconds
    global_elapsed = time.time() - min(start_times)
    if global_elapsed >= 10:
        lane_data = []
        for i in range(4):
            f = forward_counters[i] - last_forward_counts[i]
            b = backward_counters[i] - last_backward_counts[i]
            lane_data.extend([f, b])
            last_forward_counts[i] = forward_counters[i]
            last_backward_counts[i] = backward_counters[i]
            start_times[i] = time.time()

        sql = """
        INSERT INTO lane_vehicle_count (
            lane1_fwd, lane1_bwd,
            lane2_fwd, lane2_bwd,
            lane3_fwd, lane3_bwd,
            lane4_fwd, lane4_bwd
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, tuple(lane_data))
        db.commit()
        print(f"[DB] Inserted: {lane_data}")

    # Exit on ENTER key
    if cv2.waitKey(1) == 13:
        break

# Release all
for cap in videos:
    cap.release()

cv2.destroyAllWindows()
cursor.close()
db.close()
