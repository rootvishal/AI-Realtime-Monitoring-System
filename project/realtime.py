import cv2
import face_recognition
import pickle
import numpy as np
from datetime import datetime
import mysql.connector
from shared_frame import get_shared_frame  # Import shared frame getter

# Database connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Vishal@2003",
    database="ai_monitoring"
)
cursor = conn.cursor()

# Load trained model
with open("face_recognition_model.pkl", 'rb') as f:
    clf, classes = pickle.load(f)

# Define periods (1-hour slots)
periods = {
    1: (10, 11), 2: (11, 12), 3: (12, 13), 4: (13, 14),
    5: (14, 15), 6: (17, 18)
}

def get_current_period():
    current_hour = datetime.now().hour
    for period, (start, end) in periods.items():
        if start <= current_hour < end:
            return period
    return None

def mark_attendance(student_id):
    today = datetime.now().strftime("%Y-%m-%d")
    current_period = get_current_period()

    if current_period is None:
        return

    cursor.execute("SELECT * FROM attendance WHERE student_id=%s AND date=%s AND period=%s",
                   (student_id, today, current_period))
    result = cursor.fetchone()

    if not result:
        cursor.execute("INSERT INTO attendance (student_id, date, period, status) VALUES (%s, %s, %s, %s)",
                       (student_id, today, current_period, "Present"))
        conn.commit()
        print(f"Attendance marked for Student ID: {student_id} in Period {current_period}")

def run_attendance_detection():
    print("[INFO] Attendance detection started.")
    while True:
        frame = get_shared_frame()
        if frame is None:
            continue

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        face_locations = face_recognition.face_locations(small_frame)
        face_encodings = face_recognition.face_encodings(small_frame, face_locations)

        for (top, right, bottom, left), face_enc in zip(face_locations, face_encodings):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            proba = clf.predict_proba([face_enc])[0]
            confidence = np.max(proba)
            if confidence > 0.8:
                student_id = classes[np.argmax(proba)]
                mark_attendance(student_id)
            else:
                student_id = "Unknown"

            # Optional: Visual debug
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.putText(frame, student_id, (left + 6, bottom - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Optional display
        # cv2.imshow("Attendance", frame)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

# Uncomment if using standalone
# run_attendance_detection()

# Close database connection gracefully (when used as standalone)
# cursor.close()
# conn.close()
