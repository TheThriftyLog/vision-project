# Phase 0 — Bench Checklist (Stock Freenove Build)

**Goal of this phase:** prove every hardware subsystem works on stock Raspberry
Pi OS *before* ROS 2 exists. When something breaks later, you want zero
doubt the hardware is sound.

**SD card A = Raspberry Pi OS.** (Card B stays blank for Ubuntu + Jazzy later.)

**Status: complete.** Every subsystem passed except infrared line tracking
(dead module; line following isn't used in this project).

---

## A. Flash the OS (Raspberry Pi Imager v2.0.x)

- [x] Device: **Raspberry Pi 4**
- [x] OS: **Raspberry Pi OS (64-bit) with Desktop** (Freenove requires Desktop)
- [x] Storage: card A selected — **confirm the size matches your card**
- [x] Customisation (appears before Writing, or via APP OPTIONS):
  - [x] Hostname: `tank-pios`
  - [x] Username + real password (not the old pi/raspberry default)
  - [x] WiFi SSID + password + correct country
  - [x] Locale / timezone
  - [x] **Enable SSH** (password auth is fine)
- [x] Write, then first boot

## B. First contact (headless)

- [x] `ping tank-pios.local` resolves from your laptop
- [x] `ssh <user>@tank-pios.local` logs in
- [x] `sudo apt update && sudo apt full-upgrade -y` then reboot

---

## C. Get the code (Freenove Ch.1)

- [x] `cd ~`
- [x] `git clone --depth 1 https://github.com/Freenove/Freenove_Tank_Robot_Kit_for_Raspberry_Pi.git`
- [x] `sudo chmod 755 -R ~/Freenove_Tank_Robot_Kit_for_Raspberry_Pi`
- [x] `cd ~/Freenove_Tank_Robot_Kit_for_Raspberry_Pi/Code`
- [x] `sudo python setup.py`
  - [x] Camera type when prompted: **ov5647** (verify the label on the PCB)
- [x] `sudo reboot`
- If install failed (usually network): rerun `sudo python setup.py`

---

## D. Assembly gates (Freenove Ch.2) — the ones that bite

- [x] **Servo centering done live.** Run `sudo pigpiod` (V1.0 PCB, non-Pi5),
      then `sudo python servo.py`, keep it running, attach servo horns ONLY
      after the servo has driven to its set angle. A wrong zero here corrupts
      every tf2 transform downstream — this is the highest-consequence step.
      (Verified afterward with a drop test.)
- [x] Ultrasonic sensor mounted and facing forward (you'll reuse it as a
      safety stop later)
- [x] Tracks tensioned, wheels seated

---

## E. Module tests (Freenove Ch.3)

Run from `~/Freenove_Tank_Robot_Kit_for_Raspberry_Pi/Code/Server`.
For motor/servo, S1 **and** S2 must be pressed (battery power).

- [x] `sudo python test.py Motor` — fwd / back / left / right, then stop
  - If it runs backward first: swap the two motor wires
- [ ] `sudo python test.py Infrared` — prints Left / Middle / Right vs black tape
      — **failed: dead module.** Line following isn't used in this project.
- [x] `sudo python test.py Led` — RGB LEDs light and change
- [x] `sudo python test.py Servo` — both servos sweep and return to center
- [x] `sudo python test.py Ultrasonic` — distance readings track a moving hand
- [x] `sudo python test.py Camera` — image/preview confirmed

---

## F. Phase 0 exit gate

- [x] Every module test in section E passed, except infrared (not needed for
      this project)
- [x] Robot drives on the ground under `test.py Motor` without falling apart
- [x] `About_Battery.pdf` read; batteries charged and stored safely

When all of the above are true, power down, pull card A, and Phase 1 begins:
Ubuntu 24.04 + ROS 2 Jazzy on card B.

---

### Measurements captured for later phases

All taken on the carpet the robot will drive on. Details are in
[hardware-setup.md](hardware-setup.md).

| Measurement | Method | Result | Feeds |
|---|---|---|---|
| Track separation (center-to-center) | calipers | 0.143 m | `track_separation_m` |
| Top speed at full PWM | distance covered in a timed 2.0 s run, three runs | 0.98 m/s | `max_linear_mps` |
| Stiction floor (PWM where tracks start) | free-spin, warm, and cold-start sweeps | 750 (18.3% duty) | `min_pwm` |
| Camera lens height above floor | ruler | 0.080 m | URDF + ground-plane deprojection |
