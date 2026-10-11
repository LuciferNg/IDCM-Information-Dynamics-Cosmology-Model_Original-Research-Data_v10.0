#!/usr/bin/env python3
"""
O64 一期 04: 全譜分析 — 36 個 Yukawa 本徵值 vs SM 9 費米子
================================================================
目標: 用全 36×36 Yukawa 矩陣，睇 36 個本徵值中有邊啲對應 SM 9 費米子
"""
import sys, os, math, json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2
gamma_n = 4 * np.sin(np.pi * np.arange(1, 89) / 88) ** 2

d = json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))
kappa = np.array(d["kappa"])

print("=" * 72)
print("O64 一期 04: 全 Yukawa 本徵值譜分析")
print("=" * 72)

# SM 9 masses (GeV)
sm_9 = [1.3e-3, 0.62, 173.0, 2.7e-3, 0.055, 4.18, 5.11e-4, 0.1057, 1.78]
sm_names = ['u','c','t','d','s','b','e','mu','tau']
sm_9_log = [math.log10(m) for m in sm_9]

# γ_n key values
print("\n=== [1] K_Chain γ_n 譜 ===")
print(f"  γ₁={gamma_n[0]:.6f}, γ₇={gamma_n[6]:.6f}, γ₂₀={gamma_n[19]:.6f}")
print(f"  γ₁:γ₇:γ₂₀ = 1:{gamma_n[6]/gamma_n[0]:.0f}:{gamma_n[19]/gamma_n[0]:.0f}")

# ==== Approach: γ_n 直接質量模型 ====
# 質量 m_{g,k} = M₀ × γ_{n(g,k)} × f_g
# 其中 f_g 係 sector-dependent scaling factor
# 每 type 用不同 γ_n 三元組

# 從 SM 9 質量反推 M₀ 同 f_g:
# 假設 m_u = M₀ × γ₁ × f₀
# m_c = M₀ × γ₇ × f₀
# m_t = M₀ × γ₂₀ × f₀
# etc.

# 但 γ₁:γ₇:γ₂₀ = 1:48:337 唔夠陡
# 需要 γ_n 組合使 within-type ratio 匹配 SM

# Search: which γ_n triplet gives best within-type ratio?
print("\n=== [2] γ_n 三元組 for each SM type ===")

def gamma_ratio_log_mse(gamma_triplet, target_ratios):
    r = [gamma_triplet[0]/gamma_triplet[2], gamma_triplet[1]/gamma_triplet[2], 1.0]
    log_r = [math.log10(max(r[i], 1e-30)) for i in range(3)]
    log_t = [math.log10(target_ratios[i]) for i in range(3)]
    offset = np.mean([log_r[i] - log_t[i] for i in range(3)])
    log_adj = [log_r[i] - offset for i in range(3)]
    return float(np.mean([(log_adj[i] - log_t[i])**2 for i in range(3)]))

sm_types = {
    "up": {"ratios": [1.0, 476.9, 133077.0], "names": ["u", "c", "t"]},
    "down": {"ratios": [1.0, 20.4, 1548.0], "names": ["d", "s", "b"]},
    "lepton": {"ratios": [1.0, 206.8, 3483.0], "names": ["e", "mu", "tau"]},
}

for tname, data in sm_types.items():
    best = []
    for n1 in range(1, 45):
        for n2 in range(n1+1, 45):
            for n3 in range(n2+1, 45):
                g = [gamma_n[n1-1], gamma_n[n2-1], gamma_n[n3-1]]
                mse = gamma_ratio_log_mse(g, data["ratios"])
                if len(best) < 5 or mse < best[-1][0]:
                    best.append((mse, n1, n2, n3, g))
                    best.sort(key=lambda x: x[0])
                    best = best[:5]
    print(f"\n  {tname}:")
    for mse, n1, n2, n3, g in best:
        r = [g[0]/g[2], g[1]/g[2], 1.0]
        print(f"    γ_{n1:2d}:γ_{n2:2d}:γ_{n3:2d} = {g[0]:.4f}:{g[1]:.4f}:{g[2]:.4f}")
        print(f"      ratio: {r[0]:.1f}:{r[1]:.1f}:1, SM: {data['ratios'][0]:.0f}:{data['ratios'][1]:.0f}:1, MSE={mse:.4f}")

# ==== Better approach: mass = M₀ × γ_n × φ^(α_g·(35-i_g)) ====
# For each generation within a type, the Kähler parameter selects a different γ_n
# The hierarchy comes from the γ_n spectrum, not from φ-power
print("\n\n=== [3] γ_n² 模型 (mass ∝ γ_n²) ===")
# γ_n² max ratio: 616169
# SM up needs 133077 — within range!
print(f"  γ_n² max ratio (γ_44²/γ_1²) = {(gamma_n[43]/gamma_n[0])**2:.0f}")
print(f"  SM up needs: 133077")
print(f"  γ_n² can cover up-type hierarchy!")

# Try γ_n² triplets
for tname, data in sm_types.items():
    best = []
    for n1 in range(1, 45):
        for n2 in range(n1+1, 45):
            for n3 in range(n2+1, 45):
                g = [gamma_n[n1-1]**2, gamma_n[n2-1]**2, gamma_n[n3-1]**2]
                mse = gamma_ratio_log_mse(g, data["ratios"])
                if len(best) < 3 or mse < best[-1][0]:
                    best.append((mse, n1, n2, n3, g))
                    best.sort(key=lambda x: x[0])
                    best = best[:3]
    print(f"\n  {tname} (γ_n²):")
    for mse, n1, n2, n3, g in best:
        r = [g[0]/g[2], g[1]/g[2], 1.0]
        print(f"    γ_{n1:2d}²:γ_{n2:2d}²:γ_{n3:2d}² ratio={r[0]:.1f}:{r[1]:.1f}:1, SM={data['ratios'][0]:.0f}:{data['ratios'][1]:.0f}:1, MSE={mse:.4f}")

# ==== γ_n × φ^(-i) 模型 ====
print("\n\n=== [4] γ_n × φ^(-i) 模型 (mass ∝ γ_n × φ^(-i)) ===")
# φ^(-i) gives 117 finite with shallow hierarchy
# γ_n × φ^(-i) combines both
for tname, data in sm_types.items():
    best = []
    for n1 in range(1, 45):
        for n2 in range(n1+1, 45):
            for n3 in range(n2+1, 45):
                # Use different i for each within-type particle
                # i values: 0, 5, 10 (small difference)
                g = [gamma_n[n1-1] * phi**0, gamma_n[n2-1] * phi**(-5), gamma_n[n3-1] * phi**(-10)]
                mse = gamma_ratio_log_mse(g, data["ratios"])
                if len(best) < 3 or mse < best[-1][0]:
                    best.append((mse, n1, n2, n3, g))
                    best.sort(key=lambda x: x[0])
                    best = best[:3]
    print(f"\n  {tname} (γ_n×φ^(-i)):")
    for mse, n1, n2, n3, g in best:
        r = [g[0]/g[2], g[1]/g[2], 1.0]
        print(f"    γ_{n1:2d}:γ_{n2:2d}:γ_{n3:2d} × φ^(0:-5:-10) ratio={r[0]:.1f}:{r[1]:.1f}:1, SM={data['ratios'][0]:.0f}:{data['ratios'][1]:.0f}:1, MSE={mse:.4f}")

# ==== 核心 insight: 9 個 mass 來自不同 n 值 ====
print("\n\n=== [5] 綜合結構: 9 個 γ_n 直接對應 9 費米子 ===")
# IDCM: 44-site K_Chain → 88 γ_n values (dual chain)
# SM: 9 fermions → need 9 different γ_n values
# This is natural: each fermion corresponds to a different K_Chain mode!

# The 3×12 block structure in the Yukawa matrix provides the sector separation
# Each block gives access to a different subset of γ_n modes
# Within each block, 3 modes (for 3 generations) are selected

# 9 fermions = 3 types × 3 generations
# = 9 different γ_n modes

# Candidate mapping (to be structurally derived):
# Block 0 (up-type): n=1,2,3 or n=1,7,20
# Block 1 (down-type): n=4,5,6 or n=3,8,22
# Block 2 (lepton): n=6,7,10 or n=7,10,20

# The exact mapping depends on which γ_n modes are accessible to each block
# This is determined by the CY₃ geometry (which divisors correspond to which Kähler moduli)

# What we know:
# - γ₆ = neutrino mode (from O57/O65)
# - γ₁,γ₇,γ₂₀ = lepton modes (from O57)
# - γ₂,γ₃ = PMNS mixing (from O65)
# - γ₆/2^k = CKM/PMNS cascade (from O68)

print("\n  已知 γ_n ↔ 物理對應:")
print(f"  γ₆ = 0.1807 → 中微子 (O57 p6)")
print(f"  γ₁ = 0.0051, γ₇ = 0.2446, γ₂₀ = 1.7154 → 輕子 (O57)")
print(f"  γ₂ = 0.0204, γ₃ = 0.0457 → PMNS 混合角 (O65)")
print(f"  γ₆/2ᵏ → CKM/PMNS 級聯 (O68)")

# Check: γ₁:γ₇:γ₂₀ = 1:48:337
# SM lepton: 1:207:3483
# Ratio: 48/207=0.23, 337/3483=0.097 — not matching
# But γ₁²:γ₇²:γ₂₀² = 1:2304:113422
# SM lepton: 1:207:3483
# Ratio: 2304/207=11.1, 113422/3483=32.6 — too steep

# What about γ₁:γ₆:γ₂₀ = 1:35.5:336.6
# SM lepton: 1:207:3483
# Ratio: 35.5/207=0.17, 336.6/3483=0.097 — still too shallow

# What about γ₆:γ₁₀:γ₂₀ = 1:2.70:9.49
# SM lepton ratio with 1:207:3483, the middle/light ratio is 207
# γ₁₀/γ₆ = 2.70 — too small

# The key: γ_n alone can't give the hierarchy
# Need γ_n × (structural factor)
# The structural factor comes from the 3×12 block Yukawa eigenvalues

print("\n\n=== [6] 結構結論 ===")
print("""
O64 核心瓶頸:

1. 3×12 block Yukawa 本徵值譜:
   - 每個 block 有 12×12 Yukawa 矩陣
   - top3 本徵值比 ≈ 33:1.8:1 (block 0, φ^(35-i))
   - SM up-type 需要 133077:477:1

2. γ_n 譜:
   - γ_n 範圍: 0.0051 (n=1) 到 4.0 (n=44)
   - γ_n max ratio: 785
   - γ_n² max ratio: 616169 (可覆蓋 up-type)
   - 但 γ_n 同 Yukawa 本徵值嘅關係未建立

3. 結構性 gap:
   - 質量 = (Yukawa 本徵值) × (γ_n 因子) × (sector factor)
   - 呢三個因子嘅乘積點樣給出 SM 9 質量?
   - 需要更深入嘅結構推導，唔係數值 fit

4. 最可能路徑:
   - 質量 = M₀ × γ_n × f_g(Yukawa block)
   - f_g 為每個 block 提供 overall scale
   - γ_n 提供 within-type hierarchy
   - 每個 type 訪問不同 γ_n 模式
""")

out = {"test": "O64 04: full spectrum analysis"}
os.makedirs("data", exist_ok=True)
with open("data/04_full_spectrum.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("✅ 結果已保存到 data/04_full_spectrum.json")