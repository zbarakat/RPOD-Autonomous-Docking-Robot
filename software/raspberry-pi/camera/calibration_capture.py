#!/usr/bin/env python3
"""Headless IMX219 chessboard photo capture dashboard for RPOD project.
Use SSH tunnel: ssh -N -L 8001:127.0.0.1:8001 robot@romi-pi.local
Then browser: http://localhost:8001/
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
import time
import cv2
from picamera2 import Picamera2

PATTERN = (9, 6)  # INNER chessboard corners: 10 x 7 colored squares
OUT = Path.home() / "ArduCam" / "Calibration" / "images"
OUT.mkdir(parents=True, exist_ok=True)
LOCK = threading.Lock()
LATEST = None
LATEST_VALID = False
COUNT = len(list(OUT.glob("cal_*.jpg")))
FLAGS = cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE | cv2.CALIB_CB_FAST_CHECK

camera = Picamera2()
camera.configure(camera.create_preview_configuration(
    main={"size": (640, 480), "format": "RGB888"}
))
camera.start()
time.sleep(2)

PAGE = """<!DOCTYPE html><html><head><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">
<title>RPOD Camera Calibration</title></head>
<body style=\"font-family:Arial;background:#131a22;color:white;text-align:center;max-width:760px;margin:20px auto\">
<h2>RPOD / Camera Calibration</h2>
<p>Show the entire 9x6-corner printed chessboard to the camera. Green = ready to capture.</p>
<img src=\"/video\" style=\"width:96%;max-width:640px;border:2px solid #45515b\">
<p><button style=\"font-size:20px;padding:12px 26px;cursor:pointer\" onclick=\"snap()\">Capture good view</button></p>
<p id=\"status\">Capture 15-25 sharp images at DIFFERENT angles and positions.</p>
<script>
async function snap(){let r=await fetch('/capture',{method:'POST'});document.getElementById('status').innerText=await r.text()}
</script></body></html>""".encode("utf-8")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(PAGE)))
            self.end_headers()
            self.wfile.write(PAGE)
            return
        if self.path != "/video":
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        while True:
            image = camera.capture_array()
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            good, corners = cv2.findChessboardCorners(gray, PATTERN, FLAGS)
            with LOCK:
                global LATEST, LATEST_VALID, COUNT
                LATEST = image.copy()
                LATEST_VALID = bool(good)
                count = COUNT
            if good:
                cv2.drawChessboardCorners(image, PATTERN, corners, good)
                status, color = f"CHESSBOARD FOUND - {count} saved", (20, 240, 65)
            else:
                status, color = f"SHOW FULL CHESSBOARD - {count} saved", (20, 110, 255)
            cv2.rectangle(image, (0, 0), (640, 35), (0, 0, 0), -1)
            cv2.putText(image, status, (8, 23), cv2.FONT_HERSHEY_SIMPLEX, .55, color, 2)
            ok, jpg = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 70])
            if ok:
                data = jpg.tobytes()
                try:
                    self.wfile.write(b"--frame\r\nContent-Type: image/jpeg\r\n" +
                                     f"Content-Length: {len(data)}\r\n\r\n".encode() +
                                     data + b"\r\n")
                except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
                    break
            time.sleep(.35)

    def do_POST(self):
        if self.path != "/capture":
            self.send_error(404)
            return
        global COUNT
        with LOCK:
            frame = None if LATEST is None else LATEST.copy()
            valid = LATEST_VALID
            if frame is not None and valid:
                # Never overwrite images from earlier capture sessions.
                existing = sorted(OUT.glob("cal_*.jpg"))
                idx = 1
                while (OUT / f"cal_{idx:03d}.jpg").exists():
                    idx += 1
                path = OUT / f"cal_{idx:03d}.jpg"
                if cv2.imwrite(str(path), frame):
                    COUNT = len(existing) + 1
                    msg = f"Saved {path.name} - total {COUNT}. Change viewpoint before next capture."
                else:
                    msg = "Could not save image - check SD storage."
            else:
                msg = "Board not detected. Move back so the entire grid is visible, then retry."
        body = msg.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass

server = ThreadingHTTPServer(("127.0.0.1", 8001), Handler)
try:
    print("Calibration capture running at http://localhost:8001/ through SSH tunnel")
    print(f"Images will be saved in: {OUT}")
    print("Use Ctrl+C to stop")
    server.serve_forever()
except KeyboardInterrupt:
    print("\nStopping camera")
finally:
    server.server_close()
    camera.stop()
