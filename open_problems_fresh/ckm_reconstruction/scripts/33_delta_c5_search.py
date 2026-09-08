"""
IDCM v10.0 — delta_CKM C5-origin search (P3/P4)
================================================
Target: delta = 66.40 deg (framework value; PDG 65.9 +/- 3.3 = CKM gamma).
Zero-parameter structural candidates, chain-sector only (Q(zeta176)+-expressible):
  S1: atan(beat(a,b)/beat(c,d)) ~ 66.40 deg, a,b,c,d <= 44
  S2: atan(beat(a,b)/beat(c,d)) ~ 5.60 deg  (= 72 - 66.40 correction)
  S4: 72 - atan(beat ratio) ~ 66.40 deg  (Z5 phase minus chain angle)
  S5: rational angles 360*k/N (N in 44,88,176,352) near 5.60 / 66.40
Verdict rule: structural iff small indices AND chain-sector quantity (no phi-power).
"""
import numpy as np
import math

TARGET = 66.40
CORR = 72.0 - TARGET      # 5.60
TOL = 0.05


def beat(a, b):
    return 4 * math.sin(abs(a - b) * math.pi / 176) * math.cos((a + b) * math.pi / 176)


pairs = [(a, b) for a in range(1, 45) for b in range(1, 45) if a != b]
vals = np.array([beat(a, b) for a, b in pairs])
Np = len(vals)
print(f"pair count = {Np}")


def scan(target, label, toptext):
    hits = []
    for i in range(Np):
        vi = vals[i]
        if abs(vi) < 1e-14:
            continue
        r = vals / vi
        ang = np.degrees(np.arctan(r))
        m = np.abs(ang - target) < TOL
        for j in np.where(m)[0]:
            a1, b1 = pairs[i]
            a2, b2 = pairs[j]
            score = max(a1, b1, a2, b2)
            hits.append((abs(ang[j] - target), score, (a1, b1), (a2, b2), ang[j]))
    hits.sort()
    print(f"\n{toptext} (tol {TOL} deg), top 8:")
    for h in hits[:8]:
        print(f"    {h[4]:.4f} deg (d={h[0]:.4f}) beat{h[2]}/beat{h[3]}  "
              f"sim={h[1]}")
    return hits


h1 = scan(TARGET, "S1", "S1 atan(beat/beat) ~ 66.40 deg")
h2 = scan(CORR, "S2", "S2 atan(beat/beat) ~ 5.60 deg")
h4 = scan(TARGET, "S4", "S4 72 - atan(beat/beat) ~ 66.40 deg  (i.e. atan ~ 5.60)")

# S5 rational angles
print("\nS5 rational angles 360*k/N near targets:")
found5 = False
for N in (44, 88, 176, 352):
    for k in range(1, N):
        ang = 360.0 * k / N
        for tgt, name in ((TARGET, "66.40"), (CORR, "5.60")):
            if abs(ang - tgt) < TOL:
                found5 = True
                print(f"    {ang:.4f} deg = 360*{k}/{N}  (target {name}, d={ang - tgt:+.4f})")
if not found5:
    print("    none within tol")

# Summary
print("\nSUMMARY: any S1/S2/S4 candidate with sim <= 20 = structural candidate; "
      "otherwise 5.60 deg has no chain-sector source (consistent with audit).")
