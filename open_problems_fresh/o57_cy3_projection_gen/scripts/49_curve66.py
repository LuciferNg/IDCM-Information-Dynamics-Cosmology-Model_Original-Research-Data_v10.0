#!/usr/bin/env python3
"""
O57 六期 49: Curve Volumes × 66 態 — 質量階層最終測試
=======================================================
五期 43: CYTools compute_curve_volumes(φ^(35-i)) = 117 pos, range 1e8, 5 個有限質量
六期 48: C⊗K 直接耦合冇巨大階層 (range 23.7)

最終測試: 用 CYTools curve volumes 直接對應 66 態!
  - 66 態 = 36 K + 30 C
  - curve volumes = 185 個 (對應 toric curves)
  - 用 66 態嘅 Kähler/CPX 分量投影 curve volumes
  → 66 個「質量」= 每個態嘅幾何體積壓抑
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
DATA = os.path.join(BASE, "data")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 六期 49: Curve Volumes × 66 態")
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
basis = cy.divisor_basis()

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
print(f"  66 態: {len(K_idx)} K + {len(C_idx)} C")

# ============ 2. Curve volumes ============
print("\n[2] Curve volumes (φ^(35-i))")
t36 = phi ** (35 - np.arange(36))
t32 = np.array([t36[b-1] for b in basis])
cv = np.array(cy.compute_curve_volumes(t32))
print(f"  Curve volumes: {len(cv)} 個, {np.sum(cv>0)} positive")
pos_cv = cv[cv > 0]
print(f"  Positive range: {pos_cv.max()/pos_cv.min():.2e}")
print(f"  Positive (sorted, first 15): {np.sort(pos_cv)[:15]}")

# ============ 3. 66 態質量 ============
print("\n[3] 66 態質量 (e^{-V_curve})")
# 每個 66 態嘅質量 = 佢喺 Kähler 分量嘅 curve volume 壓抑
# 方法: 用 W_K (K 態 Kähler 分量 36×36) 投影 curve volumes
W_K = evecs_pos[:36, K_idx]  # 36×36
W_C = evecs_pos[36:, C_idx]  # 98×30

# K 態質量: W_K^T · diag(e^{-V_curve}) · W_K 對角
# curve volumes 有 185 個 (對應 divisor basis? 定 36 個?)
# 用 32-dim divisor basis 嘅 curve volumes
# CYTools curve_basis 有 32 個
cb = cy.curve_basis()
print(f"  curve_basis: {len(cb)}")

# 方法 A: 用 e^{-V} 對角矩陣直接壓抑 K 態
# curve volumes 對應 divisor basis 座標 — 需要 map 返 36
# 但 curve_basis = divisor_basis (32 個) — 用 CYTools 直接計
# 每個 K 態: mass = exp(-<K_i | V | K_i>)?
# 簡化: 用 36 個 prime divisors 嘅 volumes (compute_divisor_volumes)
dv = np.array(cy.compute_divisor_volumes(t32))
print(f"  Divisor volumes: {len(dv)} 個, {np.sum(dv>0)} positive")
pos_dv = dv[dv > 0]
print(f"  Divisor positive range: {pos_dv.max()/pos_dv.min():.2e}")

# K 態質量 (36 個): 用 divisor volumes 做 weight
# W_K: 36×36, 每個 K 態係 36-dim Kähler 分量
# mass_i = exp(-<w_i | V_div | w_i>)?
V_div = np.diag(np.where(dv > 0, dv, 1e6))  # negative → 壓到 0
m_K = np.exp(-np.diag(W_K.T @ V_div @ W_K))
print(f"\n  K 態質量 (36 個):")
print(f"    sorted: {np.sort(m_K)[::-1]}")
print(f"    finite: {np.sum(m_K > 1e-30)}")

# C 態質量 (30 個): 用 γ98 (K_Chain 譜)
gamma = 4 * np.sin(np.pi * np.arange(1, 45) / 88) ** 2
gamma98 = np.concatenate([gamma, gamma, gamma[:10]])
m_C = np.exp(-np.abs(np.diag(W_C.T @ np.diag(gamma98) @ W_C)))
print(f"\n  C 態質量 (30 個):")
print(f"    sorted: {np.sort(m_C)[::-1]}")
print(f"    finite: {np.sum(m_C > 1e-30)}")

# 合併 66 個質量
m_all = np.concatenate([m_K, m_C])
ms = np.sort(m_all)[::-1]
print(f"\n  66 態質量譜 (top 20): {ms[:20]}")
print(f"  66 態質量譜 (bottom 10): {ms[-10:]}")
n_finite = np.sum(ms > 1e-30)
print(f"  Finite: {n_finite}/66")
if n_finite > 1:
    mf = ms[:n_finite]
    print(f"  質量比: {mf.max()/mf.min():.2e}")

# ============ 4. 3 代結構 ============
print("\n[4] 3 代結構")
# K 態 36 = 3×12? C 態 30 = 3×10?
# 睇 K 態質量有冇 3 組
m_K_sorted = np.sort(m_K)[::-1]
if len(m_K_sorted) >= 3:
    print(f"  K 態最大 3 個: {m_K_sorted[:3]}")
    print(f"  K 態比值: {m_K_sorted[0]/m_K_sorted[1]:.2f}, {m_K_sorted[1]/m_K_sorted[2]:.2f}")

# ============ 5. 總結 ============
print("\n" + "=" * 72)
print("六期 49 總結:")
print("=" * 72)
print(f"""
  Curve Volumes × 66 態:
  ─────────────────────────────────
  1. Curve volumes: {np.sum(cv>0)} positive, range {pos_cv.max()/pos_cv.min():.2e}
  2. Divisor volumes: {np.sum(dv>0)} positive, range {pos_dv.max()/pos_dv.min():.2e}
  3. 66 態質量: {n_finite} finite, ratio {mf.max()/mf.min() if n_finite>1 else 'NA':.2e}

  {'✅ 有質量階層!' if n_finite >= 3 else '❌ 有限質量太少'}
""")

results = {
    "test": "O57 六期 49: Curve × 66 態",
    "cv_pos": int(np.sum(cv > 0)),
    "cv_range": float(pos_cv.max()/pos_cv.min()),
    "n_finite": int(n_finite),
    "mass_ratio": float(mf.max()/mf.min()) if n_finite > 1 else None,
    "passed": passed, "failed": failed
}
with open("data/49_curve66.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 六期 49 完成!")
