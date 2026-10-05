#!/usr/bin/env python3
"""
O137 — Phase 1: CY₃ 同調特徵值 vs K_Chain 本徵諧振
====================================================
核心方程 (roadmap 項目 C):
  Y_ab = Σ_c κ_abc · v_c   (CY₃ 同調算子, v = Kähler VEV)
  γ_n = 4sin²(nπ/88)       (K_Chain 本徵值)

共振條件: γ_n ≈ λ_α (Y 嘅特徵值) → 模式 n 係 CY₃ 嘅本徵諧振
"""
import math, json, os
import numpy as np

phi = (1 + math.sqrt(5)) / 2
Nd = 44
M0 = 27.900915

gamma = np.array([4 * math.sin(math.pi * n / 88)**2 for n in range(1, Nd+1)])
omega = np.array([2 * math.sin(math.pi * n / 88) for n in range(1, Nd+1)])

data_dir = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o53_cy3_reality/data/polytopes"
kappa = np.array(json.load(open(f"{data_dir}/cy36_98_intersection_full.json"))['kappa'])

LEPTONS = [1, 7, 20]
QUARKS = [14, 33, 34]

print("=" * 72)
print("O137 Phase 1: CY₃ 同調特徵值 vs K_Chain")
print("=" * 72)

# ============================================================
# 1. 各種 VEV 下嘅 Y = κ·v 特徵譜
# ============================================================
print("\n[1] Y = κ·v 特徵值 (多種 v)")

def y_eigenvalues(v):
    """Y_ab = Σ_c κ_abc·v_c, 返回特徵值 (sorted desc)"""
    Y = np.einsum('abc,c->ab', kappa, v)
    evals = np.linalg.eigvalsh(Y)
    return np.sort(evals)[::-1]

def v_phi_power(k_max=35):
    return np.array([phi ** (k_max - i) for i in range(36)])

def v_phi_inv():
    return np.array([phi ** (-i) for i in range(36)])

def v_ones():
    return np.ones(36)

def v_kchain():
    """v = γ_n 前 36 個 (K_Chain 本徵值做 VEV)"""
    return gamma[:36].copy()

vevs = {
    "φ^(35−i)": v_phi_power(),
    "φ^(−i)": v_phi_inv(),
    "ones": v_ones(),
    "γ_n (K_Chain)": v_kchain(),
}

for name, v in vevs.items():
    evals = y_eigenvalues(v)
    print(f"\n  v = {name}:")
    print(f"    特徵值 (前12): {evals[:12]}")
    print(f"    特徵值 (後6): {evals[-6:]}")
    print(f"    正數: {np.sum(evals > 0)}/{len(evals)}, tr = {evals.sum():.4f}")

# ============================================================
# 2. 共振匹配: γ_n vs 特徵值
# ============================================================
print("\n" + "=" * 72)
print("[2] 共振匹配: γ_n ≈ λ_α")
print("=" * 72)

def match_gamma_to_evals(evals, tol=0.05):
    """搵 γ_n 匹配特徵值 λ_α (相對誤差 < tol)"""
    matches = []
    for n in range(1, Nd+1):
        g = gamma[n-1]
        # 找最接近的特徵值
        idx = np.argmin(np.abs(evals - g))
        lam = evals[idx]
        rel = abs(g - lam) / max(abs(lam), 1e-10)
        if rel < tol and lam > 0:
            matches.append((n, lam, rel))
    return matches

for name, v in vevs.items():
    evals = y_eigenvalues(v)
    matches = match_gamma_to_evals(evals)
    print(f"\n  v = {name}: γ_n 匹配特徵值 (tol 5%):")
    for n, lam, rel in matches:
        marker = "★" if n in LEPTONS else ("☆" if n in QUARKS else "")
        print(f"    n={n:2d}{marker}: γ_n = {gamma[n-1]:8.6f} vs λ = {lam:8.6f} (rel {rel*100:.2f}%)")

# ============================================================
# 3. 12×12 WDVV d_tensor (如果存在)
# ============================================================
print("\n" + "=" * 72)
print("[3] WDVV d_tensor 特徵值")
print("=" * 72)

dtensor_path = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/data/d_tensor_final.npy"
if not os.path.exists(dtensor_path):
    # 試其他位置
    for cand in [
        "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/data/d_tensor_final.npy",
        "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/data/d_tensor_positive.npy",
    ]:
        if os.path.exists(cand):
            dtensor_path = cand
            break

if os.path.exists(dtensor_path):
    d = np.load(dtensor_path)
    print(f"  d_tensor: {d.shape}")
    if d.ndim == 3 and d.shape[0] == 12:
        # Y = d·v with v = φ^(−k/12)
        v12 = np.array([phi ** (-k/12) for k in range(12)])
        Y12 = np.einsum('abc,c->ab', d, v12)
        ev12 = np.sort(np.linalg.eigvalsh(Y12))[::-1]
        print(f"  Y12 特徵值: {ev12}")
        print(f"  tr(Y12) = {np.trace(Y12):.6f} (66 = 0.54% closure 候選)")
        # 匹配 γ_n
        matches12 = match_gamma_to_evals(ev12, tol=0.10)
        print(f"  γ_n 匹配 (tol 10%):")
        for n, lam, rel in matches12:
            marker = "★" if n in LEPTONS else ("☆" if n in QUARKS else "")
            print(f"    n={n:2d}{marker}: γ_n = {gamma[n-1]:8.6f} vs λ = {lam:8.6f} (rel {rel*100:.2f}%)")
else:
    print("  d_tensor_final.npy 唔存在, 跳過")

# ============================================================
# 4. ω_n 匹配 (拍頻 vs 特徵值)
# ============================================================
print("\n" + "=" * 72)
print("[4] ω_n 匹配特徵值")
print("=" * 72)

for name, v in vevs.items():
    evals = y_eigenvalues(v)
    matches = []
    for n in range(1, Nd+1):
        w = omega[n-1]
        idx = np.argmin(np.abs(evals - w))
        lam = evals[idx]
        rel = abs(w - lam) / max(abs(lam), 1e-10)
        if rel < 0.05 and lam > 0:
            matches.append((n, lam, rel))
    print(f"\n  v = {name}: ω_n 匹配特徵值 (tol 5%):")
    for n, lam, rel in matches:
        marker = "★" if n in LEPTONS else ("☆" if n in QUARKS else "")
        print(f"    n={n:2d}{marker}: ω_n = {omega[n-1]:8.6f} vs λ = {lam:8.6f} (rel {rel*100:.2f}%)")

# ============================================================
# 5. 完整譜: 全部 36 特徵值 vs 全部 44 γ_n
# ============================================================
print("\n" + "=" * 72)
print("[5] 特徵值流 vs γ_n 譜 (完整)")
print("=" * 72)

for name, v in vevs.items():
    evals = y_eigenvalues(v)
    print(f"\n  v = {name} — 特徵值 (全 36):")
    for i, lam in enumerate(evals):
        print(f"    λ_{i+1:2d} = {lam:12.6f}")

# ============================================================
# 6. 保存
# ============================================================
results = {
    "test": "O137 Phase 1: 同調特徵值共振",
    "gamma": gamma.tolist(),
    "evals_phi_power": y_eigenvalues(vevs["φ^(35−i)"]).tolist(),
    "evals_ones": y_eigenvalues(vevs["ones"]).tolist(),
}
with open("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o137_cy3_topological_resonance/data/02_homology_eigenvalues.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\n結果已保存 data/02_homology_eigenvalues.json")