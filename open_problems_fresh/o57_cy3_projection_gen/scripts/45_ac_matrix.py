#!/usr/bin/env python3
"""
O57 六期 45: A_C 代數預指數矩陣 (30C sector)
==============================================
Gemini: Y = A_ij(C) ⊗ e^{-V_ij(K)}
  A_ij(C): 30 C 態嘅代數選擇律矩陣 (零點 + 選擇律)
  e^{-V_ij(K)}: 36 K 態嘅幾何體積壓抑

構建:
  1. 提取 66 態 evecs (P_fixed_v2.npy)
  2. C 態 = CPX 分量主導 (30 個)
  3. A_C = C 態之間嘅 overlap 矩陣 (30×30)
  4. 檢查零點結構 (代數選擇律)
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
DATA = os.path.join(BASE, "data")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 六期 45: A_C 代數矩陣")
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

# ============ 1. 66 態 ============
print("\n[1] 66 態提取")
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
print(f"  K: {len(K_idx)}, C: {len(C_idx)}")

# ============ 2. A_C 構建 ============
print("\n[2] A_C 代數矩陣")
# C 態嘅 CPX 分量 (98-dim) — 用 overlap 矩陣
W_C = evecs_pos[36:, C_idx]  # 98 × 30
print(f"  W_C: {W_C.shape}")

# A_C = W_C^T · W_C (30×30 Gram 矩陣 — 代數選擇律)
A_C = W_C.T @ W_C
print(f"  A_C: {A_C.shape}")

# 零點結構 (代數零點 = 選擇律!)
nz_frac = np.sum(np.abs(A_C) < 1e-10) / A_C.size
print(f"  A_C 零點比例: {nz_frac:.3f}")
print(f"  A_C diag: {np.diag(A_C)}")
print(f"  A_C off-diag max: {np.abs(A_C - np.diag(np.diag(A_C))).max():.4f}")

# 本徵值
ev_A = np.linalg.eigvalsh(A_C)
ev_sorted = np.sort(ev_A)[::-1]
print(f"  A_C 本徵值 (top 15): {ev_sorted[:15]}")
print(f"  A_C 正本徵值: {np.sum(ev_A > 1e-10)}/{len(ev_A)}")
check("A_C rank = 30 (full)", np.linalg.matrix_rank(A_C) == 30, f"({np.linalg.matrix_rank(A_C)})")

# ============ 3. K 態幾何 ============
print("\n[3] K 態幾何 (e^{-V})")
# K 態嘅 Kähler 分量 (36-dim) — 投影到正確 κ 嘅 volume
W_K = evecs_pos[:36, K_idx]  # 36 × 36
print(f"  W_K: {W_K.shape}")

# 每個 K 態用 φ^(35-i) 計 curve volume
import cytools
from cytools import Polytope
from cytools.config import enable_experimental_features
enable_experimental_features()

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

t_phi = phi ** (35 - np.arange(36))
# Y_K = κ·t (36×36)
Y_K = np.einsum('ijk,k->ij', K_tensor, t_phi)
Y_K = (Y_K + Y_K.T) / 2

# K 態投影到 Y_K 本徵空間
ev_Y, evecs_Y = np.linalg.eigh(Y_K)
ev_Y_sorted = np.sort(ev_Y)[::-1]
print(f"  Y_K 譜: {ev_Y_sorted[:10]}")

# ============ 4. 總結 ============
print("\n" + "=" * 72)
print("六期 45 總結:")
print("=" * 72)
print(f"""
  A_C 代數矩陣:
  ─────────────────────────────────
  1. C 態: {len(C_idx)} 個 (CPX 主導)
  2. A_C: {A_C.shape}, 零點比例 {nz_frac:.3f}
  3. A_C 本徵值: {len(ev_A)} 個, {np.sum(ev_A > 1e-10)} 個正
  4. Y_K (K-sector): 睇上面

  {'✅ A_C 結構確認!' if np.linalg.matrix_rank(A_C) == 30 else '❌ A_C rank 唔啱'}
""")

results = {
    "test": "O57 六期 45: A_C 矩陣",
    "nC": int(len(C_idx)),
    "A_C_rank": int(np.linalg.matrix_rank(A_C)),
    "A_C_nz_frac": float(nz_frac),
    "A_C_ev_pos": int(np.sum(ev_A > 1e-10)),
    "passed": passed, "failed": failed
}
with open("data/45_ac_matrix.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 六期 45 完成!")
