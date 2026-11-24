# Hardware Snapshot and Wiring — Nov 24, 2026
This is an **observational engineering record**, not an electrically certified schematic.

## Photos
- `hardware/photos/2026-11/teammate_topview_layout_98873.jpg`: teammate's top-view hand sketch of Romi layout, camera/front expansion region and Anker bank aft.
- `hardware/photos/2026-11/teammate_wiring_diagram_99919.jpg`: original proposed electrical wiring from teammate.
- `hardware/photos/2026-11/IMG_0726.jpeg` through `IMG_0729.jpeg`: close-ups of built, densely wired Nano/Pi/IMU/#3543/camera installation.
- `hardware/photos/2026-11/IMG_0732.jpeg`: full assembled Romi photo showing Pi USB connectors, Nano white cable and black OTG USB-A female adapter.
- Credential-containing network photo intentionally **NOT INCLUDED**.

## Working deployment USB map
```text
Anker USB-A OUT ---- USB-A male → Pi micro-USB PWR IN
Pi micro-USB DATA -- micro-USB OTG → USB-A female
USB-A female <---- white USB-A male → Nano USB-C
```
The laptop connects via Wi-Fi/SSH, NOT a direct physical USB cable while deployed.

## Power layout
```text
6 NiMH AA batteries → Pololu #3543 battery contacts → switched motor power → two DC motors
                                             ↘ regulated/board logic + encoder support
Anker power bank (5V USB) → Raspberry Pi PWR IN → Pi USB host → Arduino Nano USB
```
**WARNING:** Check +5V architecture, common ground, wiring, and switching with a meter. Do not allow board VREG to fight USB 5V. Verify particular Romi motor allowable voltage before high PWM. Mount Anker with two Velcro straps through perforations and optional anti-slip pad; do not cover ports, ventilation, wheels/caster, or AA access.

## Proposed Arduino connections, verify at hardware
| Device | Pins |
|---|---|
| #3543 left motor DIR/PWM | D7/D5 |
| #3543 right motor DIR/PWM | D9/D6 |
| Encoder left A/B | D2/D4 |
| Encoder right A/B | D3/D8 |
| MPU6050 I2C SDA/SCL | A4/A5 |

## What is tested
- Real left/right wheel spins after loading motor test to Nano from laptop over good **data-capable** USB cable, Arduino IDE COM4, 115200 baud. Motors powered by AA/#3543. Test code one shot 350 ms, PWM ~50/255.
- Nano serial command parser and Pi camera/AprilTag previously worked separately.

## Not tested
- Encoder tick/IMU readouts; Pi USB serial connection; Pi wireless motor command; long motion under load; PID, odometry, fusion, docking.
- User asked to reverse **meaning** of manual `L/R`: `L` = robot turns left using right wheel, `R` = robot turns right using left wheel. Whether that change was flashed remains unknown.
