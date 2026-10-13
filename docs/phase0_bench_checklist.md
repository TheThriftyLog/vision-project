# Phase 0 — Bench Checklist (Stock Freenove Build)

**Goal of this phase:** prove every hardware subsystem works on stock Raspberry
Pi OS *before* ROS 2 exists. When something breaks in Phase 5, you want zero
doubt the hardware is sound.

**SD card A = Raspberry Pi OS.** (Card B stays blank for Ubuntu + Jazzy later.)

---

## A. Flash the OS (Raspberry Pi Imager v2.0.x)

- [ ] Device: **Raspberry Pi 4**
- [ ] OS: **Raspberry Pi OS (64-bit) with Desktop** (Freenove requires Desktop)
- [ ] Storage: card A selected — **confirm the size matches your card**
- [ ] Customisation (appears before Writing, or via APP OPTIONS):
  - [ ] Hostname: `tank-pios`
  - [ ] Username + real password (not the old pi/raspberry default)
  - [ ] WiFi SSID + password + correct country
  - [ ] Locale / timezone
  - [ ] **Enable SSH** (password auth is fine)
- [ ] Write, then first boot

## B. First contact (headless)

- [ ] `ping tank-pios.local` resolves from your laptop
- [ ] `ssh <user>@tank-pios.local` logs in
- [ ] `sudo apt update && sudo apt full-upgrade -y` then reboot

---

## C. Get the code (Freenove Ch.1)

- [ ] `cd ~`
- [ ] `git clone --depth 1 https://github.com/Freenove/Freenove_Tank_Robot_Kit_for_Raspberry_Pi.git`
- [ ] `sudo chmod 755 -R ~/Freenove_Tank_Robot_Kit_for_Raspberry_Pi`
- [ ] `cd ~/Freenove_Tank_Robot_Kit_for_Raspberry_Pi/Code`
- [ ] `sudo python setup.py`
  - [ ] Camera type when prompted: **ov5647** (verify the label on the PCB)
- [ ] `sudo reboot`
- [ ] If install failed (usually network): rerun `sudo python setup.py`

---

## D. Assembly gates (Freenove Ch.2) — the ones that bite

- [ ] **Servo centering done live.** Run `sudo pigpiod` (V1.0 PCB, non-Pi5),
      then `sudo python servo.py`, keep it running, attach servo horns ONLY
      after the servo has driven to its set angle. A wrong zero here corrupts
      every tf2 transform downstream — this is the highest-consequence step.
- [ ] Ultrasonic sensor mounted and facing forward (you'll reuse it as a
      safety stop later)
- [ ] Tracks tensioned, wheels seated

---

## E. Module tests (Freenove Ch.3) — **ALL must pass**

Run from `~/Freenove_Tank_Robot_Kit_for_Raspberry_Pi/Code/Server`.
For motor/servo, S1 **and** S2 must be pressed (battery power).

- [ ] `sudo python test.py Motor` — fwd / back / left / right, then stop
      - [ ] If it runs backward first: swap the two motor wires
- [ ] `sudo python test.py Infrared` — prints Left / Middle / Right vs black tape
- [ ] `sudo python test.py Led` — RGB LEDs light and change
- [ ] `sudo python test.py Servo` — both servos sweep and return to center
- [ ] `sudo python test.py Ultrasonic` — distance readings track a moving hand
- [ ] `sudo python test.py Camera` — image/preview confirmed

**Record as you go** (you'll need these numbers in later phases):
- [ ] Motor direction correct without rewiring?  Y / N
- [ ] Servo center offsets (pan / tilt actual angle at "center"): ____ / ____
- [ ] Ultrasonic reading at a known 30 cm: ______ cm (accuracy sanity check)

---

## F. Phase 0 exit gate

- [ ] Every box in section E ticked
- [ ] Robot drives on the ground under `test.py Motor` without falling apart
- [ ] `About_Battery.pdf` read; batteries charged and stored safely

When all of the above are true, power down, pull card A, and Phase 1 begins:
Ubuntu 24.04 + ROS 2 Jazzy on card B.

---

### Quick reference — measurements to capture for later phases
| Measurement | Tool | Feeds |
|---|---|---|
| Track separation (center-to-center) | calipers | `track_separation_m` |
| Top speed over 2 m at full PWM | tape + stopwatch | `max_linear_mps` |
| Stiction floor (PWM where tracks start) | trial | `min_pwm` |
| Camera lens height above floor | ruler | URDF + ground-plane deprojection |
