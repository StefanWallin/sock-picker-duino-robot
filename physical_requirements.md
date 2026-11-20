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
- **PR-2** `[user]` Ground clearance under the chassis: **23 mm**.
- **PR-3** `[A]` Everything (incl. crane at rest and box) fits within the ⌀250
  cylinder; the crane may reach *outside* only while working. **[confirm — Q2]**

## 3. Drive & chassis
- **PR-4** `[user]` Two driven wheels, **⌀67 mm**. `[A]` differential/tank steering
  (no steering servo). **[confirm — Q1]**
- **PR-5** `[user]` Third contact point = **metal pivot wheel with flat-topped
  housing, 20 mm total height incl. housing**, at the rearmost point.
- **PR-6** `[user]` **Battery rests low, in the rear, on top of the pivot-wheel
  housing, between the drive wheels** — doubles as counterweight against
  forward picking loads.
- **PR-7** `[user]` Crane working/lifting zone: wedge **±60° from the front
  centerline**.
- **PR-8** `[user]` Drive-wheel placement tension: far forward fights nose-tilt;
  too far forward raises sideways-tip risk. Initial instinct: ~10% (≈12.5 mm)
  ahead of body centreline. To be settled by support-triangle analysis
  (stability section below). **[analysis pending]**
- **PR-9** `[A]` Wheel wells: axle at 33.5 mm height vs 23 mm floor ⇒ wheels sit
  in body cutouts; plan the shell as bed-tray + 2–3 printed shell sections.

## 4. Layout onboard
- **PR-10** `[user]` Crane occupies the **front 60%** of the plan view, the **small
  box the rear 40%** (box contents/capacity to define — **[Q5]**).
- **PR-11** `[user]` **Low center of gravity is a primary design driver.**

## 5. Front bumper + sensing
- **PR-12** `[user]` Rounded **spring-loaded front crash bar** acting as the hard
  bump stop.
- **PR-13** `[user+inv]` Bumper must actuate at least one trip sensor. On-hand
  candidates: button switch, hit sensor, vibration shock, tilt switch.
- **PR-14** `[user]` Front array: **2× dual ultrasonic + 1× obstacle avoidance
  (IR)**. Side/rear sensing TBD **[Q6]**.

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

## 9. Decisions log (confirmed with user)
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
  universal wheel on a 4-screw flange at the rear.

## 10. Still open (do not design before these close)
- [ ] **Q10 → resolved as D8** pending one user check: does the 4×AA holder from
      the ZYC0055 actually exist and can it be spared from the old car?
- [ ] **Q11 → resolved as D9** (≤200° working arc, slew servo fixed to base,
      crane servos rotate on the turret, unwind discipline; no slip ring, no
      true-360 servo mounting gymnastics).
- [ ] **Q12 → resolved as D7/D8** (hollow shell + rear-low ballast pockets,
      not a ballast-filled body, no U-notch) — awaiting user acceptance.
- [ ] **Q9 (measurements, how-to below — ruler only):**
  1. **Track width** = distance between the two wheels' ground-contact centres.
     Easiest: stand the car on paper, mark both contact patches, measure
     centre-to-centre. This sets the sideways-tip defence (support triangle).
  2. **Wheel hub & motor mounts**: how the 67 mm wheel grips the TT motor's
     ⌀3 shaft (press-on hub? screw? D-flat?), and how the TT motors fasten to
     the acrylic (bracket? double-sticky? the kit's plastic clamps?) — we must
     reprint equivalents on the new chassis.
  3. **Caster dome**: outer diameter, total height (should be ≈20 mm per your
     spec), the 4-screw flange spacing, and position from the rear edge.
  4. **18650 holder** outer dimensions (for the bay): if 2×18650 holder is not
     on hand, note that too.
  5. **Front bumper span**: how wide the crash bar should wrap around the front
     (chord across the ⌀250 at the front), and the free travel your printed
     accordion spring has when compressed by ~5 mm.
- [ ] **Q6** Side/rear sensor coverage (which spare modules).
- [ ] **Q7** Docking/charging: out of scope for v1?
- [ ] **QC-TT (calipers, when built)** confirm TT gearbox dims: length, width,
      height, shaft-to-mount-face distances, and the two rear-mount hole
      positions on the gearbox front face.

## 11. Assistant recommendation on internal architecture (answering Q12)
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
