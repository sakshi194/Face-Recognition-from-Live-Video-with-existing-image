from flask import Flask, render_template, Response, request, jsonify, send_from_directory
import cv2
import face_recognition
import threading
import os
import base64
import pickle
import atexit

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
capture_running = True

# Load Haar cascade classifier for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# File paths for storing face encodings and names
encodings_file = os.path.join(app.config['UPLOAD_FOLDER'], 'encodings.pkl')
names_file = os.path.join(app.config['UPLOAD_FOLDER'], 'names.pkl')

# Function to save face encodings and names to disk
def save_face_data():
    with open(encodings_file, 'wb') as f:
        pickle.dump(known_face_encodings, f)
    with open(names_file, 'wb') as f:
        pickle.dump(known_face_names, f)

# Function to load face encodings and names from disk
def load_face_data():
    if os.path.exists(encodings_file) and os.path.exists(names_file):
        with open(encodings_file, 'rb') as f:
            encodings = pickle.load(f)
        with open(names_file, 'rb') as f:
            names = pickle.load(f)
        return encodings, names
    return [], []

# Initial known face encodings and names
known_face_encodings, known_face_names = load_face_data()

# Global variables for the camera frame, recognized names, and the lock
current_frame = None
recognized_names = []
frame_lock = threading.Lock()

# Function to add new face encodings
def add_face_encoding(name, image_file):
    image = face_recognition.load_image_file(image_file)
    encoding = face_recognition.face_encodings(image)
    if encoding:
        known_face_encodings.append(encoding[0])
        known_face_names.append(name)
        save_face_data()

# Open the primary camera
camera = cv2.VideoCapture(0)

# Set camera resolution to a higher value
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

def capture_frames():
    global current_frame, capture_running
    while capture_running:
        success, frame = camera.read()
        if success:
            with frame_lock:
                current_frame = frame


# Start the frame capture thread
frame_thread = threading.Thread(target=capture_frames)
frame_thread.daemon = True
frame_thread.start()

def gen_frames():
    global recognized_names
    while True:
        # with frame_lock:
        #     frame = current_frame.copy() if current_frame is not None else None

        # if frame is None:
        #     continue   
        with frame_lock:
            if current_frame is None:
                continue
            frame = current_frame.copy()                                                        

        # Resize frame to a smaller size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Detect faces and face encodings
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            # name = "Unknown"
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match = face_distances.argmin()
            if face_distances[best_match] < 0.45:
                name = known_face_names[best_match]
            else:
                name = "Unknown"

            face_names.append(name)

        recognized_names = face_names

        # Draw rectangles around faces and put the name below each face
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/2 size
            top *= 2
            right *= 2
            bottom *= 2
            left *= 2
            cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2)
            cv2.putText(frame, name, (left, bottom + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index1():
    global camera, capture_running

    # Re-open backend camera only if closed
    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(0)
        capture_running = True

        threading.Thread(target=capture_frames, daemon=True).start()

    photos = [f for f in os.listdir(app.config['UPLOAD_FOLDER'])
              if f.endswith(('.png', '.jpg', '.jpeg'))]

    return render_template('index1.html', photo_count=len(photos), photos=photos)


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/recognized_names')
def get_recognized_names():
    global recognized_names
    return jsonify(recognized_names)


import time
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    global camera, capture_running

    # STOP BACKEND CAMERA COMPLETELY
    if camera is not None:
        capture_running = False
        try:
            camera.release()
        except:
            pass

    if request.method == 'POST':
        data = request.get_json()
        name = data['name']
        image_data = data['image'].split(",")[1]
        image_data = base64.b64decode(image_data)

        filename = f"{name}_{int(time.time())}.png"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        with open(filepath, "wb") as f:
            f.write(image_data)

        add_face_encoding(name, filepath)

        return jsonify({"success": True})

    return render_template('upload.html')



@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)

# Release the video capture device when the app stops
def cleanup():
    camera.release()
    cv2.destroyAllWindows()

atexit.register(cleanup)