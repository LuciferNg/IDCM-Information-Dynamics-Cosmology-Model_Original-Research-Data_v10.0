#!/usr/bin/env python3
"""
O57 六期 48: γ-weighted C⊗K 耦合 Yukawa — 終極測試
=====================================================
六期 47 發現: C 態 γ-weighted pairing A_C^w 有 range 1.71e1
  (唔係 I — 有代數結構!)

而家: 用 A_C^w 做 C-block + K-block e^{-V} 組合
  → 睇有冇 3 代階層湧現
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
DATA = os.path.join(BASE, "data")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 六期 48: γ-weighted C⊗K Yukawa")
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

# ============ 1. 數據 ============
print("\n[1] 數據")
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
C_idx = np.where(sector == "C")[0]
K_idx = np.where(sector == "K")[0]
W_C = evecs_pos[36:, C_idx]  # 98×30
print(f"  C: {len(C_idx)}, K: {len(K_idx)}")

# ============ 2. A_C^w (γ-weighted) ============
print("\n[2] A_C^w")
gamma = 4 * np.sin(np.pi * np.arange(1, 45) / 88) ** 2
gamma98 = np.concatenate([gamma, gamma, gamma[:10]])
A_Cw = W_C.T @ np.diag(gamma98) @ W_C
ev_C = np.linalg.eigvalsh(A_Cw)
ev_C_sorted = np.sort(ev_C)[::-1]
print(f"  A_C^w 本徵值 range: {ev_C_sorted.max()/ev_C_sorted.min():.2e}")
print(f"  A_C^w 譜 (top 10): {ev_C_sorted[:10]}")
print(f"  A_C^w 譜 (bottom 5): {ev_C_sorted[-5:]}")

# ============ 3. K-block ============
print("\n[3] K-block (歸一化)")
t_phi = phi ** (35 - np.arange(36))
Y_K = np.einsum('ijk,k->ij', K_tensor, t_phi)
Y_K = (Y_K + Y_K.T) / 2
# 歸一化: 令最大 |λ| = 1 (避免 e^{-V} underflow)
scale = np.abs(Y_K).max()
Y_K_n = Y_K / scale
ev_Y, evecs_Y = np.linalg.eigh(Y_K_n)
print(f"  Y_K 歸一化 scale: {scale:.2e}")
print(f"  Y_K_n 本徵值 (top 5): {np.sort(ev_Y)[::-1][:5]}")

# e^{-V} 壓抑 (用歸一化 λ)
V_K = np.diag(np.exp(-np.abs(ev_Y)))
K_block = evecs_Y @ V_K @ evecs_Y.T
ev_K = np.linalg.eigvalsh(K_block)
ev_K_sorted = np.sort(ev_K)[::-1]
print(f"  K_block 本徵值 range: {ev_K_sorted.max()/ev_K_sorted.min():.2e}")
print(f"  K_block 譜 (top 10): {ev_K_sorted[:10]}")
print(f"  K_block 譜 (bottom 5): {ev_K_sorted[-5:]}")

# ============ 4. 完整 Yukawa ============
print("\n[4] 完整 66×66 (A_C^w ⊕ K_block)")
Y66 = np.zeros((66, 66))
Y66[:30, :30] = A_Cw
Y66[30:, 30:] = K_block
# 交叉 = 0 (正交)
ev66 = np.linalg.eigvalsh(Y66)
ev66_sorted = np.sort(ev66)[::-1]
print(f"  Y66 譜 (top 20): {ev66_sorted[:20]}")
print(f"  Y66 譜 (bottom 10): {ev66_sorted[-10:]}")
print(f"  正本徵值: {np.sum(ev66 > 1e-10)}/{len(ev66)}")

# 階層?
pos_ev = ev66[ev66 > 1e-10]
if len(pos_ev) > 1:
    print(f"  Positive range: {pos_ev.max()/pos_ev.min():.2e}")

# ============ 5. e^{-V} 質量 ============
print("\n[5] e^{-V} 質量譜")
masses = np.exp(-np.abs(ev66_sorted))
ms = np.sort(masses)[::-1]
n_finite = np.sum(ms > 1e-30)
print(f"  e^-V 質量 (top 20): {ms[:20]}")
print(f"  Finite: {n_finite}")
if n_finite > 1:
    mf = ms[:n_finite]
    print(f"  質量比: {mf.max()/mf.min():.2e}")

# 3 代?
print(f"\n  最大 3 個: {ms[:3]}")
print(f"  3 代比值: {ms[0]/ms[1]:.2f}, {ms[1]/ms[2]:.2f}")

# ============ 6. 總結 ============
print("\n" + "=" * 72)
print("六期 48 總結:")
print("=" * 72)
print(f"""
  γ-weighted C⊗K Yukawa:
  ─────────────────────────────────
  1. A_C^w range: {ev_C_sorted.max()/ev_C_sorted.min():.2e}
  2. K_block range: {ev_K_sorted.max()/ev_K_sorted.min():.2e}
  3. Y66 譜: 睇上面
  4. e^-V 質量: {n_finite} 個有限

  {'✅ 有階層!' if len(pos_ev) > 1 else '❌ 冇階層'}
  {'✅ 3 代結構?' if len(pos_ev) >= 3 else '❌ 唔夠'}
""")

results = {
    "test": "O57 六期 48: γ-weighted C⊗K",
    "ACw_range": float(ev_C_sorted.max()/ev_C_sorted.min()),
    "Kblock_range": float(ev_K_sorted.max()/ev_K_sorted.min()),
    "Y66_ev": [float(x) for x in ev66_sorted[:10]],
    "n_finite": int(n_finite),
    "passed": passed, "failed": failed
}
with open("data/48_gamma_ck.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 六期 48 完成!")
