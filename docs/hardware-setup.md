# Hardware Setup: Freenove Tank Robot

Bring-up notes for the Freenove Tank Robot Kit on a Raspberry Pi 4: what was tested, what was measured, and what I learned from the kit's code.

## Platform

| Component | Details |
|---|---|
| Chassis | Freenove Tank Robot Kit for Raspberry Pi (tracked, left and right geared DC motors) |
| Computer | Raspberry Pi 4 |
| Camera | OV5647 sensor (confirmed with `rpicam-hello --list-cameras`), run headless |
| Range sensor | HC-SR04 ultrasonic (trigger GPIO 27, echo GPIO 22) |
| Other | Two servos, RGB LEDs (SPI), infrared line sensors |
| Power | 18650 battery pack; switch S1 powers the Pi, S2 the motor/servo rail |
| Laptop | Windows 11 + WSL2 (Ubuntu 24.04, ROS 2 Jazzy), RTX 4060 for inference |

## Two SD cards

| Card | OS | Used for |
|---|---|---|
| A | Raspberry Pi OS (Trixie) | Freenove's stock code and phone app |
| B | Ubuntu 24.04 + ROS 2 Jazzy | All ROS work |

Freenove's tutorial assumes Raspberry Pi OS Bookworm, so expect some package and path drift on Trixie. Freenove's `main.py` and phone-app server need a GUI (Qt), which makes them a dead end for headless ROS work.

## Acceptance tests

| Subsystem | Result | Notes |
|---|---|---|
| Motor drive | Pass | |
| Servos | Pass | Centering validated (drop test) |
| Ultrasonic sensor | Pass | |
| RGB LEDs (SPI) | Pass | |
| Camera capture | Pass | OV5647, headless |
| Infrared line tracking | Fail | Dead module; not used in this project |

## Drivetrain and camera calibration

All measurements were taken on the carpet the robot will operate on, so they reflect operating conditions rather than a bench.

| Parameter | Value |
|---|---|
| Track separation (L) | 0.143 m |
| Top speed at full PWM (4095) | 0.98 m/s |
| Minimum PWM to move (`min_pwm`) | 750 (18.3% duty) |
| Camera lens height | 0.080 m |
| Camera rotation | 180° |

### Track separation

0.143 m, centerline to centerline. This is the L in the differential-drive equations, where each track's speed is v ± ωL/2.

### Top speed

Three timed 2.0 s runs at full PWM (4095) covered 194.5, 195.5, and 196.5 cm, an average of 195.5 cm, or 0.98 m/s.

The motor node caps PWM at 2500 for drivetrain headroom, so usable top speed is lower (roughly 0.6 m/s). It will be re-measured at that ceiling so the m/s-to-PWM mapping matches what the robot can actually do.

### Stiction floor

750, or 18.3% duty (750/4095). Free-spin, warm, and cold-start sweeps all converged near 750, which means the floor is set by the gearbox rather than by the surface or temperature.

The left track breaks free slightly before the right, and 750 moves both with margin. Equal PWM to both tracks won't drive perfectly straight at low speed; closed-loop control will handle that, so it isn't worth fixing mechanically.

Still to measure: the minimum PWM for pivot turns. A tracked robot pivoting on carpet drags its tracks sideways, so the in-place turning floor is likely higher than 750.

### Camera

The lens sits 0.080 m above the floor. That height drives ground-plane distance estimates: which pixel row the cat's feet are on tells you how far away she is.

The sensor is mounted upside down, so the camera node rotates frames 180° at capture. Doing it at capture means nothing downstream ever sees a flipped frame, which would silently corrupt the pixel-to-bearing geometry.

## Power and handling

- **Check voltage first.** When something network-shaped breaks, meter the battery pack under load before theorizing. Dying 18650s (down to 2.2 V) once looked like a WiFi band problem, and later a brownout froze SSH while the Pi's CPU kept running.
- **Read the LEDs.** On the Pi 4, a dark red power LED means undervoltage. A flickering green LED means the Pi is still running.
- **Shut down cleanly, every time.** Run `sudo shutdown now`, wait for the green ACT LED to go dark, then switch off S1.

## Freenove code: what's reused

Freenove's code is licensed CC BY-NC-SA 3.0, so none of it is copied into this repository. The ROS nodes import Freenove's drivers from Freenove's own folder on `PYTHONPATH`.

| Freenove file | Use | Notes |
|---|---|---|
| `motor.py` | Imported | `setMotorModel(left, right)`, ±4095, negative reverses |
| `servo.py` | Imported | `setServoAngle(channel, angle)` |
| `ultrasonic.py` | Imported | Uses gpiozero's `DistanceSensor`, which reports the median of its last 9 readings taken about 60 ms apart, so readings lag reality by roughly 0.25 s |
| `camera.py` | Idea only | Applies the 180° flip inside the camera pipeline (a libcamera transform). Uses Picamera2, which is built for Raspberry Pi OS and awkward to install on Ubuntu |
| `car.py`, ultrasonic mode | Not reused | Reactive obstacle avoidance timed with blocking `time.sleep()` calls, so it's blind mid-maneuver. Its validity check tests for 0, but the driver's error code is -1 |
| PC client color tracker | Idea only | Blob centroid for bearing and apparent size for distance (pinhole model). Despite the PID class, the actual control law is three-position with a deadband |
