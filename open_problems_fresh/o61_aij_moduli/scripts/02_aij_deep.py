#!/usr/bin/env python3
"""
O61 一期 02: A_ij(z) 深層結構 — 3×10 block + 世代階梯 + 權重方案
================================================================
一期 01 發現:
  - A_C (30×30) 有 3×10 block 結構 (diag/off = 5.40)
  - 但 eigenvalue 比 1.734/1.442 唔似 φ 結構
  - 3 gen block diag: 0.284, 0.232, 0.187 (遞減但唔係 φ)

本輪:
  1. 驗證 3×10 block 係咪真結構 (vs 隨機)
  2. 世代階梯: block diag 比 = ? (0.284/0.232 = 1.22, 0.232/0.187 = 1.24)
  3. 換權重方案: γ98 vs 其他 (constant, γ², 1/γ, 排序)
  4. 用真 CY₃ 幾何 (CYTools intersection) 對比
  5. A_ij 嘅 rank 結構 (66 態 ↔ 98 moduli 嘅 mapping)
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DATA = os.path.join(BASE, "main_problems", "p15_early_derivations", "data")  # 2026-10-08 修正: 原 BASE/data 斷裂
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O61 一期 02: A_ij(z) 深層結構")
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

# ============ 1. 攞 W_C (98×30) ============
print("\n[1] 攞 W_C")
P = np.load(os.path.join(DATA, "P_fixed_v2.npy"))
P66 = P @ P.T
evals, evecs = np.linalg.eigh(P66)
idx = np.argsort(evals)[::-1]
evals = evals[idx]
evecs = evecs[:, idx]
pos = evals > 1e-10
evecs_pos = evecs[:, pos][:, :66]
e_k = np.sum(evecs_pos[:36, :]**2, axis=0)
e_c = np.sum(evecs_pos[36:, :]**2, axis=0)
sector = np.where(e_k > e_c, "K", "C")
C_idx = np.where(sector == "C")[0]
K_idx = np.where(sector == "K")[0]
W_C = evecs_pos[36:, C_idx]  # 98×30
print(f"  W_C: {W_C.shape} (98×30)")

gamma = 4 * np.sin(np.pi * np.arange(1, 45) / 88) ** 2
gamma98 = np.concatenate([gamma, gamma, gamma[:10]])

# ============ 2. 權重方案比較 ============
print("\n[2] 權重方案比較")
schemes = {
    "γ98": gamma98,
    "constant": np.ones(98),
    "γ98²": gamma98 ** 2,
    "1/γ98": 1 / (gamma98 + 1e-10),
    "γ98 sorted": np.sort(gamma98)[::-1],
    "even-odd": np.where(np.arange(98) % 2 == 0, gamma98, gamma98[::-1]),
}
results_schemes = {}
for name, w in schemes.items():
    A = W_C.T @ np.diag(w) @ W_C
    ev = np.sort(np.linalg.eigvalsh(A))[::-1]
    # 3×10 block (按 diag 排序)
    order = np.argsort(np.diag(A))[::-1]
    A_s = A[np.ix_(order, order)]
    block_means = np.zeros((3, 3))
    for g1 in range(3):
        for g2 in range(3):
            block_means[g1, g2] = np.mean(np.abs(A_s[g1*10:(g1+1)*10, g2*10:(g2+1)*10]))
    diag_b = [block_means[i, i] for i in range(3)]
    off_b = [block_means[i, j] for i in range(3) for j in range(3) if i != j]
    ratio = max(diag_b) / max(off_b) if max(off_b) > 0 else float('inf')
    # 世代階梯
    ladder = [diag_b[i] / diag_b[i+1] for i in range(2)] if diag_b[1] > 0 and diag_b[2] > 0 else [0, 0]
    results_schemes[name] = {
        "ev_top5": [float(x) for x in ev[:5]],
        "block_diag": [float(x) for x in diag_b],
        "diag_off_ratio": float(ratio),
        "ladder": [float(x) for x in ladder],
    }
    print(f"  {name}: diag/off={ratio:.2f}, ladder={[f'{x:.3f}' for x in ladder]}")

# γ98 方案係咪最好?
print("\n  對比 φ 結構:")
print(f"    φ = {phi:.3f}, φ² = {phi**2:.3f}, φ³ = {phi**3:.3f}")
# 世代階梯期望: 0.284/0.232 = 1.224, 0.232/0.187 = 1.241 (γ98)
# 睇邊個方案嘅 ladder 最接近 φ

# ============ 3. 隨機對照 ============
print("\n[3] 隨機對照 (3×10 block 係咪真結構)")
rng = np.random.default_rng(42)
random_ratios = []
for trial in range(200):
    W_rand = rng.standard_normal((98, 30))
    W_rand /= np.linalg.norm(W_rand, axis=0)
    A_r = W_rand.T @ np.diag(gamma98) @ W_rand
    order_r = np.argsort(np.diag(A_r))[::-1]
    A_rs = A_r[np.ix_(order_r, order_r)]
    bm = np.zeros((3, 3))
    for g1 in range(3):
        for g2 in range(3):
            bm[g1, g2] = np.mean(np.abs(A_rs[g1*10:(g1+1)*10, g2*10:(g2+1)*10]))
    d = [bm[i, i] for i in range(3)]
    o = [bm[i, j] for i in range(3) for j in range(3) if i != j]
    random_ratios.append(max(d) / max(o) if max(o) > 0 else 999)
random_ratios = np.array(random_ratios)
true_ratio = results_schemes["γ98"]["diag_off_ratio"]
p_value = np.mean(random_ratios >= true_ratio)
print(f"  真值 diag/off = {true_ratio:.2f}")
print(f"  隨機 200 trials: mean={random_ratios.mean():.2f}, std={random_ratios.std():.2f}, max={random_ratios.max():.2f}")
print(f"  p = {p_value:.3f} ({np.sum(random_ratios >= true_ratio)}/200 ≥ 真值)")
check("3×10 block 顯著 (p<0.05)", p_value < 0.05, f"p={p_value:.3f}")

# ============ 4. 世代階梯對比 ============
print("\n[4] 世代階梯")
# γ98 方案: ladder = [1.224, 1.241]
ladder_g = results_schemes["γ98"]["ladder"]
print(f"  γ98 ladder: {[f'{x:.4f}' for x in ladder_g]}")
# 候選結構: φ^(k) 定 Lucas?
candidates = {
    "φ": phi, "φ²": phi**2, "φ³": phi**3,
    "L4/L3": 7/4, "L5/L4": 11/7, "L6/L5": 18/11,
    "4/3": 4/3, "5/4": 5/4, "6/5": 6/5,
    "B/(B-1)": 4/3, "F5/F4": 5/3, "F6/F5": 8/5, "F7/F6": 13/8,
}
print(f"  候選比:")
for cname, cval in candidates.items():
    print(f"    {cname} = {cval:.4f}")
# 搵最接近
best = []
for l in ladder_g:
    dists = {cname: abs(cval - l) for cname, cval in candidates.items()}
    bc = min(dists, key=dists.get)
    best.append((bc, dists[bc]))
print(f"  最接近: {best}")
check("ladder[0] ≈ 4/3 或 φ", min(abs(ladder_g[0]-4/3), abs(ladder_g[0]-phi)) < 0.1)

# ============ 5. A_ij rank 結構 ============
print("\n[5] A_ij rank 結構 (98 moduli ↔ 66 態)")
# 98 moduli, 66 態: 邊個 mapping?
# 66 = 30 C + 36 K → C 態 30 個用 98-dim 嘅 subspace
# A_C 30×30: rank?
rank_AC = np.linalg.matrix_rank(A_C := W_C.T @ np.diag(gamma98) @ W_C, tol=1e-8)
print(f"  A_C rank: {rank_AC}/30")
check("A_C full rank", rank_AC == 30)

# 30 C 態嘅能量結構
print("\n  30 C 態 (按能量排序):")
e_c_vals = np.sort(e_c[C_idx])[::-1]
print(f"    {[f'{x:.4f}' for x in e_c_vals]}")

# ============ 6. 真 CY₃ 幾何對比 (CYTools) ============
print("\n[6] 真 CY₃ 幾何 (CYTools intersection)")
try:
    import cytools
    from cytools import Polytope
    from cytools.config import enable_experimental_features
    enable_experimental_features()
    O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
    d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
    pts = np.array(d["points"])
    p = Polytope(pts)
    tri = p.triangulate()
    cy = tri.get_cy()
    basis = cy.divisor_basis()
    print(f"  divisor basis: {len(basis)}")
    # triple intersection κ_ijk
    # 用 curve volumes 做 pairing? 或者直接 intersection
    # CYTools: cy.compute_curve_volumes(t) 需要 Kähler 參數
    # 建構 A_ij 嘅幾何版本: ∫ α_i ∧ β_j 用 triple intersection
    print(f"  CYTools CY 建立成功")
    check("CYTools CY 建立", True)
except Exception as e:
    print(f"  CYTools: {e}")
    check("CYTools CY 建立", False, str(e)[:80])

# ============ 7. 總結 ============
print("\n" + "=" * 72)
print("O61 一期 02 總結:")
print("=" * 72)
print(f"""
  A_ij(z) 深層結構:
  ─────────────────────────────────
  1. 3×10 block 結構: diag/off = {results_schemes['γ98']['diag_off_ratio']:.2f}, p={p_value:.3f}
  2. 世代階梯 (γ98): {[f'{x:.3f}' for x in ladder_g]}
  3. A_C rank: {rank_AC}/30

  {'✅ 結構驗證完成' if failed == 0 else '❌ 有失敗'}
""")
results = {
    "test": "O61 02: A_ij 深層結構",
    "schemes": results_schemes,
    "random_p": float(p_value),
    "ladder_candidates": best,
    "rank_AC": int(rank_AC),
    "passed": passed, "failed": failed
}
with open("data/02_aij_deep.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 O61 一期 02 完成!")
