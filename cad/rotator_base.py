"""HooverBot step 2 — rotator base, turret deck and catch basket.

Parametric build with FreeCAD headless:
    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd cad/rotator_base.py

Exports (mm, Z-up, origin = centre of the base disc at floor level):
    stl/base_platter.stl   D250 fixed base: servo well, wire pass-throughs,
                           rear battery dock, buzzer pocket
    stl/turret_deck.stl    D169.6 rotating deck (rides on the well rim)
    stl/catch_basket.stl   lattice basket seating on the rear dock

All dimensions parameterised below; units are millimetres.
"""

import math
import os

import FreeCAD as App
import Part
import MeshPart
import Mesh

# --------------------------------------------------------------------------
# parameters — printer and platform
# --------------------------------------------------------------------------
PLATE_D = 250.0          # base disc diameter (user wish: 25 cm, == bed size)
PLATE_T = 4.0

# SG90 micro servo — USER-MEASURED body dims; flange/boss/horn from datasheet
SERVO_L = 22.8           # body length (along X below)
SERVO_W = 12.5           # body width
SERVO_H = 22.9           # body height (bottom -> top of body)
FLANGE_L = 32.5          # mounting tab span (both directions)
FLANGE_T = 2.5           # tab thickness, sits at the top of the body
SHAFT_Z_ABOVE_BODY = 6.6 # knuckle boss + spline above body top
HORN_D = 20.0            # round disc horn diameter (SG90 accessory)
HORN_T = 3.0             # horn disc thickness
HORN_LOCK_D = 2.8        # central horn->spline screw hole (long screw)
BOSS_WRAP_T = 2.0        # horn boss wrap height below the disc

CLEAR = 0.7              # printing clearance for drop-in fits
WALL_T = 3.0             # housing wall thickness

# derived — servo housing pocket
SERVO_POCKET_L = SERVO_L + 2 * CLEAR          # X span of the drop opening
SERVO_POCKET_W = SERVO_W + CLEAR              # Y span
FLANGE_SEAT_Z = PLATE_T + SERVO_H             # body stands on plate; flange
                                              # rests on the ledges at this z
SHAFT_TOP_Z = FLANGE_SEAT_Z + SHAFT_Z_ABOVE_BODY   # knuckle+spline top

# derived — deck bearing and horn clearance
DECK_R = 85.4                                 # deck outer radius
DECK_D = 2 * DECK_R
DECK_T = 5.0
COLLAR_IR = 85.1                              # deck bearing collar inner radius
COLLAR_OR = 89.0                              # collar outer radius (fusion into hull)
HORN_RECESS_T = 0.0                           # horn hangs below deck; no recess
DOCK_CLEAR = 3.0                              # min clearance deck vs dock top

# rear dock — full-width power-bank slide (Anslut 10000 mAh ≈ 148 × 68 × 17)
DOCK_W = 156.0                                # outer width (cell = 150)
DOCK_D = 71.0                                 # radial depth (Y)
DOCK_REAR_Y = -112.0                          # open front at Y = -41
DOCK_H = 22.0                                 # bank (17) slides flat, easy swap

# deck underside z: above the spline tip AND clear of the dock top
WELL_TOP_Z = max(PLATE_T + SERVO_H + SHAFT_Z_ABOVE_BODY + 0.2,   # spline tip
                 PLATE_T + DOCK_H + DOCK_CLEAR)                  # dock pass
HULL_ID = 172.0                               # hull ring inner diameter
HULL_H = 16.0                                 # hull top z = PLATE_T + HULL_H

# buzzer pocket (front-left hull rim)
BUZ_W = 32.0
BUZ_DEPTH = 18.0
BUZ_H = 12.0
BUZ_POS = (-38.0, 104.0)                      # pocket centre (X, Y)

# catch basket (rides on the rotating deck, rear side; deck-local slots)
BASKET_W = 96.0
BASKET_D = 44.0
BASKET_H = 56.0
BASKET_T = 2.4
TAB_W = 8.0
TAB_L = 8.0
TAB_T = 4.0
TAB_PCD_X = 40.0                              # tab spacing (±20)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "stl")

# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------
V = App.Vector
ZDIR = V(0, 0, 1)


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl(x, y, r, z0, z1):
    return Part.makeCylinder(r, z1 - z0, V(x, y, z0), ZDIR)


def cone(x, y, r_bot, r_top, z_bot, z_top):
    return Part.makeCone(r_bot, r_top, z_top - z_bot, V(x, y, z_bot), ZDIR)


def fuse_all(shapes):
    out = shapes[0]
    for s in shapes[1:]:
        out = out.fuse(s)
    return out


def cut_all(shape, tools):
    for t in tools:
        shape = shape.cut(t)
    return shape


def export(shape, name):
    path = os.path.normpath(os.path.join(OUT, name))
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.25,
                                  AngularDeflection=0.5, Relative=False)
    mesh.write(path)
    chk = Mesh.Mesh(path)
    bb = chk.BoundBox
    ok = bool(chk.isSolid()) and shape.isValid()
    print("%-22s bbox=(%.1f x %.1f x %.1f) mm  volume=%.0f mm3  solid=%s"
          % (name, bb.XLength, bb.YLength, bb.ZLength, shape.Volume, ok))
    assert ok, name + " failed validation!"
    return path

# --------------------------------------------------------------------------
# 1) base platter
# --------------------------------------------------------------------------
def build_platter():
    zp = PLATE_T
    # --- positive core: plate, hull ring, deck-bearing collar
    plate = cyl(0, 0, PLATE_D / 2, 0, zp)
    hull = cyl(0, 0, PLATE_D / 2, zp, zp + HULL_H).cut(
        cyl(0, 0, HULL_ID / 2, 0, zp + HULL_H + 1))
    # full-height collar: its top ring carries the rotating deck. A rear
    # sector is skipped (Y < -35) so the collar never crosses the dock.
    collar = cyl(0, 0, COLLAR_OR, zp, WELL_TOP_Z).cut(
        cyl(0, 0, COLLAR_IR, -0.1, WELL_TOP_Z + 1)).cut(
        box(-COLLAR_OR - 10, COLLAR_OR + 10, -COLLAR_OR - 10, -35.0,
            -1.0, WELL_TOP_Z + 1))
    solid = fuse_all([plate, hull, collar])

    # --- servo housing: drop pocket (Y guides) + flange ledges
    pl = SERVO_POCKET_L / 2                    # ±12.1 body-drop opening in X
    pw = SERVO_POCKET_W / 2                    # ±6.6, guides body in Y
    # Y end guides stop below the horn-disc sweep (disc bottom z = 28.9)
    z_end_top = FLANGE_SEAT_Z + 1.5
    solid = solid.fuse(box(-pl - WALL_T, pl + WALL_T, pw, pw + WALL_T,
                           zp, z_end_top))
    solid = solid.fuse(box(-pl - WALL_T, pl + WALL_T, -pw - WALL_T, -pw,
                           zp, z_end_top))
    # flange ledges: X stop for the 32.5 mm flange; rest height z = 26.9.
    # They span the full housing width so they fuse into the Y guides.
    led_x0 = SERVO_L / 2 - 0.3                  # slight overlap under the tab
    solid = fuse_all([solid,
                      box(led_x0, pl + WALL_T, -pw - WALL_T, pw + WALL_T,
                          FLANGE_SEAT_Z, SHAFT_TOP_Z),
                      box(-pl - WALL_T, -led_x0, -pw - WALL_T, pw + WALL_T,
                          FLANGE_SEAT_Z, SHAFT_TOP_Z)])

    # --- rear dock: full-width power-bank slide (open front + top)
    dx0, dx1 = -DOCK_W / 2, DOCK_W / 2
    dy0, dy1 = DOCK_REAR_Y, DOCK_REAR_Y + DOCK_D
    dock = box(dx0, dx1, dy0, dy1, zp, zp + DOCK_H)
    bank_cell = box(dx0 + WALL_T, dx1 - WALL_T,
                    dy0 + WALL_T, dy1, zp, zp + DOCK_H + 0.5)  # open front+top
    dock = dock.cut(bank_cell)
    solid = solid.fuse(dock)

    # --- buzzer pocket on the front-left rim
    bx, by = BUZ_POS
    bw, bd = BUZ_W / 2, BUZ_DEPTH / 2
    bt = 2.4
    bz0 = zp + HULL_H
    solid = solid.fuse(fuse_all([
        box(bx - bw, bx + bw, by - bd, by - bd + bt, bz0, bz0 + BUZ_H),
        box(bx - bw, bx + bw, by + bd - bt, by + bd, bz0, bz0 + BUZ_H),
        box(bx - bw, bx - bw + bt, by - bd, by + bd, bz0, bz0 + BUZ_H),
        box(bx + bw - bt, bx + bw, by - bd, by + bd, bz0, bz0 + BUZ_H)]))

    # --- negative cuts -----------------------------------------------------
    cuts = []
    # servo drop opening through the housing walls
    cuts.append(box(-pl, pl, -pw, pw, zp, SHAFT_TOP_Z + 1))
    # servo cable: notch in the +Y housing wall, bore through the plate
    cuts.append(box(-7.0, 7.0, pw, pw + WALL_T + 0.2, zp, zp + 6.0))
    cuts.append(cone(0, 7.2, 6.5, 5.0, -0.1, zp))
    cuts.append(cyl(0, 7.2, 5.0, -0.1, zp + 1.0))
    # future boom/gripper wires: second bore beside the horn disc
    cuts.append(cone(0, 16.0, 6.5, 5.0, -0.1, zp))
    cuts.append(cyl(0, 16.0, 5.0, -0.1, zp + 1.0))
    # buzzer: 3-pin slit in the pocket floor + wire bore through plate
    cuts.append(box(bx - 8, bx + 8, by - 1.6, by + 1.6, bz0 - 2.0, bz0 + 1.0))
    cuts.append(cyl(bx, by, 4.5, -0.1, bz0 + 1.0))

    solid = cut_all(solid, cuts)
    solid = solid.removeSplitter()
    return solid

# --------------------------------------------------------------------------
# 2) turret deck
# --------------------------------------------------------------------------
def build_deck():
    r = DECK_D / 2
    deck = cyl(0, 0, r, 0, DECK_T)
    cuts = []
    # central horn->spline screw from the top, countersunk
    cuts.append(cyl(0, 0, HORN_LOCK_D * 0.7, -0.1, DECK_T + 1))
    cuts.append(cone(0, 0, 4.6, 7.5, DECK_T - 1.9, DECK_T + 0.1))
    # radial self-tap slots matching the horn disc hole pattern (PCD ~10),
    # two families 45 deg apart so any horn orientation finds slots
    for ang in range(0, 360, 45):
        th = math.radians(ang)
        slot = box(0.0, 7.0, -1.4, 1.4, -0.1, DECK_T + 1)
        slot.rotate(V(0, 0, 0), ZDIR, ang)
        slot.translate(V(7.0 * math.cos(th), 7.0 * math.sin(th), 0))
        cuts.append(slot)
    # wire pass-through (rear side, clear of the 10 mm radius horn disc)
    cuts.append(cyl(0, 16.0, 5.0, -0.1, DECK_T + 1))
    # basket locating slots at the rear (basket tabs drop in at (±20, +55))
    for s in (1, -1):
        cuts.append(box(s * 20 - 4.1, s * 20 + 4.1, 55 - 4.1, 55 + 4.1,
                        -0.1, DECK_T + 1))
    # M3 mounting slots for upcoming mast/pulley parts (PCD 34 and 100)
    for pcd in (34.0, 100.0):
        for ang in (0, 90, 180, 270):
            th = math.radians(ang)
            cx, cy = pcd / 2 * math.cos(th), pcd / 2 * math.sin(th)
            if ang in (0, 180):
                cuts.append(box(cx - 3.5, cx + 3.5, cy - 1.7, cy + 1.7,
                                -0.1, DECK_T + 1))
            else:
                cuts.append(box(cx - 1.7, cx + 1.7, cy - 3.5, cy + 3.5,
                                -0.1, DECK_T + 1))
    # finger lift notches at the rim
    cuts.append(box(r - 10, r + 1, -2.5, 2.5, 0, DECK_T))
    cuts.append(box(-r - 1, -r + 10, -2.5, 2.5, 0, DECK_T))
    deck = cut_all(deck, cuts)
    deck = deck.removeSplitter()
    return deck


# --------------------------------------------------------------------------
# 3) catch basket (mounts on the rotating deck, rear side)
# --------------------------------------------------------------------------
def build_basket():
    w, d, h, t = BASKET_W / 2, BASKET_D, BASKET_H, BASKET_T
    # local origin = footprint centre on the deck; front lip faces -Y
    # (towards the deck centre / gripper). When mounted, basket centre sits
    # at deck-local (0, +41) so tabs land on the deck slots at (+/-20, +55).
    slab = box(-w, w, -d, d, 0, 2.0)
    front = box(-w, w, -d, -d + t, 0, h)
    back = box(-w, w, d - t, d, 0, h)
    left = box(-w, -w + t, -d, d, 0, h)
    right = box(w - t, w, -d, d, 0, h)
    b = fuse_all([slab, front, back, left, right])

    cuts = []
    # front slats (basketwork) facing the gripper
    n = 5
    pitch = (BASKET_W - 2 * t - 10) / n
    for i in range(n):
        x0 = -w + t + 5 + i * pitch
        cuts.append(box(x0, x0 + pitch - 4, -d - 0.5, -d + t + 0.5, 6, h - 6))
    # side windows, two rows
    for z0 in (14.0, 34.0):
        cuts.append(box(-w - 1, -w + t + 1, -d + 5, d - 5, z0, z0 + 18))
        cuts.append(box(w - t - 1, w + 1, -d + 5, d - 5, z0, z0 + 18))
    # back portholes
    for cx in (-30, 0, 30):
        cuts.append(cyl(cx, d - t / 2, 8, 10, h - 6))
    b = cut_all(b, cuts)
    # locating tabs (drop into the deck slots at local (-/+20, +14))
    for tx in (TAB_PCD_X / 2, -TAB_PCD_X / 2):
        b = b.fuse(box(tx - TAB_W / 2, tx + TAB_W / 2,
                       14 - TAB_L / 2, 14 + TAB_L / 2, -TAB_T, 0))
    # drain holes in the slab
    for cx in (-24, 0, 24):
        for cy in (-8, 8):
            b = b.cut(cyl(cx, cy, 5, -0.1, 2.1))
    b = b.removeSplitter()
    return b


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def main():
    os.makedirs(os.path.normpath(OUT), exist_ok=True)
    print("HooverBot rotator base: building 3 parts ...")
    export(build_platter(), "base_platter.stl")
    export(build_deck(), "turret_deck.stl")
    export(build_basket(), "catch_basket.stl")
    print("done.")


main()

