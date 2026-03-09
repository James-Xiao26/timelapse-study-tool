import cv2
import time
import os
import threading
import asyncio
import numpy as np
from datetime import datetime
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
from winsdk.windows.storage.streams import DataReader

# --- CONFIGURATION ---
INTERVAL = 10      
QUALITY = 50       
WIDTH = 854
HEIGHT = 480
THUMB_SIZE = 80   
FPS = 30           

# Global variables to store music info so the camera thread can grab them
current_song_name = "No Music Detected"
current_thumbnail = None

def fetch_music_worker():
    """Background worker that updates music info without stopping the camera."""
    global current_song_name, current_thumbnail
    
    async def get_info():
        try:
            sessions = await MediaManager.request_async()
            current_session = sessions.get_current_session()
            if not current_session: return "No Music", None
            
            info = await current_session.try_get_media_properties_async()
            song = f"{info.title} - {info.artist}"
            
            thumb = None
            if info.thumbnail:
                stream = await info.thumbnail.open_read_async()
                reader = DataReader(stream.get_input_stream_at(0))
                await reader.load_async(stream.size)
                data = bytes(reader.read_buffer(stream.size))
                thumb = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
            return song, thumb
        except:
            return "Searching...", None

    while True:
        try:
            current_song_name, current_thumbnail = asyncio.run(get_info())
        except:
            pass
        time.sleep(2) # Only check music every 2 seconds

# --- INITIALIZATION ---
desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
BASE_DIR = os.path.join(desktop, "Timelapses")
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
SAVE_FOLDER = os.path.join(BASE_DIR, f"timelapse_{timestamp}")

if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

# Start the music fetcher in a separate background thread
music_thread = threading.Thread(target=fetch_music_worker, daemon=True)
music_thread.start()

print(f"!!! ENGINE STARTED !!!", flush=True)
print(f"Saving frames to: {SAVE_FOLDER}", flush=True)

# Try different backends if the default fails
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
    cap = cv2.VideoCapture(0) # Fallback to default backend

cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

try:
    count = 0
    while True:
        # 1. Grab Frame (This is the priority)
        ret, frame = cap.read()
        
        if not ret or frame is None:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] CAMERA ERROR: Retrying...", flush=True)
            time.sleep(1)
            continue

        # 2. Process Frame
        frame = cv2.resize(frame, (WIDTH, HEIGHT))
        
        # Overlay music info collected from the background thread
        if current_thumbnail is not None:
            try:
                t_resized = cv2.resize(current_thumbnail, (THUMB_SIZE, THUMB_SIZE))
                frame[HEIGHT-THUMB_SIZE-10:HEIGHT-10, 10:10+THUMB_SIZE] = t_resized
            except: pass
        
        cv2.putText(frame, current_song_name, (THUMB_SIZE + 20, HEIGHT - 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

        # 3. Save to disk
        filename = os.path.join(SAVE_FOLDER, f"frame_{count:04d}.jpg")
        cv2.imwrite(filename, frame, [int(cv2.IMWRITE_JPEG_QUALITY), QUALITY])
        
        # 4. Success Signal
        print(f"Captured Frame {count} | {current_song_name}", flush=True)
        count += 1

        # 5. Wait for next interval
        time.sleep(INTERVAL)

except KeyboardInterrupt:
    print(f"\nClosing... Processing {count} images into video.", flush=True)
    images = sorted([img for img in os.listdir(SAVE_FOLDER) if img.endswith(".jpg")])
    
    if images:
        video_path = os.path.join(SAVE_FOLDER, "timelapse_result.mp4")
        out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'mp4v'), FPS, (WIDTH, HEIGHT))
        for img_name in images:
            img_path = os.path.join(SAVE_FOLDER, img_name)
            f = cv2.imread(img_path)
            if f is not None: out.write(f)
        out.release()
        print(f"VIDEO COMPLETE: {video_path}", flush=True)

finally:
    cap.release()
