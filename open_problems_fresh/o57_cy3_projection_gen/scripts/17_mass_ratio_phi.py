#!/usr/bin/env python3
"""
O57 二期 17: 66 態質量比嘅 φ 結構 + SM 已知質量比對照
======================================================
核心: 唔好夾硬匹配 SM 絕對質量, 而係檢查 66 態質量譜內部嘅比例結構,
     然後同 SM 已知嘅質量比對照 (m_t/m_b, m_τ/m_μ, m_c/m_s...)

SM 已知質量比 (PDG):
  m_t/m_b = 172760/4180 = 41.33
  m_τ/m_μ = 1776.86/105.66 = 16.82
  m_c/m_s = 1270/93.4 = 13.60
  m_μ/m_e = 105.66/0.511 = 206.8
  m_t/m_τ = 172760/1776.86 = 97.23
  m_b/m_c = 4180/1270 = 3.29
  m_τ/m_c = 1776.86/1270 = 1.40

φ 冪:
  φ⁵ = 11.09, φ⁶ = 17.94, φ⁷ = 29.03, φ⁸ = 46.98
  φ¹⁰ = 122.99, φ¹¹ = 199.0

66 態內部比 (未壓抑, √λ):
  λ₁/λ₂ = ?
  代 mean 比: 11.93, 3.97
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DATA = os.path.join(BASE, "data")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 二期 17: 質量比 φ 結構")
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

# ============ 1. SM 質量比 ============
print("\n[1] SM 已知質量比")
sm_ratios = {
    "m_t/m_b": 172760/4180,
    "m_τ/m_μ": 1776.86/105.66,
    "m_c/m_s": 1270/93.4,
    "m_μ/m_e": 105.66/0.511,
    "m_t/m_τ": 172760/1776.86,
    "m_b/m_c": 4180/1270,
    "m_τ/m_c": 1776.86/1270,
    "m_W/m_Z": 80377/91187.6,
    "m_Z/m_H": 91187.6/125250,
}
for k, v in sm_ratios.items():
    print(f"    {k} = {v:.3f}  (φ^({math.log(v)/math.log(phi):+.3f}))")

# ============ 2. 66 態內部比 ============
print("\n[2] 66 態內部比 (√λ)")
P = np.load(os.path.join(DATA, "P_fixed_v2.npy"))
PPT = P @ P.T
evals, _ = np.linalg.eigh(PPT)
idx = np.argsort(evals)[::-1]
evals = evals[idx]
pos = evals > 1e-10
evals_pos = evals[pos][:66]
sq = np.sqrt(evals_pos)

# 代 mean 比
g_means = [sq[g*22:(g+1)*22].mean() for g in range(3)]
print(f"  代 mean: {[f'{m:.4f}' for m in g_means]}")
print(f"  Gen1/Gen2 = {g_means[0]/g_means[1]:.4f}  φ^({math.log(g_means[0]/g_means[1])/math.log(phi):+.3f})")
print(f"  Gen2/Gen3 = {g_means[1]/g_means[2]:.4f}  φ^({math.log(g_means[1]/g_means[2])/math.log(phi):+.3f})")

# 個別態比
print(f"\n  個別態比:")
pairs = [(0, 21), (22, 44), (45, 65), (0, 22), (21, 45), (0, 45)]
for i, j in pairs:
    r = sq[i] / sq[j]
    print(f"    √λ_{i+1}/√λ_{j+1} = {r:.4f}  φ^({math.log(r)/math.log(phi):+.3f})")

# ============ 3. SM vs 66 比對照 ============
print("\n[3] SM vs 66 比對照")
# SM m_t/m_b = 41.33 ≈ ?
# 66 態: √λ₁/√λ_? = 41.33?
sq_sorted = sq
for target_name, target in sm_ratios.items():
    # 搵最接近嘅 √λ_i/√λ_j
    best = None
    best_err = 1e9
    for i in range(66):
        for j in range(i+1, 66):
            r = sq[i]/sq[j]
            err = abs(r - target)/target
            if err < best_err:
                best_err = err
                best = (i+1, j+1, r)
    print(f"    {target_name} = {target:.3f} → 66態 √λ_{best[0]}/√λ_{best[1]} = {best[2]:.3f} (err {best_err*100:.1f}%)")

# ============ 4. 66 態嘅 φ 指數譜 ============
print("\n[4] 66 態 √λ 嘅 φ 指數")
# k_i = log_φ(λ₁/λ_i)
k = np.array([math.log(evals_pos[0]/evals_pos[i])/math.log(phi) for i in range(66)])
print(f"  φ 指數: {k[0]:.3f}, {k[1]:.3f}, ..., {k[-1]:.3f}")
print(f"  範圍: [{k.min():.3f}, {k.max():.3f}]")

# 檢查整數/半整數?
near_int = sum(1 for x in k if abs(x - round(x)) < 0.05)
print(f"  近整數 (|k−round|<0.05): {near_int}/66")
print(f"  近半整數: {sum(1 for x in k if abs(x - (round(2*x)/2)) < 0.05)}/66")

# cluster 嘅 φ 指數
clusters = [(1,1), (2,20), (21,22), (23,58), (59,66)]
print(f"  Cluster φ 指數:")
for lo, hi in clusters:
    seg = k[lo-1:hi]
    print(f"    [{lo:2d}-{hi:2d}]: {seg[0]:.2f} ~ {seg[-1]:.2f} (mean {seg.mean():.2f})")

# ============ 5. 特定比對 ============
print("\n[5] 特定 SM 比對 (log-φ)")
# SM 比嘅 φ 指數:
sm_phi = {name: math.log(val)/math.log(phi) for name, val in sm_ratios.items()}
for name, val in sm_phi.items():
    print(f"    {name}: φ^{val:+.3f}")

# 66 態 cluster 比:
# λ₁ (t) / λ₂ (H?) = ?
r12 = evals_pos[0]/evals_pos[1]
print(f"  λ₁/λ₂ = {r12:.3f} φ^({math.log(r12)/math.log(phi):+.3f})")
# SM m_t/m_H = 172760/125250 = 1.38
print(f"  SM m_t/m_H = {172760/125250:.3f}")

# λ₁/λ₆?
r16 = evals_pos[0]/evals_pos[5]
print(f"  λ₁/λ₆ = {r16:.3f} φ^({math.log(r16)/math.log(phi):+.3f})")

# ============ 6. 總結 ============
print("\n" + "=" * 72)
print("二期 17 總結:")
print("=" * 72)
print(f"""
  66 態質量比 φ 結構:
  ─────────────────────────────────
  1. 代 mean 比: Gen1/Gen2 = {g_means[0]/g_means[1]:.3f} (φ^{math.log(g_means[0]/g_means[1])/math.log(phi):+.2f}),
     Gen2/Gen3 = {g_means[1]/g_means[2]:.3f} (φ^{math.log(g_means[1]/g_means[2])/math.log(phi):+.2f})
  2. SM 比 φ 指數: m_t/m_b = φ^{sm_phi['m_t/m_b']:+.2f}, m_τ/m_μ = φ^{sm_phi['m_τ/m_μ']:+.2f}
  3. 66 態 φ 指數: {k[0]:.2f} ~ {k[-1]:.2f}

  ⚠️ 誠實:
  - 66 態嘅 φ 指數唔係乾淨整數 (中間有連續譜)
  - SM 質量比冇簡單對應 66 態內部比
  - 質量標籤需要真正嘅 cycle volume (CYTools), 唔可以夾硬匹配
""")

results = {
    "test": "O57 二期 17: 質量比 φ 結構",
    "gen_ratios": {"g1_g2": float(g_means[0]/g_means[1]), "g2_g3": float(g_means[1]/g_means[2])},
    "sm_phi_exponents": {name: float(val) for name, val in sm_phi.items()},
    "phi_exponent_range": [float(k.min()), float(k.max())],
    "honest": "66態 φ 指數非整數, 質量標籤需 CYTools",
    "passed": passed, "failed": failed
}
with open("data/17_mass_ratio_phi.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 二期 17 完成!")
