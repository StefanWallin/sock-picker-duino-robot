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

## 10. Still open (do not design before these close)
- [ ] **Q10 (new)** Servo power rail: SG90s want 4.8–6 V, but the 2×18650 pack
      is 7.4 V nominal (out of spec for SG90) and the power bank's 5 V/2 A line
      is shared with the MKR. Options on hand: share the bank (brownout risk on
      double stall), an AA×4 holder if one exists in the drawers, or an approved
      buck converter purchase (needs user sign-off).
- [ ] **Q11 (new, interpretation)** Slew-arc semantics: does "not more than 200°
      for reaching" mean a ±100° window around the front centerline (dump =
      slew the long way around to the rear), and wires twist/unwind without a
      slip ring? *(provisional: yes)*
- [ ] **Q12 (new, user asked assistant)** Internal architecture: ballast-filled
      body vs U-notch front — assistant recommendation recorded below (D7),
      pending user acceptance.
- [ ] **Q9 (measurement)** Track width between 67 mm drive-wheel contact
      patches, wheel hub type, caster housing diameter/position — needed for
      the support-triangle math (SM-1/SM-2).
- [ ] **Q6** Side/rear sensor coverage (which spare modules).
- [ ] **Q7** Docking/charging: out of scope for v1?

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
