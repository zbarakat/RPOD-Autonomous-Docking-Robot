import cv2
import time
from pathlib import Path
from picamera2 import Picamera2

aruco = cv2.aruco
dictionary = aruco.getPredefinedDictionary(
    aruco.DICT_APRILTAG_36h11
)

# Compatible with older and newer OpenCV versions
if hasattr(aruco, "ArucoDetector"):
    detector = aruco.ArucoDetector(dictionary)
    def detect(image):
        return detector.detectMarkers(image)
else:
    def detect(image):
        return aruco.detectMarkers(image, dictionary)

camera = Picamera2()
camera.configure(camera.create_preview_configuration(
    main={"size": (640, 480), "format": "RGB888"}
))
camera.start()
time.sleep(2)

print("Searching for AprilTag ID 0...")
output = Path.home() / "ArduCam/AprilTag/detection.jpg"

try:
    deadline = time.monotonic() + 30

    while time.monotonic() < deadline:
        frame = camera.capture_array()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = detect(gray)

        if ids is not None and 0 in ids.flatten():
            index = list(ids.flatten()).index(0)
            points = corners[index][0]
            cx, cy = points.mean(axis=0)

            aruco.drawDetectedMarkers(frame, corners, ids)
            cv2.imwrite(str(output), frame)

            print("APRILTAG DETECTED!")
            print("Tag ID: 0")
            print(f"Center: ({cx:.1f}, {cy:.1f}) pixels")
            print(f"Saved: {output}")
            break
    else:
        print("No tag found. Try moving closer or improving lighting.")
finally:
    camera.stop()
