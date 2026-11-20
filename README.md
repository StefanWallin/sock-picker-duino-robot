# HooverBot

**Long-term goal:** a self-propelled robot that roams the room, finds socks (and
dog toys), picks them up and carries them to a drop point.
**Learn-first plan:** before buying ~18 × $33 motors for the "dream build"
(sphere/folding-leg robot), build a cheap **pulley-driven digger arm** with the
already-owned SG90 micro servos — replicating a Volvo material handler
(`image.png`) as inspiration. Everything is 3D-printed on the AnyCubic Kobra S1.

---

## Current status & goals

- [x] Phase 0 — capture all project knowledge (ChatGPT threads, inventory, decisions) into this README
- [x] Agent instructions (`AGENTS.md`)
- [x] CAD toolchain ready — FreeCAD 1.1.1 headless (`freecadcmd`), parametric Python scripts
- [x] **Step 2 — Rotator base + servo housing STLs** (`stl/base_platter.stl`, `stl/turret_deck.stl`, `stl/catch_basket.stl`; battery dock, basket, buzzer mount, 3-wire pass-throughs)
- [ ] Print & fit-test the three printed parts (user, with real SG90 + battery + buzzer module)
- [ ] Step 3 — mast + boom with fishing-line pulley winch STLs
- [ ] Step 4 — gripper (clamshell) STL driven by fishing line / servo
- [ ] Step 5 — prototype kinematics library for the arm on the Nano
- [ ] Step 6 — combine digger kinematics + car movement under MKR WiFi 1010 control (web UI)
- [ ] Step 7 — integrate onto the car base (weight, power, centre of gravity)
- [ ] Step 8 — sock detection experiments (ultrasonic + TCS3200 colour + IR)
- [ ] Stretch — revisit 18-servo folding sphere bot with the lessons learned

## Quick facts

| Item | Value |
|---|---|
| Print volume | 250 × 250 × 250 mm (AnyCubic Kobra S1 Combo + ACE Pro 1) |
| Learning servos | 4 × SG90 9 g micro servo (~1.8 kg·cm @ 4.8 V, 4.8–6 V, ~0.1 s/60°) |
| Butter-cheap pulley line | 0.5 mm fishing line |
| Rotator base diameter | 250 mm (user-requested; exactly fills the bed) |
| Far-future motors (dream build) | ~$33/each × 18 joints ≈ $600 — deferred |

---

## Session history (documented from ChatGPT threads)

### Thread 1 — Arduino car programming (`chatgpt.com/share/6b002572…`)
…(documented in Chat 1 facts section below)…

### Thread 2 — from sphere robot to servo digger (`chatgpt.com/share/6b00259a…`)
…(chat 2 facts)…

### Thread 1 — Arduino car programming (`chatgpt.com/share/6b002572…`)

- **Boards owned:** Arduino MKR WiFi 1010 (main brain, 3.3 V logic), Arduino Uno R3
  (from the Arduino Starter Kit), Duino Nano (from the robot kit).
- **Kits owned:** ZYC0055 robot car (two driven wheels + steel ball caster, supplied
  the Nano), Kjell & Company module kit 87291 (39 sensor modules), Arduino Starter Kit.
- **Goal of that thread:** a car that drives smoothly around the room without hitting
  things, WiFi over HTTP, and microphone audio streaming.
- Vehicle is a perfect circle → tank turns are fine.
- Motor driving evolved from raw 4-pin `digitalWrite` sequences to an H-bridge-style
  driver with pins `A_IA/A_IB` (left) and `B_IA/B_IB` (right); on the Nano the left
  motor used pins 9/10 and pin 5/6 were tried earlier.
- The **left motor was mounted upside down** → its forward/backward is inverted;
  helper functions `leftMotorForward/Backward/Stop`, `rightMotor*` and
  `moveForward/moveBackward/turnLeft/turnRight/stopMovement` were written,
  then split into multiple files.
- **Nano pin D10 appears broken** — reads `1` in both HIGH and LOW states.
  Swapping the two motor wires (D9↔D10 ↔ A_IA↔A_IB) reversed the motor as expected.
- Wanted calibrated motion (`moveForwardCm`, `turnLeftDegrees`, …) — the current
  `RobotMotion` sketch has exactly these as `Movement.h/cpp` + `MotorControl.h/cpp`.
- Architecture chosen: **Nano = movement brain, MKR WiFi 1010 = main brain**.
  First tried I²C with resistor dividers (5 V ↔ 3.3 V); the current firmware uses
  a **UART text protocol** at 9600 baud (`Serial1` on MKR ↔ `SoftwareSerial(2,3)` on Nano):
  `FWD <cm> | REV <cm> | LEFT <deg> | RIGHT <deg> | STOP` → `OK` / `ERR UNKNOWN COMMAND`,
  the Nano prints `READY` at boot.
- MKR WiFi 1010 "no port" problem was a **charge-only USB cable** (double-press reset +
  a data cable fixed it).
- Resistor stock identified by colour code: 220 Ω, 1 kΩ (×5 extra), 4.7 kΩ, 6.8 kΩ,
  10 kΩ, 100 kΩ, 1 MΩ; plus 1N4007 diodes.
- A **Raspberry Pi Pico (2020)** was later discovered in inventory.

### Thread 2 — from sphere robot to servo digger (`chatgpt.com/share/6b00259a…`)

- Original ambition: a 400 mm sphere that unfolds into 6–8 walking legs (2–3 powered
  joints per leg), weight < 2 kg (then 3–5 kg), able to climb 22 cm stair steps.
- Candidate motor: **Luxorparts stepper motor with gearbox + driver, 4-pack**
  (Kjell / p90775). Stepper-vs-servo-vs-brushless was discussed; ~18 joints × $33
  ≈ $600 total.
- **Decision:** start cheap — **4 × SG90 9 g micro servos** to learn servo control.
- Pivoted build: an **excavator arm** with a **pulley drive using 0.5 mm fishing
  line** — one servo for the horizontal rotation at the base, one for the gripper;
  real-world inspiration photo of a cable/pulley-driven Volvo material handler.
- Requirements: stable circular platform (⌀160 mm in that thread; grown to ⌀250 mm in
  this repo after the user got the Kobra S1), must not flip over while picking socks
  and dog toys; parts must fit the 250 × 250 × 250 mm printer.

## Hardware inventory

**Compute / motion**

| Item | Notes |
|---|---|
| Arduino MKR WiFi 1010 | Main brain, WiFi (NINA-W102), 3.3 V logic, SAMD21 |
| Duino Nano / Arduino-compatible Nano | Movement brain, 5 V logic, ATmega328P; **pin D10 possibly broken** |
| Arduino Uno R3 | Spare / prototyping |
| Raspberry Pi Pico (2020) | Spare |
| 4 × SG90 9 g micro servo | The actors of the digger: base rotation, winch, gripper, spare |
| H-bridge motor driver (ZYC0055 car) | Pins `A_IA/A_IB`, `B_IA/B_IB` on the Nano; left motor mounted upside-down |
| Spare motors | Luxorparts steppers 4-pack w/ gearbox & driver (Kjell p90775) — deferred option for heavy joints |

**Printer:** AnyCubic Kobra S1 Combo + ACE Pro 1, 250 × 250 × 250 mm usable volume.

**Sensor kit (39 pcs, Kjell 87291)** — grouped by expected task:

| Group | Modules |
|---|---|
| Obstacle / distance | Obstacle avoidance, dual ultrasonic, IR receiver + 5 mm IR LED, laser module |
| Colour / light | TCS3200 colour sensor, LDR, 2× light seeking, RGB LED, RGB SMD, 2× two-colour LEDs, 7-colour flash |
| Motion / contact | Hit, vibration shock, tilt switch, touch, button switch, joystick, rotary encoder, reed switch (large + mini), linear Hall, hall effect |
| Environment | DHT temperature & humidity, DS18B20, analog temp, digital temp, flame sensor |
| Sound | Large microphone, small microphone, **active buzzer**, **passive buzzer** |
| Line / misc | Line tracking, optical broken (beam), pulse sensor, relay (5 V), tracking module |

Small parts: resistors (220 Ω, 4.7 kΩ, 6.8 kΩ, 10 kΩ, 100 kΩ, 1 MΩ, 5 × 1 kΩ),
1N4007 diodes, breadboards, jumper wires.

## Firmware (as repo'd today)

`ArduinoProject` (symlink → `~/Documents/Arduino/HooverBot`):

```
RobotBrain/   RobotBrain.ino      MKR 1010: forwards text commands from
                                  USB Serial to Serial1 (9600) and echoes Nano replies
RobotMotion/  RobotMotion.ino     Nano: parses FWD/REV/LEFT/RIGHT/STOP over SoftwareSerial(2,3)
              MotorControl.h/.cpp moveForward/Backward, pivotLeft/Right, stopMotors
              Movement.h/.cpp     calibrated moveForwardCm / turnLeftDegrees …
```

Protocol: `FWD <cm>`, `REV <cm>`, `LEFT <deg>`, `RIGHT <deg>`, `STOP` →
`OK` after completion or `ERR UNKNOWN COMMAND`; Nano boots with `READY`.

## CAD — step 2 deliverables (rotator base, servo housing, deck, basket)

Source of truth: **`cad/rotator_base.py`** (parametric FreeCAD Part scripting).
Rebuild all STLs:

```bash
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd cad/rotator_base.py
```

Generated STLs in `stl/` (validated: solid/watertight, all within print volume):

| File | Size (mm) | Volume | Print notes |
|---|---|---|---|
| `base_platter.stl` | 250 × 250 × 33.7 | ~647 cm³ (≈800 g PLA) | One chunk; plate fills the bed → print **with skirt (3–5 mm), no brim**; no supports needed |
| `turret_deck.stl` | ⌀170.8 × 5 | ~111 cm³ | Flat print; no supports |
| `catch_basket.stl` | 96 × 88 × 60 | ~38 cm³ | Flat print (tabs up); no supports |

Height references (from floor): plate top 4 mm · hull ring top 20 mm · **dock top 26 mm** ·
servo body top / flange ledges 26.9 mm · spline top 33.5 mm · **deck underside 33.7 mm · deck top 38.7 mm** ·
basket (on deck) top 94.7 mm.

### How the mechanism works
1. The **SG90 (base rotation) stands upright in the center housing** of the base
   platter: it drops in through a 24.2 × 13.2 mm opening (X-guided, body resting
   on the plate), and the 32.5 mm mounting flange clamps onto printed ledges at
   z = 26.9 mm (servo body top). No screws needed; add a velcro/foam strap later
   if it ever rattles.
2. A **⌀10 mm bore in the housing floor + base plate** (at X = 0, Y = +7.2 mm,
   countersunk underneath) lets the **3 servo wires pass through to below the
   base** — the servo drops in from the top, wires exit the bottom.
3. A **second ⌀10 mm bore** at (0, +16 mm) runs from below the plate up through
   the deck (deck hole at the same point, clear of the ⌀20 horn disc) into the
   turret — reserved for the future boom/gripper servo wires. Without a slip
   ring, **keep turret swings within ±180°** and sweep back to unwind.
4. The **turret deck (⌀170.8)** rides on a bearing collar (r 85.1–89 mm) — a
   printed lazy-susan with no bearings. The collar **skips its rear sector
   (Y < −35)** so it never crosses the battery dock; the deck floor clears the
   dock top by 7.7 mm through the full 360° swing. A wax crayon or PTFE spray
   on the collar top reduces friction for the SG90.
5. Deck → servo coupling uses the **SG90's round disc horn underneath the
   deck**: it hangs on the spline, the deck's 8 radial slots (PCD ~10 mm, two
   45°-offset families, self-tap ⌀2.8) catch the horn's hole pattern, and the
   **long center screw (≈M2 × 10, from the SG90 bag) self-taps into the spline
   center** through the countersunk deck hole. If the long screws are too
   short to also span deck→horn on the side slots, one drop of cyanoacrylate
   between horn disc and deck underside solves it — glue AFTER test-fitting.
6. **Battery = the Anslut 10000 mAh power bank** (`powerbank.jpg`, ≈148 × 68 × 17 mm
   — *estimated from the photo, measure yours*): it lies **flat and slides into the
   rear dock from the front**, cell ≈150 × 68 × 18.5 mm, open front + open top, so
   swapping takes seconds and no tools. The dock top (z = 26) sits under the
   rotating deck's sweep (deck underside 33.7). The Nano/breadboard stays on the
   desk next to the digger (that's also where USB programming happens).
7. **Basket rides on the rotating deck** (rear side, 96 × 44 × 56 mm, slatted
   gripper-facing front + windows + drain holes): two tabs drop into slots in the
   deck at local (±20, +55); place the basket centre at deck-local (0, +41).
   Riding with the deck means the gripper always dumps into it and nothing fixed
   is ever in the deck's sweep zone. Lift off (or unscrew later) to empty.
8. **Buzzer/speaker**: 32 × 18 × 12 mm pocket on the front-left rim with a
   3-pin slit and a wire bore through the platter; fits the kit's active buzzer
   module (passive buzzer = fun with `tone()` later).

### Wiring plan for the digger (4 SG90: base, winch/boom, gripper, spare)
- Signal pins from the Nano PWM pins (9/10 are motor-driver pins on the car —
  use 3, 5, 6, 11 or A-pins on the digger prototype; **remember D10 may be dead**).
- Power servos **from their own 4.8–6 V pack (battery dock), common GND with the
  Nano** — never from the Nano's 5 V pin under load (SG90 stall ≈ 0.65–0.8 A each).

### Verified part dimensions used
SG90 **user-measured**: body 22.8 × 12.5 × 22.9 mm (L×W×H). Datasheet values for the
rest: flange 32.5 mm span (drop ledges clamp it — slots/0.7 mm clearance absorb
variance), knuckle boss + spline ≈ 6.6 mm above the body, spline ⌀4.8
(round horn ⌀20 × 3 mm disc accessory). Control range ≈ 180°, 4.8–6 V,
1.8 kg·cm @ 4.8 V.

## Assumptions & open questions
- SG90 clones vary ±0.5 mm; the drop pocket has 0.7 mm clearance and the deck's
  horn slots are radial, so hole-pattern and spline-clocking variance is absorbed.
- Power bank dims (≈148 × 68 × 17) are estimated from `powerbank.jpg` — measure
  it with a ruler and adjust `DOCK_W / DOCK_D / DOCK_H` in `cad/rotator_base.py`
  if my numbers are off; regenerate and the dock refits.
- The long horn screw from the SG90 bag (≈M2 × 10) is needed for the deck↔spline
  connection; if the bag's screws are too short for the four side slots, use one
  long center screw + a drop of cyanoacrylate on the horn disc (after test-fitting).
- No slip ring: keep swings ≤ ±180° (or add unwinding sweeps).
- SG90 stall current (~0.7 A each) vs power bank 5 V USB output (~2 A): fine for
  1–2 servos moving at a time, which the digger's kinematics guarantee.

## Repo layout
```
HooverBot/
├── README.md            this file — all facts + goals
├── AGENTS.md            standing instructions for coding agents
├── image.png            inspiration: Volvo cable/pulley material handler
├── powerbank.jpg        the battery: Anslut 10000 mAh power bank (dock is sized for it)
├── ArduinoProject -> ../../Documents/Arduino/HooverBot   firmware (outside repo)
├── cad/rotator_base.py  parametric FreeCAD build script (mm, Z-up)
└── stl/                 generated STLs (regenerate, never hand-edit)
```



