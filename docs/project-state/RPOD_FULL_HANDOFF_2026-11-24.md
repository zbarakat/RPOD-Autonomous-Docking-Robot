# RPOD Autonomous Rendezvous and Docking Robot — Full Project Handoff
**State as of November 24, 2026** | **Owner: Zein Barakat** | **UCF EGN 4060C Introduction to Robotics**

> **Read this document first in a new chat.** It is a detailed continuity record assembled from the project conversation, user-shared images, project assets, source scripts, and terminal outputs. It does not assert that the latest change was pushed to GitHub or that an untested subsystem works. The repository on Zein's Windows PC and deployed files on the Raspberry Pi remain the sources of truth for exact code. No Wi-Fi passwords or secret credentials belong in this document or repository.

## 0. User expectations and immediate task
- User is **Zein**, aerospace/mechanical engineering dual major at UCF, focusing on GN&C + robotics. Wants a serious educational engineering collaboration: assistant can write code, but user wants derivations and decisions explained for **PID, EKF, robot kinematics, frame transforms, AprilTag pose, trajectory planning, and validation**. Prefer casual, concise direct tone, rigorous technical content. No em dashes in drafted prose.
- Near-term priority **get fully untethered wireless movement working, read encoders/IMU, build PID speed control, odometry, and curved-path guidance**. User does not want to design/finalize the physical magnetic docking station yet. Do not overfocus on docking mechanics. Controlled wheel spin has **already worked** on the physical robot via Arduino Nano attached to Windows laptop. Pi-to-Nano wireless motor control has **not yet been demonstrated**.
- Immediate context: Wi-Fi at the teammate's WhiteSky apartment was recreated as a Windows Mobile Hotspot to regain SSH; home NETGEAR10 credentials were eventually saved and `nmcli connection up NETGEAR10` disconnected SSH, but the new Pi IP/home connectivity **has not been confirmed**. Windows `.local` name resolution is unreliable. The user opted to defer troubleshooting and use hotspot as fallback. User asked to preserve everything and update existing GitHub; the current handoff package is **not proof of a GitHub push**.

## 1. Mission / architecture
- **Autonomous Rendezvous & Docking (RPOD) Ground Robot**, spacecraft-inspired guidance/navigation/control applied to an affordable 2D nonholonomic differential-drive rover.
- Baseline: stationary magnetic docking contact at a specific known location and final heading. AprilTags are **measurement references**, never substitutes for the physical docking point. The mission will later require an approach waypoint, curved/arcing/spline trajectory, deceleration, final alignment, slow short final contact. Target motion is a stretch goal only after repeatable stationary docking.
- Functional loop: **Arducam IMX219 → Pi perception (AprilTag PnP) + Arduino encoder/IMU telemetry → pose fusion EKF (planned) → curved guidance and terminal approach → wheel velocity commands → Arduino PID (planned) → Pololu #3543 onboard motor drivers → wheels → feedback**.
- Be honest: vision, serial parser, chassis/wiring, and basic motor commands are individually demonstrated; integrated controls, odometry, EKF, autonomous docking have **not** been tested as a system.

## 2. Team and course
- Project team: **Zein Barakat, Justin Puran, Santiago Calderon-Rueda, Ryan Flowers**.
- Course: **EGN4060C Introduction to Robotics**, UCF; instructor Mingyo (the course announcement was signed Mingyo).
- Progress review oral presentation Nov 9, 2026; IEEE conference-format 4-page maximum report incl references/appendix due Nov 13, 2026; attach PDF slides. Draft artifacts exist: 3-page IEEE report in PDF and editable DOCX, 7-slide presentation PDF and PowerPoint.
- Reported progress in the slides: chassis and wiring assembled, Pi/vision demonstrated, Nano serial commands tested, calibration 48 photos and 0.864 px constrained reprojection RMS; not yet motor telemetry/fusion/docking at presentation time. **Subsequent motor actuation succeeded after the presentation**.

## 3. Hardware inventory and current photographed layout
| Item | Function | Current status / location |
|---|---|---|
| **Pololu Romi chassis #3500** | Differential drive mechanical platform; two DC gearmotors, two wheels, rear ball caster, battery compartment | Assembled |
| **Pololu #3543 motor-driver and power-distribution board** | Romi-compatible board with two DRV8838 driver channels, battery contacts, power switch/regulator/encoder interface | Installed large black central PCB. **Replaces previous separate TB6612FNG plan.** Does NOT itself run PID or estimate odometry. |
| **Two Pololu 12-CPR motor-shaft magnetic quadrature encoder assemblies #3542** | Measure motor-shaft rotation, enabling wheel speed/odometry | Physically integrated by teammate, **counts not validated**. Counts per wheel revolution depend on gearbox ratio and counting convention. |
| **ELEGOO Arduino Nano ATmega328P USB-C** | Low-level motor DIR/PWM, encoder interrupts, IMU I2C, watchdog, serial interface | Wired/mounted in a printed holder on black plate; visually blue board; flashed and tested with laptop |
| **Raspberry Pi Zero 2 W** (32-bit Raspberry Pi OS Lite, 512 MB) | Higher-level computer for camera, AprilTag, navigation/guidance and serial commands | Mounted partly under the expansion plate, microSD installed, powered by USB bank |
| **Arducam 8MP IMX219 with CSI ribbon** | Forward camera, AprilTag detection, metric pose estimate from PnP | Functioning vision; orange ribbon connected. Camera bracket needs reprint/rigid mount, previously dangling in photos. |
| **GY-521 MPU-6050 six-axis IMU** | Gyroscope angular rates and accelerometer specific force | Small blue breakout mounted at side/edge, appears wired; orientation and telemetry not validated |
| **Six rechargeable NiMH AA cells** | Battery pack for #3543 and motors (nominal 7.2 V six-cell pack, depending on exact wiring) | Installed during successful wheel-spin tests |
| **Anker ~10,000 mAh USB power bank** | Stable regulated USB 5 V to Pi; may in turn power Nano over USB | Needs secure mounting on rear semicircular expansion plate, proposed **two reusable Velcro straps through plate holes** and optional anti-slip patch |
| **3D-printed expansion plate/standoffs and Nano bracket** | Mechanical packaging | Installed, crowded; ensure caster and wheel clearance, and strain relief |
- See `hardware/photos/2026-11/` for user-supplied actual assembly photos and earlier teammate's annotated layout plus wiring diagram. These are *not* full wiring verification, merely references. Exclude photos of apartment Wi-Fi credentials (not in package).
- Structural vs electronic: the **black perforated semicircular plates** are mounting structures, whereas the **large black central PCB** is #3543.
- Motor operating voltage requires care. Six NiMH AA = 7.2 V nominal and standard Romi motor recommended operating voltage may be ~4.5 V; don't command unrestricted full PWM/stall before reviewing board configuration, measured supply and motor specifications. Initial low duty, wheels raised.

## 4. Team's proposed wiring/pin map — VERIFY against physical build
| Signal | Arduino pin | Notes |
|---|---|---|
| Left motor DIR / PWM | D7 / D5 | #3543 DIR/PWM interface, not TB6612 IN1/IN2 logic |
| Right motor DIR / PWM | D9 / D6 | Need ground truth left/right and polarity |
| Left encoder A / B | D2 / D4 | D2 interrupt capable |
| Right encoder A / B | D3 / D8 | D3 interrupt capable |
| MPU6050 SDA / SCL | A4 / A5 | Nano ATmega328P I2C |
| Pi↔Nano | USB serial, 115200 baud | Pi USB data port → OTG female adapter → white USB-A from Nano USB-C cable |
- The chart is taken from teammate's wiring design **not multimeter/pin-by-pin verified**. Final physical harness must be checked.
- USB port connections while deployed: **white USB-A male from Nano** goes into **black USB-A female OTG adapter** attached to Pi's **USB** micro-USB data port. A **separate USB-A male cable** from Pi's **PWR IN** micro-USB goes to **Anker bank's USB-A output**. These Pi ports are **micro-USB**, not USB-C. Laptop not physically tethered for wireless control.
- Power sources: AA cells → #3543 motor and encoder/motor circuitry; bank → Pi 5 V and (likely) Nano via Pi's USB host. **Before simultaneous supplies, verify USB/Nano 5 V cannot backfeed/short to the #3543's 5 V regulator; common ground is required, and the actual harness hasn't been electrically audited.**
- #3543 has onboard power control, but bank power is separate; Pi and motor supply can be on independently. Follow safe orderly startup/shutdown. Moving robot must have loose cables strapped out of wheels/caster and bank securely attached.

## 5. Confirmed bench/software accomplishments
### Arduino / serial
- Arduino Nano Blink program tested; USB serial `PING`→`PONG` tested. Previous base firmware parsed `PING`, `STOP`, `STATUS`, `SET leftRPM rightRPM`; 2-second watchdog logic implemented (not a verified motor safety watchdog on latest standalone motor test).
- On Windows, initial Nano upload `COM3` failed due cable incapable of transferring data; swap to verified USB-A-to-USB-C **data** cable fixed it. Arduino was detected on **COM4**. Arduino IDE board Nano / processor ATmega328P / baud **115200**.
- `motor_test.ino` compiled (reported 2464 program bytes and 296 global bytes). User sent `L`, `R`, `F` in Arduino Serial Monitor; messages `Test complete; motors stopped` plus `Unknown command`. `Unknown command` came from line endings; set Serial Monitor **No Line Ending**, or improve parser. Motor rotation **then verified physically** after AA supply/#3543 enabled.
- Test sketch exposed `L` spinning **left wheel**, causing robot to pivot right; user requested **semantic change** `L` = turn LEFT → spin right wheel; `R` = turn RIGHT → spin left wheel. Assistant proposed swapped manual handlers. **Unknown whether this changed sketch has actually been flashed since**. A reconstructed annotated candidate is in `software/arduino/motor_test/motor_test.ino` in this update package. Do not claim it is byte-for-byte the live Nano image.
- Typical one-shot open-loop test `TEST_PWM=50` (of 255) and `TEST_MS=350`. In first sketch, wheel runs ~350 ms then stops. Commands `F`,`L`,`R`,`S` are *not Linux shell commands*, so typing `L` directly at `robot@romi-pi:~ $` produces `bash: L: command not found`.
- **Not validated:** actual encoder tick counter, wheel speed RPM, IMU serial telemetry, wheel PID control, odometry, wireless Pi-to-Nano motor actuation, floor driving and tracking.

### Raspberry Pi / camera
- Pi hostname: `romi-pi`; user account `robot`; previous access `ssh robot@romi-pi.local` on known accessible LAN, but Windows `.local` resolution intermittently fails.
- Pi script directory: `/home/robot/ArduCam/Scripts/`. Pi calibration photos/files: `/home/robot/ArduCam/Calibration/`. Repo camera scripts in `software/raspberry-pi/camera/`.
- Camera works at **640×480** under Picamera2; AprilTag family **36h11**, tag **ID 0** recognized by detector and live dashboard; image `detection.jpg` and demo screenshot in prior files.
- Scripts: `detect_apriltag.py` (still images), `live_apriltag.py` (MJPEG dashboard on `127.0.0.1:8000`), `calibration_capture.py` (checkerboard capture dashboard port `8001`), `calibrate_camera.py`, `pose_live.py` (PnP six-DoF relative-pose dashboard port `8002`). Access via Windows SSH local forwarding, e.g. `ssh -N -L 8002:127.0.0.1:8002 robot@ACTUAL_PI_IP`; browse `http://localhost:8002`.
- Camera printed checkerboard: 9×6 **inner corners**, 18 mm squares, letter paper, printed actual size; **48 valid calibration photos**.
- Unconstrained camera calibration **RMS 0.769 px**, K approximately `[[1817.10,0,226.75],[0,1878.46,67.57],[0,0,1]]`, dist `[-0.3501,21.9096,-0.0752,-0.0078,-154.207]` (large implausible distortion/off-center optical center).
- Constrained fit **RMS 0.864 px**, K approximately `[[1487.60,0,319.5],[0,1488.53,239.5],[0,0,1]]`, radial `k1=+0.6584` with k2/k3 zero and tangential zero (still suspicious/needs physical validation). Source saved `camera_640x480.npz` and constrained version `camera_640x480_constrained.npz` on Pi. **Very important:** the `pose_live.py` snapshot present in the conversation explicitly loads `camera_640x480.npz`, the *original unconstrained fit*, not constrained. Check real deployed file and validate/recalibrate before relying on pose distances.
- `pose_live.py` snapshot uses `TAG_SIZE_M = 0.100` and `time.sleep(.35)` in streaming loop, which caps ~2.86 FPS before processing; an earlier conversation suggested reducing the artificial sleep to `.15`, but do not assume deployed file was updated. **Physical width of actual black outer tag square must be measured**; print target nominal 100 mm not proof of actual printed black border size.
- Demo screenshot showed e.g. ID0, reported range ~1.451 m, depth Z ~1.441 m, X +0.059 m, Y +0.156 m, bearing +2.3°, yaw −11.9°, but ground truth unrecorded. Pose is **reported, not yet validated for accuracy**. Validate at known 0.5, 0.75, 1.0 m camera optical-center-to-tag distances, vary lateral offsets/face yaw and compare actual measured values.
- Some camera scripts may be missing in this transfer because the repository contains earlier committed versions and the only mounted files in this conversation were a subset. Never overwrite newer local/remote scripts with old attachments without comparing diffs.

## 6. GNC equations, conventions, next design lessons
- Differential-drive kinematics for wheel radius `r`, track width `b`, physical angular wheel speeds `ω_R`,`ω_L`:
  - `v = r(ω_R + ω_L)/2`
  - `θ_dot = r(ω_R − ω_L)/b`
  - `x_dot = v cos θ`, `y_dot = v sin θ`
  - `R = v/θ_dot` when θ_dot nonzero, useful for curved arcs. Sign and wheel polarity must be verified physically. Left/right user **manual turn commands** distinct from physical motor identifiers.
- Encoder conversion will require motor shaft counts, gearbox gear ratio, quadrature counting mode (x1, x2, x4), wheel diameter and slip testing. Wheel PID closed-loop control should handle saturation, anti-windup, and low-speed dead zone.
- State vector likely 2D `(x,y,θ)` with velocities and biases as appropriate; propagate with encoder odometry and gyro, update using camera target pose and known tag/dock geometry. EKF not implemented yet. IMU accelerometer does not yield reliable long-term position by naïve double integration.
- **3D rigid transforms**: `^A T_B` means coordinates B→A, a 4×4 homogeneous transform with rotation R (3×3), translation t (3×1), row `[0 0 0 1]`. Formula `^C T_D = ^C T_Ti * ^Ti T_D`, where `C` camera optical frame, `Ti` individual tag, `D` physical dock/magnet. Composition rotation `R_CD=R_CTi R_TiD` and translation `t_CD=R_CTi t_TiD+t_CTi`. OpenCV optical axes x-right,y-down,z-forward; don't mix with 2D top-view convention x-right,y-forward.
- Proposed future **multiple unique AprilTags** ID0 frontal, ID1 left (~45°), ID2 right (~45°), maybe ID3 rear, each vertical with measured rigid offsets relative to the **single dock reference frame**. Current detector only ID0. Multi-tag transforms can maintain pose estimate over curved approaches; tag ambiguity/occlusion/FOV and calibration need testing. No LiDAR required for fiducial tracking, though LiDAR could help obstacles/range. Moving-target intercept requires estimated velocity and continuous replanning; deferred stretch goal.
- Emphasize user preference for **optimal and curved trajectory guidance** (Dubins arcs, splines, constrained optimization/MPC) rather than basic straight-line pursuit; but implement stable baseline and measured performance first. Plan to evaluate cross-track RMSE, heading error, final pose error, time to target, and docking success once station exists.

## 7. Wi-Fi / SSH recovery and precise remaining state (Nov 23–24)
- On teammate's apartment network, Pi had saved `WhiteSky-PointeAtCentral` Wi-Fi, password was shared in user photo (**DO NOT print, put in code, or upload to public GitHub**).
- At user's current location, laptop Wi-Fi network `NETGEAR10`, gateway previously `192.168.4.1`, laptop `192.168.4.25`, netmask `/22`, and an `NETGEAR10-5G` SSID also exists. Although laptop reported SSID NETGEAR10 and 5GHz radio, **Pi Zero 2 W only supports 2.4 GHz**; on same LAN, laptop and Pi can be on different bands.
- Windows Mobile Hotspot was configured with teammate's SSID/password, **2.4 GHz**, and Pi joined. Hotspot assigned Pi **192.168.137.141**, laptop hotspot interface **192.168.137.1**. Verified working SSH: `ssh robot@192.168.137.141`. Pi login `robot`. Windows `romi-pi.local` frequently says `No such host is known`, even when SSH works via IP.
- `nmcli device wifi list` shows NETGEAR10 strong, including channel 11 and channel 1 access points. `nmcli connection show`: `netplan-wlan0-WhiteSky-PointeAtCentral` active on `wlan0`; `NETGEAR10` saved but initially idle. Earlier attempted `sudo nmcli --ask device wifi connect "NETGEAR10"`; SSH disconnected and Pi returned to hotspot because connection lacked password. NetworkManager logs explicitly said `no-secrets` (NOT a Pi lock to Wi-Fi).
- Later user ran the needed **password-saving command**:
  ```bash
  read -rsp "NETGEAR10 password: " WIFI_PASS; echo
  sudo nmcli connection modify NETGEAR10 wifi-sec.key-mgmt wpa-psk wifi-sec.psk "$WIFI_PASS"
  unset WIFI_PASS
  sudo nmcli connection modify NETGEAR10 connection.autoconnect yes connection.autoconnect-priority 50
  sudo nmcli connection up NETGEAR10
  ```
  (Commands occurred across turns; priority first, password later.) Last `connection up` caused `client_loop: send disconnect: Connection reset`; **it may have succeeded** but Windows couldn't resolve `romi-pi.local` afterward. Do NOT assume success or failure from this alone.
- To resume, with hotspot ON or Pi reachable by other means, check **on Pi** `nmcli -f NAME,DEVICE connection show --active` and `ip -4 addr show wlan0` or `hostname -I`. To test home LAN, laptop connected to NETGEAR10, find Pi's **new IP on router DHCP client list** or otherwise scan/check ARP/SSH. `192.168.137.141` is **only the Windows hotspot IP**, not the home IP. `ssh robot@192.168.137.141` from Windows works only when the hotspot connection is active. Avoid trying to run `sudo nmcli ...` from `PS C:\...>` because that's Windows, not Pi. Do not SSH `robot@romi-pi.local` from inside Pi as an external connectivity test; it connects from Pi to itself.
- User wants long-term wireless direct control anywhere. Consider Pi-hosted access point `RPOD-Romi` as future implementation **only after reliable recovery path** and accounting for Pi single Wi-Fi radio switching between client and hotspot; avoid lockout. Windows Mobile Hotspot fallback is acceptable temporarily.
- Network recovery is DEFERRED per user request. Next engineering priority remains motor+sensor testing, not Wi-Fi debugging. If user wants immediately to drive wirelessly, the verified fallback is Windows hotspot (then SSH). The earlier one-shot `manual_serial_control.py` idea was proposed but not yet tested on Pi.

## 8. Repository, local paths, version control
- **Authoritative local Windows repo path**: `C:\Users\zbara\Downloads\EGN4060C Robotics Project\RPOD-Autonomous-Docking-Robot`
- **Public remote**: `https://github.com/zbarakat/RPOD-Autonomous-Docking-Robot` (URL from prior Git transcript; `main` branch).
- Previously successful commit `df3153b` on Nov 7: `Add camera calibration and pose estimation`; pushed `calibrate_camera.py`, `calibration_capture.py`, and `pose_live.py`; earlier code and hardware CAD README also committed. There may be newer commits/working files. **Do not assert current GitHub HEAD** without inspecting repo.
- Structure known from previous interactions: `software/arduino/Arduino.ino`, `software/raspberry-pi/camera/{detect_apriltag.py,live_apriltag.py,calibration_capture.py,calibrate_camera.py,pose_live.py}`, `hardware/CAD/README.md`, `docs/presentations/`, `tests/arduino/`, `_local/ArduCam/` (gitignored screenshots/calibration raw data); excludes vendor binary CAD, raw frames, passwords, logs.
- **This transfer package** stages only new `docs/project-state`, a reconstructed separate `software/arduino/motor_test/motor_test.ino`, optional experimental Pi serial controller, recent actual photos/hardware reference images, and report PDF/DOCX/slides PDF. Don't replace original `Arduino.ino` or deployed `pose_live.py` without confirming latest version. Reconstructed sketch is clearly labeled.
- **GitHub not updated as a direct result of creating this package** until repo owner runs provided publish steps or connects a functioning GitHub integration; do not misrepresent upload status.

## 9. Mechanical / electrical safety and immediate next milestones
1. Finish **two Velcro-strap** bank mount on rear expansion plate through perforations, ideally supplemented with anti-slip pad; bank low/centered without covering vents/ports, rear caster/wheels/battery access, strain-relief all USB/ribbon cables. Rigidly reprint/remount camera bracket (fix orientation for optical frame).
2. **Verify actual circuits** with battery/motor power initially OFF: separate Nano USB and #3543 VREG supply (avoid competing 5V/backfeed), common ground, motor driver pins D7/D5 D9/D6, encoders, IMU. Use multimeter; do not rely on diagrams alone.
3. Confirm fresh Arduino `motor_test.ino` versus actually flashed code and `L/R` semantics. Wheels lifted, run `L`,`R`,`F` via Arduino IDE serial monitor. **This has already worked on bench**; repeat if changed wiring.
4. On Pi over USB OTG, inspect `ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null`; install `python3-serial` if needed. Run a **one-shot wireless test** from laptop SSH → Pi → Nano, with wheels lifted, using correct firmware. This end-to-end Wi-Fi-driven movement is NOT yet demonstrated.
5. Implement **quadrature encoder tick counting**, check direction and counts per rev, timestamped telemetry. Add IMU I2C readout/calibrate axes/gyro bias.
6. Open-loop speed sweep on raised wheels, then cautious short floor tests on clear surface with a **real emergency stop**, verify desired forward directions, wheel circumference and track width; log commanded vs measured RPM.
7. Wheel speed PID with anti-windup, saturation and watchdog; odometry straight/turn/arc trials and error characterization.
8. Validate visual pose metric calibration, camera-to-base extrinsics, time sync and camera FPS/latency; then encoder/gyro/vision fusion EKF.
9. Curved guided approach toward a **temporary marked waypoint** (no final docking structure required yet). Add magnet/guide fixture only when ready for actual docking trials. Moving target is stretch.

## 10. Working files and artifacts to preserve
- Latest relevant uploaded images: `98873.jpg` team's annotated top-view layout, `99919.jpg` proposed full wiring diagram; `IMG_0726.jpeg`, `IMG_0727.jpeg`, `IMG_0728.jpeg`, `IMG_0729.jpeg` assembly, `IMG_0732.jpeg` USB arrangement. All present in this transfer `hardware/photos/2026-11/`, **except apartment password photo intentionally omitted**.
- Project report PDF `RPOD_IEEE_Progress_Review_DRAFT.pdf`, editable `RPOD_IEEE_Progress_Review_Editable.docx`, actual slides PDF `RPOD_Presented_Slides.pdf`, presentation PPTX `RPOD_Progress_Review.pptx` in previous conversation assets; package stages only selected PDFs/DOCX under `docs/reports/` and leaves existing PPTX path alone.
- Camera script snapshots were already committed Nov7; original conversation attached `pose_live.py`, `calibration_capture.py`, `calibrate_camera.py`, detection pictures and printables. Printed AprilTag `apriltag_36h11_id0_100mm_letter.pdf`, checkerboard `calibration_chessboard_9x6_18mm_letter.pdf`. The raw constrained calibration results **should be copied from Pi or user's `_local` folder before trying to back them up**.

## 11. What new assistant should do FIRST
- Treat this as a continuing engineering project, not a fresh idea. Don't re-ask identities/components/addresses or make them recreate prior work. **Check the actual status of GitHub synchronization** (if connected) and of the user's local repo/Pi code before assuming anything was pushed.
- User has repeatedly wanted practical real robot progress rather than endless network troubleshooting. Do not return to Wi-Fi repair until user requests it. If they ask for next action, first physically secure bank/camera and confirm existing power safety, then test Pi→Nano motor commands over the known fallback hotspot.
- **Verify any pasted instructions against actual version** because current plan moved from TB6612FNG to #3543; never overwrite the serial parser or motor test sketch blindly. Track status as DONE / TESTED / PLANNED.

## 12. Startup prompt for fresh ChatGPT conversation
> I'm Zein and this is the continuation of my UCF EGN4060C RPOD Autonomous Docking Romi project. Read `RPOD_FULL_HANDOFF_2026-11-24.md` thoroughly and use it as our engineering project state, with the GitHub-ready update package as artifacts. Do not start from scratch or ask about details already documented. Real hardware motor actuation works using the Nano + #3543 and AA batteries. Camera/AprilTag PnP demo works, though metric pose and calibration are not validated. Raspberry Pi Zero 2 W SSH previously works over temporary WhiteSky Windows hotspot at 192.168.137.141; NETGEAR10 was configured, but current home IP is unverified and name resolution fails. I want to focus on finishing power-bank/camera mounting, Pi→Nano wireless motion, encoders/IMU telemetry, PID, odometry and curved guidance, not final docking hardware yet. Explain GN&C math/engineering decisions while handling implementation. First help me continue precisely from current verified status and confirm any GitHub push claims against actual evidence.
