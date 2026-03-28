import cv2
import face_recognition
import numpy as np
import threading
import time
import os
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

# Global data
known_face_encodings = []
known_face_names = []
team_members = []

# Global state protected by a lock
output_frame = None
lock = threading.Lock()
door_locked = True
last_visited = [] # List of dicts: {"time": "HH:MM:SS", "name": "Name"}
visit_cooldowns = {} # name -> timestamp
current_faces_in_frame = []
last_seen_known_time = 0 # Timestamp of the last time a known person was exclusively in frame

# New state for decoupled fast frame streaming
raw_frame = None
raw_frame_lock = threading.Lock()
current_detections = [] # list of tuples: ((top, right, bottom, left), name)

def load_team():
    """Loads team members from team.txt and encodes their faces"""
    global known_face_encodings, known_face_names, team_members
    known_face_encodings = []
    known_face_names = []
    team_members = []
    
    if not os.path.exists("team.txt"):
        with open("team.txt", "w") as f:
            f.write("raghav,raghav.jpg\n")
            
    with open("team.txt", "r") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            if "," in line:
                name, img_path = line.split(",", 1)
                name = name.strip()
                img_path = img_path.strip()
                team_members.append((name, img_path))
                if os.path.exists(img_path):
                    try:
                        img = face_recognition.load_image_file(img_path)
                        encodings = face_recognition.face_encodings(img)
                        if len(encodings) > 0:
                            known_face_encodings.append(encodings[0])
                            known_face_names.append(name.capitalize())
                            print(f"Loaded {name} from {img_path}")
                        else:
                            print(f"No face found in {img_path}")
                    except Exception as e:
                        print(f"Error loading {img_path}: {e}")
                else:
                    print(f"Warning: {img_path} not found")

def capture_video():
    """Background thread running camera capture as fast as possible for smooth video"""
    global output_frame, raw_frame, raw_frame_lock, current_detections
    global door_locked, current_faces_in_frame, lock
    
    video_capture = cv2.VideoCapture(1)
    if not video_capture.isOpened():
        video_capture = cv2.VideoCapture(0)
        
    # Request 60 FPS from the camera (if supported)
    video_capture.set(cv2.CAP_PROP_FPS, 60)
        
    while True:
        ret, frame = video_capture.read()
        if not ret:
            time.sleep(0.01)
            continue
            
        with raw_frame_lock:
            # Drop a raw frame for the background face recognition thread to pick up
            raw_frame = frame.copy()
            
        with lock:
            detections = current_detections.copy()
            dl = door_locked
            
        # Draw bounding boxes
        for (top, right, bottom, left), name in detections:
            # Green (0,255,0) for known, Red (0,0,255) for unknown
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            
        # Add a subtle visual indicator of door state on the feed itself
        indicator_text = "DOOR LOCKED" if dl else "DOOR OPENED"
        indicator_col = (0, 0, 255) if dl else (0, 255, 0)
        cv2.putText(frame, indicator_text, (20, 40), cv2.FONT_HERSHEY_DUPLEX, 1.0, indicator_col, 2)
        
        # Encode as JPEG
        ret_enc, buffer = cv2.imencode('.jpg', frame)
        if ret_enc:
            with lock:
                output_frame = buffer.tobytes()

def process_faces():
    """Background thread running CPU-intensive face recognition"""
    global raw_frame, raw_frame_lock, current_detections
    global door_locked, last_visited, current_faces_in_frame, lock, visit_cooldowns, last_seen_known_time
    
    TOLERANCE = 0.6
    
    while True:
        with raw_frame_lock:
            if raw_frame is None:
                frame_to_process = None
            else:
                frame_to_process = raw_frame.copy()
                
        if frame_to_process is None:
            time.sleep(0.05)
            continue
            
        # Resize frame of video to 1/4 size
        small_frame = cv2.resize(frame_to_process, (0, 0), fx=0.25, fy=0.25)
        # Convert BGR to RGB exactly as original
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        current_faces_temp = []
        frame_should_unlock = False 
        detections_temp = []
        
        for face_encoding, face_location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=TOLERANCE)
            name = "Unknown"
            
            if known_face_encodings:
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                    
            current_faces_temp.append(name)
            
            # Scale back up face locations since we resized to 1/4 size
            top, right, bottom, left = face_location
            top *= 4; right *= 4; bottom *= 4; left *= 4
            detections_temp.append(((top, right, bottom, left), name))
            
            # Door Logic Rules
            if name != "Unknown":
                # Known person found in this frame
                frame_should_unlock = True
                
                now = time.time()
                # Add to last visited with 30s cooldown per person
                if name not in visit_cooldowns or (now - visit_cooldowns[name]) > 30:
                    visit_cooldowns[name] = now
                    with lock:
                        dt_str = datetime.now().strftime("%I:%M:%S %p")
                        last_visited.insert(0, {"name": name, "time": dt_str})
                        if len(last_visited) > 10:
                            last_visited.pop()

        # Final decision for this frame
        # We only really want to unlock if there are NO unknown people and at least one known person.
        actually_recognized = frame_should_unlock and ("Unknown" not in current_faces_temp)
        
        now = time.time()
        if actually_recognized:
            last_seen_known_time = now
                            
        with lock:
            current_detections = detections_temp
            current_faces_in_frame = current_faces_temp
            
            # Implementation of the 1-second delay
            if actually_recognized:
                door_locked = False
            else:
                # If we're not seeing a known person (or seeing an unknown person), 
                # check if the 1-second "grace period" has expired.
                if (now - last_seen_known_time) > 1.0:
                    door_locked = True
                else:
                    # Keep it unlocked for that 1 second buffer
                    door_locked = False
                
        # Small delay to reduce CPU unneeded strain
        time.sleep(0.01)

def generate_mjpeg():
    """Generator for streaming JPEG frames"""
    global output_frame, lock
    while True:
        with lock:
            frame = output_frame
            
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            time.sleep(0.05)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    load_team()
    
    t1 = threading.Thread(target=capture_video)
    t1.daemon = True
    t1.start()
    
    t2 = threading.Thread(target=process_faces)
    t2.daemon = True
    t2.start()
    
    yield
    # Shutdown logic (optional)

app = FastAPI(lifespan=lifespan)

# Make sure templates directory exists for Jinja
os.makedirs("templates", exist_ok=True)
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root(request: Request):
    # Pass the listed team members to the Jinja template
    # Use keyword arguments to avoid parameter order issues in different FastAPI versions
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"team": [name.capitalize() for name, _ in team_members]}
    )

@app.get("/video_feed")
async def video_feed():
    # Continuous MJPEG stream
    return StreamingResponse(generate_mjpeg(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/status")
async def status():
    # JSON polling endpoint for door status & logs
    global door_locked, current_faces_in_frame, last_visited, lock
    with lock:
        return {
            "door_locked": door_locked,
            "current_faces": current_faces_in_frame,
            "last_visited": last_visited
        }

if __name__ == "__main__":
    # Ensure port 8000 is used
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)