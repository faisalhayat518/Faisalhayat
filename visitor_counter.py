import cv2
import mediapipe as mp
import face_recognition
import numpy as np
import os
import pandas as pd
from datetime import datetime, timedelta

# Paths
STAFF_DIR = "staff_images"
LOG_FILE = "visitor_log.csv"
ATTENDANCE_FILE = "staff_attendance.csv"

# Load MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

# Load Staff Images and Encode Faces
def load_staff():
    staff_encodings = []
    staff_names = []
    if not os.path.exists(STAFF_DIR):
        os.makedirs(STAFF_DIR)

    for file in os.listdir(STAFF_DIR):
        if file.endswith(".jpg") or file.endswith(".png"):
            path = os.path.join(STAFF_DIR, file)
            image = face_recognition.load_image_file(path)
            encoding = face_recognition.face_encodings(image)
            if encoding:
                staff_encodings.append(encoding[0])
                staff_names.append(os.path.splitext(file)[0])
    
    return staff_encodings, staff_names

# Initialize staff data
staff_encodings, staff_names = load_staff()

# Function to mark attendance
def mark_attendance(name):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df = pd.DataFrame([[name, now]], columns=["Staff Name", "Timestamp"])
    
    if not os.path.exists(ATTENDANCE_FILE):
        df.to_csv(ATTENDANCE_FILE, index=False)
    else:
        df.to_csv(ATTENDANCE_FILE, mode='a', header=False, index=False)

# Function to log visitor count
def log_visitor_count(count):
    now = datetime.now().strftime('%Y-%m-%d')
    df = pd.DataFrame([[now, count]], columns=["Date", "Visitors"])
    
    if not os.path.exists(LOG_FILE):
        df.to_csv(LOG_FILE, index=False)
    else:
        df.to_csv(LOG_FILE, mode='a', header=False, index=False)

# Function to recognize staff using face distance
def recognize_staff(face_encodings):
    recognized_staff = set()
    
    for encoding in face_encodings:
        if staff_encodings:
            distances = face_recognition.face_distance(staff_encodings, encoding)
            min_distance = min(distances)
            if min_distance < 0.5:  # Adjust threshold for better matching
                matched_idx = np.argmin(distances)
                recognized_staff.add(staff_names[matched_idx])
    
    return recognized_staff

# Open CCTV Camera
cap = cv2.VideoCapture(0)  # Change this to your CCTV camera feed

# Variables
daily_attendance_marked = False
visitor_records = []  # List to store (encoding, timestamp)
visitor_count = 0
VISITOR_TIMEOUT = timedelta(minutes=5)  # Recount visitors after 5 minutes
FACE_DISTANCE_THRESHOLD = 0.6  # Threshold for face matching

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Detect faces using face_recognition
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    # Recognize staff
    recognized_staff = recognize_staff(face_encodings)

    # Mark attendance at store opening (First detection of staff)
    if not daily_attendance_marked and recognized_staff:
        for staff in recognized_staff:
            mark_attendance(staff)
        daily_attendance_marked = True  # Ensure attendance is marked only once per day

    # Count non-staff visitors uniquely using time-based tracking
    current_time = datetime.now()
    
    for encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
        # Check if the person is a staff member
        if any(face_recognition.compare_faces(staff_encodings, encoding, tolerance=0.5)):
            continue  # Skip staff members

        # Check if this visitor was seen recently
        seen_before = False
        for stored_encoding, last_seen_time in visitor_records:
            distance = face_recognition.face_distance([stored_encoding], encoding)[0]
            if distance < FACE_DISTANCE_THRESHOLD and (current_time - last_seen_time) < VISITOR_TIMEOUT:
                seen_before = True
                break  # Ignore this face since it's a repeat

        if not seen_before:
            # New visitor detected
            visitor_records.append((encoding, current_time))
            visitor_count += 1

            # Draw bounding box around visitors
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.putText(frame, "Visitor", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # Display output
    cv2.putText(frame, f"Visitors: {visitor_count}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    cv2.imshow("Visitor Counter", frame)

    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Log visitor count at the end of the day
log_visitor_count(visitor_count)

# Cleanup
cap.release()
cv2.destroyAllWindows()
