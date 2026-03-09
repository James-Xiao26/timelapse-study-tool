import cv2
import time
import os
import asyncio
from datetime import datetime
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as TestCase

# --- CONFIGURATION ---
INTERVAL = 10
QUALITY = 50       # Slightly higher to keep text readable
WIDTH = 854
HEIGHT = 480

async def get_current_song():
    """Fetches the current song title and artist from the system."""
    try:
        sessions = await TestCase.request_async()
        current_session = sessions.get_current_session()
        if current_session:
            info = await current_session.try_get_media_properties_async()
            return f"{info.title} - {info.artist}"
    except:
        pass
    return "No Music Playing"

def get_dir_size(path):
    total = sum(os.path.getsize(os.path.join(path, f)) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)))
    return total / (1024 * 1024)

# 1. Start Command
while True:
    user_input = input("Type 'start' to begin: ").strip().lower()
    if user_input == 'start':
        break

# 2. Setup Folder
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
SAVE_FOLDER = f"timelapse_{timestamp}"
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

print(f"Recording to {SAVE_FOLDER}...")

try:
    count = 0
    while True:
        ret, frame = cap.read()
        if ret:
            # 3. Get Music Info
            song_info = asyncio.run(get_current_song())
            
            # 4. Draw text onto the frame
            # (Image, Text, Position (x,y), Font, Scale, Color (BGR), Thickness)
            cv2.putText(frame, f"Song: {song_info}", (20, HEIGHT - 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)

            filename = f"{SAVE_FOLDER}/frame_{count:04d}.jpg"
            cv2.imwrite(filename, frame, [int(cv2.IMWRITE_JPEG_QUALITY), QUALITY])
            
            print(f"Saved: {filename} | Music: {song_info}")
            count += 1
        
        time.sleep(INTERVAL)

except KeyboardInterrupt:
    print("\nTimelapse stopped.")
finally:
    cap.release()
