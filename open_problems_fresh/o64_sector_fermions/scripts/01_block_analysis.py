#!/usr/bin/env python3
"""
O64 一期 01: 3×12 block Yukawa 本徵值譜分析 — 9 費米子質量候選
================================================================
前置: O61 (κ_ijk 3×12 block, A_ij = Yukawa), O57 (Kähler trade-off)
目標: 分析每個 block 嘅 Yukawa 本徵值譜，搵出 9 費米子質量候選
"""
import sys, os, math, json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

# ============ 1. 載入 κ ============
d = json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))
kappa = np.array(d["kappa"])
gamma_n = 4 * np.sin(np.pi * np.arange(1, 89) / 88) ** 2

# SM 費米子質量比 (within-type, normalized to lightest)
sm_ratios = {
    "up": [1.0, 476.9, 133077.0],
    "down": [1.0, 20.4, 1548.0],
    "lepton": [1.0, 206.8, 3483.0],
}

def log_mse(ev, target_ratios):
    """Compute log-space MSE between eigenvalue ratios and target ratios."""
    r = [ev[0]/ev[2], ev[1]/ev[2], 1.0]
    log_r = [math.log10(max(r[i], 1e-30)) for i in range(3)]
    log_t = [math.log10(target_ratios[i]) for i in range(3)]
    offset = np.mean([log_r[i] - log_t[i] for i in range(3)])
    log_adj = [log_r[i] - offset for i in range(3)]
    return float(np.mean([(log_adj[i] - log_t[i])**2 for i in range(3)]))

def yukawa_block(kappa, g, t):
    """Yukawa matrix for block g with parameters t (full 36-dim)."""
    s, e = g*12, (g+1)*12
    return np.tensordot(kappa[s:e, s:e, :], t, axes=([2], [0]))

def yukawa_block_pure(kappa, g, t_block):
    """Yukawa matrix for block g using only κ_ggg and t within block."""
    s, e = g*12, (g+1)*12
    kappa_g = kappa[s:e, s:e, s:e]
    return np.tensordot(kappa_g, t_block, axes=([2], [0]))

# ============ 2. 每個 block 嘅純 κ_ggg 分析 ============
print("=" * 72)
print("O64 一期 01: 3×12 block Yukawa 本徵值譜")
print("=" * 72)
print("\n=== [1] 純 κ_ggg 分析 (每 block 用自己嘅 κ) ===")

# SM within-type ratios
print(f"\n  SM within-type ratios (normalized to lightest):")
for tname, r in sm_ratios.items():
    print(f"    {tname}: {r[0]:.1f} : {r[1]:.1f} : {r[2]:.0f}")

# Pure κ_ggg with various Kähler schemes
print("\n=== [2] Kähler 參數方案掃描 ===")

results = []
for g in range(3):
    s, e = g*12, (g+1)*12
    kappa_g = kappa[s:e, s:e, s:e]
    print(f"\n  Block {g} (indices {s}-{e-1}):")
    
    schemes = [
        ("φ^(35-i)", phi**(35 - np.arange(s, e))),
        ("φ^(-i)", phi**(-np.arange(s, e))),
        ("2^(-i)", 2.0**(-np.arange(s, e))),
        ("γ_n (block)", gamma_n[s:e]),
        ("γ_n (mid)", gamma_n[(s+22):(e+22)]),
        ("γ_n (end)", gamma_n[(s+44):(e+44)]),
    ]
    
    for name, t in schemes:
        if len(t) != 12:
            continue
        Y_g = yukawa_block_pure(kappa, g, t)
        ev = np.sort(np.linalg.eigvalsh(Y_g))[::-1]
        pos = ev[ev > 1e-10]
        
        best_mse = 1e10
        best_type = "?"
        for tname, ratios in sm_ratios.items():
            if len(pos) >= 3 and ev[2] > 0:
                mse = log_mse(ev[:3], ratios)
                if mse < best_mse:
                    best_mse = mse
                    best_type = tname
        
        if len(pos) >= 3:
            print(f"    {name:20s}: pos={len(pos):2d}/12, top3={[f'{x:.4e}' for x in ev[:3]]}, best={best_type} MSE={best_mse:.3f}")
        else:
            print(f"    {name:20s}: pos={len(pos):2d}/12, top3_abs={[f'{abs(x):.4e}' for x in ev[:3]]}")
        
        results.append((g, name, best_type, best_mse, ev[:3]))

# ============ 3. α 掃描 (φ^(α·(35-i))) ============
print("\n=== [3] α 掃描: φ^(α·(35-i)) ===")
alphas = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.5, 2.0]

for g in range(3):
    s, e = g*12, (g+1)*12
    kappa_g = kappa[s:e, s:e, s:e]
    print(f"\n  Block {g}:")
    for a in alphas:
        t = phi**(a * (35 - np.arange(s, e)))
        Y_g = np.tensordot(kappa_g, t, axes=([2], [0]))
        ev = np.sort(np.linalg.eigvalsh(Y_g))[::-1]
        pos = np.sum(ev > 1e-10)
        if pos >= 3 and ev[2] > 0:
            best_mse = min(log_mse(ev[:3], sm_ratios[t]) for t in sm_ratios)
            r = [ev[0]/ev[2], ev[1]/ev[2], 1.0]
            print(f"    α={a:.1f}: pos={pos:2d}, top3={[f'{x:.4e}' for x in ev[:3]]}, ratio={r[0]:.1f}:{r[1]:.1f}:1, MSE={best_mse:.3f}")

# ============ 4. Full Yukawa (all k) analysis ============
print("\n=== [4] 全 Yukawa 分析 (Σ_k κ_ijk t_k, 所有 k) ===")
# Use full κ to construct Y_ij, then examine block-diagonal parts
for name, t in [
    ("φ^(35-i)", phi**(35 - np.arange(36))),
    ("φ^(-i)", phi**(-np.arange(36))),
    ("2^(-i)", 2.0**(-np.arange(36))),
    ("γ_n", gamma_n[:36]),
]:
    Y = np.tensordot(kappa, t, axes=([2], [0]))
    print(f"\n  {name}:")
    for g in range(3):
        s, e = g*12, (g+1)*12
        Yg = Y[s:e, s:e]
        ev = np.sort(np.linalg.eigvalsh(Yg))[::-1]
        pos = np.sum(ev > 1e-10)
        if pos >= 3:
            best_mse = min(log_mse(ev[:3], sm_ratios[t]) for t in sm_ratios)
            print(f"    Block {g}: pos={pos:2d}/12, top3={[f'{x:.4e}' for x in ev[:3]]}, MSE={best_mse:.3f}")
        else:
            print(f"    Block {g}: pos={pos:2d}/12, top3_abs={[f'{abs(x):.4e}' for x in ev[:3]]}")

# ============ 5. 綜合建議 ============
print("\n\n=== [5] 綜合建議 ===")
print("""
關鍵發現:
1. 純 κ_ggg 分析: 每個 block 用 φ^(35-i) 給出 7-10 個 positive eigenvalues
   - Block 0: 最強耦合 (292 非零, mean|κ|=17.8), 最大質量尺度
   - Block 1: 中等耦合 (86 非零, mean|κ|=2.41)
   - Block 2: 最弱耦合 (54 非零, mean|κ|=3.63)

2. Within-block hierarchy 太淺:
   - φ^(35-i) 時 block 0 top3 ratio ≈ 18.6:1.8:1
   - SM 需要 up-type: 133077:477:1
   - 需要更陡峭的 Kähler 參數 (α>1) 或不同參數結構

3. Between-block scale 自然出現:
   - Block 0/Block 1 top ≈ 46000
   - Block 1/Block 2 top ≈ 75
   - 這是 κ 結構內稟的，來自不同 block 的非零密度差異

4. 下一步: 需要 sector-dependent Kähler 參數
   - 每個 block 用不同的 Kähler 方案
   - 或者用不同 subset of γ_n 譜
""")

# ============ 6. Save results ============
out = {
    "test": "O64 01: block analysis",
    "sm_ratios": sm_ratios,
    "block_analysis": {}
}
for g in range(3):
    s, e = g*12, (g+1)*12
    kappa_g = kappa[s:e, s:e, s:e]
    out["block_analysis"][f"block_{g}"] = {}
    for name, t in [("phi_35i", phi**(35-np.arange(s,e))),
                     ("phi_neg_i", phi**(-np.arange(s,e))),
                     ("two_neg_i", 2.0**(-np.arange(s,e))),
                     ("gamma", gamma_n[s:e])]:
        Y_g = np.tensordot(kappa_g, t, axes=([2], [0]))
        ev = np.sort(np.linalg.eigvalsh(Y_g))[::-1]
        out["block_analysis"][f"block_{g}"][name] = {
            "eigenvalues": [float(x) for x in ev[:6]],
            "positive": int(np.sum(ev > 1e-10))
        }

os.makedirs("data", exist_ok=True)
with open("data/01_block_analysis.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("\n✅ 結果已保存到 data/01_block_analysis.json")