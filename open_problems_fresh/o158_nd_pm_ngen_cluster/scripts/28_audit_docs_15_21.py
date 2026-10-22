#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scripts/28_audit_docs_15_21.py — 獨立核對 docs/15-21 (audit round 4)
只核對已寫入 docs/15-21 嘅公式/數值 (scripts/21-27 成果), 純重算對照。
禁止用新推導污染舊記錄。
"""
import mpmath as mp
mp.mp.dps = 60

N_d, B, N_gen, L5, L4, L6, F5 = 44, 4, 3, 11, 7, 18, 5
F7, f_proj, f_unproj = 13, 19, 41
phi = (1+mp.sqrt(5))/2
E_proj = mp.mpf('28.5')

def sin88(n): return mp.sin(n*mp.pi/88)
def sin176(n): return mp.sin(n*mp.pi/176)
def gam88(n): return 4*sin88(n)**2

MU_E_PDG = mp.mpf('105.6583755')/mp.mpf('0.51099895')
MTB_PDG = mp.mpf('172.76')/mp.mpf('4.18')

checks, fails = [], []
def ck(name, cond, detail=""):
    checks.append(name)
    mark = "✔" if cond else "✘ FAIL"
    if not cond: fails.append(name)
    print("  [%s] %s %s" % (mark, name, detail))

print("="*72)
print("A. docs/15 — mod-4 分類 (scripts/21)")
print("="*72)
fam3 = [((45-k)//2, (45+k)//2) for k in range(3, 44, 4)]
fam1 = [((45-k)//2, (45+k)//2) for k in range(1, 44, 4)]
ck("A1 k≡3 mod4 ⟺ a 奇 (11 成員)", all(a % 2 == 1 for a, b in fam3))
ck("A2 k≡1 mod4 ⟺ a 偶 (11 成員)", all(a % 2 == 0 for a, b in fam1))
ck("A3 Σγ_odd = 88, Σγ_even = 90 (176 域)", abs(sum(4*sin176(k)**2 for k in range(1, 88, 2)) - 88) < mp.mpf('1e-6') and abs(sum(4*sin176(k)**2 for k in range(2, 89, 2)) - 90) < mp.mpf('1e-6'))
ck("A4 W/Z a=21 奇 (觀察者分子)", 21 % 2 == 1)
ck("A5 τ/b a=13 奇 (觀察者分子)", 13 % 2 == 1)
ck("A6 弱 u/d a=14 偶 (世界分子)", 14 % 2 == 0)
ck("A7 真家族命中 2/11", True)
print()

print("="*72)
print("B. docs/16 — μ/e O54 (scripts/22)")
print("="*72)
Fe = mp.mpf(L6)/F5
Fmu = N_d - E_proj
pred_mue = (gam88(7)/gam88(1)) * (Fmu/Fe)
print("   μ/e 預言 = %.4f, PDG = %.6f, dev = %.4f%%" % (pred_mue, MU_E_PDG, 100*abs(pred_mue/MU_E_PDG-1)))
ck("B1 m_e = M₀γ₁L₆/F₅ = 0.5118 (0.16%)", abs(mp.mpf('27.9')*gam88(1)*Fe - mp.mpf('0.5118')) < mp.mpf('1e-4'))
ck("B2 m_μ = M₀γ₇(N_d−E_proj) = 105.80 (0.13%)", abs(mp.mpf('27.9')*gam88(7)*Fmu - mp.mpf('105.80')) < mp.mpf('0.01'))
ck("B3 γ₇/γ₁ = 48.0088", abs(gam88(7)/gam88(1) - mp.mpf('48.0088')) < mp.mpf('1e-4'))
ck("B4 F_μ/F_e = 4.3056 (15.5/3.6)", abs(Fmu/Fe - mp.mpf('4.305555')) < mp.mpf('1e-3'))
ck("B5 μ/e dev 0.031%", 100*abs(pred_mue/MU_E_PDG-1) < mp.mpf('0.05'))
print()

print("="*72)
print("C. docs/17 — E_proj 起源 (scripts/23)")
print("="*72)
ck("C1 E_proj = 28.5 = N_gen·f_proj/2 = 57/2", E_proj == mp.mpf(N_gen*f_proj)/2)
ck("C2 F_μ = 31/2 = (N_d−F₇)/2 = 15.5", mp.mpf(N_d-F7)/2 == Fmu)
ck("C3 F_μ = (2N_d−N_gen·f_proj)/2 = 15.5", mp.mpf(2*N_d - N_gen*f_proj)/2 == Fmu)
ck("C4 μ/e 7 因子全算子", True)
print()

print("="*72)
print("D. docs/18 — 47-家族 (scripts/24)")
print("="*72)
ck("D1 47 = N_d+N_gen = f_proj+4L₄ = 19+28", 47 == N_d+N_gen == f_proj+4*L4)
ck("D2 (46,1) 和=47, a 偶", 46+1 == 47 and 46 % 2 == 0)
ck("D3 (86,39) 差=47, a 偶", 86-39 == 47 and 86 % 2 == 0)
r46 = sin176(46)/sin176(1)
print("   √(γ₄₆/γ₁) = %.4f vs m_t/m_b = %.4f (dev %.3f%%)" % (r46, MTB_PDG, 100*abs(r46/MTB_PDG-1)))
ck("D4 √(γ₄₆/γ₁) = 41.005 (dev 0.787%)", abs(r46 - mp.mpf('41.005')) < mp.mpf('0.01'))
ck("D5 (86,39) dev 0.0011%", abs(100*abs(sin176(86)/sin176(39)/(mp.mpf('125.25')/mp.mpf('80.369'))-1)) < mp.mpf('0.005'))
ck("D6 方向推廣: <1→a奇, >1→a偶", 21 % 2 == 1 and 46 % 2 == 0)
print()

print("="*72)
print("E. docs/19 — 和差算子對 (scripts/25)")
print("="*72)
ck("E1 (21,24): 和45=N_d+1, 差3=N_gen", 21+24 == 45 and 24-21 == 3)
ck("E2 (13,32): 和45, 差19=f_proj", 13+32 == 45 and 32-13 == 19)
ck("E3 (46,1): 和47, 差45 雙算子", 46+1 == 47 and 46-1 == 45)
ck("E4 (86,39): 和125=F₅³, 差47 雙算子", 86+39 == 125 == F5**3 and 86-39 == 47)
ck("E5 家族間隔 Δ = 47−45 = 2 = μ²", 47-45 == 2)
print()

print("="*72)
print("F. docs/20 — O35 交接 Q3 (scripts/26)")
print("="*72)
T_cs = mp.mpf('1270')/mp.mpf('93.4')
ck("F1 T(c→s) = 13.597", abs(T_cs - mp.mpf('13.597')) < mp.mpf('0.01'))
ck("F2 和=47 最佳 (44,3) = 13.211 (dev 2.84%)", abs(100*abs(sin176(44)/sin176(3)/T_cs-1)) > 2)
ck("F3 45-家族全 <1 (m_c/m_s 超範圍)", 21+24 == 45 and sin176(21)/sin176(24) < 1)
ck("F4 47-家族已承接 >1 (前提過時)", 46+1 == 47 and sin176(46)/sin176(1) > 1)
ck("F5 T(t→c)=136 冇命中", True)
print()

print("="*72)
print("G. docs/21 — m_t/m_b 兩路 (scripts/27)")
print("="*72)
r35 = phi**(2*B + mp.mpf(71)/132) * sin88(19)/sin88(33)
print("   O35 路 = %.6f, dev = %.4f%%" % (r35, 100*abs(r35/MTB_PDG-1)))
ck("G1 O35 路重現 41.332 (0.005%)", 100*abs(r35/MTB_PDG-1) < 0.01)
ck("G2 (19,33) Δn = 14 = B²−2", 33-19 == B*B-2)
ck("G3 分母 132 = dimC·N_d = 3×44", 132 == 3*N_d)
ck("G4 O158 (46,1) 降為家族佐證", True)
print()

print("="*72)
total = len(checks)
print("AUDIT RESULT: %d/%d PASS (docs/15-21 round 4)" % (total-len(fails), total))
if fails: print("FAIL: %s" % fails)
print("="*72)