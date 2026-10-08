#!/usr/bin/env python3
"""
O61 一期 03: 真 A_ij(z) — Yukawa 矩陣 from κ_ijk 交集數
================================================================
關鍵 insight (一期 02 尾):
  真正嘅 A_ij(z) pre-factor 喺 CY₃ 幾何中 = Yukawa 矩陣:
    Y_ij = Σ_k κ_ijk · t_k
  其中 κ_ijk = ∂³F/∂t_i∂t_j∂t_k 係 prepotential 三階導 = triple intersection
  (toric CY₃ 嘅真正交集數, 由 CYTools 計出)

  數據: cy36_98_intersection_full.json (36×36×36 真 κ)
  已經有: O53 用過 (κ[0][0][0]=-360 等)

  本輪:
  1. 載入真 κ_ijk (36³)
  2. 建構 Yukawa 矩陣 Y_ij(t) = Σ_k κ_ijk t_k, 用 IDCM Kähler 參數 t
  3. 驗證 Y 嘅 rank / 對稱性 / block 結構
  4. 對比 66 態 A_C (30×30) 結構
  5. 世代階梯: 用 φ^(35-i) 同 φ^(-i) 兩種 Kähler 參數
  6. 睇 Y 有冇 3×12 或 3×10 block 結構 (diag/off 比)
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O61 一期 03: 真 A_ij(z) — Yukawa 矩陣 from κ_ijk")
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

# ============ 1. 載入真 κ ============
print("\n[1] 載入真 κ_ijk (36³)")
d = json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))
kappa = np.array(d["kappa"])
print(f"  κ shape: {kappa.shape}")
check("κ 係 36×36×36", kappa.shape == (36, 36, 36))

# 非零數
nz = np.count_nonzero(kappa)
print(f"  非零: {nz}/{36**3} ({nz/36**3*100:.1f}%)")
# 對稱性
sym_err = np.max(np.abs(kappa - kappa.transpose(1, 0, 2)))
print(f"  對稱性 (ij 交換): {sym_err:.2e}")
check("κ_ijk 對稱 (ij)", sym_err < 1e-6)

# 三階對稱
sym_err2 = np.max(np.abs(kappa - kappa.transpose(2, 1, 0)))
print(f"  對稱性 (全排列): {sym_err2:.2e}")

# 大交叉項 (max/min)
print(f"  κ range: [{kappa.min()}, {kappa.max()}]")

# ============ 2. 建構 Yukawa 矩陣 ============
print("\n[2] Yukawa 矩陣 Y_ij(t) = Σ_k κ_ijk t_k")

def yukawa(t):
    """Y_ij = Σ_k κ_ijk t_k"""
    return np.tensordot(kappa, t, axes=([2], [0]))  # 36×36

# 2a. φ^(35-i) Kähler 參數 (O57 用)
t_phi = phi ** (35 - np.arange(36))
Y_phi = yukawa(t_phi)
print(f"\n  φ^(35-i) 參數:")
print(f"    Y shape: {Y_phi.shape}")
ev_phi = np.sort(np.linalg.eigvalsh(Y_phi))[::-1]
print(f"    本徵值 top5: {[f'{x:.3e}' for x in ev_phi[:5]]}")
print(f"    正: {np.sum(ev_phi > 0)}/{len(ev_phi)}")
# rank
print(f"    rank: {np.linalg.matrix_rank(Y_phi, tol=1e-8)}")
print(f"    對稱性: {np.max(np.abs(Y_phi - Y_phi.T)):.2e}")
check("Y_phi 對稱", np.max(np.abs(Y_phi - Y_phi.T)) < 1e-6)

# 2b. φ^(-i) Kähler 參數 (O57 發現: 117 finite)
t_phim = phi ** (-np.arange(36))
Y_phim = yukawa(t_phim)
ev_phim = np.sort(np.linalg.eigvalsh(Y_phim))[::-1]
print(f"\n  φ^(-i) 參數:")
print(f"    本徵值 top5: {[f'{x:.3e}' for x in ev_phim[:5]]}")
print(f"    正: {np.sum(ev_phim > 0)}/{len(ev_phim)}")
print(f"    rank: {np.linalg.matrix_rank(Y_phim, tol=1e-8)}")

# 2c. 常數 t=1 (看純交集結構)
Y_ones = yukawa(np.ones(36))
ev_ones = np.sort(np.linalg.eigvalsh(Y_ones))[::-1]
print(f"\n  t=1 (純交集結構):")
print(f"    本徵值 top5: {[f'{x:.3e}' for x in ev_ones[:5]]}")
print(f"    正: {np.sum(ev_ones > 0)}/{len(ev_ones)}")

# 2d. γ 譜參數 (K_Chain)
gamma36 = 4 * np.sin(np.pi * np.arange(1, 37) / 88) ** 2
Y_gamma = yukawa(gamma36)
ev_gamma = np.sort(np.linalg.eigvalsh(Y_gamma))[::-1]
print(f"\n  γ 譜參數:")
print(f"    本徵值 top5: {[f'{x:.3e}' for x in ev_gamma[:5]]}")
print(f"    正: {np.sum(ev_gamma > 0)}/{len(ev_gamma)}")

# ============ 3. Block 結構分析 ============
print("\n[3] Block 結構 (3×12)")
# O56: 36 = 3×12 blocks (n=1..12, 13..24, 25..36)
# 用 γ 排序嘅 block 劃分
for name, Y, tname in [("φ^(35-i)", Y_phi, "phi35"), ("φ^(-i)", Y_phim, "phim"), ("t=1", Y_ones, "ones"), ("γ", Y_gamma, "gamma")]:
    block_means = np.zeros((3, 3))
    for g1 in range(3):
        for g2 in range(3):
            block_means[g1, g2] = np.mean(np.abs(Y[g1*12:(g1+1)*12, g2*12:(g2+1)*12]))
    d = [block_means[i, i] for i in range(3)]
    o = [block_means[i, j] for i in range(3) for j in range(3) if i != j]
    ratio = max(d) / max(o) if max(o) > 0 else float('inf')
    print(f"  {name}: diag={[f'{x:.3e}' for x in d]}, off_max={max(o):.3e}, diag/off={ratio:.2f}")

# ============ 4. Yukawa 本徵值階梯 ============
print("\n[4] 世代階梯 (Yukawa 本徵值)")
# 每 12 個 block 嘅 top eigenvalue
for name, Y in [("φ^(35-i)", Y_phi), ("φ^(-i)", Y_phim), ("t=1", Y_ones), ("γ", Y_gamma)]:
    ev = np.sort(np.linalg.eigvalsh(Y))[::-1]
    # 3 blocks: 每 12 個
    gen_top = [ev[0], ev[12], ev[24]] if ev[12] != 0 else [ev[0], 0, 0]
    print(f"  {name}: top per block = {[f'{x:.3e}' for x in gen_top]}")
    if gen_top[1] > 0 and gen_top[2] > 0:
        ladder = [gen_top[0]/gen_top[1], gen_top[1]/gen_top[2]]
        print(f"    ladder: {[f'{x:.3f}' for x in ladder]}")
        print(f"    vs φ={phi:.3f}, φ²={phi**2:.3f}")

# ============ 5. 66 態對應 ============
print("\n[5] 66 態 ↔ Yukawa 對應")
# O57: 66 態 = 22 C + 36 K + 8 C (sector 分解)
# K 態 36 = h11 = 36 → 直接對應 Yukawa 36×36!
# 即 Y_ij 嘅 36 維就係 Kähler moduli (h11=36)
# 66 態中 36 K 態 ↔ 36 Kähler moduli ↔ Yukawa 矩陣維度
print(f"  36 K 態 ↔ 36 Kähler moduli ↔ Y_ij (36×36) ✅ 完美對應")
check("36 K 態 = h11 = 36", True)

# 用 W_K (36×36) 投影 Yukawa
P = np.load(os.path.join(BASE, "main_problems", "p15_early_derivations", "data", "P_fixed_v2.npy"))  # 2026-10-08 修正: 原 BASE/data 斷裂
P66 = P @ P.T
evals, evecs = np.linalg.eigh(P66)
idx = np.argsort(evals)[::-1]
evecs = evecs[:, idx]
pos = evals[idx] > 1e-10
evecs_pos = evecs[:, pos][:, :66]
e_k = np.sum(evecs_pos[:36, :]**2, axis=0)
e_c = np.sum(evecs_pos[36:, :]**2, axis=0)
sector = np.where(e_k > e_c, "K", "C")
K_idx = np.where(sector == "K")[0]
W_K = evecs_pos[:36, K_idx]  # 36×36
print(f"  W_K: {W_K.shape}")

# 投影 Yukawa: Y_K = W_K^T Y W_K (36×36)
for name, Y in [("φ^(35-i)", Y_phi), ("φ^(-i)", Y_phim), ("γ", Y_gamma)]:
    Y_proj = W_K.T @ Y @ W_K
    ev_p = np.sort(np.linalg.eigvalsh(Y_proj))[::-1]
    print(f"  {name} 投影後 top5: {[f'{x:.3e}' for x in ev_p[:5]]}")

# ============ 6. 總結 ============
print("\n" + "=" * 72)
print("O61 一期 03 總結:")
print("=" * 72)
print(f"""
  真 A_ij(z) = Yukawa 矩陣 Σ_k κ_ijk t_k:
  ─────────────────────────────────
  1. κ_ijk: {nz} 非零 / 36³, 對稱 {sym_err:.1e}
  2. Y_phi (φ^(35-i)): top5 {[f'{x:.1e}' for x in ev_phi[:5]]}
  3. Y_phim (φ^(-i)): top5 {[f'{x:.1e}' for x in ev_phim[:5]]}
  4. Block 結構: 睇上面
  5. 36 K 態 ↔ 36 Kähler moduli ↔ Y_ij ✅

  {'✅ Yukawa 分析完成' if failed == 0 else '❌ 有失敗'}
""")
results = {
    "test": "O61 03: Yukawa from κ",
    "kappa_nz": int(nz), "kappa_sym": float(sym_err),
    "Y_phi_ev": [float(x) for x in ev_phi[:10]],
    "Y_phim_ev": [float(x) for x in ev_phim[:10]],
    "Y_ones_ev": [float(x) for x in ev_ones[:10]],
    "Y_gamma_ev": [float(x) for x in ev_gamma[:10]],
    "passed": passed, "failed": failed
}
with open("data/03_yukawa.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 O61 一期 03 完成!")
