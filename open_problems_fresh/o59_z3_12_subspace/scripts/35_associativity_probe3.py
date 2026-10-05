#!/usr/bin/env python3
"""
O59 重推 probe-3 — κ basis 診斷 + tip 對照 + 正確 metric 搜尋
=============================================================
問題: CY₃ intersection ring 理論上必然 associative (cup product)。
若所有候選 metric 都爆,只有三種可能:
  (a) κ 唔係 torch 上嘅 "intersection ring" (basis/維度問題)
  (b) metric 形式未試齊 (WDVV metric = 固定 Kähler class / 特定 pairing)
  (c) κ 真係唔 associative (不可能 if genuine CY3 cohomology ring)

CYTools compute_kappa_matrix(tip) 回傳 32×32 (唔係 36×36!) — 重大線索:
36 個 divisor 可能只有 32 個 independent (4 個 redundant)。
"""
import os, json, math
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
POLY = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

kappa = np.array(json.load(open(os.path.join(POLY, "cy36_98_intersection_full.json")))["kappa"])
Jstar = np.array(json.load(open(os.path.join(POLY, "Jstar_36D.json")))["Jstar_36D"])
ck = json.load(open(os.path.join(POLY, "cy36_98_cytools_kappa.json")))
K32 = np.array(ck["kappa"])
tip32 = np.array(ck["tip"])

print("=" * 78)
print("[1] κ 切片 rank 分析: rank(κ[:,:,i]) for i=0..35")
print("=" * 78)
ranks = []
sing = []
for i in range(36):
    g = (kappa[:, :, i] + kappa[:, :, i].T) / 2
    sv = np.linalg.svd(g, compute_uv=False)
    r = np.sum(sv > 1e-10)
    ranks.append(r)
    if r < 36:
        sing.append((i, r))
print(f"  rank 分布: {sorted(set(ranks))}")
print(f"  full-rank 切片數: {ranks.count(36)}/36")
print(f"  非 full-rank: {len(sing)} 個, 舉例: {sing[:10]}")

# 零空間結構 — 公共零空間?
print("\n 公共零空間檢查 (所有切片 share 嘅 null vector?)")
ns = None
for i in range(36):
    g = (kappa[:, :, i] + kappa[:, :, i].T) / 2
    u, s, vh = np.linalg.svd(g)
    nsv = vh[s < 1e-10]
    if len(nsv) == 0:
        continue
    proj = nsv.T @ nsv  # 投影喺 nullspace
    ns = proj if ns is None else ns + proj
if ns is not None:
    # 任何 vector 被所有切片 kill?
    ev = np.linalg.eigvalsh((ns + ns.T)/2)
    print(f"  nullspace 自和投影 eig (top): {np.round(ev[-5:], 3)}")
    print(f"  max null 投影 = {ev[-1]:.3f}")

print("=" * 78)
print("[2] 32×32 κ (compute_kappa_matrix tip) — 同 36³ 嘅關係")
print("=" * 78)
print("  K32 shape:", K32.shape, " tip32 shape:", tip32.shape)
sv32 = np.linalg.svd(K32, compute_uv=False)
print("  32×32 κ matrix singular values (first 6):", np.round(sv32[:6], 3))
print("  rank(K32):", np.sum(sv32 > 1e-8))

# tip 對照: 32D tip metric 下 32×32 κ 嘅 associativity?
# 32×32 κ matrix = intersection matrix with tip? 或泛化 toric intersection
try:
    Y32 = (K32 + K32.T) / 2
    ev32 = np.linalg.eigvalsh(Y32)
    print("  Y32(=K32) eig range:", round(ev32[0], 4), "..", round(ev32[-1], 4), " n_neg:", np.sum(ev32 < -1e-8))
except Exception as e:
    print("  Y32 計算失敗:", e)

print("=" * 78)
print("[3] Jstar 係咪有效 Kähler class? (∃ positive definite Y=κ·J?)")
print("=" * 78)
Yj = np.einsum("ijk,k->ij", kappa, Jstar); Yj = (Yj + Yj.T) / 2
evj = np.linalg.eigvalsh(Yj)
print(f"  Y(κ·Jstar): min={evj[0]:.5f} max={evj[-1]:.5f} n_neg={np.sum(evj < -1e-10)}")
print(f"  Jstar: min={Jstar.min():.5f} max={Jstar.max():.5f} 分鐘 all positive: {Jstar.min() > 0}")

# Kähler cone 要求: Y = κ·J 喺 cone 內 positive definite
# 掃描 J 分量 (docs/96 random_J_13 已做過類似)
print("\n  隨機正 J 下 Y=κ·J 嘅正定性 (20 trials)")
rng = np.random.default_rng(42)
n_posdef = 0
for _ in range(20):
    J = rng.random(36)
    Y = np.einsum("ijk,k->ij", kappa, J); Y = (Y + Y.T) / 2
    if np.all(np.linalg.eigvalsh(Y) > 1e-10):
        n_posdef += 1
print(f"  positive-definite Y 比例: {n_posdef}/20")

print("=" * 78)
print("[4] 正確 WDVV metric: 用 full 36³ 但 non-singular metric 組合")
print("=" * 78)
# WDVV 正確形式: F_abc = κ_abc, metric η = ∫ D_a D_b J (固定 class J)
# 若 Y(κ·J) 唔 positive definite, associativity constant 都可能唔存在
# 但 intersection ring 嘅 associativity 唔需要 metric!
# 直接驗: ring structure constants C^c_ab = κ_ab e η^{ec} 嘅 associativity
# 或者用最 fundamental: cohomology ring 嘅 "intersection pairing" = ∫ D_a D_b D_c 全對稱
# ⇒ 三階張量本身 double contraction d_abm d_mcd = d_acm d_mbd 先係 ring associativity
# (唔 need metric — 呢個係 "double product" 對稱性, 唔係 WDVV!)

lhs = np.einsum("abm,mcd->abcd", kappa, kappa)
rhs = np.einsum("acm,mbd->abcd", kappa, kappa)
print(f"  ring associativity (κ_abm κ_mcd vs κ_acm κ_mbd): max={np.max(np.abs(lhs-rhs)):.4e}")
lhs2 = np.einsum("abm,mcd->abcd", kappa, kappa)
rhs2 = np.einsum("bcm,amd->abcd", kappa, kappa)
print(f"  ring associativity variant (ab·cd vs bc·ad):     max={np.max(np.abs(lhs2-rhs2)):.4e}")

# 12D 同一檢查
d_native = np.load(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
                                "main_problems", "p15_early_derivations", "data", "d_tensor_native_12d.npy"))
l12 = np.einsum("abm,mcd->abcd", d_native, d_native)
r12 = np.einsum("acm,mbd->abcd", d_native, d_native)
print(f"\n  12D ring associativity (no metric): max={np.max(np.abs(l12-r12)):.4e}")
l12b = np.einsum("abm,mcd->abcd", d_native, d_native)
r12b = np.einsum("bcm,amd->abcd", d_native, d_native)
print(f"  12D ring assoc variant2:            max={np.max(np.abs(l12b-r12b)):.4e}")

print("\nDONE probe-3")