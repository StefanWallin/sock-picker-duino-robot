"""One-shot mesh diagnostics for stl/body_lower.stl (temp tool)."""
import Mesh

m = Mesh.Mesh("/Users/festiz/gitstuff/HooverBot/stl/body_lower.stl")
print("facets=%d points=%d solid=%s closed=%s nonmanifold=%s"
      % (m.CountFacets, m.CountPoints, m.isSolid(), m.isClosed(),
         m.hasNonManifolds()))

from collections import defaultdict
edge_use = defaultdict(int)
bnd_mid = []
for f in m.Facets:
    i = f.PointIndices
    for a, b in ((i[0], i[1]), (i[1], i[2]), (i[2], i[0])):
        key = (a, b) if a < b else (b, a)
        edge_use[key] += 1
boundary = [k for k, v in edge_use.items() if v == 1]
print("boundary edges:", len(boundary))
pts = m.Points
for k in boundary[:12]:
    p = pts[k[0]] + pts[k[1]]
    print("  bnd edge near (%.0f, %.0f, %.0f)" %
          (p.x / 2, p.y / 2, p.z / 2))
# cluster summary: midpoint rounded to 25 mm buckets
from collections import Counter
buckets = Counter()
for k in boundary:
    p = pts[k[0]] + pts[k[1]]
    buckets[(round(p.x / 50) * 25, round(p.y / 50) * 25,
             round(p.z / 50) * 25)] += 1
for k, v in sorted(buckets.items(), key=lambda kv: -kv[1])[:12]:
    print("  cluster near %-22s edges=%d" % (str(k), v))
