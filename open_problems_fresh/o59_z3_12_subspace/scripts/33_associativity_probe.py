#!/usr/bin/env python3
"""
O59 重推 — 12D/36D associativity（2026-10-05 拍板：唔開新 O，原地重推）
=====================================================================
第一性問題：d_tensor / κ 係咪 associative algebra？（docs/14 嘅「0.00」係同義反覆；
正確 WDVV associativity = Σ_p,q d_abp g^{pq} d_qcd 對 (b,c) 交換，其中 metric g 未定 ——
p15 solver 用 t=ones；docs 用 Y=v12-contraction。）

方法：對候選 metric 逐一測 associativity loss；zero-blind：唔好調 threshold 去就結果。
本 probe 係診斷（唔算 final），產出 metric 選擇嘅結構依據。
"""
import os, json, math
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA = os.path.join(BASE, "main_problems", "p15_early_derivations", "data")
POLY = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

d_native = np.load(os.path.join(DATA, "d_tensor_native_12d.npy"))            # 12³
kappa = np.array(json.load(open(os.path.join(POLY, "cy36_98_intersection_full.json")))["kappa"])
Jstar = np.array(json.load(open(os.path.join(POLY, "Jstar_36D.json")))["Jstar_36D"])

def wdvv_loss(d, g):
    """L = || d·g⁻¹·d - swap(b,c) ||_F —— p15 solver 嘅 associativity loss 定義
    回傳 (max_abs, rms)"""
    try:
        g_inv = np.linalg.inv(g)
    except np.linalg.LinAlgError:
        return float("inf"), float("inf")
    lhs = np.einsum("abp,pq,qcd->abcd", d, g_inv, d)
    rhs = np.einsum("acp,pq,qbd->abcd", d, g_inv, d)   # swap b,c (solver: ijkl vs iljk)
    return float(np.max(np.abs(lhs - rhs))), float(np.sqrt(np.sum((lhs - rhs) ** 2)))

# ---------- 12D ----------
print("=" * 78)
print("12D d_tensor: associativity 依 metric 而異")
print("=" * 78)
v12 = np.array([phi ** (-k/12) for k in range(12)])
ones12 = np.ones(12)
Y12 = np.einsum("ijk,k->ij", d_native, v12); Y12 = (Y12 + Y12.T) / 2
G_ones = np.einsum("ijk,k->ij", d_native, ones12); G_ones = (G_ones + G_ones.T) / 2

cands12 = {
    "g = d·ones (p15 solver 定義)": G_ones,
    "g = Y = d·v12 (docs 慣用)": Y12,
    "g = identity": np.eye(12),
}
for name, g in cands12.items():
    mx, rms = wdvv_loss(d_native, g)
    print(f"  {name:32s} max={mx:.6e}  rms={rms:.6e}")

print("\n12D: g = d·ones 之特徵譜（係咪正定？）")
evg = np.linalg.eigvalsh(G_ones)
print("  eig(g_ones) =", np.round(evg, 5))
print("  min eig =", evg[0], "-> invertible:", evg[0] > 1e-12)

print("\n對照: 隨機對稱 d 嘅同 metric loss（空模型參考，唔係 threshold）")
rng = np.random.default_rng(7)
d_rand = rng.standard_normal((12,12,12)); d_rand = d_rand + d_rand.transpose(1,0,2)
g_rand = np.einsum("ijk,k->ij", d_rand, ones12); g_rand = (g_rand+g_rand.T)/2
mx, _ = wdvv_loss(d_rand, g_rand)
print(f"  random sym d: max={mx:.6e}")

# ---------- 36D ----------
print("\n" + "=" * 78)
print("36D kappa: associativity 依 metric 而異")
print("=" * 78)
ones36 = np.ones(36)
Y36 = np.einsum("ijk,k->ij", kappa, Jstar); Y36 = (Y36 + Y36.T) / 2
G36_ones = np.einsum("ijk,k->ij", kappa, ones36); G36_ones = (G36_ones + G36_ones.T) / 2
cands36 = {
    "g = κ·Jstar (Y_36)": Y36,
    "g = κ·ones(36)": G36_ones,
    "g = identity": np.eye(36),
}
for name, g in cands36.items():
    mx, rms = wdvv_loss(kappa, g)
    print(f"  {name:28s} max={mx:.6e}  rms={rms:.6e}")

print("\n36D: eig(g) 檢查")
for name, g in [("Y_36", Y36), ("κ·ones", G36_ones)]:
    ev = np.linalg.eigvalsh(g)
    print(f"  {name}: min eig={ev[0]:.4e}  max eig={ev[-1]:.4e}  n_neg={np.sum(ev < -1e-10)}")

# ---------- 12D 嵌入 36D ----------
print("\n" + "=" * 78)
print("12D 嵌入 36D（docs/14 主張）—— 用嵌入 metric 測 associativity")
print("=" * 78)
emb = np.zeros((36,36,36)); emb[:12,:12,:12] = d_native
# 嵌入 metric: 12D 用 Y12 / g_ones，24D 補 identity-block 定全零？
# 方案 A: 36D metric = κ·J*，但 12D 塊用 d 自己 metric —— 唔一致
# 方案 B: 36D metric 全用 κ·J*，睇 12D 子空間喺內積下 closure
G_full = Y36
mx, _ = wdvv_loss(emb, G_full)
print(f"  emb 用 g = Y_36 full: max={mx:.6e}")

# 嵌入後 G_emb = emb·ones36 —— 與 G_ones 12D 塊比較
G_emb = np.einsum("ijk,k->ij", emb, ones36); G_emb = (G_emb + G_emb.T) / 2
print("  G(emb·ones36)[:12,:12] 同比 G_ones:")
print("  max|G_emb[:12,:12] - G_ones| =", np.max(np.abs(G_emb[:12,:12] - G_ones)))
print("  max|G_emb[12:,:]|（cross） =", np.max(np.abs(G_emb[12:,:])))

# 24D cross 項: d 嵌入後 associativity 喺 12D 內外 flow
lhs = np.einsum("abp,pq,qcd->abcd", emb, np.linalg.inv(G_full), emb)
rhs = np.einsum("acp,pq,qbd->abcd", emb, np.linalg.inv(G_full), emb)
diff = np.abs(lhs - rhs)
print("  diff 中 12D×12D×12D×12D 塊 max =", diff[:12,:12,:12,:12].max())
print("  diff 含 24D 指標 max      =", diff[12:,:,:,:].max() if diff[12:].size else "n/a")

# ---------- d_tensor 其他版本 ----------
print("\n" + "=" * 78)
print("旁證: 其他 d_tensor 版本（wdvv_converged / final） associativity")
print("=" * 78)
for f in ["d_tensor_wdvv_converged.npy", "d_tensor_final.npy", "d_tensor_high_precision.npy"]:
    p = os.path.join(DATA, f)
    if not os.path.exists(p):
        continue
    d2 = np.load(p)
    if d2.shape != (12,12,12):
        # 可能係 12³ float64 包裝
        print(f"  {f}: shape {d2.shape}, skip")
        continue
    G2 = np.einsum("ijk,k->ij", d2, ones12); G2 = (G2 + G2.T) / 2
    mx, _ = wdvv_loss(d2, G2)
    print(f"  {f:34s} g=ones max={mx:.6e}")

print("\nDONE — probe 完（metric 選擇結論 → docs/17）")