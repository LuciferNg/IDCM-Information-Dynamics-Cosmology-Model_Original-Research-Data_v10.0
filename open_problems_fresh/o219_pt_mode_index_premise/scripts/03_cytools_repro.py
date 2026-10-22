#!/usr/bin/env python3
"""
O219 scripts/03 -- cytools reproduction of the label structure (env-gated)
=========================================================================
scripts/01 rebuilds the label spaces from coordinates alone. This script
cross-checks that rebuild against cytools' OWN label API, which is the library
that produced the O137 data files.

Checks (SKIP, not FAIL, if cytools is unavailable):
  K1  cytools dual(points) == data/dual_polytope_points.json (set and order)
  K2  polytope Delta*: labels_facet == {73..84}, labels_not_facet == {0..72}
  K3  Delta: labels_not_facet == {0..36}, labels_facet == {37..47}
  K4  prime_toric_divisors() == 1..36 and divisor_basis() omits {0,3,4,7,8}
  K5  intersection_numbers() key set = 0..36 (0 = origin); inter[(0,0,0)] = -360
  K6  phi vector of a fresh triangulation == saved gkz_phi (phi is reproducible)
  K7  h11/h21 = 36/98 (polytope has the O137/O53 identity, so the index audit
      is being done on the right polytope)

Environment (WSL): cytools lives in ~/tools/lib with the C++ libs in ~/tools/lib:
  LD_LIBRARY_PATH=$HOME/tools/lib:/usr/local/lib /usr/bin/python3 scripts/03_cytools_repro.py
"""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
O219 = os.path.dirname(HERE)
REPO = os.path.dirname(O219)
O137 = os.path.join(REPO, "o137_cy3_topological_resonance")
O53 = os.path.join(REPO, "o53_cy3_reality")
F_DELTA = os.path.join(O53, "data", "polytopes", "cy36_98_sage_export.json")
F_DUAL = os.path.join(O137, "data", "dual_polytope_points.json")
F_GKZ = os.path.join(O137, "data", "gkz_period_data.json")

sys.path.insert(0, os.path.expanduser("~/tools/lib"))
try:
    import numpy as np
    from cytools import Polytope, config
    config.enable_experimental_features()
except Exception as e:                                    # pragma: no cover
    print("SKIP: cytools unavailable in this interpreter (%s)" % e)
    print("      rerun with: LD_LIBRARY_PATH=$HOME/tools/lib:/usr/local/lib python3 ...")
    sys.exit(0)

RES = []


def ck(name, ok, detail=""):
    RES.append({"check": name, "ok": bool(ok), "detail": str(detail)})
    print("  [%s] %s  -- %s" % ("PASS" if ok else "FAIL", name, detail))


d_pts = np.array(json.load(open(F_DELTA))["points"])
f_dual = [list(map(int, p)) for p in json.load(open(F_DUAL))["points"]]
phi_saved = list(json.load(open(F_GKZ))["gkz_phi"])

P = Polytope(d_pts)
D = P.dual()
c_dual = [list(map(int, p)) for p in D.points()]

ck("K1 cytools dual(points) == data/dual_polytope_points.json (order too)",
   c_dual == f_dual, "n=%d vs %d, identical=%s" % (len(c_dual), len(f_dual), c_dual == f_dual))
ck("K2 Delta* labels: facet-interior = 73..84, non-facet = 0..72",
   sorted(int(x) for x in D.labels_facet) == list(range(73, 85)) and
   sorted(int(x) for x in D.labels_not_facet) == list(range(73)),
   "facet=%s...%s | not_facet n=%d" % (sorted(int(x) for x in D.labels_facet)[:3],
                                        sorted(int(x) for x in D.labels_facet)[-1],
                                        len(D.labels_not_facet)))
ck("K3 Delta labels: non-facet = 0..36, facet-interior = 37..47",
   sorted(int(x) for x in P.labels_not_facet) == list(range(37)) and
   sorted(int(x) for x in P.labels_facet) == list(range(37, 48)),
   "not_facet n=%d facet=%s..%s" % (len(P.labels_not_facet),
                                     sorted(int(x) for x in P.labels_facet)[0],
                                     sorted(int(x) for x in P.labels_facet)[-1]))
tri_p = P.triangulate(backend="qhull", verbosity=0)
cy = tri_p.get_cy()
ptd = list(cy.prime_toric_divisors())
db = sorted(int(x) for x in cy.divisor_basis())
ck("K4 prime_toric_divisors = 1..36 ; divisor_basis omits {0,3,4,7,8}",
   ptd == list(range(1, 37)) and sorted(set(range(37)) - set(db)) == [0, 3, 4, 7, 8],
   "basis n=%d missing=%s" % (len(db), sorted(set(range(37)) - set(db))))
inter = cy.intersection_numbers()
keys = sorted(set(k for t in inter for k in t))
ck("K5 intersection_numbers key set = 0..36 (0 = origin), inter[(0,0,0)] = -360",
   keys == list(range(37)) and abs(inter[(0, 0, 0)] + 360) < 1e-9,
   "keys n=%d min=%d max=%d inter000=%s" % (len(keys), keys[0], keys[-1], inter[(0, 0, 0)]))
# phi is a property of the MIRROR polytope Delta* (this is what O137 built)
tri_s = D.triangulate(backend="topcom", verbosity=0)
phi_new = [int(x) for x in tri_s.gkz_phi()]
ck("K6 triangulating Delta* (topcom, as in O137) reproduces the saved gkz_phi",
   phi_new == phi_saved,
   "match=%s  fresh[:5]=%s saved[:5]=%s" % (phi_new == phi_saved, phi_new[:5], phi_saved[:5]))
try:
    q = [int(x) for x in D.triangulate(backend="qhull", verbosity=0).gkz_phi()]
    print("      INFO: qhull on Delta* gives a different chamber: %s (backend choice "
          "changes phi; the 73-label index space is invariant)" % (q[:5],))
except Exception as e:
    print("      INFO: qhull cross-check skipped (%s)" % e)
ck("K7 h11/h21 = 36/98 for the CY of this triangulation (right polytope!)",
   (cy.h11(), cy.h21()) == (36, 98), "h11=%s h21=%s" % (cy.h11(), cy.h21()))

# chamber sensitivity: the phi layers are a property of a CHAMBER, not of the
# polytope -- the O137 docs never state which backend/chamber produced them.
law = lambda p: (p[2] == 0 and p[3] % 4 == 1) or (p[2] == 1 and p[3] in (0, 1, 3, 4, 6, 7))
S_pts = [list(map(int, p)) for p in D.points()]
lawset = [i for i in range(73) if law(S_pts[i])]
rows = {}
for be in ("topcom", "qhull"):
    ph = [int(x) for x in D.triangulate(backend=be, verbosity=0).gkz_phi()]
    rows[be] = {"phi9": [i for i, v in enumerate(ph) if v == 9],
                "low_classes": {str(v): sum(1 for x in ph if x == v) for v in (6, 8, 9, 12)}}
ck("K8 (finding, expected FAIL) the phi=9 / 44=2+5+9+28 layer is triangulation-chamber "
   "invariant -- it is NOT: qhull has no phi=9 point at all",
   rows["topcom"]["phi9"] == rows["qhull"]["phi9"],
   "topcom phi9=%s classes=%s | qhull phi9=%s classes=%s | coordinate-law set=%s"
   % (rows["topcom"]["phi9"], rows["topcom"]["low_classes"],
      rows["qhull"]["phi9"], rows["qhull"]["low_classes"], lawset))

n = sum(1 for r in RES if r["ok"])
print("  RESULT: %d/%d PASS" % (n, len(RES)))
json.dump(RES, open(os.path.join(O219, "data", "03_cytools_checks.json"), "w"),
          indent=1, ensure_ascii=False)
print("  wrote data/03_cytools_checks.json")
