"""ASCII-inspect body_lower_idea.stl: bbox, top view, slices, ring scan."""
import math
import os
import struct
from collections import defaultdict

path = "/Users/festiz/gitstuff/HooverBot/stl/body_lower_idea.stl"
tris = []
with open(path, "rb") as fh:
    fh.read(80)
    (n,) = struct.unpack("<I", fh.read(4))
    for _ in range(n):
        d = struct.unpack("<12fH", fh.read(50))
        v = d[3:12]
        tris.append(((v[0], v[1], v[2]), (v[3], v[4], v[5]),
                     (v[6], v[7], v[8])))

xs = [c[0] for t in tris for c in t]
ys = [c[1] for t in tris for c in t]
zs = [c[2] for t in tris for c in t]
cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
print("triangles=%d  bbox x %.1f..%.1f  y %.1f..%.1f  z %.1f..%.1f"
      % (len(tris), min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)))

W, H = 78, 34


def project():
    lo0, hi0 = min(xs), max(xs)
    lo1, hi1 = min(ys), max(ys)
    grid = [[" "] * W for _ in range(H)]
    for t in tris:
        pts = []
        for c in t:
            u = int((c[0] - lo0) / (hi0 - lo0 + 1e-9) * (W - 1))
            w = int((c[1] - lo1) / (hi1 - lo1 + 1e-9) * (H - 1))
            pts.append((u, w))
        us = [p[0] for p in pts]
        ws = [p[1] for p in pts]
        steps = max(max(us) - min(us), max(ws) - min(ws), 1)
        for s in range(steps + 1):
            u = int(min(us) + (max(us) - min(us)) * s / steps)
            w = int(min(ws) + (max(ws) - min(ws)) * s / steps)
            grid[H - 1 - w][u] = "#"
    for row in grid:
        print("".join(row).rstrip())


def slice_at(zc):
    lo0, hi0 = min(xs), max(xs)
    lo1, hi1 = min(ys), max(ys)
    grid = [["."] * W for _ in range(H)]
    for (p0, p1, p2) in tris:
        pts = []
        for (a, b) in ((p0, p1), (p1, p2), (p2, p0)):
            dz = (a[2] - zc, b[2] - zc)
            if min(dz) <= 0 <= max(dz):
                t = dz[0] / (dz[0] - dz[1]) if dz[0] != dz[1] else 0.0
                pts.append((a[0] + (b[0] - a[0]) * t,
                            a[1] + (b[1] - a[1]) * t))
        for (px, py) in pts:
            u = int((px - lo0) / (hi0 - lo0 + 1e-9) * (W - 1))
            w = int((py - lo1) / (hi1 - lo1 + 1e-9) * (H - 1))
            grid[H - 1 - w][u] = "#"
    print("== slice z=%.1f ==" % zc)
    shown = 0
    for row in grid:
        s = "".join(row).rstrip(".")
        if s.strip():
            print(s)
            shown += 1
        if shown > 36:
            print("(crop)")
            break
    print()


def ring_occ(zc, r_lo, r_hi):
    segs = []
    for (p0, p1, p2) in tris:
        if not (min(p0[2], p1[2], p2[2]) <= zc <= max(p0[2], p1[2], p2[2])):
            continue
        pts = []
        for (a, b) in ((p0, p1), (p1, p2), (p2, p0)):
            dz = (a[2] - zc, b[2] - zc)
            if min(dz) <= 0 <= max(dz):
                t = dz[0] / (dz[0] - dz[1]) if dz[0] != dz[1] else 0.0
                pts.append((a[0] + (b[0] - a[0]) * t,
                            a[1] + (b[1] - a[1]) * t))
        segs.append(pts)
    out = []
    for deg in range(0, 360, 2):
        th = math.radians(deg)
        dx, dy = math.cos(th), math.sin(th)
        hit = False
        for pts in segs:
            if hit:
                break
            for i in range(len(pts) - 1):
                ax, ay = pts[i][0] - cx, pts[i][1] - cy
                bx, by = pts[i + 1][0] - cx, pts[i + 1][1] - cy
                if (min(ax, bx) - dx) * dx * 500 + abs(dx) > 1e9:
                    continue
                # conservatively test sampled points along the segment
                for k in range(6):
                    ux = ax + (bx - ax) * k / 5.0
                    uy = ay + (by - ay) * k / 5.0
                    r = math.hypot(ux, uy)
                    if not (r_lo <= r <= r_hi):
                        continue
                    ang = math.degrees(math.atan2(uy, ux)) % 360
                    if abs((ang - deg + 180) % 360 - 180) < 2.0:
                        hit = True
                        break
                if hit:
                    break
        out.append("#" if hit else ".")
    return "".join(out)


print("\nTOP VIEW (x right, y up):")
project()

zs_req = os.environ.get("SLICES", "12,2,-1")
for zc in (float(v) for v in zs_req.split(",")):
    slice_at(zc)

print("\nRING SCAN r=95..135 '#'=material (2 deg/char, 0deg=+X):")
for zc in (36.0, 30.0, 20.0, 12.0, 5.0):
    print("z=%5.1f |%s|" % (zc, ring_occ(zc, 95, 135)))
print("angles:   " + "".join("|" if d % 60 < 2 else " "
                              for d in range(0, 360, 2)))
print("marks:    0deg=+X(right), 90deg=+Y(front in my convention)")
