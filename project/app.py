from flask import Flask, request, jsonify, render_template,send_from_directory,send_file, redirect, url_for, session
import mysql.connector
import os
import base64
from datetime import datetime
from flask import Flask, render_template, Response
import cv2
import subprocess
import threading


#from realtime0 import mark_attendance
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",  # DB username
    password="Vishal@2003",  # DB password
    database="ai_monitoring"
)
cursor = db.cursor()
# Replace this with  RTSP stream URL
RTSP_URL = "rtsp://username:password@camera_ip:port/stream"

camera = cv2.VideoCapture(RTSP_URL)

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

#route for voilance 
VIDEO_FOLDER = r'C:\Project_version_1\project\static\detected_clips'

@app.route("/violence")
def violence_page():
    videos = [f for f in os.listdir(VIDEO_FOLDER) if f.endswith(".mp4")]
    return render_template("voilance.html", videos=videos)

@app.route("/video/<filename>")
def stream_video(filename):
    video_path = os.path.join(VIDEO_FOLDER, filename)
    if os.path.exists(video_path):
        return send_file(video_path, mimetype='video/mp4')
    else:
        return "Video not found", 404
@app.route('/cctv-live')
def cctv_live():
    return render_template('admin_dashboard_cctv_live.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')    
        
@app.route('/')
def home():
    return render_template('index.html')  # Home page

# Serve the registration HTML page
@app.route('/registration')
def registration():
    return render_template('registration.html')  # Registration page

# Serve the user login page
@app.route('/user_login')
def user_login():
    return render_template('user_login.html')  # User login page

@app.route('/student_profile/<string:erp_id>')
def student_profile(erp_id):
    try:
        # Fetch user data based on ERP ID
        user_query = "SELECT full_name, dob, mobile FROM users WHERE erp_id = %s"
        cursor.execute(user_query, (erp_id,))
        user = cursor.fetchone()

        if user:
            # Fetch attendance count for the student
            attendance_query = "SELECT COUNT(*) FROM attendance WHERE student_id = %s"
            cursor.execute(attendance_query, (erp_id,))
            attendance_count = cursor.fetchone()[0]  # Fetch count value

            total_classes = 6  # Change this dynamically if needed

            # Prepare the student data dictionary
            student_data = {
                'full_name': user[0],
                'dob': user[1],
                'mobile': user[2],
                'erp_id': erp_id,
                'attendance_count': attendance_count,
                'total_classes': total_classes
            }

            # Logging the student data for debugging (optional)
            print(student_data)

            # Render the student profile page
            return render_template('student_profile.html', student_data=student_data)
        else:
            # If the user is not found
            return "User not found", 404
    except Exception as e:
        # Handle any database or other exceptions
        return f"An error occurred: {e}", 500

# Serve the admin login page
@app.route('/admin_login')
def admin_login_page():
    return render_template('admin_login.html')  # Admin login page

# Handle user registration
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    full_name = data['fullName']
    dob = data['dob']
    mobile = data['mobile']
    erp_id = data['erpId']
    password = data['password']
    
    # Insert user info into MySQL
    query = "INSERT INTO users (full_name, dob, mobile, erp_id, password) VALUES (%s, %s, %s, %s, %s)"
    values = (full_name, dob, mobile, erp_id, password)
    cursor.execute(query, values)
    db.commit()
    
    # +folder to save photos and videos for each user
    user_folder = f"userdata/{erp_id}"
    os.makedirs(user_folder, exist_ok=True)
    
    # Save photos
    photos = data.get('photos', [])
    for i, photo in enumerate(photos):
        photo_data = base64.b64decode(photo)  # Decode base64 to binary
        photo_path = os.path.join(user_folder, f"{erp_id}_photo_{i + 1}.png")
        with open(photo_path, "wb") as photo_file:
            photo_file.write(photo_data)
    
    # Save video
    video_data = base64.b64decode(data['video'])  # Decode base64 to binary
    video_path = os.path.join(user_folder, f"{erp_id}_video.webm")
    with open(video_path, "wb") as video_file:
        video_file.write(video_data)
    
    return jsonify({"status": "success", "message": "Registration successful!"})

# Handle user login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    erp_id = data['erpId']
    password = data['password']

    # Query the database to check if the user exists
    query = "SELECT full_name, dob, mobile, password FROM users WHERE erp_id = %s"
    cursor.execute(query, (erp_id,))
    result = cursor.fetchone()

    if result is None:
        return jsonify({"status": "error", "message": "ERP ID not found!"}), 400

    stored_password = result[3]
    if stored_password == password:
        # Store login session
        session['user'] = erp_id
        return jsonify({"status": "success", "redirect_url": url_for('student_profile', erp_id=erp_id)}), 200
    else:
        return jsonify({"status": "error", "message": "Invalid password!"}), 400

# Handle admin login
@app.route('/admin_login', methods=['POST'])
def admin_login():
    data = request.json
    admin_id = data['adminId']
    password = data['password']

    # Query to check if admin credentials exist
    query = "SELECT password FROM admin_data WHERE username = %s"
    cursor.execute(query, (admin_id,))
    result = cursor.fetchone()

    if result is None:
        return jsonify({"status": "error", "message": "Admin ID not found!"}), 400

    stored_password = result[0]
    if stored_password == password:
        # Store admin session
        session['admin_username'] = admin_id
        return jsonify({"status": "success", "redirect_url": url_for('admin_dashboard')}), 200
    else:
        return jsonify({"status": "error", "message": "Invalid admin password!"}), 400
    
@app.route('/admin_dashboard_attendance')
def admin_dashboard_attendance():
    if 'admin_username' not in session:
        return redirect(url_for('admin_login_page'))

    # Assuming you want to fetch the attendance records
    query = "SELECT * FROM attendance"  # Adjust this as per your actual attendance table
    cursor.execute(query)
    attendance_records = cursor.fetchall()

    return render_template('admin_dashboard_attendance.html', attendance_records=attendance_records)

# Admin dashboard page
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_username' not in session:
        return redirect(url_for('admin_login_page'))

    # Fetch admin data
    admin_username = session['admin_username']
    query = "SELECT username FROM admin_data WHERE username = %s"
    cursor.execute(query, (admin_username,))
    admin_data = cursor.fetchone()
    #mark_attendance()

    admin_name = admin_data[0] if admin_data else "Admin"

    # Fetch registered students from users table
    cursor.execute("SELECT full_name, erp_id, dob, mobile FROM users")
    students = cursor.fetchall()

    return render_template('admin_dashboard.html', admin_name=admin_name, students=students)


# Fetch attendance records based on date and period
@app.route('/attendance', methods=['GET'])
def get_attendance():
    date = request.args.get('date')
    period = request.args.get('period')
    
    query = "SELECT student_id, status FROM attendance WHERE date = %s AND period = %s"
    cursor.execute(query, (date, period))
    records = cursor.fetchall()

    # Return attendance records as JSON
    return jsonify([{
        'student_id': record[0],
        'status': record[1]
    } for record in records])


# Update attendance records
@app.route('/update_attendance', methods=['POST'])
def update_attendance():
    data = request.json
    student_id = data['student_id']
    date = data['date']
    period = data['period']
    status = data['status']

    # Check if attendance record exists
    query = "SELECT id FROM attendance WHERE student_id = %s AND date = %s AND period = %s"
    cursor.execute(query, (student_id, date, period))
    existing_record = cursor.fetchone()

    if existing_record:
        # Update existing record
        update_query = "UPDATE attendance SET status = %s WHERE id = %s"
        cursor.execute(update_query, (status, existing_record[0]))
    else:
        # Insert new record
        insert_query = "INSERT INTO attendance (student_id, date, period, status) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (student_id, date, period, status))

    db.commit()
    return jsonify({"status": "success", "message": "Attendance updated successfully!"})

# Route to display class page with student data
@app.route('/class')
def class_page():
    # Fetch student data (including phone number instead of status)
    query = "SELECT id, name, class, ERP_id, phone_number FROM students"
    cursor.execute(query)
    students = cursor.fetchall()

    return render_template('admin_dashboard_class.html', students=students)



if __name__ == '__main__':
   
   
    app.run(debug=True)
