#!/usr/bin/env python3
"""
O59 重推 probe-2 — 36D κ metric 掃描 + 12D solver 殘差比對
==========================================================
問題 1: 36D κ 喺咩 metric 下先 associativity？（理論上 CY₃ quantum cohomology 必然
associative ⇒ 若所有候選都爆，係 κ 唔係 intersection ring，定係 metric 形式未試齊）
候選 metric 族: g^(i) = κ[:,:,i]（WDVV 標準: η_αβ = κ_αβ0）; κ·u for u∈{ones,J*,...};

問題 2: 12D solver 報嘅 L_wdvv（sum-square）同我量度嘅 max-abs 點比？先 print sum-square 版本。
"""
import os, json, math
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA = os.path.join(BASE, "main_problems", "p15_early_derivations", "data")
POLY = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

d_native = np.load(os.path.join(DATA, "d_tensor_native_12d.npy"))
kappa = np.array(json.load(open(os.path.join(POLY, "cy36_98_intersection_full.json")))["kappa"])
Jstar = np.array(json.load(open(os.path.join(POLY, "Jstar_36D.json")))["Jstar_36D"])

def wdvv_maxrms(d, g):
    try:
        g_inv = np.linalg.inv(g)
    except np.linalg.LinAlgError:
        return float("inf"), float("inf"), float("inf")
    lhs = np.einsum("abp,pq,qcd->abcd", d, g_inv, d)
    rhs = np.einsum("acp,pq,qbd->abcd", d, g_inv, d)
    diff = lhs - rhs
    return (float(np.max(np.abs(diff))),
            float(np.sqrt(np.sum(diff ** 2))),
            float(np.sum(diff ** 2)))   # solver 定義 (no sqrt)

# ---------- 問題 2: 12D solver 殘差單位 ----------
print("=" * 78)
print("12D: solver 定義 (sum-square, no sqrt) vs max-abs")
print("=" * 78)
ones12 = np.ones(12)
v12 = np.array([phi ** (-k/12) for k in range(12)])
Y12 = np.einsum("ijk,k->ij", d_native, v12); Y12 = (Y12 + Y12.T) / 2
for name, g in [("g=ones", np.einsum("ijk,k->ij", d_native, ones12)),
                ("g=Y(v12)", np.einsum("ijk,k->ij", d_native, v12))]:
    g = (g + g.T) / 2
    mx, rms, ss = wdvv_maxrms(d_native, g)
    print(f"  {name:10s} max={mx:.4e}  rms={rms:.4e}  sum_sq={ss:.4e}")

# ---------- 問題 1: 36D κ metric 掃描 ----------
print("\n" + "=" * 78)
print("36D κ: 候選 metric 族掃描")
print("=" * 78)
print("\n[A] η^i = κ[:,:,i]（WDVV 標準 flat metric 族, i=0..35）")
res = []
for i in range(36):
    g = kappa[:, :, i]
    g = (g + g.T) / 2
    mx, rms, ss = wdvv_maxrms(kappa, g)
    res.append((mx, i, rms, ss))
res.sort()
for mx, i, rms, ss in res[:8]:
    print(f"  i={i:2d}: max={mx:.4e} rms={rms:.4e}")
print(f"  ... best={res[0][1]} (min over 36)")

print("\n[B] g = κ·u（u 為向量候選）")
us = {"ones": np.ones(36), "Jstar": Jstar,
      "|Jstar|": np.abs(Jstar),
      "e_max(Y36)": None}
# 加 Y36 最大本徵向量候選
Y36 = np.einsum("ijk,k->ij", kappa, Jstar); Y36 = (Y36 + Y36.T) / 2
ev, U = np.linalg.eigh(Y36)
us["e_max(Y36)"] = U[:, -1]
us["e_min(Y36)"] = U[:, 0]
for name, u in us.items():
    if u is None: continue
    g = np.einsum("ijk,k->ij", kappa, u); g = (g + g.T) / 2
    mx, rms, ss = wdvv_maxrms(kappa, g)
    evg = np.linalg.eigvalsh(g)
    print(f"  {name:12s} max={mx:12.4e} n_neg={np.sum(evg < -1e-10)}")

print("\n[C] 一般化: metric = κ·u, u 由 J* 幂次展開 u_k = Jstar_k^p 掃描")
for p in [0, 1, 2, 3, 0.5, 2.0]:
    u = Jstar ** p
    g = np.einsum("ijk,k->ij", kappa, u); g = (g + g.T) / 2
    mx, rms, ss = wdvv_maxrms(kappa, g)
    print(f"  u=(J*)^{p:4}: max={mx:12.4e}  rms={rms:.4e}")

# ---------- sanity: κ 係咪對稱 ----------
print("\n" + "=" * 78)
print("κ 基本性質（唔 associativity 之前先睇結構）")
print("=" * 78)
print("  kappa shape:", kappa.shape)
print("  max|κ - κ^T(1,0,2)| =", np.max(np.abs(kappa - kappa.transpose(1, 0, 2))))
print("  max|κ - κ^T(2,1,0)| =", np.max(np.abs(kappa - kappa.transpose(2, 1, 0))))
print("  max|κ| =", np.max(np.abs(kappa)))
print("  min κ =", kappa.min(), " max κ =", kappa.max())
print("  Jstar: min", Jstar.min(), "max", Jstar.max(), "sum", Jstar.sum())

# 12D 嵌入 36D 嘅另一種合法測試: 用 12D 自己嘅 g_ones 做 12D 塊, 24D 用 0?
# 嵌入 associativity 只有喺 12D×12D×12D×12D 塊先有資格（24D 空缺）
print("\n" + "=" * 78)
print("12D 嵌入 36D: 喺 36D 空間內, 12D 塊嘅 associativity（用 12D 自己 g_ones）")
print("=" * 78)
g12_inv = np.linalg.inv(np.einsum("ijk,k->ij", d_native, ones12))
emb = np.zeros((36, 36, 36)); emb[:12, :12, :12] = d_native
# 12D 塊內 associativity: 只有 a,b,c,d ∈ 0..11, 用 g12_inv (12x12)
lhs = np.einsum("abp,pq,qcd->abcd", d_native, g12_inv, d_native)
rhs = np.einsum("acp,pq,qbd->abcd", d_native, g12_inv, d_native)
print("  12D-only WDVV with g_ones: max =", np.max(np.abs(lhs - rhs)))
# 用 Y12
g12y_inv = np.linalg.inv(Y12)
lhs = np.einsum("abp,pq,qcd->abcd", d_native, g12y_inv, d_native)
rhs = np.einsum("acp,pq,qbd->abcd", d_native, g12y_inv, d_native)
print("  12D-only WDVV with Y12:    max =", np.max(np.abs(lhs - rhs)))
print("\nDONE probe-2")