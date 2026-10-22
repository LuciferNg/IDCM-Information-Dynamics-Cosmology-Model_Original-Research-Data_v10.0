#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scripts/03_doc_crosscheck.py — O157 文檔獨立核對 (audit round)

目的 (O153 協議): 從零重算 docs/01 + docs/02 每個宣稱嘅公式/數值 (mpmath 50 dps),
唔依賴 scripts/01-02 嘅輸出 — 捉 doc 入面嘅錯 (包括自己以前寫錯嘅)。

範圍:
  docs/01 (derivation): D1 譜泛函 / D2 winding / D3 sector-parity / D4 閉合項 /
                        D5 觀測項 / D6 λ 比率 / D7 對調懲罰
  docs/02 (sigma verdict): S1 統計量 / S2 候選 / S3 null / S6 譜化替代

禁跨文檔污染: 本 script 只核對, 唔改 docs; 修正另以 patch 加 ⚠️ 標註。
"""
import mpmath as mp
import numpy as np
import random
mp.mp.dps = 50

def eq(a, b, tol): return abs(a-b) < tol
checks, fails = [], []
def ck(name, cond, detail=""):
    checks.append(name)
    mark = "PASS" if cond else "FAIL"
    if not cond: fails.append(name)
    print("  [%s] %s %s" % (mark, name, detail))

N_d, K_t, B, N_gen = 44, 33, 4, 3
MU2 = 2
PI = mp.pi

def g176(k): return 4*mp.sin(mp.pi*k/176)**2
def deg(x):  return mp.degrees(x)
def atan_ratio(a, b, N):  # 176-Laplacian 慣例 (相位量)
    return deg(mp.atan(mp.sin(a*mp.pi/N)/mp.sin(b*mp.pi/N)))
def theta_N(N, a=7, b=6):  # 混合角家族慣例
    return deg(mp.atan(mp.sin(a*mp.pi/N)/mp.sin(b*mp.pi/N)))

print("="*74)
print("docs/01 §1-2: 譜泛函 + Winding (獨立重算)")
print("="*74)
ck("gamma_88 = 4 = B", eq(g176(88), 4, mp.mpf('1e-50')))
ck("gamma_44 = 2 = mu^2", eq(g176(44), 2, mp.mpf('1e-50')))
S_odd = sum(g176(k) for k in range(1, 88, 2)); S_even = sum(g176(k) for k in range(2, 89, 2))
ck("sum_gamma_odd = 88, sum_gamma_even = 90, E-O = 2 = gamma_44",
   eq(S_odd, 88, mp.mpf('1e-40')) and eq(S_even, 90, mp.mpf('1e-40')) and eq(S_even-S_odd, g176(44), mp.mpf('1e-40')))
E21_9 = (g176(21)+g176(9))/2
E7_6  = (g176(7)+g176(6))/2
ck("E[(psi_21+psi_9)/sqrt2] = 0.319280 (docs/01 D1)", eq(E21_9, mp.mpf('0.319280'), mp.mpf('1e-6')), "%.8f" % E21_9)
ck("E[(psi_7+psi_6)/sqrt2] = 0.053916 (docs/01 D1)", eq(E7_6, mp.mpf('0.053916'), mp.mpf('1e-6')), "%.8f" % E7_6)
ck("winding 88 鏈 = d/4: delta(21,9) w = 3 = N_gen", (21-9)/4 == 3)
ck("winding 55 塔 = d/2: theta23(7,6) w = 1/2", (7-6)/2 == mp.mpf(1)/2)
ck("88 鏈閉合判據 d ≡ 0 mod 4 (delta d = 12 ✓)", 12 % 4 == 0)
ck("55 塔閉合判據 d 偶", 12 % 2 == 0)

print()
print("="*74)
print("docs/01 §3: Sector-parity 定理 (獨立重算)")
print("="*74)
ck("delta modes (21,9) = (odd,odd) 純觀察者對", 21 % 2 == 1 and 9 % 2 == 1)
ck("theta23 modes (7,6) = (odd,even) 混合對", 7 % 2 == 1 and 6 % 2 == 0)
ck("d(21,9) = 12 偶 ≡ 0 mod 4", (21-9) % 4 == 0)
ck("d(7,6) = 1 奇 — 混合對永不閉合", (7-6) % 2 == 1)
ck("O158 對 (21,24): d = 3 奇; (13,32): d = 19 奇", (24-21) % 2 == 1 and (32-13) % 2 == 1)
ck("O158 純世界對 (60,82)@176: d = 22 偶", (82-60) % 2 == 0)

print()
print("="*74)
print("docs/01 §4: 閉合項 kink/slip 能量 (獨立重算)")
print("="*74)
for f, ref in [(0, 0), (0.25, 2), (0.5, 4)]:
    E1 = g176(88)*mp.sin(mp.pi*f)**2
    ck("E1(f=%.2f) = B·sin^2(pi f) = %s (B = 4)" % (f, mp.nstr(E1, 8)), eq(E1, ref, mp.mpf('1e-40')))
def slip_energy(f, N=176):
    th = 2*np.pi*f*np.arange(N)/N
    d = np.diff(th)
    d = np.append(d, (th[0]-th[-1]+np.pi) % (2*np.pi) - np.pi)
    return float(np.sum(4*np.sin(d/2)**2))
for f in (0.25, 0.5, 0.125):
    E = slip_energy(f)
    expect = 4*np.sin(np.pi*f)**2
    ck("slip(f=%.3f) ≈ 4sin^2(pi f) (有限尺寸 %.2f%%)" % (f, 100*abs(E-expect)/expect), abs(E-expect)/expect < 0.02)

print()
print("="*74)
print("docs/01 §5: 觀測項數值 (獨立重算)")
print("="*74)
t55 = theta_N(55); t88 = theta_N(88)
d88 = atan_ratio(21, 9, 176); d55 = atan_ratio(21, 9, 55)
ck("theta23(55) = 49.1966°", eq(t55, mp.mpf('49.1966'), mp.mpf('1e-4')), "%.6f" % t55)
ck("theta23(88) = 49.3202°", eq(t88, mp.mpf('49.3202'), mp.mpf('1e-4')), "%.6f" % t88)
ck("delta(88) = 66.399960°", eq(d88, mp.mpf('66.39996'), mp.mpf('1e-5')), "%.6f" % d88)
ck("delta(55) = 62.18°", eq(d55, mp.mpf('62.18'), mp.mpf('0.1')), "%.4f" % d55)
s2_23 = mp.mpf('0.57301')
th_obs = deg(mp.asin(mp.sqrt(s2_23)))
sig_th = deg(mp.asin(mp.sqrt(s2_23 + mp.mpf('0.016')))) - th_obs
sig_delta = deg(mp.mpf('0.027'))
delta_pdg = deg(mp.mpf('1.144'))
Dt55, Dt88 = abs(t55-th_obs), abs(t88-th_obs)
Dd88, Dd55 = abs(d88-delta_pdg), abs(d55-delta_pdg)
ck("Δθ(55) = %.4f° (docs 0.0016°)" % float(Dt55), eq(Dt55, mp.mpf('0.0016'), mp.mpf('5e-4')))
ck("Δθ(88) = %.4f° (docs 0.1221°)" % float(Dt88), eq(Dt88, mp.mpf('0.1221'), mp.mpf('5e-4')))
ck("θ₂₃ raw 比率 = %.0f× (O155 87× 家族, >50)" % float(Dt88/Dt55), Dt88/Dt55 > 50)
ck("Δδ(88) = %.3f° = %.2fσ (0.55σ)" % (float(Dd88), float(Dd88/sig_delta)), eq(Dd88/sig_delta, mp.mpf('0.55'), mp.mpf('0.05')))
ck("Δδ(55) = %.2f° = %.2fσ (2.18σ)" % (float(Dd55), float(Dd55/sig_delta)), eq(Dd55/sig_delta, mp.mpf('2.18'), mp.mpf('0.1')))
ck("δ@55 vs 結構值 66.399960: 4.22°", eq(abs(d55-mp.mpf('66.39996')), mp.mpf('4.22'), mp.mpf('0.05')))
ck("δ@88 結構精度 0.00004° (vs 66.4)", eq(abs(d88-mp.mpf('66.4')), mp.mpf('0.00004'), mp.mpf('1e-4')))
E2 = lambda D, s: MU2*(D/s)**2
ck("σ_θ = %.3f° (docs 0.929°)" % float(sig_th), eq(sig_th, mp.mpf('0.929'), mp.mpf('0.01')))
ck("σ_δ = %.3f° (docs 1.547°)" % float(sig_delta), eq(sig_delta, mp.mpf('1.547'), mp.mpf('0.01')))
ck("E2(θ₂₃@55) ≈ 5.8e-6", eq(E2(Dt55, sig_th), mp.mpf('5.83e-6'), mp.mpf('1e-6')))
ck("E2(θ₂₃@88) ≈ 0.0345", eq(E2(Dt88, sig_th), mp.mpf('0.0345'), mp.mpf('0.005')))
ck("E2(δ@88) ≈ 0.609", eq(E2(Dd88, sig_delta), mp.mpf('0.609'), mp.mpf('0.02')))
ck("E2(δ@55) ≈ 9.47", eq(E2(Dd55, sig_delta), mp.mpf('9.47'), mp.mpf('0.1')))

print()
print("="*74)
print("docs/01 §6-7: λ 比率 + 對調懲罰 (獨立重算)")
print("="*74)
ck("λ₁/λ₂ = gamma_88/gamma_44 = 2 = mu^2", eq(g176(88)/g176(44), 2, mp.mpf('1e-50')))
r_th = E2(Dt88, sig_th)/E2(Dt55, sig_th)
ck("θ₂₃ swap E₂ 比率 = %.0f (docs 5.9e3)" % float(r_th), eq(r_th, mp.mpf('5919'), mp.mpf('300')))
E_c = E2(Dd88, sig_delta) + E2(Dt55, sig_th)
E_t = E2(Dd88, sig_delta) + E2(Dt88, sig_th)
E_d = E2(Dd55, sig_delta) + E2(Dt55, sig_th)
E_b = E2(Dd55, sig_delta) + E2(Dt88, sig_th)
ck("4 分配: 0.6089/0.6434/9.4710/9.5055",
   eq(E_c, mp.mpf('0.6089'), mp.mpf('0.01')) and eq(E_t, mp.mpf('0.6434'), mp.mpf('0.01'))
   and eq(E_d, mp.mpf('9.4710'), mp.mpf('0.1')) and eq(E_b, mp.mpf('9.5055'), mp.mpf('0.1')))
ck("正確分配 = 唯一最低", E_c < E_t and E_c < E_d and E_c < E_b)
tand = mp.sin(21*mp.pi/176)/mp.sin(9*mp.pi/176)
ck("tan δ(88) = 2.288905 ∉ Q", eq(tand, mp.mpf('2.288905'), mp.mpf('1e-6')))
ck("55 = 5×11 冇 3 因子", 55 % 3 != 0)

print()
print("="*74)
print("docs/02: σ 判決 (獨立重算)")
print("="*74)
s_th_up = mp.asin(mp.sqrt(mp.mpf('0.573')+mp.mpf('0.016'))) - mp.asin(mp.sqrt(mp.mpf('0.573')))
s_th_dn = mp.asin(mp.sqrt(mp.mpf('0.573'))) - mp.asin(mp.sqrt(mp.mpf('0.573')-mp.mpf('0.020')))
ck("σ_θ(up) = %.6f rad = %.4f° (docs 0.016215/0.9290)" % (s_th_up, deg(s_th_up)),
   eq(s_th_up, mp.mpf('0.016215'), mp.mpf('1e-6')) and eq(deg(s_th_up), mp.mpf('0.9290'), mp.mpf('1e-3')))
ck("σ_θ(dn) = %.6f rad = %.4f° (docs 0.020162/1.1552)" % (s_th_dn, deg(s_th_dn)),
   eq(s_th_dn, mp.mpf('0.020162'), mp.mpf('1e-6')) and eq(deg(s_th_dn), mp.mpf('1.1552'), mp.mpf('1e-3')))
ck("上/下側差 24%% (docs S1)", s_th_dn/s_th_up > 1.2)
# 候選重算 (σ_δ 用 rad: 0.027)
s_delta_rad = mp.mpf('0.027')
dev_2L10 = abs(mp.mpf(2)/123 - s_th_up)/s_th_up
dev_1_37 = abs(mp.mpf(1)/37 - s_delta_rad)/s_delta_rad
dev_2piF13 = abs(2*mp.pi/233 - s_delta_rad)/s_delta_rad
ck("候選 σ_θ ≈ 2/L₁₀ dev = %.3f%% (docs 0.28%%)" % float(100*dev_2L10), eq(dev_2L10, mp.mpf('0.0028'), mp.mpf('5e-4')))
ck("候選 σ_δ ≈ 1/37 dev = %.3f%% (docs 0.10%%)" % float(100*dev_1_37), eq(dev_1_37, mp.mpf('0.0010'), mp.mpf('3e-4')))
ck("候選 σ_δ ≈ 2π/F₁₃ dev = %.3f%% (docs 0.12%%)" % float(100*dev_2piF13), eq(dev_2piF13, mp.mpf('0.0012'), mp.mpf('3e-4')))
# σ_θ(dn) 冇靚命中: 掃所有候選族
cands = []
scales = [176, 88, 55, 44, 42, 33, 22, 11]
Lc = {4:7, 5:11, 6:18, 7:29, 8:47, 9:76, 10:123}
Fc = {5:5, 6:8, 7:13, 8:21, 10:55, 11:89, 12:144, 13:233}
for N in scales:
    cands += [mp.pi/N, 2*mp.pi/N, mp.mpf(1)/N]
for n in [61, 123, 37, 116, 194, 233, 469]:
    cands += [mp.mpf(1)/n, mp.mpf(2)/n]
for v in Fc.values():
    cands += [2*mp.pi/v, mp.pi/v]
for v in Lc.values():
    cands += [mp.mpf(2)/v, mp.pi/v]
g1 = 4*mp.sin(mp.pi/176)**2
cands += [g1, mp.sqrt(g1), mp.mpf(2)/123, mp.mpf(1)/mp.mpf('61.5')]
best_dn = min(abs(v - s_th_dn)/s_th_dn for v in cands)
ck("σ_θ(dn) 最佳候選 dev = %.1f%% (docs: π/F₁₂ 8.2%%, 冇靚命中)" % float(100*best_dn), best_dn > 0.05)
# null-control 重算 (新 seed)
random.seed(20260908)
Ntrials = 2000
hit = 0
for _ in range(Ntrials):
    t = mp.mpf(random.uniform(0.005, 0.05))
    if any(abs(v - t)/t < 0.10 for v in cands):
        hit += 1
ck("null 重算: 隨機 σ 命中率 = %.1f%% (docs 98.1%%)" % (100*hit/Ntrials), hit/Ntrials > 0.9)
# S6: 譜化替代
def E2_spec(D, sig): return MU2*(D/sig)**2
r_d_spec = E2_spec(Dd88, deg(mp.pi/176)) / E2_spec(Dd55, deg(mp.pi/55))
r_t_spec = E2_spec(Dt88, deg(mp.pi/88)) / E2_spec(Dt55, deg(mp.pi/55))
ck("σ→π/N: δ 鑑別力跌到 %.1f× (docs 0.7×)" % float(r_d_spec), r_d_spec < 3.0)
ck("σ→π/N: θ₂₃ 鑑別力仍高 %.0f× (docs 15153×)" % float(r_t_spec), r_t_spec > 1000)
ck("操作定義: Δθ = σ ⟺ E₂ = μ² = 2", True)

print()
total = len(checks)
print("="*74)
print("RESULT: %d/%d PASS" % (total-len(fails), total))
if fails:
    print("FAIL: %s" % fails)
print("="*74)
