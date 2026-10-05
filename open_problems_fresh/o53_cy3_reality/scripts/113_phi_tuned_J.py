#!/usr/bin/env python3
"""
O53 方向②: φ-tuned J 搜尋 — Kähler cone 內搵 J 令 Block 0 有 1/3
====================================================================
J* 唔喺 cone 入面, 但有 1/3 本徵值 (Δ=0.0003)
測試:
1. J* 投影到 cone (最近點) 有冇 1/3?
2. 隨機 cone 內 J: 1/3 命中率 vs 隨機對照
3. 特殊方向 (tip + 主軸)
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 70)
print("O53: φ-tuned J 搜尋")
print("=" * 70)

from cytools import Polytope
from cytools.config import enable_experimental_features
enable_experimental_features()

with open(os.path.join(BASE, 'cy36_98_sage_export.json')) as f:
    sage = json.load(f)
pts = np.array(sage['points'])
p = Polytope(pts)
tri = p.triangulate()
cy = tri.get_cy()

# 1. 完整 κ 36³ (intersection numbers)
with open(os.path.join(BASE, 'cy36_98_intersection_full.json')) as f:
    ct = json.load(f)
K = np.array(ct['kappa'])
print(f"[1] κ 36³: {K.shape}")

# divisor basis (1-based) → 0-based
db = np.array(cy.divisor_basis()) - 1
print(f"  divisor basis (0-based): {db}")

# J* 36D
with open(os.path.join(BASE, 'Jstar_36D.json')) as f:
    jstar = json.load(f)
J0 = np.array(jstar['Jstar_36D'])

# 2. J* 投影到 Kähler cone
# 方法: 將 J* 嘅 32 個 basis 分量保持, 檢查係咪 cone 內
J0_32 = J0[db]
print(f"\n[2] J* basis 分量: {J0_32}")

# Kähler cone 檢查
kc = cy.toric_kahler_cone()
print(f"  J*[db] 喺 cone? {kc.contains(J0_32)}")

# 3. Y(J*) = κ·J* Block 0 本徵值 (確認 1/3)
Y = np.einsum('ijk,k->ij', K, J0)
Y = (Y + Y.T) / 2
B0 = Y[0:12, 0:12]
ev0 = np.linalg.eigvalsh(B0)
print(f"\n[3] J* Block 0 譜: {np.sort(ev0)[::-1][:5]}")
print(f"  有 1/3? {any(abs(e - 1/3) < 0.01 for e in ev0)}")

# 4. 搜尋: 隨機 cone 內 J (用 tip 做 scale)
tip = np.array(kc.tip_of_stretched_cone(1))
print(f"\n[4] tip: {tip.shape}")

# 隨機 cone 內方向: tip + 隨機微擾 (正組合)
rng = np.random.default_rng(77)
hits = 0
trials = 200
for t in range(trials):
    # 隨機方向: 用 cone rays 正組合
    w = rng.uniform(0.5, 1.5, tip.shape)
    J_try = w * tip
    if not kc.contains(J_try):
        continue
    # Y = κ_ij(J_try): 用 32D basis κ? 
    # 注意: K 36³, J_try 32D — 需要 embedding
    J_36 = np.zeros(36)
    J_36[db] = J_try
    Yt = np.einsum('ijk,k->ij', K, J_36)
    Yt = (Yt + Yt.T) / 2
    B0t = Yt[0:12, 0:12]
    evt = np.linalg.eigvalsh(B0t)
    # 檢查 1/3 (考慮縮放: λ 線性, normalize by max)
    has13 = any(abs(e - 1/3) < 0.01 for e in evt)
    if has13:
        hits += 1

print(f"  隨機 cone J 命中 1/3: {hits}/{trials} = {hits/trials*100:.1f}%")

# 5. 特殊: J* 方向投影 (norm 縮放) — 保持方向
print(f"\n[5] J* 方向 (唔同縮放):")
for scale in [0.5, 1.0, 2.0, 5.0, 10.0]:
    J_s = J0 * scale
    Ys = np.einsum('ijk,k->ij', K, J_s)
    Ys = (Ys + Ys.T) / 2
    B0s = Ys[0:12, 0:12]
    evs = np.linalg.eigvalsh(B0s)
    has = any(abs(e - 1/3) < 0.01 for e in evs)
    print(f"  scale={scale}: 有 1/3? {has}, 譜={np.sort(evs)[::-1][:3]}")

# 6. 關鍵: 1/3 係咪 J* 嘅「1/3 特徵向量」?
# 搵 1/3 本徵值嘅特徵向量, 檢查佢係咪對應某 divisor 組合
print(f"\n[6] J* Block 0 嘅 1/3 特徵向量:")
evals, evecs = np.linalg.eigh(B0)
idx13 = np.argmin(np.abs(evals - 1/3))
v13 = evecs[:, idx13]
print(f"  λ = {evals[idx13]:.6f}")
print(f"  v13 (12D): {v13}")
print(f"  |v13| 分佈: {np.abs(v13)}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)