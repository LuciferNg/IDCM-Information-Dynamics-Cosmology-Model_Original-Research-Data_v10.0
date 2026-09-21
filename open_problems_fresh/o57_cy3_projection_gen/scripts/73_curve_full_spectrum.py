#!/usr/bin/env python3
"""
O57 十二期 73: 方向 A 深化 — 117 Curves 完整譜 + 9 費米子對應
================================================================
承接 scripts/43: 攞完整 117 positive curve volumes
→ e^-V 質量譜
→ 3 type × 3 gen 對應 (u/d/l × gen1/2/3)
→ 世代階梯 φ⁴~φ⁸ 出現?
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 十二期 73: 117 Curves 完整譜")
print("=" * 72)

passed = 0
failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

import cytools
from cytools import Polytope
from cytools.config import enable_experimental_features
enable_experimental_features()

# ============ 1. 建立 CY ============
print("\n[1] 建立 CY")
d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
pts = np.array(d["points"])
p = Polytope(pts)
tri = p.triangulate()
cy = tri.get_cy()
basis = cy.divisor_basis()
print(f"  divisor basis: {len(basis)}")

# ============ 2. φ^(35-i) curve volumes ============
print("\n[2] φ^(35-i) curve volumes")
t36 = phi ** (35 - np.arange(36))
t32 = np.array([t36[b-1] for b in basis])
cv = np.array(cy.compute_curve_volumes(t32))
pos_mask = cv > 1e-10
pos = cv[pos_mask]
print(f"  total: {len(cv)}, positive: {np.sum(pos_mask)}")

# 排序 + 完整譜
sorted_pos = np.sort(pos)
print(f"  positive volumes (sorted):")
for i, v in enumerate(sorted_pos):
    print(f"    [{i:3d}] {v:.6f}  (e^-V = {math.exp(-v):.3e})")

# ============ 3. e^-V 質量譜 ============
print("\n[3] e^-V 質量譜")
masses = np.exp(-sorted_pos)
n_finite = np.sum(masses > 1e-30)
print(f"  finite masses: {n_finite}")
ms = masses[masses > 1e-30][::-1]  # 大到細
for i, m in enumerate(ms):
    print(f"    m[{i}] = {m:.4e}")

if len(ms) >= 2:
    print(f"  質量比: {ms[0]/ms[-1]:.2e}")

# ============ 4. 3×3 對應 ============
print("\n[4] 3×3 世代對應 (SM)")
# SM 質量 (MeV)
m_SM = {
    "u": 2.2, "c": 1270, "t": 172760,
    "d": 4.7, "s": 93, "b": 4180,
    "e": 0.511, "mu": 105.66, "tau": 1776.86,
}
# 需要 9 個有限質量 → 我哋有幾多?
print(f"  模型有限質量: {n_finite} 個 (SM 要 9)")
if n_finite >= 9:
    # 對應: 每 type 3 gen
    types = ["u", "d", "l"]
    for t, ti in zip(types, range(3)):
        t_masses = ms[ti*3:(ti+1)*3]
        sm_t = [m_SM[k] for k in {"u": ["u","c","t"], "d": ["d","s","b"], "l": ["e","mu","tau"]}[t]]
        # log-err
        log_err = np.mean([abs(math.log(t_masses[i]/sm_t[i])) for i in range(3)])
        print(f"  {t}: model={[f'{x:.2e}' for x in t_masses]}, SM={sm_t}, log-err={log_err:.3f}")
else:
    print(f"  → 唔夠 9 個, 只有 {n_finite}")

# ============ 5. 世代階梯 ============
print("\n[5] 世代階梯 (φ 冪)")
if len(ms) >= 3:
    r12 = ms[0]/ms[1]
    r23 = ms[1]/ms[2]
    print(f"  m1/m2 = {r12:.2e}, m2/m3 = {r23:.2e}")
    print(f"  φ⁴ = {phi**4:.1f}, φ⁶ = {phi**6:.1f}, φ⁸ = {phi**8:.1f}")
    # SM 世代比
    for t, keys in [("u", ["u","c","t"]), ("d", ["d","s","b"]), ("l", ["e","mu","tau"])]:
        ms_sm = [m_SM[k] for k in keys]
        print(f"  SM {t}: m2/m1 = {ms_sm[1]/ms_sm[0]:.0f}, m3/m2 = {ms_sm[2]/ms_sm[1]:.0f}")

# ============ 6. 總結 ============
print("\n" + "=" * 72)
print("十二期 73 總結:")
print("=" * 72)
print(f"""
  117 Curves 完整譜:
  ─────────────────────────────────
  1. {np.sum(pos_mask)} positive curves
  2. {n_finite} 個有限質量
  3. 質量比: {'NA' if len(ms)<2 else f'{ms[0]/ms[-1]:.2e}'}

  {'✅ 有足夠質量做 9 費米子!' if n_finite >= 9 else '❌ 有限質量唔夠 9'}
""")

# 存完整譜
results = {
    "test": "O57 十二期 73: 117 Curves",
    "n_pos": int(np.sum(pos_mask)),
    "n_finite": int(n_finite),
    "volumes": [float(v) for v in sorted_pos],
    "masses": [float(m) for m in masses],
    "mass_ratio": float(ms[0]/ms[-1]) if len(ms) >= 2 else None,
    "passed": passed, "failed": failed
}
with open("data/73_curve_full_spectrum.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 十二期 73 完成!")
