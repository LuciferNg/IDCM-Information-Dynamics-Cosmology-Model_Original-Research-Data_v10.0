#!/usr/bin/env python3
"""
O136 — Script 43: 觀察者反作用 — φ² 指數的零參數檢驗
================================================================
Script 41/42 發現:
  位置算子 = 精確 Z₂-奇耦合 (⟨n|x|m⟩ = 0 for |n−m| 偶)
  二階自能 Δm_n = Σ|V_nm|²/(E_n−E_m): 擬合 RMS = 0.5873 (最佳)
  ★ 擬合冪次 α = 2.63344 ≈ φ² = 2.618034 (0.59%!)
  ★ 最佳配對反轉: t↔1, b↔2, τ↔3, c↔4, μ↔5, s↔7, d↔9, u↔11, e↔13

本 script: 用 α = φ² 精確值 (零參數) 檢驗
"""
import numpy as np, math, json, itertools
from pathlib import Path

OUT = Path(__file__).parent.parent / "data"
phi = (1+math.sqrt(5))/2
ph2 = phi**2
mass = {"e":0.510999,"mu":105.6584,"tau":1776.86,
        "u":2.16,"d":4.67,"s":93.4,"c":1270.0,"b":4180.0,"t":172690.0}
M9 = [1,2,3,4,5,7,9,11,13]
sp = sorted(mass, key=lambda p: mass[p])
LM = np.array([math.log(mass[p]) for p in sp])

print("=" * 94)
print("O136 Script 43: 觀察者反作用 — φ² 指數零參數檢驗")
print("=" * 94)

# ═══ 重建 44-鏈 + 位置算子 ═══════════════════════════
Nc = 44
x = np.arange(1, Nc+1, dtype=float)
Psi = np.zeros((Nc, Nc))
for n in range(1, Nc+1):
    Psi[:, n-1] = np.sin(n*math.pi*x/(Nc+1))
for n in range(Nc):
    Psi[:, n] /= np.linalg.norm(Psi[:, n])
V = Psi.T @ np.diag(x - x.mean()) @ Psi
E = np.array([4*math.sin(n*math.pi/88)**2 for n in range(1, 45)])

print(f"\n{'─'*94}")
print("1. Z₂-奇性驗證")
print(f"{'─'*94}")
same = max(abs(V[n,m]) for n in range(44) for m in range(44) if n!=m and (n-m)%2==0)
opp  = max(abs(V[n,m]) for n in range(44) for m in range(44) if (n-m)%2==1)
print(f"  max|V_nm| (|n−m| 偶) = {same:.3e}  → 應 ≈ 0  {'✅' if same<1e-10 else '🔴'}")
print(f"  max|V_nm| (|n−m| 奇) = {opp:.3e}  → 非零  {'✅' if opp>1 else '🔴'}")
print(f"  ★ 位置算子 = 精確 Z₂-奇 (世界↔觀察者) 耦合")

# ═══ 二階自能 ═══════════════════════════════════════
SE2 = {}
for n in M9:
    tot = 0.0
    for m in range(44):
        if m == n-1 or (m-(n-1)) % 2 == 0: continue
        dE = E[n-1] - E[m]
        if abs(dE) < 1e-12: continue
        tot += V[n-1, m]**2 / dE
    SE2[n] = tot

print(f"\n{'─'*94}")
print("2. 二階自能 Δm_n = Σ_m |V_nm|²/(E_n−E_m)")
print(f"{'─'*94}")
print(f"\n{'n':>3} {'γ_n':>12} {'Δm_n':>16} {'|Δm_n|':>16}")
print("-" * 50)
for n in M9:
    print(f"{n:>3} {E[n-1]:>12.6f} {SE2[n]:>16.6f} {abs(SE2[n]):>16.6f}")

# ═══ φ² 零參數檢驗 ══════════════════════════════════
print(f"\n{'─'*94}")
print("3. ★★ α = φ² 零參數檢驗")
print(f"{'─'*94}")

X = np.log(np.array([abs(SE2[n]) for n in M9]))
rev = list(range(8, -1, -1))

print(f"\n{'α':>14} {'配對':>10} {'RMS':>10} {'判定':>8}")
print("-" * 46)
for name, al in [("φ² = 2.618034", ph2), ("擬合 2.63344", 2.63344),
                 ("φ = 1.618034", phi), ("e = 2.71828", math.e), ("3.0", 3.0)]:
    for lbl, order in [("反轉", rev), ("正向", list(range(9)))]:
        Xp = X[order]
        A = np.vstack([np.ones(9), Xp]).T
        c, *_ = np.linalg.lstsq(A, LM, rcond=None)
        rms = float(np.sqrt(np.mean((A@c-LM)**2)))
        # fixed exponent
        pred = LM.mean() + al*(Xp - Xp.mean())
        rmsf = float(np.sqrt(np.mean((pred-LM)**2)))
        v = '🟢' if rmsf < 0.3 else ('🟡' if rmsf < 0.8 else '🔴')
        print(f"{name:>14} {lbl:>10} {rmsf:>10.4f} {v:>8}")

# 詳細表
Xp = X[rev]
c0 = LM.mean() - ph2*Xp.mean()
print(f"\n{'─'*94}")
print("4. 詳細表: α = φ² 固定, 反轉配對")
print(f"{'─'*94}")
print(f"\n{'粒子':>6} {'模式 n':>7} {'|Δm_n|':>14} {'pred ln m':>12} {'實際 ln m':>12} {'誤差':>10}")
print("-" * 68)
for i, p in enumerate(sp):
    n = M9[rev[i]]
    pred = c0 + ph2*Xp[i]
    print(f"{p:>6} {n:>7} {abs(SE2[n]):>14.6f} {pred:>12.4f} {LM[i]:>12.4f} {100*(math.exp(pred-LM[i])-1):>9.2f}%")

rms_fixed = math.sqrt(float(np.mean((c0 + ph2*Xp - LM)**2)))
print(f"\n★ RMS (α=φ² 固定, 零參數指數) = {rms_fixed:.4f}")
print(f"★ RMS (α 擬合 2.63344)        = 0.5873")
print(f"★ RMS (sin 譜)                = 1.1178")
print(f"★ 無解釋上限                  = {LM.std():.4f}")
print(f"\n→ 典型誤差 = e^{rms_fixed:.3f} = {math.exp(rms_fixed):.2f}×")

# ═══ 質量標度 ═══════════════════════════════════════
print(f"\n{'─'*94}")
print("5. 質量標度常數")
print(f"{'─'*94}")
C = math.exp(c0)
print(f"\nm_n = C · |Δm_n|^{{φ²}}")
print(f"  C = exp({c0:.6f}) = {C:.6e} MeV")
print(f"  (對照 M₀ = 27.900915 MeV)")

# ═══ 保存 ═══════════════════════════════════════════
with open(OUT/"43_phi2_exponent_test.json", "w") as f:
    json.dump({
        "z2_odd_check": {"same_parity_max": same, "opp_parity_max": opp},
        "self_energies": {str(n): SE2[n] for n in M9},
        "alpha_phi2": {"value": ph2, "rms_fixed": rms_fixed, "C": C},
        "pairing": {p: M9[rev[i]] for i, p in enumerate(sp)},
        "reference": {"sin_rms": 1.1178, "fitted_alpha": 2.63344,
                      "fitted_rms": 0.5873, "upper_bound": float(LM.std())},
    }, f, indent=2, ensure_ascii=False)
print(f"\n✅ 結果已寫入 data/43_phi2_exponent_test.json")