# Autonomous RPOD Docking Robot

An autonomous ground robot designed to demonstrate
spacecraft-inspired rendezvous, proximity operations,
and docking (RPOD).

Developed for UCF's Introduction to Robotics course.

## Objectives
- Detect docking targets using AprilTags
- Estimate relative position and orientation
- Fuse camera, encoder, and IMU measurements
- Plan autonomous rendezvous and docking trajectories
- Implement closed-loop differential-drive control

## Hardware
- Pololu Romi differential-drive chassis
- Raspberry Pi Zero 2 W
- Arducam IMX219 8MP camera
- Arduino Nano
- TB6612FNG motor driver
- MPU-6050 IMU
- Quadrature wheel encoders

## Progress
- [x] Raspberry Pi setup and SSH
- [x] Camera capture
- [x] AprilTag detection
- [x] Arduino serial communication
- [ ] Camera calibration and metric pose estimation
- [ ] Motor control and encoder feedback
- [ ] State estimation and sensor fusion
- [ ] Autonomous guidance and docking validation

## Technologies
Python, OpenCV, Picamera2, Arduino, C++, MATLAB

## Status
Work in progress.
