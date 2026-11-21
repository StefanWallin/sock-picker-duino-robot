"""HooverBot step 2 (car phase) — body shell v2, built on the user's
stl/body_lower_idea.stl intent (see Feature map in README.md).

Rebuild:
    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd cad/car_body.py

Exports (mm, Z-up, origin = floor centre, front = +Y):
    stl/body_shell.stl   one-piece hull: floor, walls (top 120), internal
                         wheel-well space (wheels parallel at x = +/-95),
                         motor brackets, battery stack (MI-4 tray + bank
                         tier), ballast pockets, hatch opening + snap lip,
                         bumper slide channels, sensor windows, casters,
                         slew pedestal seat, perch shelf for electronics
    stl/hatch_door.stl   tool-free battery hatch door (snap tabs)
    stl/bumper_bar.stl   TPU 80-arc bumper, flush with the D250 line, slides
                         inward; sensor apertures + hall magnet pocket

TODO(measure): WHEEL_W (tyre width), BANK dims (est 148 x 68 x 17),
AA_HOLDER footprint if the 4xAA pack should also live in a tray.
"""

import math
import os

import FreeCAD as App
import Part
import MeshPart
import Mesh

FONT = "/System/Library/Fonts/supplemental/Arial.ttf"

# --------------------------------------------------------------------------
# parameters
# --------------------------------------------------------------------------
BED = 250.0
R_OUT = 125.0               # PR-1 silhouette (hard)
R_IN = 122.0                # wall 3 mm
Z_FLOOR = 23.0              # PR-2 clearance; floor slab z 23..26
FLOOR_T = 3.0
Z_TOP = 120.0               # PR-1 rev: hull top 120 (was 150)
Z_SPLIT = 125.0             # unused (single shell) kept for crane refs
CLEAR = 0.7
HOLE_D = 3.2

# wheels: PARALLEL pair, fully recessed inside the well space (user idea)
WHEEL_R = 33.5
AXLE_Z = WHEEL_R
WHEEL_W = 26.0              # TODO(measure)
WHEEL_RC = 95.0             # wheel centre radius (outer face ~108: in-well)
WELL_X0 = 73.0              # interior kept clear x >= 73 on both sides
MOTOR_L = 66.0              # TT gearbox+can, hub inward
MOTOR_W = 22.5
MOTOR_H = 18.0
MI1_C2C = 17.0
MI1_OFF = 19.0
MI1_HOLE = 3.0

# battery stack: 18650 tray (MI-4) between the wells + bank tier above
TRAY_X0, TRAY_X1 = 13.5, 58.5      # 45 wide segment between wells
TRAY_Y0, TRAY_Y1 = -47.0, 45.0     # 92 long (MI-4)
TRAY_H = 22.0                      # holder height
MI4_SQ_X, MI4_SQ_Y = 39.0, 30.0
MI4_FROM_END = 21.0                # from the non-cable short side (y=-47)
BANK_W, BANK_L, BANK_H = 68.0, 148.0, 17.0
BANK_Y1 = 34.0                     # bank sits across X: x -59..59
RAIL_T = 2.0
TK2_Z0 = Z_FLOOR + FLOOR_T + TRAY_H       # 48 bank tier floor
TK2_Z1 = TK2_Z0 + BANK_H + RAIL_T + 2.0   # 69 bank tier top

# tool-free hatch (user review): opening under the 18650 tray
HATCH_X0, HATCH_X1 = 12.5, 59.5
HATCH_Y0, HATCH_Y1 = -46.0, 46.0

# ballast pockets (D16) along the rear inner wall
POCKETS = [(24.0, 66.0, -104.0, -76.0, 46.0),
           (-66.0, -24.0, -104.0, -76.0, 46.0)]

# casters (MI-3)
CAST_PL_X, CAST_PL_Y, CAST_CC = 48.0, 33.0, 39.0
CASTER_Y = (-100.0, 100.0)
POD_DROP = 3.0

# perch shelf for electronics (front quadrant, above bumper channel zone)
PERCH_Y0, PERCH_Y1 = 55.0, 112.0
PERCH_Z0, PERCH_Z1 = 70.0, 73.0

# slew pedestal seat (crane_concept.py)
SLEW_HOLES = ((17.0, 35.0), (17.0, 55.0), (-17.0, 35.0), (-17.0, 55.0))
SLEW_WIRE = (0.0, 54.0, 6.0)

# bumper (MI-5 rev): flush D250 arc, slides inward, internal C-channels
BUMP_ZN, BUMP_ZF = 27.0, 118.0     # bar face z band
BUMP_R0, BUMP_R1 = 122.5, 125.2
BUMP_HALF = 40.0
FLG1_Z0, FLG1_Z1 = 33.0, 35.5      # inward flanges (slide rails)
FLG2_Z0, FLG2_Z1 = 100.0, 102.5
CH_LEDGE_C = 32.5                  # channel ledge centre z
CH_LIP = (99.0, 104.0)             # top lip z that traps the upper flange
SONAR_ANG = 20.0                   # board aim, windows through the TPU bar
HALL_W = 90.0                      # hall window centre z on the bar

# sensor windows (cut through shell behind the bar apertures)
WIN_SONAR = ((52.0, 72.0), (8.0, 32.0), (148.0, 172.0))   # (z0,z1), aims L/R
WIN_IR = (28.0, 38.0, 3.0)                                # z0,z1, half-ang
WIN_CLIFF = ((24.0, 36.0), 26.0, 154.0)  # z band, half-ang, centres 64/154?? 

# rear storage partition (dump tub = y < 18)
PART_Y, PART_X, PART_T, PART_Z1 = 18.0, 60.0, 2.5, 110.0

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "stl")
LABELS = []                        # (text, x, y, z, axis, mirror)

# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
V = App.Vector
ZDIR = V(0, 0, 1)
XDIR = V(1, 0, 0)


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0),
                        V(min(x0, x1), min(y0, y1), min(z0, z1)))


def cyl(x, y, r, z0, z1):
    return Part.makeCylinder(r, z1 - z0, V(x, y, z0), ZDIR)


def cylx(y, z, r, x0, x1):
    d = XDIR if x1 > x0 else V(-1, 0, 0)
    return Part.makeCylinder(r, abs(x1 - x0), V(min(x0, x1), y, z), d)


def cone(x, y, r0, r1, z0, z1):
    return Part.makeCone(r0, r1, z1 - z0, V(x, y, z0), ZDIR)


def sector_ring(r0, r1, z0, z1, a0, a1):
    """Arc of a ring, CCW from +X, tangency-safe trims."""
    outer = Part.makeCylinder(r1, z1 - z0, V(0, 0, z0), ZDIR,
                              math.radians(a1 - a0))
    outer.rotate(V(0, 0, 0), ZDIR, a0)
    inner = Part.makeCylinder(r0, z1 - z0 + 4, V(0, 0, z0 - 2), ZDIR,
                              math.radians(a1 - a0 + 4))
    inner.rotate(V(0, 0, 0), ZDIR, a0 - 2)
    return outer.cut(inner)


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
    ok = (bool(chk.isSolid()) and shape.isValid()
          and max(bb.XLength, bb.YLength, bb.ZLength) <= BED)
    print("%-18s bbox=(%.1f x %.1f x %.1f) mm  volume=%.0f mm3  solid=%s"
          % (name, bb.XLength, bb.YLength, bb.ZLength, shape.Volume, ok))
    assert ok, name + " failed validation (solid/watertight/bed)!"
    return path


def apply_labels(shape, depth=0.8, size=4.5):
    """Fuse raised text. Entries: (text, x, y, z, axis, mirror).
    axis 'z' = flat on the floor, 'y' = on a wall facing +Y,
    'x' = facing +X."""
    for (text, x, y, z, axis, mirror) in LABELS:
        wires = Part.makeWireString(text, FONT, size)
        solids = []
        for grp in wires:
            for w in grp:
                try:
                    f = Part.Face([w])
                    solids.append(f.extrude(V(0, 0, depth)))
                except Exception:
                    pass
        if not solids:
            continue
        txt = fuse_all(solids)
        if axis == "y":
            txt = txt.rotate(V(0, 0, 0), XDIR, 90)
        elif axis == "x":
            txt = txt.rotate(V(0, 0, 0), YDIR, 90)
        txt = txt.translate(V(x, y, z))
        shape = shape.fuse(txt)
    return shape


# --------------------------------------------------------------------------
# 1) body shell (one piece) — every feature listed in the README feature map
# --------------------------------------------------------------------------
def build_shell():
    zf, it = Z_FLOOR, FLOOR_T
    parts = [
        cyl(0, 0, 87.0, zf, zf + it),                       # central floor
        cyl(0, 0, R_OUT, zf, Z_TOP).cut(cyl(0, 0, R_IN, zf - 1, Z_TOP + 1)),
        cyl(0, 0, R_OUT, Z_TOP, Z_TOP + 2).cut(             # rim cap
            cyl(0, 0, 116.0, Z_TOP - 1, Z_TOP + 3)),
    ]
    solid = fuse_all(parts)

    # ---- battery stack: MI-4 tray rails + bank tier ----
    for fy in (TRAY_Y0, TRAY_Y1 - RAIL_T):
        solid = solid.fuse(box(TRAY_X0, TRAY_X1, fy, fy + RAIL_T,
                               zf + it, zf + it + 10))
    for s in (1, -1):
        solid = solid.fuse(box(s * (TRAY_X1 - RAIL_T), s * TRAY_X1,
                               TRAY_Y0, TRAY_Y1, zf + it, zf + it + 10))
    solid = solid.fuse(box(-59.0, 59.0, -34.0, -32.0, TK2_Z0, TK2_Z0 + 2))
    solid = solid.fuse(box(-59.0, 59.0, 32.0, 34.0, TK2_Z0, TK2_Z0 + 2))
    solid = solid.fuse(box(-59.0, -57.0, -34.0, 34.0, TK2_Z0, TK2_Z1))
    solid = solid.fuse(box(57.0, 59.0, -34.0, 34.0, TK2_Z0, TK2_Z1))

    # ---- hatch alignment lip on the +Y edge ----
    solid = solid.fuse(box(HATCH_X0, HATCH_X1, HATCH_Y1,
                           HATCH_Y1 + 4.0, zf - 2, zf))

    # ---- ballast pockets ----
    for (px0, px1, py0, py1, pz1) in POCKETS:
        solid = solid.fuse(box(px0, px1, py0, py1, zf + it, pz1))
        solid = solid.fuse(box(px0, px1, py0, py1, pz1, pz1 + 2))

    # ---- rear storage tub partition ----
    for s in (1, -1):
        solid = solid.fuse(box(s * 26.0, s * PART_X, PART_Y, PART_Y + PART_T,
                               zf + it, PART_Z1))

    for s in (1, -1):
        wa0, wa1 = (86.0, 94.0) if s > 0 else (266.0, 274.0)
        solid = solid.fuse(sector_ring(112.0, R_IN + 1.5, 26.0, 62.0,
                                       wa0, wa1))
        solid = solid.fuse(box(s * 30.0, s * 95.0, -14.0, -10.5,
                               zf + it, 43.0))
        solid = solid.fuse(box(s * 30.0, s * 95.0, 10.5, 14.0,
                               zf + it, 43.0))
        solid = solid.fuse(box(s * 24.0, s * 27.5, -17.0, 17.0,
                               24.0, 53.0))
        solid = solid.fuse(box(s * 21.0, s * 30.0, -13.0, 13.0,
                               46.0, 59.5))

    # ---- perch shelf for electronics (front quadrant) ----
    solid = solid.fuse(box(-55.0, 55.0, PERCH_Y0, PERCH_Y1,
                           PERCH_Z0, PERCH_Z1))
    for s in (1, -1):
        solid = solid.fuse(box(s * 44.0, s * 55.0, PERCH_Y0, PERCH_Y0 + 6,
                               zf + it, PERCH_Z1))
        solid = solid.fuse(box(s * 30.0, s * 42.0, PERCH_Y1 - 8, PERCH_Y1,
                               zf + it, PERCH_Z1))

    # ---- bumper slide channels (internal C, MI-5 rev) ----
    for zz in ((30.0, 33.0), (105.0, 108.0)):
        solid = solid.fuse(sector_ring(109.0, 122.5, zz[0], zz[1],
                                       90.0 - BUMP_HALF, 90.0 + BUMP_HALF))

    # ---- caster pods ----
    for cy in CASTER_Y:
        solid = solid.fuse(box(-CAST_PL_X / 2 - 2, CAST_PL_X / 2 + 2,
                               cy - CAST_PL_Y / 2 - 2, cy + CAST_PL_Y / 2 + 2,
                               Z_FLOOR - POD_DROP, zf))
        solid = solid.fuse(box(-16.0, 16.0, cy - CAST_PL_Y / 2,
                               cy + CAST_PL_Y / 2,
                               Z_FLOOR - POD_DROP - 1.5, Z_FLOOR - POD_DROP))

    # ---- negative cuts ---------------------------------------------------
    cuts = []
    cuts.append(box(HATCH_X0, HATCH_X1, HATCH_Y0, HATCH_Y1, 15.0, zf + it))
    for s in (1, -1):
        cuts.append(Part.makeCylinder(8.0, 44.0,
                                      V(s * 84.0, 0.0, AXLE_Z),
                                      V(s * 1.0, 0.0, 0.0)))
        cuts.append(Part.makeCylinder(MI1_HOLE / 2, 12.0,
                                      V(s * 34.0, MI1_C2C / 2.0,
                                        AXLE_Z + MI1_OFF),
                                      V(-s * 1.0, 0.0, 0.0)))
        cuts.append(Part.makeCylinder(MI1_HOLE / 2, 12.0,
                                      V(s * 34.0, -MI1_C2C / 2.0,
                                        AXLE_Z + MI1_OFF),
                                      V(-s * 1.0, 0.0, 0.0)))
    for cy in CASTER_Y:
        cuts.append(cyl(0, cy, 16.0, 19.0, 27.0))
        for sx in (1, -1):
            cuts.append(cyl(sx * CAST_CC / 2, cy, HOLE_D / 2, 17.0, 24.0))
    for (fx, fy) in SLEW_HOLES:
        cuts.append(cyl(fx, fy, HOLE_D / 2, 18.0, 29.0))
    cuts.append(cyl(SLEW_WIRE[0], SLEW_WIRE[1], SLEW_WIRE[2], 18.0, 29.0))
    cuts.append(cone(SLEW_WIRE[0], SLEW_WIRE[1], 8.5, 5.0, 18.0, 25.0))
    for a in (45.0, 135.0, 225.0, 315.0):
        th = math.radians(a)
        cuts.append(cyl(119.0 * math.cos(th), 119.0 * math.sin(th),
                        HOLE_D / 2, Z_TOP - 1, Z_TOP + 2))
    # sensor windows: front (behind the bar apertures) + rear sonar window
    for (z0, z1), (a_lo, a_hi) in ((WIN_SONAR[0], WIN_SONAR[1]),
                                   (WIN_SONAR[0], WIN_SONAR[2])):
        cuts.append(sector_ring(R_IN - 1.0, R_OUT + 1.0, z0, z1, a_lo, a_hi))
        solid = solid.fuse(sector_ring(108.0, R_IN - 0.5, z0 - 3.0, z0,
                                       a_lo, a_hi))
    cuts.append(sector_ring(R_IN - 1.0, R_OUT + 1.0,
                            WIN_IR[0], WIN_IR[1],
                            90.0 - WIN_IR[2], 90.0 + WIN_IR[2]))
    cuts.append(sector_ring(R_IN - 1.0, R_OUT + 1.0,
                            24.0, 36.0, 90.0 + 24.0, 90.0 + 30.0))
    cuts.append(sector_ring(R_IN - 1.0, R_OUT + 1.0,
                            24.0, 36.0, 90.0 - 30.0, 90.0 - 24.0))
    cuts.append(sector_ring(R_IN - 1.0, R_OUT + 1.0, 52.0, 72.0, 250.0, 290.0))
    solid = solid.fuse(sector_ring(108.0, R_IN - 0.5, 49.0, 52.0, 250.0, 290.0))
    solid = cut_all(solid, cuts)

    global LABELS
    LABELS = [
        ("18650 BAY", 36.0, -30.0, zf + it, "z", False),
        ("BANK HERE", -40.0, 0.0, TK2_Z0 + 2, "z", False),
        ("HATCH DOOR BELOW", 36.0, 10.0, zf - 0.1, "z", False),
        ("BALLAST", 45.0, -95.0, zf + it, "z", False),
        ("SOCK BIN", -8.0, -60.0, zf + it, "z", False),
        ("MOTOR MOUNT", 40.0, -17.0, zf + it, "z", False),
        ("PERCH ELECTRONICS", 0.0, 62.0, PERCH_Z1, "z", False),
        ("SLEW PEDESTAL HERE", 0.0, 45.0, zf + it, "z", False),
        ("SONAR L", 0.0, 110.0, 40.0, "y", False),
        ("SONAR R", 0.0, 110.0, 40.0, "y", True),
        ("IR NOSE", -8.0, 112.0, 20.0, "y", False),
        ("BATTERY 18650 X2", 0.0, -55.0, 40.0, "y", False),
    ]
    solid = apply_labels(solid)
    clean = solid.removeSplitter()
    if not clean.isValid():
        try:
            clean.fix(1e-7, 1e-7, 1e-7)
        except Exception:
            pass
    if not clean.isValid():
        clean = solid
    return clean


# --------------------------------------------------------------------------
# 2) hatch door — tool-free battery access (snap tabs, no screws)
# --------------------------------------------------------------------------
def build_hatch():
    t = 3.0
    dx0, dx1 = HATCH_X0 - 0.7, HATCH_X1 + 0.7
    dy0, dy1 = HATCH_Y0 - 0.7, HATCH_Y1 + 0.7
    door = box(dx0, dx1, dy0, dy1, 0.0, t)
    # snap tabs on the -Y edge (clip under the far lip), two per side
    for sx in (1, -1):
        door = door.fuse(box(sx * 12.0 - 4.0, sx * 12.0 + 4.0,
                             dy0 - 2.0, dy0 + 3.0, -3.0, t))
        door = door.fuse(box(sx * 40.0 - 4.0, sx * 40.0 + 4.0,
                             dy0 - 2.0, dy0 + 3.0, -3.0, t))
    # finger slot at the +Y edge
    door = door.cut(box(-12.0, 12.0, dy1 - 6.0, dy1 + 1.0, t - 1.6, t + 1.0))
    # label
    door = apply_labels_static(door, [("BATTERY DOOR", 0.0, 0.0, t, "z")],
                               36.0, 0.0)
    clean = door.removeSplitter()
    if not clean.isValid():
        clean = door
    return clean


def apply_labels_static(shape, entries, cx=0.0, cy=0.0, depth=0.8, size=6.0):
    for (text, ox, oy, oz, axis) in entries:
        wires = Part.makeWireString(text, FONT, size)
        solids = []
        for grp in wires:
            for w in grp:
                try:
                    f = Part.Face([w])
                    solids.append(f.extrude(V(0, 0, depth)))
                except Exception:
                    pass
        if not solids:
            continue
        txt = fuse_all(solids).translate(V(cx + ox, cy + oy, oz))
        shape = shape.fuse(txt)
    return shape


# --------------------------------------------------------------------------
# 3) bumper bar — TPU, 80-arc flush with the D250 line, slides inward
# --------------------------------------------------------------------------
def build_bumper():
    bar = sector_ring(BUMP_R0, BUMP_R1, BUMP_ZN, BUMP_ZF,
                      90.0 - BUMP_HALF, 90.0 + BUMP_HALF)
    # inward slide flanges (ride the printed channels)
    bar = bar.fuse(sector_ring(112.0, BUMP_R0, FLG1_Z0, FLG1_Z1,
                               90.0 - BUMP_HALF, 90.0 + BUMP_HALF))
    bar = bar.fuse(sector_ring(112.0, BUMP_R0, FLG2_Z0, FLG2_Z1,
                               90.0 - BUMP_HALF, 90.0 + BUMP_HALF))
    # sensor apertures (labeled): sonar L/R, IR nose, cliffs L/R
    bar = bar.cut(sector_ring(111.0, 126.0, 50.0, 72.0, 98.0, 122.0))
    bar = bar.cut(sector_ring(111.0, 126.0, 50.0, 72.0, 58.0, 82.0))
    bar = bar.cut(sector_ring(111.0, 126.0, 26.0, 40.0, 87.0, 93.0))
    bar = bar.cut(sector_ring(111.0, 126.0, 24.0, 38.0, 114.0, 120.0))
    bar = bar.cut(sector_ring(111.0, 126.0, 24.0, 38.0, 60.0, 66.0))
    # hall magnet pocket on the inner face
    bar = bar.cut(sector_ring(122.4, 126.0, 87.0, 95.0, 86.0, 94.0))
    clean = bar.removeSplitter()
    if not clean.isValid():
        clean = bar
    return clean


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def main():
    os.makedirs(os.path.normpath(OUT), exist_ok=True)
    print("HooverBot car body v2: building 3 sketch parts ...")
    export(build_shell(), "body_shell.stl")
    export(build_hatch(), "hatch_door.stl")
    export(build_bumper(), "bumper_bar.stl")
    print("done.")


main()
