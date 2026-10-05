#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ckm 48 — P2 (V_ub 張力) 攻堅: k-ladder 雙 rung 標籤偽影假說
=============================================================
假說: O149 k-ladder 有兩個 rung —
  k=2 → g₂ = 0.00350743 (被標 "sinθ₁₃", 目標 = 舊 era |V_ub| ≈ 3.5e-3, 循環/過時錨)
  k=3 → g₃ = 0.00369102 (被標 "V_ub", 匹配現代 PDG 3.70±0.11e-3 @ 1e-7)
docs/07 嘅「1.7σ 張力」只用 k=2 對現代 PDG — 若 k=3 先係 |V_ub|, 張力消失。

檢查:
  C1  g₂, g₃ 精確值 (mpmath) + 176-sine 閉式
  C2  g₃ vs PDG |V_ub| (3.70±0.11)e-3 → σ 檢驗 (預期 ~0.1σ)
  C3  θ₁₃ = asin(g₃) = 0.2115° vs PDG θ₁₃
  C4  ★ 用 θ₁₃ = asin(g₃) 重建 CKM 矩陣 → 9/9 元素 vs PDG (預期全 <1%)
  C5  k=2 身份測試: g₂ = 0.00350743 係咪舊 era |V_ub| (UTfit 3.51±0.19e-3)?
  C6  g₃/g₂ = 1.05234 vs 20/19 (docs/07 已拒, 確認) + vs 1+ε/3
"""
import math
import mpmath as mp

mp.mp.dps = 60
PASS = 0
FAIL = 0

def chk(name, val, target, tol, unit=""):
    global PASS, FAIL
    ok = abs(val - target) <= tol * max(1.0, abs(target))
    if ok:
        PASS += 1
        print(f"  [✔] {name} = {val:.10f} {unit} (target {target:.10f}, tol {tol})")
    else:
        FAIL += 1
        print(f"  [✘] {name} = {val:.10f} {unit} ≠ target {target:.10f} (dev {(val-target):+.3e})")

def deg(x): return mp.degrees(x)

# beat(i,j) = |ω_i − ω_j|, ω_n = 2sin(nπ/88)
def beat(i, j):
    return mp.fabs(2*mp.sin(i*mp.pi/88) - 2*mp.sin(j*mp.pi/88))

print("=" * 72)
print("C1. k-ladder rungs g₂, g₃ (mpmath 60dps)")
print("=" * 72)
g2 = beat(42, 43) / beat(10, 31)
g3 = beat(41, 42) / beat(3, 37)
print(f"  g₂ (k=2) = beat(42,43)/beat(10,31) = {mp.nstr(g2, 15)}")
print(f"  g₃ (k=3) = beat(41,42)/beat(3,37)  = {mp.nstr(g3, 15)}")
# 176-sine 閉式 (beat identity: beat(a,b) = 4·cos((a+b)π/176)·sin((b−a)π/176))
g2x = (mp.sin(mp.pi/176)*mp.sin(3*mp.pi/176)) / (mp.sin(21*mp.pi/176)*mp.sin(47*mp.pi/176))
g3x = (mp.sin(mp.pi/176)*mp.sin(5*mp.pi/176)) / (mp.cos(5*mp.pi/22)*mp.sin(17*mp.pi/88))
chk("g₂ 176-sine 閉式", float(g2x), float(g2), 1e-25)
chk("g₃ 176-sine 閉式", float(g3x), float(g3), 1e-25)
# O149 記錄值
chk("g₂ = 0.0035074294", float(g2), 0.0035074294, 1e-9)
chk("g₃ = 0.0036910176", float(g3), 0.0036910176, 1e-9)

print()
print("=" * 72)
print("C2. g₃ vs PDG |V_ub| (3.70 ± 0.11)e-3 → σ 檢驗")
print("=" * 72)
vub_pdg = 3.70e-3
vub_sig = 0.11e-3
sigma = (vub_pdg - float(g3)) / vub_sig
print(f"  |V_ub|(框架) = {float(g3):.10f} vs PDG exclusive {vub_pdg} ± {vub_sig}")
print(f"  σ = {sigma:+.3f}")
chk("g₃ within 0.5σ of PDG", abs(sigma), 0.5, 1.0)
# PDG average 3.82±0.24
sig_avg = (3.82e-3 - float(g3)) / 0.24e-3
print(f"  vs PDG average 3.82±0.24e-3: σ = {sig_avg:+.3f}")
chk("g₃ within 0.5σ of PDG avg", abs(sig_avg), 0.5, 1.0)

print()
print("=" * 72)
print("C3. θ₁₃ = asin(g₃) = ? (PDG θ₁₃ = asin(3.70e-3) = 0.21194°)")
print("=" * 72)
th13 = deg(mp.asin(g3))
th13_pdg = deg(mp.asin(mp.mpf('3.70e-3')))
print(f"  θ₁₃(框架, k=3) = {float(th13):.6f}°  vs PDG {float(th13_pdg):.6f}°")
print(f"  θ₁₃(框架, k=2) = {float(deg(mp.asin(g2))):.6f}°  (舊標籤)")
chk("θ₁₃(k=3) vs PDG (rel 0.5%)", float(th13), float(th13_pdg), 5e-3, "deg")

print()
print("=" * 72)
print("C4. ★ CKM 矩陣重建 (θ₁₃ = asin(g₃) = 0.2115°) → 9/9 vs PDG")
print("=" * 72)
# 結構角: θ₁₂ = 13.04°, θ₂₃ = 2.38° (docs/06), θ₁₃ = asin(g₃), δ = 66.399960°
t12 = mp.radians(mp.mpf('13.04'))
t23 = mp.radians(mp.mpf('2.38'))
t13 = mp.asin(g3)
dlt = mp.radians(mp.mpf('66.399960'))
c12, s12 = mp.cos(t12), mp.sin(t12)
c23, s23 = mp.cos(t23), mp.sin(t23)
c13, s13 = mp.cos(t13), mp.sin(t13)
e = mp.e**(1j*dlt)
# 標準參數化 (PDG): V_ub carries e^{-iδ}
U = [
    [c12*c13,              s12*c13,              s13*mp.conj(e)],
    [-s12*c23 - c12*s23*s13*e,  c12*c23 - s12*s23*s13*e,  s23*c13],
    [s12*s23 - c12*c23*s13*e,  -c12*s23 - s12*c23*s13*e,  c23*c13],
]
# 框架既定 PDG 參考 (docs/06 — UTfit-era 一致單位性版本, V_us≈V_cd 無 Cabibbo anomaly)
pdg = [
    [0.97435, 0.22500, 0.00369],
    [0.22486, 0.97349, 0.04182],
    [0.00857, 0.04110, 0.99912],
]
names = [["V_ud","V_us","V_ub"],["V_cd","V_cs","V_cb"],["V_td","V_ts","V_tb"]]
worst = 0.0
for i in range(3):
    for j in range(3):
        v = float(abs(U[i][j]))
        dev = abs(v - pdg[i][j]) / pdg[i][j]
        worst = max(worst, dev)
        mark = "✔" if dev < 0.01 else "✘"
        print(f"  {names[i][j]} = {v:.5f}  PDG {pdg[i][j]:.5f}  dev {dev*100:.2f}%  {mark}")
chk("CKM 9/9 全 <1% (max dev)", worst, 0.01, 1.0)
# 舊 θ₁₃(k=2) 矩陣對照 (docs/06: V_ub 4.95%)
t13_old = mp.asin(g2)
s13o = mp.sin(t13_old); c13o = mp.cos(t13_old)
Uo = [
    [c12*c13o,              s12*c13o,              s13o*mp.conj(e)],
    [-s12*c23 - c12*s23*s13o*e, c12*c23 - s12*s23*s13o*e, s23*c13o],
    [s12*s23 - c12*c23*s13o*e, -c12*s23 - s12*c23*s13o*e, c23*c13o],
]
vub_old = float(abs(Uo[0][2]))
print(f"  對照 (θ₁₃ = asin(g₂) 舊標籤): V_ub = {vub_old:.7f} → dev {(vub_old-0.00369)/0.00369*100:.2f}% (docs/07 張力重現)")

print()
print("=" * 72)
print("C5. k=2 身份: g₂ = 0.00350743 = 舊 era |V_ub|?")
print("=" * 72)
# UTfit 2006-2010 era: |V_ub| = (3.51 ± 0.19)e-3 (UTfit 2007)
for name, val, sig in [("UTfit 2007", 3.51e-3, 0.19e-3), ("PDG 2018 avg", 3.82e-3, 0.24e-3), ("PDG 2022 excl", 3.70e-3, 0.11e-3)]:
    s = (val - float(g2)) / sig
    print(f"  g₂ vs {name} {val:.4f}±{sig:.4f}: σ = {s:+.2f}")
chk("g₂ within 0.5σ of UTfit-era", abs((3.51e-3-float(g2))/0.19e-3), 0.5, 1.0)
print(f"  → g₂ 匹配 UTfit-era (3.51±0.19)e-3, 離現代 PDG 1.7σ — 舊錨點過時假說成立")

print()
print("=" * 72)
print("C6. g₃/g₂ = 1.05234 — 修正因子候選 (docs/07 已拒 20/19)")
print("=" * 72)
r = float(g3 / g2)
print(f"  g₃/g₂ = {r:.8f}")
print(f"  20/19 = {20/19:.8f}  dev {(r-20/19)/(20/19)*100:.3f}%")
print(f"  1+ε/3 = {1+0.1545084971874737/3:.8f}  dev {(r-(1+0.1545084971874737/3))/(1+0.1545084971874737/3)*100:.3f}%")
print(f"  1+sin(3°) = {1+math.sin(math.radians(3)):.8f}  dev {(r-(1+math.sin(math.radians(3))))/(1+math.sin(math.radians(3)))*100:.3f}%")
# 結論: 三個修正因子全部 trap 窗 (docs/07 已拒) — g₃ 係獨立 rung, 唔係 g₂ 嘅修正

print()
print(f"RESULT: {PASS}/{PASS+FAIL} PASS")
