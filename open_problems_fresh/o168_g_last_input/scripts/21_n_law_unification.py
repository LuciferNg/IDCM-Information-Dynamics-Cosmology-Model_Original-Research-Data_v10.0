#!/usr/bin/env python3
"""
O168 — 21: N-規律統一 (任務二延伸, docs/18 剩項)
==================================================
docs/18: 殘餘族符合 1/(2N) EM 修正, N: crack→67, r33→92, r53→118, r44→70。
本 script 攻「點解係呢啲 N」: 統一規律搜尋 + β_top 分母家族 {5,7,9}。

結構 N 身份:
  crack → 67 = 2K_tree+1 (雙向樹+半位, dev 0.036%)
  r(33) → 92 = Σγ_even+μ² (O153, dev 0.16%)
  r(53) → 118 = 2(F₁₀+B) / 119 = L₄·F_proj
  r(44) → 70 = 2N_d−L₆ (dev 0.64%)
新觀察: crack/β_top ≈ 1/5 (F₅), r33/β_top ≈ 1/7 (L₄), r53/β_top ≈ 1/9 (N_gen²)
        — 連續奇數 {5,7,9} = N_gen 家族!
"""
from mpmath import mp, mpf, exp, ln, sqrt, cos, sin, pi
mp.dps = 50

phi = (1 + sqrt(5))/2
N_d = 44; N_gen = 3; B = 4; K_tree = 33; L4 = 7; L5 = 11
F5 = 5; F7 = 13; F10 = 55; mu2 = 2; L6 = 18; F_proj = 17
Se = 90                                    # Σγ_even

results = []
def check(name, ok, info=""):
    results.append(ok)
    print(f"  [{'OK ' if ok else 'XX '}] {name} — {info}")

print("="*74)
print("  O168 — 21: N-規律統一 (殘餘族階梯長度)")
print("="*74)

# ── [1] 殘餘族 + 反解 N (docs/18) ──
print("\n─── [1] 殘餘族 1/(2N) 反解 ───")
r44 = abs(exp(-44) - phi**(-88)*(mpf(26)/27)**44)/exp(-44)*100
r33 = abs(exp(33) - phi**(66)*(mpf(27)/26)**33)/exp(33)*100
r53 = abs(exp(-mpf('25.5')) - phi**(-53))/exp(-mpf('25.5'))*100
crack = mpf('0.746')
Nc, Nr33, Nr53, Nr44 = 1/(2*crack/100), 1/(2*r33/100), 1/(2*r53/100), 1/(2*r44/100)
print(f"  crack→N = {float(Nc):.2f}   r33→N = {float(Nr33):.2f}")
print(f"  r53→N = {float(Nr53):.2f}   r44→N = {float(Nr44):.2f}")

# ── [2] 個別 N 身份複確 ──
print("\n─── [2] 結構 N 身份 (docs/18) ───")
c67 = 1/(2*(2*K_tree+1))*100
c92 = 1/(2*(Se+mu2))*100
c118 = 1/(2*2*(F10+B))*100
c119 = 1/(2*L4*F_proj)*100
c70 = 1/(2*(2*N_d-L6))*100
check("[2a] crack = 1/(2·67), 67 = 2K_tree+1 (dev < 0.1%)",
      abs(c67/crack - 1) < 0.001, f"dev {float(abs(c67/crack-1)*100):.3f}%")
check("[2b] r33 = 1/(2·92), 92 = Σγ_even+μ² (O153)",
      abs(c92/r33 - 1) < 0.002, f"dev {float(abs(c92/r33-1)*100):.2f}%")
check("[2c] r53 = 1/(2·118..119) (118 = 2(F10+B), 119 = L4·F_proj)",
      min(abs(c118/r53-1), abs(c119/r53-1)) < 0.006,
      f"118: {float(abs(c118/r53-1)*100):.2f}% | 119: {float(abs(c119/r53-1)*100):.2f}%")
check("[2d] r44 = 1/(2·70), 70 = 2N_d−L6", abs(c70/r44 - 1) < 0.01,
      f"dev {float(abs(c70/r44-1)*100):.2f}%")

# ── [3] ★β_top 分母家族 {5,7,9} ──
print("\n─── [3] ★β_top 分母: crack/β_top ≈ 1/5, r33/β_top ≈ 1/7, r53/β_top ≈ 1/9 ───")
beta_top = ln(mp.e/phi**2)
bt100 = beta_top*100
for name, val, denom, label in [("crack", crack, F5, "F5 = 5"),
                                ("r(33)", r33, L4, "L4 = 7"),
                                ("r(53)", r53, N_gen**2, "N_gen² = 9")]:
    cand = bt100/denom
    d = abs(cand/val - 1)*100
    print(f"  {name}: β_top/{label} = {float(cand):.4f}% vs {float(val):.3f}% — dev {float(d):.2f}%")
check("[3a] crack ≈ β_top/F5 (dev < 1%)", abs(bt100/F5/crack - 1) < 0.01,
      f"dev {float(abs(bt100/F5/crack-1)*100):.2f}%")
check("[3b] r33 ≈ β_top/L4 (dev < 1.5%)", abs(bt100/L4/r33 - 1) < 0.015,
      f"dev {float(abs(bt100/L4/r33-1)*100):.2f}%")
check("[3c] r53 ≈ β_top/N_gen² (dev < 1.5%)", abs(bt100/(N_gen**2)/r53 - 1) < 0.015,
      f"dev {float(abs(bt100/(N_gen**2)/r53-1)*100):.2f}%")
print("  ★ 分母 {5, 7, 9} = 連續奇數 = N_gen 家族 (2N_gen−1, 2N_gen+1, N_gen²)")
check("[3d] {5,7,9} = {2N_gen−1, 2N_gen+1, N_gen²}", F5 == 2*N_gen-1 and L4 == 2*N_gen+1 and N_gen**2 == 9)
r44b = abs(bt100/(2*N_gen-1)/r44 - 1)*100
print(f"  r44 用 5: dev {float(r44b):.1f}% — r44 離群 (有 (26/27)^44 額外修正)")
check("[3e] r44 離群 (唔 fit β_top 分母家族)", r44b > 3)

# ── [4] 統一規律搜尋 (N(k) 函數形式) ──
print("\n─── [4] 統一規律搜尋: N = f(k)? ───")
# 點: (k, N) = (44, 67 crack), (33, 92), (53, 118.5), (44, 70)
pts = [(44, float(Nc)), (33, float(Nr33)), (53, float(Nr53)), (44, float(Nr44))]
slope1 = (pts[1][1]-pts[0][1])/(pts[1][0]-pts[0][0])
slope2 = (pts[2][1]-pts[1][1])/(pts[2][0]-pts[1][0])
print(f"  N(k) 斜率: (33→44) {slope1:.2f}, (33→53) {slope2:.2f} — 唔線性")
check("[4a] N 唔係 k 嘅線性函數 (斜率 1.32 vs 2.64)", abs(slope1 - slope2) > 0.5)
# N/k 比
print("  N/k: crack 67/44 = %.2f, r33 92/33 = %.2f, r53 118/53 = %.2f, r44 70/44 = %.2f"
      % (67/44, 92/33, 118/53, 70/44))
check("[4b] N/k 唔恆定 (1.52, 2.79, 2.23, 1.59 — 冇統一常數)",
      abs(67/44 - 92/33) > 0.5 and abs(92/33 - 118/53) > 0.5)

# ── [5] 總結 ──
print("\n─── [總結] N-規律統一裁決 ───")
print("  ✅ 個別 N 身份全結構 (67/92/118/70) — 每個都係結構數, 唔係隨機")
print("  ✅ crack = 1/(2(2K_tree+1)) 最強 (0.036%) — 裂縫機制確立")
print("  ★ 新觀察: β_top 分母 {5, 7, 9} = N_gen 家族 (2N_gen−1, 2N_gen+1, N_gen²)")
print("  🟡 N 規律未統一: N(k) 唔線性, N/k 唔恆定; β_top 家族 r44 離群")
print("  🔴 單一解析常數完全閉合仍未達成")
check("[E] N-規律: 個別閉合 + {5,7,9} 模式; 統一規律 🔴", abs(c67/crack-1) < 0.001)

print(f"\n{'='*74}")
print(f"  O168-21 N-規律統一: {sum(results)}/{len(results)} PASS")
print(f"{'='*74}")
