# RPOD Test Results and Pending Validation — as of Nov 24, 2026

| Test | Outcome | Evidence caveat |
|---|---|---|
| Nano Blink/upload | PASS | Earlier team testing |
| Nano USB serial `PING`/`PONG` | PASS | Earlier firmware test, 115200 |
| `SET`, `STATUS`, `STOP` parser | BASIC TESTED | Watchdog logic implemented but full failure-injection not proven |
| AprilTag 36h11 ID0 detection | PASS | Actual camera captures |
| Live PnP camera pose dashboard | OUTPUT DEMONSTRATED | Metric accuracy unverified |
| Camera checkerboard capture | 48 views | 9x6 inner corners at 18mm nominal square |
| Camera unconstrained reprojection RMS | 0.769 px | K/distortion implausible, validate |
| Camera constrained reprojection RMS | 0.864 px | Focal ~1488px, k1 +0.658, still validate |
| Real motor actuation, left/right/both | PASS, Nov 23 | User confirmed motors physically spin after AA/#3543 on |
| Manual turn `L/R` remapping | REQUESTED / PROPOSED | No proof revised sketch actually flashed |
| Encoder tick count | NOT TESTED | Important next milestone |
| IMU I2C telemetry | NOT TESTED | Important next milestone |
| Pi SSH over recovered WhiteSky Windows hotspot | PASS | Pi at 192.168.137.141 on hotspot |
| Pi HOME NETGEAR10 connection | UNKNOWN | Password profile saved, attempt reset SSH; home IP not found |
| Pi→Nano USB serial motor command | NOT TESTED | Wireless control script previously proposed |
| PID speed control, odometry, EKF | NOT IMPLEMENTED / NOT TESTED | Main engineering work ahead |
| Floor trajectory tracking | NOT TESTED | Need bank + camera mounting and safe motor tests |
| Physical magnetic docking | NOT BUILT/TESTED | Deliberately deferred |

When logging future tests add date, power source, sketch commit/hash, robot orientation, measured currents/voltages, wheel travel, observed behavior and relevant failures.
