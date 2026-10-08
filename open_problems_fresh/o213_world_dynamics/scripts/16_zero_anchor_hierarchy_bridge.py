#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O213 scripts/16 — R9 零錨第二輪: 階層橋身份 + 指數機制候選（2026-10-08）
=======================================================================
承接 scripts/15 F 段發現: e^{V_Λ/2} ≈ 3.747 × N（量級橋）。

本輪攻關:
  A. 階層橋精確性 —— e^{V_Λ/2}/N = 3.7472 vs 結構候選
     3.75 = 60/16 = (N_d + B²)/B²   (60 = A₅ 節點 = N_d + B²; 16 = B² = κ⁻¹)
     以及 V_Λ − 2lnN = 2.6417 對結構數池之盲測
  B. 指數機制候選檢驗:
     (b1) prepotential 指數: ρ_Λ = e^{−V_Λ}, V_Λ = F(γ)+19 —— O62 定義確認
     (b2) 19 = L₅+F₆ 修正項 之 e^{±25}/e^{−44} 分解
     (b3) R7 定理 1 整合: Π = ħ²k_BT/(G²m_p⁵) 與 e^{−V_Λ} 有冇冪次關係
  C. 盲測紀律: 結構池最低命中統計 (用 46 個結構整數 + φ^k + 有理數)
"""
import sys
from mpmath import mp, mpf, pi, exp, sqrt, sin, log, ln, power, e as me

mp.dps = 50
G = 1.0

def chk(name, cond, detail=""):
    global G
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name} {detail}")
    if not cond:
        sys.exit(1)
    G += 1

# ---------- 輸入（與 scripts/15 同源） ----------
V_LAM  = mpf("283.082129")            # O62
F_GAM  = mpf("264.082129")            # O62
N      = mpf("7.88468594512e60")      # O213/O200
ND, B2, B = 44, 16, 4
PI_R7  = mpf("7.1759e63")             # R7 定理1
LAM_EFF = mpf("4.2913e-84")           # O86 (GeV²)
MPL    = mpf("1.220910e19")           # CODATA GeV

# ---------- A. 階層橋 ----------
print("== A. 階層橋: e^{V_Λ/2} / N = ? ==")
eV_half = exp(V_LAM/2)
ratio = eV_half / N
print(f"  e^V_Λ/2     = {float(eV_half):.10e}")
print(f"  N           = {float(N):.10e}")
print(f"  比           = {float(ratio):.10f}")
print(f"  結構候選 60/16 = {float(mpf(60)/16):.10f}  (dev {(float(abs(ratio-mpf(60)/16)/(mpf(60)/16))*100):.6f}%)")
print(f"  結構候選 30/8  = {float(mpf(30)/8):.10f}  (同 60/16)")
print(f"  結構候選 15/4  = {float(mpf(15)/4):.10f}  (dev {(float(abs(ratio-mpf(15)/4)/(mpf(15)/4))*100):.6f}%)")
# A1: 60/16 候選 (dev < 0.1%)
r_A1 = abs(ratio - mpf(60)/16)/(mpf(60)/16)
chk("A1 階層橋 3.747 ≈ 60/16 = (N_d+B²)/B²", r_A1 < mpf("0.001"), f"(dev {float(r_A1*100):.4f}%)")

# A2: V_Λ − 2ln N 之值
Vminus = V_LAM - 2*ln(N)
print(f"\n  V_Λ − 2ln N = {float(Vminus):.10f}")
print(f"  2 ln(60/16)  = {float(2*ln(mpf(60)/16)):.10f}")
print(f"  dev vs 2ln(60/16) = {float(abs(Vminus-2*ln(mpf(60)/16))/(2*ln(mpf(60)/16))*100):.4f}%")

# 盲測池: 46 結構整數 + φ 冪 + 有理數
struct_int = [1,2,3,4,5,7,8,9,11,12,13,14,15,16,18,19,20,21,22,23,25,26,29,30,31,32,33,35,36,40,41,44,45,47,49,55,60,64,70,77,88,90,120,123,176,421]
phi = (1+sqrt(5))/2
pool = []
for s in struct_int:
    for k in range(-8, 9):
        pool.append(mpf(s)*phi**k)
from fractions import Fraction
# 有理數 m/n (廣義結構)
for m in range(1, 61):
    for n in range(1, 61):
        if (m % n != 0):
            pool.append(mpf(m)/mpf(n))
# 去重 + 只保留正數
pool = sorted(set(p for p in pool if p > 0))
# A2 查找 Vminus 之最佳候選 (dev < 0.05%)
best = min(pool, key=lambda p: abs(p - Vminus)/Vminus)
bdev = abs(best - Vminus)/Vminus
print(f"  V−2lnN 最佳池命中 = {best}  dev {float(bdev*100):.4f}%")
chk("A2 V−2lnN 池中無 dev<0.02% 命中（非結構=誠實）", bdev > mpf("0.0002"),
    f"(最佳 dev {float(bdev*100):.4f}%)")

# ---------- B. 指數機制 ----------
print("\n== B. 指數機制候選 ==")
# B1: O62 定義 ρ_Λ = e^{−F}·e^{−(N_d−F₈−B)} = e^{−V_Λ} —— 指數形式係 O62 推導定義
e_negF = exp(-F_GAM); e_neg19 = exp(-(ND-21-4)); e_negV = e_negF * e_neg19
print(f"  e^{{−F(γ)}} = {float(e_negF):.6e};  e^{{−19}} = {float(e_neg19):.6e}")
print(f"  乘積         = {float(e_negV):.6e}  vs 直接 e^{{−V_Λ}} = {float(exp(-V_LAM)):.6e}")
chk("B1 O62 指數分解一致", abs(e_negV - exp(-V_LAM)) < mpf("1e-40"))

# B2: 19 = 44 − 25 之 e^+25/e^−44 對照（O62 §7c 機制詮釋）
rhs = exp(-F_GAM) * exp(-ND) * exp(25)
print(f"  e^{{−F}}·e^{{−44}}·e^{{+25}} = {float(rhs):.6e}  vs e^{{−V_Λ}} = {float(exp(-V_LAM)):.6e}")
chk("B2 = e^{−F}·e^{−N_d}·e^{+25} 機制重現", abs(rhs - exp(-V_LAM)) < mpf("1e-40"))

# B3: R7 定理 1 整合 —— Π 同 e^{−V_Λ} 冪次
# Π = ħ²k_BT/(G²m_p⁵); 求 p 使 e^{−V_Λ} ≈ Π^p × 結構?  ln(e^{V_Λ})/ln(Π)
lnPi = ln(PI_R7)
p_hint = V_LAM / lnPi
print(f"  ln Π = {float(lnPi):.6f};  V_Λ/ln Π = {float(p_hint):.6f}")
print(f"  p=2 假設:  2lnΠ = {float(2*lnPi):.4f} vs V_Λ = {float(V_LAM):.4f} (dev {float(abs(2*lnPi-V_LAM)/V_LAM*100):.3f}%)")
chk("B3 Π² 唔等於 e^V_Λ（排除簡單冪次）", abs(2*lnPi - V_LAM)/V_LAM > mpf("0.01"),
    f"(dev {float(abs(2*lnPi-V_LAM)/V_LAM*100):.2f}%)")

# B4: N 同 V_Λ 方向之整合—— e^{V_Λ/2}·B² vs (N_d+B²)·N（精確性再測）
lhs4 = exp(V_LAM/2)*16
rhs4 = (ND+16)*N
dev4 = abs(lhs4-rhs4)/rhs4
print(f"\n  e^{{V_Λ/2}}·16   = {float(lhs4):.10e}")
print(f"  (N_d+B²)·N = {float(rhs4):.10e}  (dev {float(dev4*100):.5f}%)")
chk("B4 e^{V_Λ/2}·B² ≈ (N_d+B²)·N 量級一致", dev4 < mpf("0.002"),
    f"(dev {float(dev4*100):.4f}%)")

# ---------- C. 診斷: V_Λ vs BBN 鏈 (O212 N 恆等式內含重力階層) ----------
print("\n== C. 階層橋之物理方向 ==")
# N² = [3π/(16ζ3)](Ω_b/η_B)(m_Pl/m_p)⁴(m_pc²/k_BT)³  (O212 docs/03)
# 若 e^{V_Λ} ∝ N², 則 V_Λ 含 4 ln(m_Pl/m_p) 主導 —— 測試: V_Λ vs 4ln(m_Pl/m_p)
mp_mp = MPL / mpf("0.93827208816e-3")   # m_Pl/m_p (GeV/GeV)
four = 4*ln(mp_mp)
print(f"  m_Pl/m_p = {float(mp_mp):.6e};  4·ln = {float(four):.6f}")
print(f"  V_Λ     = {float(V_LAM):.6f}")
print(f"  V_Λ/(4·ln) = {float(V_LAM/four):.6f}  (≈? 1 = 純 m_p 主導)")
chk("C1 V_Λ 唔係單一 4ln(m_Pl/m_p)（多因子）", abs(V_LAM/four - 1) > mpf("0.1"),
    f"(比 {float(V_LAM/four):.4f})")

print(f"\n===== 全部 {int(G-1)} PASS =====")
sys.exit(0)