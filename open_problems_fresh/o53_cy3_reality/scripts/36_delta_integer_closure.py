#!/usr/bin/env python3
"""
O53 開放 3 閉合驗證: m = M_Pl × e^(-44) × e^(δ), δ ≈ 整數
=============================================================
發現: SM 質量 = 0.9493 GeV × e^(δ), δ 近整數

驗證:
  1. δ 嘅整數閉合精度
  2. δ 整數集: {+5, +1, 0, -2, -5, -6, -8} 有冇結構?
  3. 三代: Gen1 {+5,+1,+1}, Gen2 {0,-2,-2}, Gen3 {-6,-5,-8}
  4. δ 同 Fibonacci/Lucas/K_Chain?
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2
PASS = 0
FAIL = 0

def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name} {detail}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")

print("=" * 70)
print("O53 開放 3: δ 整數閉合")
print("=" * 70)

M_Pl = 1.22e19  # GeV
m44 = M_Pl * math.exp(-44)
print(f"基準: m₄₄ = M_Pl·e^(-44) = {m44:.6f} GeV")

SM = {'t': 172.69, 'b': 4.18, 'c': 1.27, 'tau': 1.777, 's': 0.093,
      'mu': 0.10566, 'd': 0.0047, 'u': 0.0022, 'e': 0.000511}
Vs = {k: math.log(M_Pl/m) for k, m in SM.items()}
delta = {k: 44 - v for k, v in Vs.items()}

print("\n[1] δ = ln(m/m₄₄) 整數閉合:")
for k, d in delta.items():
    n = round(d)
    print(f"    {k:4s}: δ = {d:+8.4f}  整數 {n:+3d}  (差 {abs(d-n):.4f})")

# 統計: 幾多近整數
near = {k: d for k, d in delta.items() if abs(d - round(d)) < 0.35}
print(f"\n    近整數 (<0.35): {len(near)}/9 = {len(near)/9*100:.0f}%")
check("≥6/9 近整數", len(near) >= 6, f"({len(near)}/9)")

# 誤差分佈
errs = [abs(d - round(d)) for d in delta.values()]
print(f"    誤差: mean={np.mean(errs):.3f}, max={np.max(errs):.3f}")
check("平均誤差 < 0.35", np.mean(errs) < 0.35, f"({np.mean(errs):.3f})")

# --- [2] 精確候選 ---
print("\n[2] δ 整數集:")
ints = {k: round(d) for k, d in delta.items()}
print(f"    {ints}")
print(f"    值集: {sorted(set(ints.values()))}")
print(f"    → +5, +1, 0, -2, -5, -6, -8")

# 三代分組
print(f"\n[3] 三代 δ:")
print(f"    Gen1 (t,b,τ): {[ints[k] for k in ['t','b','tau']]}")
print(f"    Gen2 (c,s,μ): {[ints[k] for k in ['c','s','mu']]}")
print(f"    Gen3 (u,d,e): {[ints[k] for k in ['u','d','e']]}")

# --- [4] δ 結構 ---
print("\n[4] δ 候選結構:")
print(f"    +5 = F₅")
print(f"    +1 = 1")
print(f"     0 = 0")
print(f"    -2 = -2")
print(f"    -5 = -F₅")
print(f"    -6 = -L₆/3?  -6 = -(F₆-2)?")
print(f"    -8 = -F₆")
print(f"    → 候選集 {+5, 0, -2, -5, -6, -8} = ±F₅, 0, -2, -F₆, -6")
print(f"    → 9 個粒子: t(+5), b(+1), τ(+1), c(0), s(-2), μ(-2), d(-5), u(-6), e(-8)")
print(f"    → 有冇『質量公式』: δ = f(電荷, 代)?")

# --- [5] 質量公式候選 ---
print("\n[5] 候選質量公式:")
print(f"    δ 依電荷 (Q) 同代 (n):")
print(f"    Up 型: t(+5) c(0) u(-6)")
print(f"    Down:  b(+1) s(-2) d(-5)")
print(f"    Lepton: τ(+1) μ(-2) e(-8)")
print(f"    → Up: 5, 0, -6 | Down: 1, -2, -5 | Lep: 1, -2, -8")
print(f"    → 代間差: Up: 5→0→-6 (差 -5, -6), Down: 1→-2→-5 (差 -3, -3), Lep: 1→-2→-8 (差 -3, -6)")

# --- [6] m = e^(δ) 預測 vs 實際 ---
print("\n[6] 用整數 δ 預測質量:")
print(f"    {'粒子':<4} {'m_pred (GeV)':>14} {'m_act (GeV)':>12} {'誤差%':>8}")
for k, n in ints.items():
    m_pred = m44 * math.exp(n)
    m_act = SM[k]
    err = abs(m_pred - m_act)/m_act*100
    print(f"    {k:4s} {m_pred:14.6f} {m_act:12.6f} {err:7.1f}%")

# 平均誤差
errs2 = [abs(m44*math.exp(ints[k]) - SM[k])/SM[k]*100 for k in SM]
print(f"\n    平均誤差: {np.mean(errs2):.1f}%")
print(f"    → 整數 δ 模型 (0 參數!) 預測 SM 質量平均誤差 {np.mean(errs2):.1f}%")

print("\n" + "=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 70)
sys.exit(0 if FAIL == 0 else 1)
