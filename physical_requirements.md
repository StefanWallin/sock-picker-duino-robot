# HooverBot — Physical Requirements

> **STATUS: DRAFT — requirements gathering in progress.**
> Nothing here is final until jointly confirmed. Tags: `[user]` = stated requirement,
> `[A]` = assistant assumption, needs confirmation, `[Q#]` = open question.

## 1. Mission
Self-propelled car that roams a room, finds socks / dog toys, picks them up with a
crane and stores them onboard — the car-crane contraption. One machine: **drive
system + crane + carry box** in a single ⌀250 mm footprint.

## 2. Envelope & platform
- **PR-1** `[user]` Body = vertical cylinder, **⌀250 mm (hard limit — print bed)**,
  height ≈ **150 mm**.
- **PR-1b** `[A, from crossbar scenario]` A crane on top means the robot's
  **total stowed height `H_stow` ≈ 200–230 mm** (boom parked vertical). Any
  horizontal clearance < `H_stow` + 20 mm is a **no-go zone** (example: chair
  crossbars at 15 cm): the robot must detect the edge and not enter —
  it *cannot* fit, sensors included.
- **PR-2** `[user]` Ground clearance under the chassis: **23 mm**.
- **PR-3a** `[A]` Everything (incl. crane at rest and box) fits within the ⌀250 mm
  cylinder; the crane may reach *outside* only while working. **[confirm — Q2]**
- **PR-3b** `[user]` All electronics should fit within the ⌀250 mm cylinder and
  be protected from mechanical interference with the crane and storage box.

## 3. Drive & chassis
- **PR-4** `[user]` Two driven wheels, **⌀67 mm**. `[A]` differential/tank steering
  (no steering servo). **[confirm — Q1]**
- **PR-5** `[user]` Third contact point = **metal pivot wheel with flat-topped
  housing, 20 mm total height incl. housing**, at the rearmost point.
- **PR-6** `[user]` **Battery rests low, in the rear, on top of the pivot-wheel
  housing, between the drive wheels** — doubles as counterweight against
  forward picking loads.
- **PR-7** `[user]` Crane working arc: **wish ±100°** (fallback ±60°). The
  **200 g payload is the hard requirement** and outranks arc coverage; the final
  arc is whatever stability/torque analysis supports at that payload.
- **PR-8** `[user]` Drive-wheel placement tension: far forward fights nose-tilt;
  too far forward raises sideways-tip risk. Initial instinct: ~10% (≈12.5 mm)
  ahead of body centreline. To be settled by support-triangle analysis
  (stability section below). **[analysis pending]**
- **PR-32** `[A]` **Drive voltage limiting**: TT motors are rated ≤6 V while
  the pack is 7.4–8.4 V ⇒ cap motor PWM duty in software (~75% max; final
  value depends on the H-bridge's voltage drop, QC-1). No hardware needed.
- **PR-9** `[A]` Wheel wells: axle at 33.5 mm height vs 23 mm floor ⇒ wheels sit
  in body cutouts; plan the shell as bed-tray + 2–3 printed shell sections.

## 4. Layout onboard
- **PR-10** `[user]` Crane occupies the **front 60%** of the plan view, the
  **storage backpack ("small box") the rear 40%**. Box: **~3–5 socks** +
  maybe one small toy; the crane dumps into it from above after slewing rear.
- **PR-11** `[user]` **Low center of gravity is a primary design driver.**
- **PR-33** `[A]` The current `stl/` desktop-digger parts are **learning
  artifacts**, not car parts; the car-phase turret/slew ring will be
  re-derived, carrying over the horn coupling and ⌀10 wire pass-through
  concepts.

## 5. Front bumper + sensing
- **PR-12** `[user]` Rounded **spring-loaded front crash bar** acting as the hard
  bump stop.
- **PR-13** `[user+inv]` Bumper actuates at least one trip sensor: **hall +
  magnet** (contactless, recommended — see MI-5) with the button switch as
  wired-OR backup.
- **PR-14** `[user]` Owned sensing hardware: 2× dual ultrasonic, 1× IR obstacle.
  Sensor **requirements**: stop-before-contact across the bumper arc · cruise
  object detection ahead · close-range soft/dark-item detection (a sock is
  sonar- and IR-invisible — the hardest case) · fine gripper approach ranging ·
  **negative-obstacle (stairs/cliff) detection** · **threshold crossing up to
  the Q13 rise budget without false cliff trips**. Utilisation plan:
  **D15 / §5b**.
- **PR-14b** `[A]` Bumper z-band: the crash bar must cover the touchable
  silhouette, roughly **z 10–150 mm**, so nothing at body height slides under
  it.

### 5b. Sensor plan (D15 — proposal; owned modules only)
| Module | Mount | Job |
|---|---|---|
| Stereo sonar **board A** (parallel pair, unsplitable) | Body **front**, **level (0° tilt)**, height 60–80 mm | Vertical surfaces (walls/legs/boxes) at cruise ranges **+ overhead crossbars**: a 15 cm crossbar enters the level beam cone from ≈30 cm out ⇒ stop before entering. At ≥25 cm the cone spans z ≈ 0–150 mm — the whole mid-band between floor and body height |
| Stereo sonar **board B** (same type) | Body **rear**, 10–15° downtilt | Reversing safety + floor/step awareness behind |
| IR obstacle module | Body front centre, low (~30 mm) | Owns z 0–50 mm inside ~30 cm; backstop for dark/soft items sonar misses |
| **Downward IR reflectance ×2** (channels of the line-tracking module or spare obstacle modules, per kit inventory) | Nose, left + right, aimed at the floor ~5–10 cm ahead | **Cliff/stair vote (FLOOR-1..3)** — floor-present check |
| Bumper trip (hall + magnet / button) | Crash bar, MI-5 | Contact truth for z 10–150 mm — always wired as a stop |
| Crane-top **whisker** + tilt/vibration sensor | Highest point of the stowed crane | Contact last-resort against anything above the body (crossbars above beam cone included) |
| *(v2, owned)* TCS3200 + LDR pair | Gripper/turret | Sock-vs-floor discrimination at hover (sonar can't see cloth) |

**Z-coverage ladder (floor → above body):** downward IR pair (floor presence
at the nose) → IR obstacle low (z 0–50 ≤ 30 cm) → level sonar cone (z 0–150 at
≥25–30 cm) → bumper (z 10–150, contact) → crane whisker (above body).
Residual gap: ≤4 cm items at 15–30 cm range, grazing-weak echo — that height
class is usually the *target* (sock), not an obstacle; handled by pick logic.

**Floor rules (FLOOR-1..3):**
- **FLOOR-1 cliff vote**: floor-missing on **both** down channels (>50 ms)
  **and** level-sonar range jumped out ⇒ stop, reverse, mark the edge. Rationale:
  a sock or shadow can blind one channel, never both; wide stairs blind both.
- **FLOOR-2 threshold climb**: floor *present and closer* (stronger reflectance)
  never trips FLOOR-1 ⇒ climbing stays enabled up to the Q13 rise budget
  (25–35 tuned / 40–50 stretch).
- **FLOOR-3 single-channel loss** = not a cliff: log, slow, continue.

**Clearance & rotation rules (CEIL + ROT):**
- **CEIL-1** `H_stow` (PR-1b) is a tracked design constraint; the crane is
  designed so the stowed pose is as **short and narrow** as possible.
- **CEIL-2 ceiling state machine**: `UNKNOWN → LEVEL-SCAN → CLEAR / LOW`.
  `LOW` = any level-beam target above the body height, whisker trip, or
  unverified space. In `LOW`: crane motion, in-place rotation and forward
  entry are **locked**; only straight reverse-out is allowed. `CLEAR` requires
  a verified level scan plus the 360° ring check below.
- **CEIL-3** Recovery if already under low furniture: crane to stowed, stop,
  **reverse straight out** along the entry line; no rotation (the entry line
  is the only verified corridor).
- **ROT-1..3 (in free space ≥ `H_stow`+20)**: crane stowed; rotate in ≤15°
  segments with both boards reporting the ring clear (front beam leads, rear
  beam mirrors ⇒ CW/CCW symmetric); turret dump-swing only inside a verified
  dump-clearance zone (⌀ ≥ ~350 mm at crane heights).
- Forward light: **not needed in v1** — every v1 sensor is active (ultrasonic,
  own-IR, contact); no IR flood either (saturates the obstacle module). v2
  colour reading uses the TCS3200's on-board white LEDs; the owned LED module
  is an optional MKR-driven status beacon only.
- Pings are staggered (A then B) to avoid sonar crosstalk.

## 6. Crane actuation inventory (hard constraints)
- **PR-15** `[user]` **4× SG90** in total; **one is dedicated to turret slew**.
- **PR-16** `[user]` **2× DC motors** available if reeling-in heavy items needs them.
- **PR-17** `[user]` Weak-motor mitigations explicitly on the table: **ballast,
  counterbalance, elevated pivot points, pulley & tackle**.
- **PR-18** `[A→user]` Payload decided: **up to ~200 g** per pick (socks + small
  per pick. Preliminary physics check (NOT a design commitment): crank/linkage
  or counterbalance can put this inside 2× SG90 capability — the DC motors stay
  **reserve** (optional winch/if we need higher grip force), not a requirement
  at this stage.
- **PR-19** `[A]` Crane function split for 4 servos candidates: {slew, boom/jib,
  grab, spare→stick elbow} or {slew, boom, grab, drum for counter-pulley};
  **still undecided — mechanics phase decides, not here**.

## 7. Stability math to be done (placeholders)
- **SM-1** Support polygon = drive contacts (2) + caster contact (1); body CG +
  cargo + max working pick load must stay inside under: static, acceleration,
  10° threshold/rug climbs.
- **SM-2** Counterweight budget: bank (218 g) on the caster housing vs reach and
  payload at ±60° reach — compute the required rear mass.
- **SM-3** Track vs wheelbase trade-off behind PR-8 (needs actual track width).

## 8. Decisions log (confirmed with user)
- **D1** — Chassis: **custom Roomba-style chassis**, reusing ZYC0055 components
  (drivetrain motors, battery holder); power bank is an *option* where useful
  (e.g. logic rail). *(Q1 answered)*
- **D2** — Payload: **up to ~200 g** per pick (socks + small dog toys).
  *(Q3 answered, revised upward)*
- **D3** — v1 control: **USB/WebSerial + keyboard first, WiFi later**. *(Q4)*
- **D4** — Crane envelope: tip must reach **≥70–80 mm outside the ⌀250
  perimeter**; slew **mechanically 360°**, with the **working (reaching) arc
  limited to ≤200°** and the rest available to **dump into the rear "backpack"
  compartment**. *(Q2 answered)*
- **D5** — Drive battery: **2×18650 Li-ion** in the reused ZYC0055-style holder;
  power bank (5 V) reserved for logic. *(Q8)*
- **D6** — Rear box: **small — ~3–5 socks** (plus maybe one small toy).
  *(Q5)*
- **D8 (proposed — power architecture, zero purchases)** *(from Q8 + car photo)*:
  **2×18650 Li-ion → drive motors + Nano VIN** (7.4 V is inside Nano VIN spec,
  out of SG90 spec); **the ZYC0055 4×AA holder → servo rail** (4×AA = 6.0 V
  nominal, dead-center of the SG90's 4.8–6 V spec; SG90 stall ~0.7 A × 2 =
  1.4 A < 4×AA realistic pulse capability for short stalls); **power bank
  (5 V USB) → MKR 1010 only**. Common GND across all three rails.
- **D9 (proposed — slew architecture, answers "motors under the ring")**:
  the **slew servo stays fixed to the base**, driving the turret through the
  horn/deck coupling already moulded into the deck centre — its wires never
  twist. The crane servos (boom, grab, future stick) **mount low on the turret
  and rotate with it** (low CG, your instinct), and their wires cross the
  rotating joint once through the ⌀10 pass-through; twist stays small because
  the **working arc is ≤200°** and we unwind during the rear dump swing.
  Rationale against mounting ALL motors incl. slew under the ring: their wires
  would still cross the joint, and a rotating link for the slew servo adds
  precision loss — the horn-under-deck path is simpler and already printed.
- **D10 (proposed — bumper spring)**: use the **3D-printed accordion spring**
  (`spring.jpeg`) as the crash-bar spring: geometry is a free design parameter
  (zigzag depth/count/wall tune stiffness at the bench); pairs with the button
  switch module as the trip sensor.
- **D11 (hardware identification — from photos)**: drive motors are **standard
  yellow TT gearbox motors** (typ. gearbox ~66 × 22.5 × 18 mm, twin ⌀3 plastic
  output shafts, ~1:48 gearing class, 3–6 V — *verify against calipers*), as
  in `car.webp`: acrylic ZYC0055 platform, 4×AA holder amidships, dome
  universal wheel on a 4-screw flange at the rear. *(updated by HardwareImages
  folder: real chassis is black moulded ABS kit plate; battery box on the real
  car is the 2×18650 holder; driver is a blue H-bridge board under the Nano
  expansion shield — model TBD)*
- **D12 (materials)** — prototypes in **PLA**; final chassis + crane in
  **PETG-CF**; **TPU** where compliance helps (bumper skin/pads, optional wheel
  fairings, printed springs). **Operational note: user has a hardened-steel
  nozzle installed — PETG-CF/abrasive filaments are cleared for the final
  runs regardless of nozzle wear.**
- **D13 (slew transmission — option registered, not decided)**: direct horn
  drive is the default; a **printed spur gear ring on the turret + servo pinion
  (~2–3:1)** is allowed if bench friction tests show the slew servo struggles
  under full 200 g reach. Trade-off: ~2–3× torque for ~2–3× slower slew
  (still ≥200°/s), plus ~0.5–1° tooth backlash — acceptable at sock-picking
  accuracy. Decision deferred to mechanics phase with real friction data.
- **D15 (proposed)** — Sensor plan, table in §5b with **z-coverage ladder**,
  **floor rules FLOOR-1..3** (two-channel cliff vote ≠ sock shadow; thresholds
  never trip it) and **clearance gates**: sonar board A front **level**
  (vertical surfaces + overhead crossbars from ≈30 cm; covers z 0–150 at ≥25 cm),
  board B rear downtilted (reversing + floor), nose-down IR pair for cliffs,
  IR backstop low, bumper = contact truth z 10–150, **crane-top whisker +
  vibration = contact last-resort**; ceiling state machine locks crane/rotation
  under low furniture (PR-1b no-go zones); missing echo ⇒ obstacle; staggered
  pings. v2: TCS3200 + LDR for sock discrimination. *(pending user acceptance)*
- **D14 (chassis provenance)** — the Roomba-style chassis is designed **from
  scratch**; *no* moulded/machined part is reused (no acrylic, no kit plate).
  Only **components** are carried over: 2× TT motors, 2× ⌀67 wheels (yellow
  hubs), 2×18650 holder, 4×AA holder, dome caster, blue H-bridge module, Nano
  + expansion shield, MKR, dual-ultrasonic units, buzzer modules, printed
  accordion spring.

## 9. Measured interfaces (Q9 answers — design inputs)
- **MI-1 TT motor mount** `[measured]`: 2 × ⌀3 fixing screws, **17 mm
  centre-to-centre**, on the motor face; that screw centreline is **19 mm
  from the axle centreline** → printed bracket geometry per side.
- **MI-2 Track width** `[user decision]`: not bound to the old car. Target
  **outer track ≈ 230–250 mm** (as stable as fits; wheels nearly tangent to the
  ⌀250 silhouette, recessed into wheel wells; wells must clear ⌀67 wheel +
  tyre width; body silhouette stays ⌀250).
- **MI-3 Caster** `[measured + user brief]`: mount plate **48 × 33 mm**;
  fixing screws **2 × 39 mm c-c** on opposite sides of the dome; dome casing
  **⌀26–30 tapered**; total height ≈20 mm. Position from the rear edge: chosen
  by assistant to support **40–50 mm threshold climbs** — see IC-5/Open (likely
  ≈30–35 mm from rear edge, plate flush with the internal floor; battery sits
  directly above it per PR-6).
- **MI-4 2×18650 holder** `[measured]`: **92 × 43 × 22 mm**; mount holes square
  pattern **39 × 30 mm**, **21 mm from the short side opposite the
  cable/switch end**; cells load from the cable end. Bay must allow quick
  cell swap.
- **MI-5 Bumper** `[user decision]`: **straight linear push** (no pivot),
  covering **±40° from centreline (80° arc ⇒ chord ≈ 161 mm at the ⌀250
  edge)**; travel **5–8 mm**.
  - *Early detection with full travel:* the trip sensor fires early (~2–3 mm)
    while a series compliance (printed accordion spring / TPU pad) absorbs the
    remaining travel — same principle as commercial robot vacuums.
  - *Trip sensor candidates (on hand)*: hall effect/linear hall with a small
    magnet on the bar (contactless, no plunger wear — recommended), button
    switch module as wired-OR backup.
  - Bar/skin printed in TPU (D12); travel guided by printed rails.

## 10. Consistency scan & decision tree

```
Mission: roam → find sock/toy → pick (≤200 g, ±60° front wedge) → store (backpack, rear 40%)
│
├─ MOBILITY (drives 67 mm wheels, track 230–250) ──────────── stable?
│   ├─ Drive power: 2×18650 = 7.4–8.4 V vs TT motors rated ≤6 V
│   │   → IC-1 RESOLVED: cap PWM duty (≈75% max) in software; verify H-bridge
│   │     model (L298N-class drop actually helps; MX1508-class needs stricter cap) [QC-1]
│   ├─ MKR VIN must NOT see 8.4 V → MKR on power bank USB only (D8) ✓
│   ├─ Servo rail: 4×AA = 6.0 V (D8) — fresh alkalines peak ≈6.4 V
│   │   → IC-3: prefer NiMH 4×AA (4.8–5.2 V) or accept short peaks [QC-2]
│   ├─ Thresholds 40–50 mm vs ⌀67 wheels (r=33.5): a 50 mm step is 75% of the
│   │   wheel radius — only climbable with CG-forward pivot + chamfered nose
│   │   + caster that never catches
│   │   → IC-5 OPEN: accept 25–35 mm realistic, or add trailing-arm caster +
│   │     nose ramp for the 40–50 stretch [USER — Q13]
│   └─ Track/axle placement vs tipping: needs SM-1/SM-2 with real masses
│       (structure not yet drawn) [BENCH + MATH]
│
├─ CRANE (4× SG90, one = slew)
│   ├─ PRIORITY (PR-7 revised): 200 g payload is HARD; working arc is the wish
│   │   (±100° target, ±60° fallback, over-reach 70–80 mm)
│   ├─ Torque at shoulder with 200 g payload ⇒ torque multiplier required
│   │   → mechanisms phase decides: crank+link / counterbalance / gearing /
│   │     DC-motor winch reserve (D13-style option list) [MECHANICS]
│   ├─ Slew ≤200° working arc + 360° mechanical for rear dump (D4/D9) ✓
│   ├─ Slew transmission: direct vs gear ring (D13) [MECHANICS + BENCH]
│   └─ Spare servo role (elbow? counter drum?) [OPEN — MECHANICS]
│
├─ STORAGE (backpack rear 40%, ~3–5 socks)
│   ├─ Crane dumps from above into body-fixed rear compartment ✓
│   └─ Lid/opening/capacity fine-tuning [LAYOUT]
│
├─ SENSING (strategy D15 proposal, §5b — owned modules only)
│   ├─ Bumper = contact truth, z 10–150 mm (MI-5 + PR-14b) ✓
│   ├─ Sonar board A front, LEVEL: walls/legs + 15 cm crossbars from ≈30 cm;
│   │   cone covers z 0–150 at ≥25 cm (the whole mid-band) ✓
│   ├─ Sonar board B rear, downtilt: reversing + floor/step awareness ✓
│   ├─ Nose-down IR pair: cliff vote (both dark + sonar jump = stair);
│   │   thresholds never trip it (FLOOR-1..3, Q13 budget) ✓
│   ├─ Ceiling state machine (CEIL-2): LOW locks crane + rotation, reverse-out
│   │   only (PR-1b no-go zones under H_stow) ✓
│   ├─ Crane-top whisker + vibration = contact last-resort ✓
│   ├─ Close-range backstop: IR obstacle module for sonar-invisible items ✓
│   └─ v2 discrimination: TCS3200 + LDR pair at hover [PROPOSED]
│
├─ POWER (D8 rails) — QC-2 above; add: total current budget check
│   (2 drive stalls ~1.5–2 A? measure TT stall @5V-equivalent) [BENCH]
│
└─ CONTROL (USB/WebSerial keyboard first) — bench rig stays off-robot;
    only crane services rotate ✓ (IC-8 resolved)
```

**Inconsistency scan result:** no fatal contradictions found. Open/conflicting
leaves to settle before mechanics:
1. **IC-5 / Q13** — threshold target: realistic 25–35 mm vs stretch 40–50 mm
   (decides caster type, nose shape).
2. **QC-1** — identify the blue H-bridge module (voltage + drop) from its
   printing/silkscreen.
3. **QC-2** — which 4×AA chemistry (fresh alkaline peaks 6.4 V vs NiMH 4.8–5.2 V).
4. Smile-item: the existing `stl/` desktop parts are **learning artifacts**;
   the car-phase turret/ring will be re-derived (the horn-coupling and
   pass-through concepts carry over) — PR-33.
## 11. Open items (consolidated)
- [ ] **Q13 (from IC-5)** — threshold target: **25–35 mm realistic** (caster as
      spec'd, chamfered nose) or **40–50 mm stretch** (adds trailing-arm caster
      + nose ramp + stricter CG discipline)? Decides caster/nose geometry.
- [ ] **QC-1** — identify the blue H-bridge module (read its silkscreen; need max
      voltage + voltage drop) → finalises PR-32 PWM cap.
- [ ] **QC-2** — 4×AA chemistry for the servo rail: NiMH (4.8–5.2 V) preferred;
      fresh alkalines peak ≈6.4 V (above SG90 nominal, below its absolute max).
- [ ] **Q6** — are D15's safe-rotation rules (ROT-1..3) and front/rear sonar
      coverage enough, or does the robot need more side/rear sensing?
- [ ] **Q7** — docking/charging: confirmed out of scope for v1?
- [ ] **QC-TT (calipers)** — TT gearbox: L×W×H, shaft-to-face distances, mount
      hole positions (cross-check MI-1).
- [ ] **BENCH-1** — TT motor stall current at ≈5 V equivalent (for the power
      budget in §10 POWER).
- [ ] **BENCH-2** — printed accordion spring: force vs 5–8 mm travel (bumper
      threshold setting, MI-5).
- [ ] **BENCH-3** — slew friction with a loaded deck (gates D13 direct-vs-geared).
- [ ] **MATH-1** — SM-1/SM-2/SM-3 stability + ballast budget once the layout
      mass table exists (needs PR-8 wheel placement decision).

## 12. Assistant recommendation on internal architecture (answering Q12)
Neither "fill the entire body with ballast" nor a U-shaped front notch is my
recommendation. Rationale:
- A filled body adds 1–2 kg of dead mass the drive motors must haul, and ballast
  placed *forward* works against us; ballast is only useful **low and rear**.
- A U-shaped front notch shortens the needed boom, but costs shell stiffness,
  internal volume, and print simplicity — and the crane only needs ~7–8 cm of
  over-reach, achievable with boom length instead (crane occupies the front 60%
  anyway, so the shoulder sits ahead of the body centre already).
- **D7 (proposed)**: keep the full ⌀250 cylinder shell (2–3 printed sections);
  hollow interior; **tunable ballast pockets at the rear-bottom perimeter**
  (free mass: washers/bolts/scrap from the drawers) plus the 18650 pack + power
  bank as fixed rear mass. Ballast amount tuned at bench time to keep the CG
  behind the drive-axle line at full ±60°/200 g reach — computed in SM-2 once
  measurements (Q9) arrive.
