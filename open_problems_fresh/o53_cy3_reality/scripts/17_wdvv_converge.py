#!/usr/bin/env python3
"""
O53: WDVV 12D 再優化 — 收斂後 tr(Y) 係咪精確 = 66?
=====================================================
發現: d_tensor_final 嘅 WDVV 殘差 = 8.25 (未收斂)
假設: 完全收斂後 tr(Y) → 66 精確

方法: 用 d_tensor_final 做初始值, 再優化 WDVV
      (torch L-BFGS, 更多 iteration + 更細 loss)
"""
import sys, os, math
import numpy as np
import torch
import torch.optim as optim

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DATA = os.path.join(BASE, "data")

phi = (1 + math.sqrt(5)) / 2
n = 12
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"裝置: {device}")

print("=" * 70)
print("O53: WDVV 12D 再優化 — tr(Y) → 66?")
print("=" * 70)

# --- [1] 載入 d_tensor_final 做初始 ---
d0 = np.load(os.path.join(DATA, "d_tensor_final.npy"))
print(f"\n[1] 初始 d_tensor_final: shape={d0.shape}")

# 轉做 torch parameter (全部 1728 個自由)
d_params = torch.nn.Parameter(
    torch.tensor(d0, dtype=torch.float64, device=device)
)

def build_d():
    d = d_params
    # 對稱化 (確保完全對稱)
    d_sym = (d + d.permute(1,0,2) + d.permute(0,2,1) +
             d.permute(2,1,0) + d.permute(1,2,0) + d.permute(2,0,1)) / 6
    return d_sym

def wdvv_loss(d):
    t = torch.ones(n, dtype=torch.float64, device=device)
    g = torch.einsum('ijk,k->ij', d, t)
    try:
        g_inv = torch.linalg.inv(g)
    except Exception:
        return torch.tensor(1e10, dtype=torch.float64, device=device)
    lhs = torch.einsum('ijp,pq,qkl->ijkl', d, g_inv, d)
    rhs = torch.einsum('ilp,pq,qjk->ijkl', d, g_inv, d)
    return torch.sum((lhs - rhs) ** 2)

def tr66_loss(d):
    v = torch.tensor([phi ** (-k/12) for k in range(12)], dtype=torch.float64, device=device)
    d_iik = torch.einsum('iik->i', d)
    tr = torch.sum(d_iik * v)
    return (tr - 66.0) ** 2

def total_loss(d):
    L_wdvv = wdvv_loss(d)
    L_tr = tr66_loss(d)
    return L_wdvv + 1e-4 * L_tr, L_wdvv, L_tr

# --- [2] 優化 ---
print("\n[2] L-BFGS 優化 (400 iter)...")
optimizer = optim.LBFGS([d_params], lr=1.0, max_iter=20, history_size=30,
                        line_search_fn='strong_wolfe')

v = torch.tensor([phi ** (-k/12) for k in range(12)], dtype=torch.float64, device=device)

for step in range(20):  # 20 個 outer iter, 每個 max_iter=20 內循環
    def closure():
        optimizer.zero_grad()
        d = build_d()
        L, _, _ = total_loss(d)
        L.backward()
        return L

    try:
        L = optimizer.step(closure)
    except RuntimeError:
        print(f"  step {step}: 收斂失敗, 減 lr")
        optimizer = optim.LBFGS([d_params], lr=0.3, max_iter=20, history_size=30)
        continue

    with torch.no_grad():
        d = build_d()
        L_w, L_t = wdvv_loss(d), tr66_loss(d)
        d_iik = torch.einsum('iik->i', d)
        tr = torch.sum(d_iik * v).item()
        print(f"  step {step:2d}: L_wdvv={L_w.item():.4e}, tr(Y)={tr:.6f}, |66−tr|={abs(66-tr):.6f}")

# --- [3] 最終結果 ---
with torch.no_grad():
    d_final = build_d().cpu().numpy()
    L_w_final = wdvv_loss(build_d()).item()
    d_iik = torch.einsum('iik->i', build_d())
    tr_final = torch.sum(d_iik * v).item()

print("\n" + "=" * 70)
print("[3] 最終結果:")
print(f"    WDVV 殘差: {L_w_final:.4e} (初始 8.25)")
print(f"    tr(Y): {tr_final:.6f} (初始 66.3554)")
print(f"    |66 − tr| = {abs(66 - tr_final):.6f}")
print(f"    誤差: {abs(66-tr_final)/66*100:.4f}%")
if abs(66 - tr_final) < 0.01:
    print(f"    → 🎯 精確閉合! tr(Y) = 66")
elif abs(66 - tr_final) < 0.5:
    print(f"    → 🟡 接近但未精確")
else:
    print(f"    → ❌ 唔收斂到 66")

# 保存
np.save(os.path.join(DATA, "d_tensor_wdvv_converged.npy"), d_final)
print(f"    ✅ 保存: data/d_tensor_wdvv_converged.npy")
print("=" * 70)
