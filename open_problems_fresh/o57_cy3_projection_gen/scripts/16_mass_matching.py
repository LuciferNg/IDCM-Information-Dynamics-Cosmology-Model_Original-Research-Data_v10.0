#!/usr/bin/env python3
"""
O57 二期 16: 66 態質量譜 ↔ SM 質量直接匹配
=============================================
核心: 用 e^{-V} 壓抑後嘅 66 態質量, 直接匹配 SM 質量譜

方法:
  1. 66 態質量 m_i = M_Pl × √λ_i × e^{-V_i}
  2. V_i = cycle volume (每代/每 cluster)
  3. 匹配 SM 15 個粒子質量 (log 空間)

關鍵問題:
  - 66 態質量排序 vs SM 質量排序
  - 有冇「自然」嘅 V 結構令匹配成立?
  - 定係需要太多自由參數 (→ 唔算閉合)?
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DATA = os.path.join(BASE, "data")
phi = (1 + math.sqrt(5)) / 2
M_Pl = 1.220890e22  # MeV

print("=" * 72)
print("O57 二期 16: 66 態 ↔ SM 質量匹配")
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

# ============ 1. 66 態質量 ============
P = np.load(os.path.join(DATA, "P_fixed_v2.npy"))
PPT = P @ P.T
evals, _ = np.linalg.eigh(PPT)
idx = np.argsort(evals)[::-1]
evals = evals[idx]
pos = evals > 1e-10
evals_pos = evals[pos][:66]
m66 = np.sqrt(evals_pos) * M_Pl  # MeV

# SM 質量 (log 空間)
SM = {
    "nu_e": 0.001, "nu_mu": 0.009, "nu_tau": 0.05,
    "e": 0.511, "u": 2.16, "d": 4.67,
    "mu": 105.66, "s": 93.4, "c": 1270.0,
    "tau": 1776.86, "b": 4180.0,
    "W": 80377.0, "Z": 91187.6, "H": 125250.0, "t": 172760.0,
}
sm_masses = np.array(sorted(SM.values()))
sm_names = [k for k, v in sorted(SM.items(), key=lambda x: x[1])]
print(f"  SM 質量 (排序):")
for n, m in zip(sm_names, sm_masses):
    print(f"    {n:6s}: {m:10.4f} MeV  log10={np.log10(m):.3f}")

# ============ 2. 單一 V 壓抑 ============
print("\n[1] 單一 V 壓抑嘗試")
# m = M_Pl × √λ × e^{-V}
# 目標: m66 max ≈ m_t = 172760
# e^{-V} = m_t / (M_Pl × √λ_max)
V_fit = math.log(M_Pl * np.sqrt(evals_pos[0]) / 172760)
print(f"  用 m_t 校準: V = {V_fit:.4f}")
m_fit = np.sqrt(evals_pos) * M_Pl * math.exp(-V_fit)
print(f"  壓抑後質量譜: {m_fit[0]:.1f} ~ {m_fit[-1]:.4f} MeV")
print(f"  範圍: [{m_fit.min():.4f}, {m_fit.max():.1f}] MeV")
print(f"  SM 範圍: [0.001, 172760] MeV")

# 66 態質量同 SM 15 個質量嘅 log-空間相關?
log_m_fit = np.log10(m_fit)
log_sm = np.log10(sm_masses)
print(f"  66 態 log10 質量: {log_m_fit[:10]}...")

# 匹配: 66 態揀 15 個最接近 SM?
matched = []
for sm_m in sm_masses:
    diffs = np.abs(m_fit - sm_m)
    best = np.argmin(diffs)
    matched.append((sm_m, m_fit[best], diffs[best]/sm_m))
for sm_m, pred, err in matched[:8]:
    print(f"    SM {sm_m:10.1f} vs pred {pred:10.1f} err={err*100:.1f}%")

# ============ 3. 每代 V 壓抑 ============
print("\n[2] 每代 V 壓抑")
# 66 = 3×22: 每代 22 態
# 每代一個 V?
# V_gen = {V1, V2, V3}
# 目標: 代 mean 匹配 SM 代 mean

# SM 代 mean (log):
# Gen1 (u,d,e,νe): mean ≈ log10(0.001×2.16×4.67×0.511)^(1/4)?
# 用幾何 mean
g1_sm = np.array([0.001, 0.511, 2.16, 4.67])
g2_sm = np.array([0.009, 105.66, 93.4, 1270.0])
g3_sm = np.array([0.05, 1776.86, 4180.0, 172760.0])
print(f"  SM 代幾何 mean:")
print(f"    Gen1: {np.exp(np.mean(np.log(g1_sm))):.4f}")
print(f"    Gen2: {np.exp(np.mean(np.log(g2_sm))):.3f}")
print(f"    Gen3: {np.exp(np.mean(np.log(g3_sm))):.1f}")

# 66 態代 mean (未壓抑)
m66_g = [np.sqrt(evals_pos[g*22:(g+1)*22]).mean() * M_Pl for g in range(3)]
print(f"  66 態代 mean (M_Pl×√λ):")
print(f"    Gen1: {m66_g[0]:.3e}, Gen2: {m66_g[1]:.3e}, Gen3: {m66_g[2]:.3e}")

# V_gen = ln(m66_gen / m_sm_gen)
sm_g = [np.exp(np.mean(np.log(g))) for g in [g1_sm, g2_sm, g3_sm]]
V_gen = [math.log(m66_g[g] / sm_g[g]) for g in range(3)]
print(f"  需要 V_gen: {[f'{v:.3f}' for v in V_gen]}")
print(f"  差: V1−V2 = {V_gen[0]-V_gen[1]:.3f}, V2−V3 = {V_gen[1]-V_gen[2]:.3f}")

# ============ 4. V 結構有冇 φ/Lucas 身份? ============
print("\n[3] V_gen 嘅結構身份")
print(f"  V_gen = {[f'{v:.4f}' for v in V_gen]}")
print(f"  φ 冪? {[f'{v/math.log(phi):.3f}' for v in V_gen]}")
print(f"  L 數? L₅=11, L₆=18, L₇=29, L₈=47, L₉=76, L₁₀=123")
print(f"  V1 ≈ L₇−? {V_gen[0]:.1f} (L₇=29)")
print(f"  V2 ≈ L₆+? {V_gen[1]:.1f} (L₆=18)")
print(f"  V3 ≈ L₅+? {V_gen[2]:.1f} (L₅=11)")

# 如果 V_gen = {44, 33, 22} (orbifold 舊模型):
V_old = [44, 33, 22]
print(f"  舊模型 V = {{44, 33, 22}}:")
m_old = [np.sqrt(evals_pos[g*22:(g+1)*22]).mean() * M_Pl * math.exp(-V_old[g]) for g in range(3)]
print(f"    質量: {[f'{m:.4e}' for m in m_old]}")
print(f"    SM: {[f'{s:.4e}' for s in sm_g]}")

# ============ 5. 66 態 cluster 質量匹配 ============
print("\n[4] Cluster 結構匹配")
# 66 態 cluster: 1, 19, 2, 36, 8
# SM 分組: 
#   1 = t (172760)
#   19 = H, W, Z, b, τ, c, s, μ, d, u, e, ν... (好多)
#   2 = ?
#   36 = ?
#   8 = ?

# 每個 cluster 嘅質量範圍 (用 V_fit):
clusters = [(1,1), (2,20), (21,22), (23,58), (59,66)]
for lo, hi in clusters:
    seg = m_fit[lo-1:hi]
    print(f"    [{lo:2d}-{hi:2d}] ({hi-lo+1:2d}): {seg[0]:.2f} ~ {seg[-1]:.2f} MeV")

# 對應 SM?
# [1]: 172760 = t ✓ (λ₁ 單獨 = top!)
# [2-20] (19): 105~10⁵ → H, W, Z, b, τ, c...
# [21-22] (2): ? 
# [23-58] (36): ? 
# [59-66] (8): 輕? 

# 檢查 [59-66] 8 個: m_fit 最輕 8 個?
print(f"\n  最輕 8 個 (m_fit):")
light8 = np.argsort(m_fit)[:8]
print(f"    indices: {light8+1}")
print(f"    質量: {[f'{m_fit[i]:.4f}' for i in light8]}")

# 8 = 2B: 呢 8 個係分支邊界態?
# 質量 ~ 10⁻² ~ 10⁻¹ MeV? 
print(f"    對應 SM: ν (0.001-0.05) + e (0.511)?")

# ============ 6. 總結 ============
print("\n" + "=" * 72)
print("二期 16 總結:")
print("=" * 72)
print(f"""
  66 態 ↔ SM 質量匹配:
  ─────────────────────────────────
  1. 單一 V 校準: V = {V_fit:.3f} (由 m_t)
     壓抑後範圍: [{m_fit.min():.3f}, {m_fit.max():.1f}] MeV
     SM 範圍: [0.001, 172760] MeV
  2. 每代 V: V_gen = {[f'{v:.2f}' for v in V_gen]}
     差: V1−V2 = {V_gen[0]-V_gen[1]:.2f}, V2−V3 = {V_gen[1]-V_gen[2]:.2f}
  3. Cluster 結構:
     [1] = t (λ₁ 單獨!)
     [2-20] 19 個: H/W/Z/b/τ/c...
     [59-66] 8 個: 最輕 (ν/e?)

  ⚠️ 誠實:
  - 66 態質量排序同 SM 冇明顯 1:1 對應
  - e^-V 壓抑需要每代 V, 自由度大
  - 單一 V 時, 66 態質量唔匹配 SM 15 粒子
  - 需要真正嘅 cycle volume 結構 (CYTools) 先可以閉合
""")

results = {
    "test": "O57 二期 16: 質量匹配",
    "V_fit": float(V_fit),
    "V_gen": [float(v) for v in V_gen],
    "mass_range": [float(m_fit.min()), float(m_fit.max())],
    "cluster_masses": [[float(m_fit[lo-1]), float(m_fit[hi-1])] for lo, hi in clusters],
    "honest": "66態質量排序 ≠ SM 1:1; 需 CYTools cycle volumes",
    "passed": passed, "failed": failed
}
with open("data/16_mass_matching.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 二期 16 完成!")
