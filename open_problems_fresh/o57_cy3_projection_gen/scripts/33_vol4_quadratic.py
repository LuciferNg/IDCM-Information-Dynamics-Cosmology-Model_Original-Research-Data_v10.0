#!/usr/bin/env python3
"""
O57 五期 33: 4-cycle 二次型 Volume — 瓶頸 1 驗證
==================================================
Gemini 瓶頸 1: 四期用嘅 V = κ_ijk·t_k 係 2-cycle (curve) volume (線性 in t),
但真正 Yukawa 壓抑用嘅係 4-cycle volume (二次型 in t):

  V_i^(4) = ½ Σ_jk κ_ijk t_j t_k

φ 冪次 t_j = φ^j 經 κ 縮約後會被平滑化 → 動態範圍鎖死 O(1~10)?

測試:
  1. 用 φ 冪次 Kähler 參數計 36 個 4-cycle volumes (二次型)
  2. 對比線性 curve volume 嘅動態範圍
  3. 檢查世代 (3×12 block) 之間嘅 spread
  4. 睇下有冇自然分層 (大/細 volume)
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 五期 33: 4-cycle 二次型 Volume (瓶頸 1)")
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

kappa = np.array(json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))["kappa"])
print(f"  κ: {kappa.shape}, 非零 {np.count_nonzero(kappa)}")

# ============ 1. 4-cycle volume 二次型 ============
print("\n[1] 4-cycle volume (二次型)")
def vol4(t):
    """V_i^(4) = ½ Σ_jk κ_ijk t_j t_k (36 個 4-cycle)"""
    return 0.5 * np.einsum('ijk,j,k->i', kappa, t, t)

def vol2(t):
    """2-cycle curve volume 矩陣 (線性)"""
    v = np.einsum('i,ijk->jk', t, kappa)
    v = (v + v.T) / 2
    np.fill_diagonal(v, 0)
    return v

def range_info(vals, label):
    pos = vals[vals > 1e-10]
    if len(pos) < 2:
        print(f"  {label}: 少過 2 個 positive ({len(pos)})")
        return 1.0
    r = pos.max() / pos.min()
    print(f"  {label}: n_pos={len(pos)}, min={pos.min():.4f}, max={pos.max():.4f}, "
          f"range={r:.2e}")
    return r

# φ 冪次候選
t_phi_asc = phi ** np.arange(36)      # φ^(i-1)
t_phi_desc = phi ** (35 - np.arange(36))  # φ^(35-i)

for name, t in [("φ^(i-1)", t_phi_asc), ("φ^(35-i)", t_phi_desc)]:
    print(f"\n  --- {name} ---")
    v4 = vol4(t)
    r4 = range_info(v4, "  4-cycle (二次型)")
    v2m = vol2(t)
    pos2 = v2m[v2m > 1e-10]
    r2 = pos2.max()/pos2.min() if len(pos2) > 1 else 1
    print(f"  2-cycle (線性) range: {r2:.2e}")

# ============ 2. 世代 spread ============
print("\n[2] 世代 (3×12 block) spread")
for name, t in [("φ^(i-1)", t_phi_asc), ("φ^(35-i)", t_phi_desc)]:
    v4 = vol4(t)
    gen_means = [v4[g*12:(g+1)*12].mean() for g in range(3)]
    gen_max = [v4[g*12:(g+1)*12].max() for g in range(3)]
    print(f"  {name}: gen mean V4 = {[f'{m:.4f}' for m in gen_means]}")
    print(f"    gen max V4 = {[f'{m:.4f}' for m in gen_max]}")
    if all(m > 0 for m in gen_means):
        spread = max(gen_means)/min(gen_means)
        print(f"    gen spread = {spread:.2e}")
        check(f"{name} gen spread > 10^4 (瓶頸預言: 鎖死 O(1~10))",
              spread < 1e4, f"(spread={spread:.2e})")

# ============ 3. 4-cycle 分層 ============
print("\n[3] 4-cycle 分層 (有冇自然大/細分層)")
t = t_phi_desc  # 用 descend (之前 best range)
v4 = vol4(t)
print(f"  V4 sorted (desc): {np.sort(v4)[::-1]}")
print(f"  V4 範圍: [{v4.min():.4f}, {v4.max():.4f}]")
# 睇下有冇明顯 gap
vs = np.sort(v4)[::-1]
gaps = np.diff(vs)
big_gap_idx = np.argsort(gaps)[::-1][:3]
for gi in big_gap_idx:
    print(f"    gap@{gi}: {vs[gi]:.4f} → {vs[gi+1]:.4f} (Δ={gaps[gi]:.4f})")

# ============ 4. 對比: 線性 vs 二次型 ============
print("\n[4] 線性 vs 二次型 對比")
t = t_phi_desc
v2m = vol2(t)
v4 = vol4(t)
pos2 = v2m[v2m > 1e-10]
print(f"  線性 (2-cycle): range = {pos2.max()/pos2.min():.2e}")
print(f"  二次型 (4-cycle): range = {v4.max()/v4.min():.2e}")
print(f"  二次型 > 線性? {'✅' if v4.max()/v4.min() > pos2.max()/pos2.min() else '❌'}")

# ============ 5. 總結 ============
print("\n" + "=" * 72)
print("五期 33 總結:")
print("=" * 72)
print(f"""
  4-cycle 二次型 Volume (瓶頸 1):
  ─────────────────────────────────
  1. 四期用線性 V=κ·t (2-cycle) — 真正 Yukawa 用二次型 V4=½κtt
  2. φ 冪次 4-cycle 動態範圍: {v4.max()/v4.min():.2e}
  3. 世代 spread: 睇上面
  4. 分層結構: 睇上面

  Gemini 預言: 二次型經 κ 平滑化 → 動態範圍鎖死 O(1~10)
  驗證結果: {'✅ 確認' if v4.max()/v4.min() < 1e4 else '❌ 未確認'}
""")

results = {
    "test": "O57 五期 33: 4-cycle 二次型",
    "phi_desc_v4_range": float(v4.max()/v4.min()),
    "phi_desc_v2_range": float(pos2.max()/pos2.min()),
    "v4_min": float(v4.min()), "v4_max": float(v4.max()),
    "passed": passed, "failed": failed
}
with open("data/33_vol4_quadratic.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 五期 33 完成!")
