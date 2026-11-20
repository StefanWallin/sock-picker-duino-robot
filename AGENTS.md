# AGENTS.md — HooverBot working instructions

Purpose: keep every agent session consistent. Read `README.md` first — it holds the
goals checklist, all project facts and the current design state. Update it as work
completes.

## Golden rules
1. **Never** invoke interactive pagers (`less`, `more`, bare `git log`, `git diff`,
   `git status` long-form, build tools that page). Use `git --no-pager log --oneline -5`,
   `git --no-pager diff | head -40`, `head/tail/grep`, and non-interactive flags everywhere.
2. All commands must run non-interactive; redirect long output to files and grep them.
3. Units are **millimetres**, Z-up, in all CAD files. Servo/model dims come from the
   "Verified part dimensions" section of the README; record new measurements there.
4. Nothing gets purchased without explicit user approval — design around free/printed
   joins, zip ties, fishing line, tape, and hardware already owned.
5. Every generated part must be smaller than **250 × 250 × 250 mm** and print without
   supports if at all possible; state the expected overhang behaviour in the README.

## CAD workflow (step 2 pattern — reuse for every mechanical step)
- One Python file per assembly in `cad/`, e.g. `cad/rotator_base.py`.
  Top = parameter block with comments (dims, print tool refs, clearances).
  Only standard-library + FreeCAD modules; entry point builds + exports on import.
- Build & validate:
  ```bash
  /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd cad/<file>.py 2>&1 | grep -E 'bbox|Exception|Error'
  ```
  The script itself asserts `shape.isValid()` + watertight mesh (`Mesh.Mesh(path).isSolid()`)
  and prints bbox — treat a failed assertion as broken; fix geometry, re-run.
- STLs in `stl/` are **generated artifacts**: regenerate via the script, never hand-edit.
- Booleans: `Part.makeBox/makeCylinder/makeCone` + `fuse`/`cut` + `removeSplitter()`
  at the end of each builder (proven pattern in `cad/rotator_base.py`).
- After rebuild, update the size/volume table in the README if numbers changed.

## Firmware workflow
- Firmware lives outside the repo: `ArduinoProject -> ~/Documents/Arduino/HooverBot`
  (`RobotBrain` = MKR WiFi 1010, `RobotMotion` = Nano). Keep the split-brain
  architecture: Nano drives hardware in real time; MKR owns WiFi/web/logic.
- Text protocol over UART 9600 (`FWD <cm>`, `REV <cm>`, `LEFT <deg>`, `RIGHT <deg>`,
  `STOP`; replies `OK` / `ERR UNKNOWN COMMAND`; Nano boots with `READY`).
  New digger commands follow the same style (e.g. `SPIN <deg>`, `LIFT <pct>`,
  `GRIP <pct>`).
- Only the Nano's 5 V pin powers *logic*; servo rails come from the dock battery,
  share GND. Nano pin **D10 is suspect** — avoid for anything critical.
- When changing firmware, note the change + pins in the README (facts section) so
  no agent has to re-derive wiring.

## Docs duties (per session)
- Tick off completed goals in the README checklist, in plain markdown.
- Add new decisions/facts (measurements, purchases, serial protocol changes) to the
  README instead of chat-only statements. If it's not in the README, it didn't happen.
- Keep `AGENTS.md` itself updated if a tool/command changes.

## Commit style
Short imperative subject, optional two-line body. Example:
`cad: add turret deck + basket; validate bboxes`
Fine to commit generated STLs alongside their cad/ source change.

## Current focus (rotate as steps complete)
1. Fit-test printed base parts with the real SG90, battery, buzzer module (user).
2. `cad/digger_arm.py` — mast + boom + 0.5 mm fishing-line winch (Step 3).
3. `cad/gripper.py` — clamshell gripper (Step 4).
4. `ArmServo.ino` additions on the Nano + `SPIN/LIFT/GRIP` protocol (Step 5).
