"""HooverBot step 2 (car phase) — Roomba-style body shell sketches.

Visual-review sketch: rough parametric parts for Step 3 user review.
Rebuild:
    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd cad/car_body.py

Exports (mm, Z-up, origin = floor centre, robot faces +Y):
    stl/body_lower.stl   hull band z 23..125: wheel wells, motor cradles (MI-1),
                         battery stack bays (MI-4 + power-bank tier), ballast
                         pockets, caster pods (MI-3), sensor pads, flange ring
    stl/body_upper.stl   hull band z 125..150 + top rim: bumper guide ribs,
                         hall pocket, rear storage tub partition
    stl/bumper_bar.stl   TPU crash bar face, +/-40 deg arc (MI-5)

Sketch-level simplifications (review in Step 3, revise in Step 5/7):
    - sensor pads are flat standoff pads with placeholder hole patterns
    - fastener holes are plain self-tap clearances, no threads
    - TODO(measure) dims flagged in the parameter block
"""

import math
import os

import FreeCAD as App
import Part
import MeshPart
import Mesh


# --------------------------------------------------------------------------
# parameters — envelope, structure (all mm, Z-up, front = +Y)
# --------------------------------------------------------------------------
BED = 250.0                 # print volume limit (asserted per part)
R_OUT = 125.0               # PR-1 hard silhouette
R_IN = 122.0                # wall inner radius
Z_FLOOR = 23.0              # PR-2 ground clearance
FLOOR_T = 3.0               # floor plate thickness (z 23..26)
Z_TOP = 150.0               # hull top (body ~=150 incl. clearance band)
Z_SPLIT = 125.0             # lower/upper section joint
CLEAR = 0.7                 # drop-in fit clearance
HOLE_D = 3.2                # self-tap clearance hole
FLG_Z0, FLG_Z1 = 121.0, Z_SPLIT          # section flange ring (bolts inside silhouette)
FLG_R0 = 119.0               # flange inner radius
FLG_BOLT_ANG = (30.0, 150.0, 210.0, 330.0)

# wheels + drive (MI-1/MI-2; TT motor typical dims per D11, verify w/ calipers)
WHEEL_R = 33.5
AXLE_Z = WHEEL_R            # wheels touch the floor
WHEEL_W = 26.0              # TODO(measure) tyre width
WHEEL_RC = 108.0            # wheel-centre radius; outer face ~121 (MI-2)
WELL_HALF_DEG = 19.0        # wall opening half-angle around the +-X axis
WELL_Z1 = 67.0              # wheel top 67 + margin
MOTOR_L = 66.0              # TT gearbox+can length, wheel hub inward
MOTOR_W = 22.5
MOTOR_H = 18.0
MI1_C2C = 17.0              # MI-1 screw pair, centre-to-centre
MI1_OFF = 19.0              # MI-1 screw-line offset from axle centreline
MI1_HOLE = 3.0

# batteries (PR-6/D16 rear-low stack)
BAY1_W = 43.0 + 2.0         # MI-4 holder 92 x 43 x 22 + clearance
BAY1_L = 92.0 + 2.0
BAY1_H = 22.0
MI4_SQ_X = 39.0             # MI-4 hole square pattern
MI4_SQ_Y = 30.0
MI4_FROM_END = 21.0         # from the non-cable short side
BANK_W = 68.0               # Anslut 10000 (EST — TODO measure ~148x68x17)
BANK_L = 148.0
BANK_H = 17.0
RAIL_T = 2.0
RAIL_H = 10.0               # 18650 tray rail height
TIER2_Z0 = Z_FLOOR + FLOOR_T + BAY1_H
TIER2_Z1 = TIER2_Z0 + BANK_H + RAIL_T + 2.0

# ballast pockets (D16): open-top boxes fused to the rear inner wall
POCKETS = [                 # (x0, x1, y0, y1, z1)
    (24.0, 66.0, -104.0, -76.0, 46.0),
    (-66.0, -24.0, -104.0, -76.0, 46.0),
    (70.0, 106.0, -70.0, -44.0, 64.0),
    (-106.0, -70.0, -70.0, -44.0, 64.0),
]

# caster pods (MI-3): plate 48 x 33, screws 39 c-c, dome ~D26-30, h ~20
CAST_PL_X = 48.0
CAST_PL_Y = 33.0
CAST_CC = 39.0
CAST_HOLE = 32.0            # floor hole the dome drops through
CASTER_Y = (-100.0, 100.0)  # rear + front pod
POD_DROP = 3.0              # pad hangs below the 23 mm line -> dome touches down

# rear storage tub (crane dumps from above; bin = y < 18)
PART_Y = 18.0
PART_X = 60.0               # side segments clear the slew pedestal (x <= 24)
PART_T = 2.5
PART_Z1 = 121.0

# sensors (D14) + bumper (MI-5)
SONAR_ANG = 20.0            # pad half-angle about front (+Y)
SONAR_R0, SONAR_R1 = R_OUT, R_OUT + 4.0
SONAR_Z0, SONAR_Z1 = 58.0, 64.0
IRS_ANG = 8.0
IRS_Z0, IRS_Z1 = 30.0, 36.0
CLIFF_ANG = (74.0, 80.0, 100.0, 106.0)
CLIFF_Z0, CLIFF_Z1 = 24.0, 33.0
HALL_POCKET = (-4.0, 4.0, 112.0, 118.0, 88.0, 94.0)
RAIL_ANG0, RAIL_ANG1 = 18.0, 36.0   # bumper guide rib angles about +Y
RAIL_Z0, RAIL_Z1 = 55.0, 115.0
BUMP_R0, BUMP_R1 = 126.5, 131.5     # TPU bar shell
BUMP_HALF = 40.0                    # MI-5 arc
BUMP_Z0, BUMP_Z1 = Z_FLOOR, Z_TOP
MAG_POCKET = (-4.0, 4.0, -6.0, 0.0, 88.0, 94.0)  # local coords inside the bar

# slew pedestal seat (part built in crane_concept.py; provisions here)
SLEW_FEET = (17.0, 10.0)    # foot half-sizes: x=+-17, y=35..55
SLEW_WIRE = (0.0, 54.0, 5.0)  # D10 wire bore x, y, r

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "stl")

# --------------------------------------------------------------------------
# helpers (same pattern as cad/rotator_base.py)
# --------------------------------------------------------------------------
V = App.Vector
ZDIR = V(0, 0, 1)


def box(x0, x1, y0, y1, z0, z1):
    """Axis-aligned box; each axis is normalised so x0<=x1 etc. hold."""
    return Part.makeBox(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0),
                        V(min(x0, x1), min(y0, y1), min(z0, z1)))


def cyl(x, y, r, z0, z1):
    return Part.makeCylinder(r, z1 - z0, V(x, y, z0), ZDIR)


def cone(x, y, r_bot, r_top, z0, z1):
    return Part.makeCone(r_bot, r_top, z1 - z0, V(x, y, z0), ZDIR)


def sector_ring(r0, r1, z0, z1, ang0, ang1):
    """Arc piece of a ring; angles in deg CCW from +X, trimmed 1 deg overlap."""
    outer = Part.makeCylinder(r1, z1 - z0, V(0, 0, z0), ZDIR,
                              math.radians(ang1 - ang0))
    outer.rotate(V(0, 0, 0), ZDIR, ang0)
    inner = Part.makeCylinder(r0, z1 - z0 + 4, V(0, 0, z0 - 2), ZDIR,
                              math.radians(ang1 - ang0 + 4))
    inner.rotate(V(0, 0, 0), ZDIR, ang0 - 2)
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
    print("%-18s solids=%d shells=%d valid=%s"
          % (name, len(shape.Solids), len(shape.Shells), shape.isValid()))
    mesh = None
    tried = []
    for maker in (
        lambda: MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.25,
                                       AngularDeflection=0.5, Relative=False),
        lambda: MeshPart.meshFromShape(Shape=shape, Fineness=2, SecondOrder=0,
                                       Optimize=1, AllowQuad=0),
        lambda: mesh_from_faces(shape),
    ):
        try:
            m = maker()
            tried.append("try")
        except Exception as exc:                     # noqa: BLE001
            tried.append("skip(%s)" % exc)
            continue
        if m.isSolid():
            mesh = m
            break
        for op in ("removeDuplicatedPoints", "removeDuplicatedFacets",
                   "removeDegeneratedFacets", "harmonize",
                   "removeNonManifolds", "removeFoldsOnSurface",
                   "fillupMeshHoles", "removeDuplicatedFacets"):
            fn = getattr(m, op, None)
            if fn is None:
                continue
            try:
                fn()
            except TypeError:
                try:
                    fn(1.0)
                except Exception:                        # noqa: BLE001
                    pass
            except Exception:                            # noqa: BLE001
                pass
        if m.isSolid():
            mesh = m
            tried.append("healed")
            break
        mesh = m
    healed = mesh is not None and "healed" in tried
    ok = (mesh is not None and bool(mesh.isSolid()) and shape.isValid()
          and max(mesh.BoundBox.XLength, mesh.BoundBox.YLength,
                  mesh.BoundBox.ZLength) <= BED)
    mesh.write(path)
    chk = Mesh.Mesh(path)
    bb = chk.BoundBox
    print("%-18s bbox=(%.1f x %.1f x %.1f) mm  volume=%.0f mm3  solid=%s  [%s]"
          % (name, bb.XLength, bb.YLength, bb.ZLength, shape.Volume,
             chk.isSolid(), ",".join(tried)))
    if healed and not chk.isSolid():
        print("WARNING: %s shipped with a *healed* sketch-quality mesh; "
              "regenerate in Step 5 after measured dims." % name)
    assert ok and (chk.isSolid() or healed), \
        name + " failed validation (solid/watertight/bed)!"
    return path


def mesh_from_faces(shape):
    """Last-resort mesher: tessellate each face, stitch a mesh manually."""
    verts, facets = shape.tessellate(0.25)
    m = Mesh.Mesh()
    for f in facets:
        m.addFacet(verts[f[0]], verts[f[1]], verts[f[2]])
    return m


# --------------------------------------------------------------------------
# 1) body lower — z 23..125
# --------------------------------------------------------------------------
def build_lower():
    zf = Z_FLOOR
    SEAM = 45.0               # cylinder seam moved to 45 deg: no cut crosses it
    parts = [
        cyl(0, 0, R_OUT, zf, zf + FLOOR_T).rotate(V(0, 0, 0), ZDIR, SEAM),
        cyl(0, 0, R_OUT, zf, Z_SPLIT).rotate(V(0, 0, 0), ZDIR, SEAM).cut(
            cyl(0, 0, R_IN, zf - 1, Z_SPLIT + 1)),
    ]
    # section flange ring on top (bolts inside the silhouette)
    parts.append(cyl(0, 0, R_OUT, FLG_Z0, FLG_Z1).rotate(
        V(0, 0, 0), ZDIR, SEAM).cut(
        cyl(0, 0, FLG_R0, FLG_Z0 - 1, FLG_Z1 + 1)))
    solid = fuse_all(parts)

    fuses = []
    # 18650 tray (tier 1): perimeter rails on the floor
    y0, y1 = -119.0, -25.0
    fuses.append(box(-BAY1_W / 2, BAY1_W / 2, y0, y0 + RAIL_T, zf + FLOOR_T,
                     zf + FLOOR_T + RAIL_H))
    fuses.append(box(-BAY1_W / 2, BAY1_W / 2, y1 - RAIL_T, y1, zf + FLOOR_T,
                     zf + FLOOR_T + RAIL_H))
    for s in (1, -1):
        fuses.append(box(s * (BAY1_W / 2 - RAIL_T), s * BAY1_W / 2,
                         y0, y1, zf + FLOOR_T, zf + FLOOR_T + RAIL_H))
        # power-bank tier-2: full-height side walls (stand on the floor)
        fuses.append(box(s * (BANK_W / 2 - RAIL_T), s * BANK_W / 2,
                         -119.0, 29.0, zf + FLOOR_T, TIER2_Z1))
    fuses.append(box(-BANK_W / 2, BANK_W / 2, -119.0, -117.0,
                     TIER2_Z0, TIER2_Z1))                      # tier2 back wall
    fuses.append(box(-BANK_W / 2, BANK_W / 2, -119.0, 29.0,
                     TIER2_Z0, TIER2_Z0 + 2.0))                # tier2 floor
    for b in fuses:
        solid = solid.fuse(b)
    print("stage bays valid=", solid.isValid(),
          "solids=%d" % len(solid.Solids))

    fuses = []
    # ballast pockets (open-top boxes fused at the rear inner wall)
    for (px0, px1, py0, py1, pz1) in POCKETS:
        fuses.append(box(px0, px1, py0, py1, zf + FLOOR_T, pz1))
        fuses.append(box(px0, px1, py0, py1, pz1, pz1 + 2.0))  # rim lip
    # rear storage tub partition (segments clear the slew pedestal)
    for s in (1, -1):
        fuses.append(box(s * 26.0, s * PART_X, PART_Y, PART_Y + PART_T,
                         zf + FLOOR_T, PART_Z1))
    # motor cradle rails (both sides; motor box x 29..95, y +-11.25)
    for s in (1, -1):
        for sy in (1, -1):
            fuses.append(box(s * 29.0, s * 95.0,
                             sy * 11.5, sy * 15.5, zf + FLOOR_T, 42.0))
        # MI-1 end plates + bosses (holes for screws into the motor face)
        fuses.append(box(s * 26.0, s * 29.0, -16.0, 16.0, 24.0, 53.0))
        fuses.append(box(s * 23.0, s * 30.0, -13.0, 13.0, 46.0, 59.5))
    # caster pods: pad below the floor + dome pass
    for cy in CASTER_Y:
        fuses.append(box(-CAST_PL_X / 2 - 2, CAST_PL_X / 2 + 2,
                         cy - CAST_PL_Y / 2 - 2, cy + CAST_PL_Y / 2 + 2,
                         Z_FLOOR - POD_DROP, zf))
        fuses.append(box(-CAST_PL_X / 2, CAST_PL_X / 2,
                         cy - CAST_PL_Y / 2, cy + CAST_PL_Y / 2,
                         zf, zf + 1.5))
    # sensor provisions: flush wall openings + internal mounting ledges
    # (no protrusion — the D250 silhouette is a hard limit; downtilt = Step 7)
    for b in fuses:
        solid = solid.fuse(b)
    print("stage pockets/cradles valid=", solid.isValid(),
          "solids=%d" % len(solid.Solids))

    # --- negative cuts ------------------------------------------------------
    cuts = []
    # wheel arch reveals through the wall at the axle band
    for a0 in (-19.0, 161.0):
        cuts.append(sector_ring(R_IN - 1.0, R_OUT + 2.0,
                                zf - 1.0, WELL_Z1, a0, a0 + 38.0))
    # motor floor notches (motor bottoms sit in them)
    for s in (1, -1):
        cuts.append(box(s * 28.0, s * 96.0, -12.6, 12.6, 22.0, 27.0))
        # wheel hub bore through the wall on the axle line
        cuts.append(Part.makeCylinder(8.0, 45.0, V(s * 88.0, 0.0, AXLE_Z),
                                      V(s * 1.0, 0.0, 0.0)))
        # MI-1 screw holes through the end plates (into the motor face)
        for h in (1, -1):
            cuts.append(Part.makeCylinder(MI1_HOLE / 2, 14.0,
                                          V(s * 36.0, h * MI1_C2C / 2.0,
                                            AXLE_Z + MI1_OFF),
                                          V(-s * 1.0, 0.0, 0.0)))
    # MI-4 tray holes + slew seat holes + slew wire bore
    for sx in (1, -1):
        for (hy, d) in ((-112.0, 3.2), (-82.0, 3.2)):
            cuts.append(cyl(sx * MI4_SQ_X / 2, hy, d / 2, 20.0, 28.0))
    cuts.append(cyl(0, CASTER_Y[0], CAST_HOLE / 2, 19.0, 27.0))
    cuts.append(cyl(0, CASTER_Y[1], CAST_HOLE / 2, 19.0, 27.0))
    for cy in CASTER_Y:
        for sx in (1, -1):
            cuts.append(cyl(sx * CAST_CC / 2, cy, HOLE_D / 2, 17.0, 24.0))
    for (fx, fy) in ((17.0, 35.0), (17.0, 55.0),
                     (-17.0, 35.0), (-17.0, 55.0)):
        cuts.append(cyl(fx, fy, HOLE_D / 2, 18.0, 29.0))
    cuts.append(cyl(SLEW_WIRE[0], SLEW_WIRE[1], SLEW_WIRE[2], 20.0, 29.0))
    cuts.append(cone(SLEW_WIRE[0], SLEW_WIRE[1], 7.5, 4.5, 20.0, 26.0))
    # section flange bolt holes
    for a in FLG_BOLT_ANG:
        th = math.radians(a)
        cuts.append(cyl(121.5 * math.cos(th), 121.5 * math.sin(th),
                        HOLE_D / 2, FLG_Z0 - 2.0, FLG_Z1 + 1.0))
    # hall-sensor window through the front wall (bar magnet on the other side)
    cuts.append(box(HALL_POCKET[0], HALL_POCKET[1], 110.0, R_OUT + 1.0,
                    HALL_POCKET[4], HALL_POCKET[5]))
    # flush sensor openings + ledges (board A front / board B rear / IR nose)
    for a0 in (70.0, 250.0):
        cuts.append(sector_ring(R_IN - 1.0, R_OUT + 1.0,
                                55.0, 67.0, a0, a0 + 40.0))
        solid = solid.fuse(sector_ring(110.0, R_IN + 1.5, 52.5, 55.0,
                                       a0, a0 + 40.0))
    cuts.append(sector_ring(R_IN - 1.0, R_OUT + 1.0,
                            IRS_Z0 - 1.0, IRS_Z1 + 1.0, 84.0, 96.0))
    solid = solid.fuse(sector_ring(112.0, R_IN + 1.5, 27.0, IRS_Z0 - 1.0,
                                   84.0, 96.0))
    solid = cut_all(solid, cuts)
    clean = solid.removeSplitter()
    if not clean.isValid():
        try:
            clean = solid.removeSplitter()      # fresh splitter product
        except Exception:                        # noqa: BLE001
            clean = solid
    if not clean.isValid():
        try:
            clean.fix(1e-7, 1e-7, 1e-7)
        except Exception:                        # noqa: BLE001
            pass
    if not clean.isValid() and solid.isValid():
        clean = solid
    return clean


# --------------------------------------------------------------------------
# 2) body upper — z 125..150 + rim cap
# --------------------------------------------------------------------------
def build_upper():
    wall = cyl(0, 0, R_OUT, Z_SPLIT, Z_TOP).cut(
        cyl(0, 0, R_IN, Z_SPLIT - 1, Z_TOP + 1))
    flange = cyl(0, 0, R_OUT, Z_SPLIT, Z_SPLIT + 4.0).cut(
        cyl(0, 0, FLG_R0, Z_SPLIT - 1, Z_SPLIT + 5.0))
    rim = cyl(0, 0, R_OUT, Z_TOP, Z_TOP + 2.0).cut(
        cyl(0, 0, FLG_R0, Z_TOP - 1, Z_TOP + 3.0))
    solid = fuse_all([wall, flange, rim])

    fuses = [sector_ring(R_OUT, R_OUT + 3.5, RAIL_Z0, RAIL_Z1,
                         90.0 - RAIL_ANG1, 90.0 - RAIL_ANG0),
             sector_ring(R_OUT, R_OUT + 3.5, RAIL_Z0, RAIL_Z1,
                         90.0 + RAIL_ANG0, 90.0 + RAIL_ANG1)]
    solid = solid.fuse(fuse_all(fuses))

    cuts = []
    for a in FLG_BOLT_ANG:                     # matching flange holes
        th = math.radians(a)
        cuts.append(cyl(121.5 * math.cos(th), 121.5 * math.sin(th),
                        HOLE_D / 2, Z_SPLIT - 1.0, Z_SPLIT + 2.0))
    solid = cut_all(solid, cuts)
    clean = solid.removeSplitter()
    if not clean.isValid():
        try:
            clean.fix(1e-7, 1e-7, 1e-7)
        except Exception:                        # noqa: BLE001
            pass
    if not clean.isValid():
        clean = solid
    return clean


# --------------------------------------------------------------------------
# 3) bumper bar — TPU crash face, +-40 deg arc (MI-5)
# --------------------------------------------------------------------------
def build_bumper():
    bar = sector_ring(BUMP_R0, BUMP_R1, BUMP_Z0, BUMP_Z1,
                      90.0 - BUMP_HALF, 90.0 + BUMP_HALF)
    # magnet pocket on the inner face (pairs with the hall window)
    bar = bar.cut(box(MAG_POCKET[0], MAG_POCKET[1],
                      BUMP_R0 - 1.0, BUMP_R1 + 0.5,
                      MAG_POCKET[4], MAG_POCKET[5]))
    # travel-stop ribs at both arc ends (ride the printed guide rails)
    bar = bar.fuse(sector_ring(BUMP_R0 - 1.5, BUMP_R1, BUMP_Z0, BUMP_Z1,
                               90.0 - BUMP_HALF, 90.0 - BUMP_HALF + 6.0))
    bar = bar.fuse(sector_ring(BUMP_R0 - 1.5, BUMP_R1, BUMP_Z0, BUMP_Z1,
                               90.0 + BUMP_HALF - 6.0, 90.0 + BUMP_HALF))
    clean = bar.removeSplitter()
    if not clean.isValid():
        try:
            clean.fix(1e-7, 1e-7, 1e-7)
        except Exception:                        # noqa: BLE001
            pass
    if not clean.isValid():
        clean = bar
    return clean


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def main():
    os.makedirs(os.path.normpath(OUT), exist_ok=True)
    print("HooverBot car body: building 3 sketch parts ...")
    export(build_lower(), "body_lower.stl")
    export(build_upper(), "body_upper.stl")
    export(build_bumper(), "bumper_bar.stl")
    print("done.")


main()

