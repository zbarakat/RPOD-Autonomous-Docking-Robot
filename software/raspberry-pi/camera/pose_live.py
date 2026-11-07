#!/usr/bin/env python3
"""Calibrated live AprilTag 36h11 ID 0 relative pose, Pi Zero 2 W.
Windows SSH tunnel: ssh -N -L 8002:127.0.0.1:8002 robot@romi-pi.local
Open http://localhost:8002 in Windows browser.
Adjust TAG_SIZE_M to your measured OUTER black square width.
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import math
import time
import cv2
import numpy as np
from picamera2 import Picamera2

TAG_SIZE_M = 0.100  # Printed black outer square; CHANGE if ruler says otherwise!
CAL = Path.home() / "ArduCam/Calibration/camera_640x480.npz"
if not CAL.exists():
    raise SystemExit(f"Missing calibration file {CAL}. Run calibrate_camera.py first.")
with np.load(CAL) as z:
    K = z["K"].copy()
    dist = z["dist"].copy()
    width, height = int(z["width"]), int(z["height"])
if (width, height) != (640, 480):
    raise SystemExit(f"Expected calibration for 640x480, got {width}x{height}")

dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
aruco = cv2.aruco
if hasattr(aruco, "ArucoDetector"):
    detector = aruco.ArucoDetector(dictionary)
    detect = detector.detectMarkers
else:
    detect = lambda image: aruco.detectMarkers(image, dictionary)

h = TAG_SIZE_M / 2
# Correct OpenCV IPPE_SQUARE ordering: top-left, top-right, bottom-right, bottom-left
object_corners = np.array([[-h, h, 0], [h, h, 0], [h, -h, 0], [-h, -h, 0]], np.float32)
camera = Picamera2()
camera.configure(camera.create_preview_configuration(
    main={"size": (640, 480), "format": "RGB888"}
))
camera.start()
time.sleep(2)

PAGE = b'''<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>RPOD Dock Pose</title></head><body style="background:#111923;color:white;text-align:center;font-family:Arial">
<h2>RPOD | Live Dock Position</h2>
<img src="/video" style="width:96%;max-width:800px">
<p>X=right (+), Z=forward (+), both relative to camera lens; bearing=direction to target.</p>
<p>Tag yaw estimates how the dock face is turned; it can be noisy when near front-on.</p>
<p>Values depend on printed tag size and camera calibration. Not yet robot-frame coordinates.</p>
</body></html>'''

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
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
        next_log = 0
        while True:
            frame = camera.capture_array()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners, ids, _ = detect(gray)
            cv2.drawMarker(frame, (320, 240), (255, 0, 0), cv2.MARKER_CROSS, 19, 2)
            lines = ["SEARCHING FOR APRILTAG ID 0"]
            if ids is not None and 0 in ids.flatten():
                i = np.flatnonzero(ids.flatten() == 0)[0]
                pts = np.ascontiguousarray(corners[i].reshape(4, 2), dtype=np.float32)
                ok, rvec, tvec = cv2.solvePnP(
                    object_corners, pts, K, dist, flags=cv2.SOLVEPNP_IPPE_SQUARE
                )
                if ok and float(tvec[2, 0]) > 0:
                    x, y, z = (float(v) for v in tvec.reshape(3))
                    distance = math.sqrt(x*x + y*y + z*z)
                    bearing = math.degrees(math.atan2(x, z))
                    R, _ = cv2.Rodrigues(rvec)
                    n = R[:, 2]  # tag front-facing normal in camera coordinates
                    yaw = math.degrees(math.atan2(float(n[0]), float(-n[2])))
                    lines = [f"TAG 0  |  RANGE {distance:.3f} m  |  DEPTH Z {z:.3f} m",
                             f"X (RIGHT) {x:+.3f} m   Y (DOWN) {y:+.3f} m",
                             f"BEARING {bearing:+.1f} deg   TAG FACE YAW {yaw:+.1f} deg"]
                    aruco.drawDetectedMarkers(frame, [corners[i]], np.array([[0]], dtype=np.int32))
                    cv2.drawFrameAxes(frame, K, dist, rvec, tvec, TAG_SIZE_M * .45, 2)
                    if time.monotonic() >= next_log:
                        print(" | ".join(lines), flush=True)
                        next_log = time.monotonic() + 3
            cv2.rectangle(frame, (0, 0), (640, 92), (0, 0, 0), -1)
            for j, line in enumerate(lines):
                cv2.putText(frame, line, (6, 25 + j * 27), cv2.FONT_HERSHEY_SIMPLEX,
                            .48, (0, 255, 100), 1, cv2.LINE_AA)
            encoded, jpg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            if encoded:
                data = jpg.tobytes()
                try:
                    self.wfile.write(b"--frame\r\nContent-Type: image/jpeg\r\n" +
                                     f"Content-Length: {len(data)}\r\n\r\n".encode() +
                                     data + b"\r\n")
                except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
                    break
            time.sleep(.35)

    def log_message(self, fmt, *args):
        pass

server = HTTPServer(("127.0.0.1", 8002), Handler)
try:
    print("Calibrated RPOD pose tracking: http://localhost:8002 via SSH tunnel")
    print(f"Using marker black outer width: {TAG_SIZE_M * 1000:.1f} mm")
    print("Ctrl+C to stop")
    server.serve_forever()
except KeyboardInterrupt:
    print("\nStopping")
finally:
    server.server_close()
    camera.stop()
