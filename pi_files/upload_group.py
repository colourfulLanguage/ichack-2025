import time
import subprocess

SERVER_URL = f"http://0.0.0.0:5123/upload"

def capture_and_upload(category):
    filename = f"/home/pi/{category}.jpg"
    ffmpeg_command = f"ffmpeg -y -i udp://@:1234 -frames:v 1 {filename}"
    subprocess.run(ffmpeg_command, shell=True)

    print(f"Captured {category}")

capture_and_upload("fullbody-multiple")
