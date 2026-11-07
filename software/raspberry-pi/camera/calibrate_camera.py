#!/usr/bin/env python3
"""Estimate 640x480 camera intrinsics from RPOD chessboard photos."""
from pathlib import Path
import cv2
import numpy as np

PATTERN = (9, 6)  # 9 x 6 INNER corners
SQUARE_M = 0.018  # PDF board has 18 mm squares at Actual Size
ROOT = Path.home() / "ArduCam" / "Calibration"
IMAGES = ROOT / "images"
OUT = ROOT / "camera_640x480.npz"
files = sorted(IMAGES.glob("cal_*.jpg"))
if len(files) < 12:
    raise SystemExit(f"Only {len(files)} photos. Capture 15-25 varied views first.")

obj = np.zeros((PATTERN[0] * PATTERN[1], 3), np.float32)
obj[:, :2] = np.mgrid[0:PATTERN[0], 0:PATTERN[1]].T.reshape(-1, 2)
obj *= SQUARE_M
objects, images = [], []
resolution = None
flags = cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 35, .001)
for path in files:
    frame = cv2.imread(str(path))
    if frame is None:
        print(f"SKIP unreadable: {path.name}")
        continue
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    size = (gray.shape[1], gray.shape[0])
    if resolution is None:
        resolution = size
    if size != resolution:
        print(f"SKIP different resolution: {path.name}: {size}")
        continue
    good, corners = cv2.findChessboardCorners(gray, PATTERN, flags)
    if not good:
        print(f"SKIP no corners: {path.name}")
        continue
    corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
    images.append(corners)
    objects.append(obj.copy())
    print(f"OK: {path.name}")

if len(objects) < 12:
    raise SystemExit(f"Only {len(objects)} valid views. Capture more (different tilt/distance/position).")

rms, K, dist, _, _ = cv2.calibrateCamera(objects, images, resolution, None, None)
ROOT.mkdir(parents=True, exist_ok=True)
np.savez_compressed(str(OUT), K=K, dist=dist, width=resolution[0], height=resolution[1],
                    rms=rms, images_used=len(objects))
print("\nCAMERA CALIBRATION COMPLETE")
print(f"Used {len(objects)} photographs; resolution {resolution[0]}x{resolution[1]}")
print(f"RMS reprojection error: {rms:.3f} pixels (lower is generally better)")
print("Camera matrix K:\n", K)
print("Distortion coefficients:", dist.ravel())
print("Saved:", OUT)
print("Keep the same 640x480 camera mode and lens/focus for pose estimation.")
