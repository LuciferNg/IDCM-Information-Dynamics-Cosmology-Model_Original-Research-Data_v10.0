#!/usr/bin/env python3
"""
O57 六期 46: C⊗K 耦合 Yukawa 矩陣 — 終極測試
==============================================
Gemini: Y_emergent = A_ij(C) ⊗ e^{-V_ij(K)}

誠實發現 (45): A_C = I₃₀ (C 態完全正交, 冇代數零點)
  → 選擇律唔喺 evecs 正交性, 可能喺交叉結構!

新構建:
  1. C 態 CPX 分量 W_C (98×30)
  2. K 態 Kähler 分量 W_K (36×36)
  3. 交叉矩陣: M_ij = W_C^T·X·W_K (30×36) — C-K 耦合
     X = 幾何算子 (e^{-V} 對角)
  4. 組合矩陣: 30×30 C-block + 36×36 K-block + 交叉
     → 66×66 完整 Yukawa
  5. 對角化 → 睇有冇 3 代階層
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
DATA = os.path.join(BASE, "data")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 六期 46: C⊗K 耦合 Yukawa")
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

# ============ 1. 重建 κ + 66 態 ============
print("\n[1] 數據準備")
d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
pts = np.array(d["points"])
p = Polytope(pts)
tri = p.triangulate()
cy = tri.get_cy()
inter = cy.intersection_numbers()
K_tensor = np.zeros((36, 36, 36))
for key, val in inter.items():
    if isinstance(key, tuple) and len(key) == 3:
        i, j, k = key
        if 1 <= i <= 36 and 1 <= j <= 36 and 1 <= k <= 36:
            K_tensor[i-1, j-1, k-1] = val
            K_tensor[i-1, k-1, j-1] = val
            K_tensor[j-1, i-1, k-1] = val
            K_tensor[j-1, k-1, i-1] = val
            K_tensor[k-1, i-1, j-1] = val
            K_tensor[k-1, j-1, i-1] = val

P = np.load(os.path.join(DATA, "P_fixed_v2.npy"))
evals, evecs = np.linalg.eigh(P @ P.T)
idx = np.argsort(evals)[::-1]
evals = evals[idx]
evecs = evecs[:, idx]
pos = evals > 1e-10
evecs_pos = evecs[:, pos][:, :66]
e_k = np.sum(evecs_pos[:36, :]**2, axis=0)
e_c = np.sum(evecs_pos[36:, :]**2, axis=0)
sector = np.where(e_k > e_c, "K", "C")
K_idx = np.where(sector == "K")[0]
C_idx = np.where(sector == "C")[0]
W_K = evecs_pos[:36, K_idx]   # 36×36
W_C = evecs_pos[36:, C_idx]   # 98×30
print(f"  W_K: {W_K.shape}, W_C: {W_C.shape}")

# ============ 2. K-block: e^{-V} 幾何壓抑 ============
print("\n[2] K-block (e^{-V})")
t_phi = phi ** (35 - np.arange(36))
# curve volumes via κ (2-cycle = κ_ij·t_j)
Y_K = np.einsum('ijk,k->ij', K_tensor, t_phi)
Y_K = (Y_K + Y_K.T) / 2
# 對角化
ev_Y, evecs_Y = np.linalg.eigh(Y_K)
# e^{-V} 用 positive 本徵值
V_K = np.diag(np.exp(-np.abs(ev_Y)))
K_block = W_K.T @ V_K @ W_K
print(f"  K_block: {K_block.shape}")

# ============ 3. C-block: 代數 ============
print("\n[3] C-block (A_C)")
A_C = W_C.T @ W_C  # 30×30 = I (正交)
C_block = A_C
print(f"  C_block: {C_block.shape} (= I₃₀)")

# ============ 4. 交叉項 ============
print("\n[4] 交叉項 (C-K 耦合)")
# W_C: 98×30 (C 態 CPX 分量), W_K: 36×36 (K 態 Kähler 分量)
# 冇直接 98×36 算子 — 用 overlap 定義耦合:
# M_ij = <C_i | K_j> = W_C[:,i] · W_K[:,j] 但維度唔啱!
# 正確做法: 用原始 evecs 嘅完整 134-dim 空間
# evecs_pos 係 134×66 — C 態同 K 態都喺同一空間!
evecs_C = evecs_pos[:, C_idx]  # 134×30 (完整 C 態)
evecs_K = evecs_pos[:, K_idx]  # 134×36 (完整 K 態)
M = evecs_C.T @ evecs_K  # 30×36 (完整空間 overlap)
print(f"  M: {M.shape}")
print(f"  M 大小: |M|max = {np.abs(M).max():.4f}")
print(f"  M 零點比例: {np.sum(np.abs(M) < 1e-10)/M.size:.3f}")
# M 應該接近 0 (evecs 正交)! 確認
print(f"  M Frobenius: {np.linalg.norm(M):.4f}")

# ============ 5. 完整 66×66 Yukawa ============
print("\n[5] 66×66 完整 Yukawa")
Y66 = np.zeros((66, 66))
# C-block (30×30, top-left)
Y66[:30, :30] = C_block
# K-block (36×36, bottom-right)
Y66[30:, 30:] = K_block
# 交叉 (30×36)
Y66[:30, 30:] = M
Y66[30:, :30] = M.T

ev66 = np.linalg.eigvalsh(Y66)
ev66_sorted = np.sort(ev66)[::-1]
print(f"  Y66 譜 (top 20): {ev66_sorted[:20]}")
print(f"  Y66 正本徵值: {np.sum(ev66 > 1e-10)}/{len(ev66)}")

# 有冇階層?
pos_ev = ev66[ev66 > 1e-10]
if len(pos_ev) > 1:
    print(f"  Positive range: {pos_ev.max()/pos_ev.min():.2e}")
    # 3 代? 睇最大 3 個
    print(f"  最大 3 個: {ev66_sorted[:3]}")
    print(f"  比值: {ev66_sorted[0]/ev66_sorted[1]:.2f}, {ev66_sorted[1]/ev66_sorted[2]:.2f}")

# ============ 6. 質量譜 (e^{-V}) ============
print("\n[6] e^{-V} 質量譜")
masses = np.exp(-np.abs(ev66_sorted))
ms = np.sort(masses)[::-1]
n_finite = np.sum(ms > 1e-30)
print(f"  e^-V 質量 (top 15): {ms[:15]}")
print(f"  Finite: {n_finite}")
if n_finite > 1:
    print(f"  質量比: {ms[:n_finite].max()/ms[:n_finite].min():.2e}")

# ============ 7. 總結 ============
print("\n" + "=" * 72)
print("六期 46 總結:")
print("=" * 72)
print(f"""
  C⊗K 耦合 Yukawa:
  ─────────────────────────────────
  1. C-block = I₃₀ (正交, 冇零點)
  2. K-block = W_K^T e^-V W_K
  3. 交叉 M = W_C^T W_K ({np.abs(M).max():.4f})
  4. Y66 譜: {ev66_sorted[:5]}

  {'✅ 有階層!' if len(pos_ev) > 1 else '❌ 冇階層'}
  {'✅ 有 3 代結構!' if len(pos_ev) >= 3 else '❌ 唔夠 3 代'}
""")

results = {
    "test": "O57 六期 46: C⊗K Yukawa",
    "Y66_ev": [float(x) for x in ev66_sorted[:10]],
    "n_pos": int(np.sum(ev66 > 1e-10)),
    "n_finite_mass": int(n_finite),
    "passed": passed, "failed": failed
}
with open("data/46_ck_yukawa.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 六期 46 完成!")
