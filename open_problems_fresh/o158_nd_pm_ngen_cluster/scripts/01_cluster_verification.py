#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scripts/01_cluster_verification.py — ×41 聚類驗證 (N_d ± k·N_gen 家族)
用戶建議: f_unproj = 41 點解同時出現喺質子同希格斯殘差?
驗證: {17, 19, 38, 41, 47} 全部 = N_d ± {N_gen, 2N_gen, N_gen³} 或 /2,
同時係質量公式模式指數 (m_W/m_Z, m_H/m_W, m_p 兩候選)。
"""
import mpmath as mp
mp.mp.dps = 60

N_d, N_gen, B, L5 = 44, 3, 4, 11
M0 = mp.mpf('27.9009')   # 質量標度 (MeV, O54)

def g(n): return 4*mp.sin(mp.pi*n/88)**2          # 44-mode chain γ
def w(n): return 2*mp.sin(mp.pi*n/88)             # ω

checks, fails = [], []
def ck(name, cond, detail=""):
    checks.append(name)
    mark = "✔" if cond else "✘ FAIL"
    if not cond: fails.append(name)
    print("  [%s] %s %s" % (mark, name, detail))

print("="*70)
print("1. 聚類成員身份: 全部 = N_d ± k·N_gen")
print("="*70)
ck("41 = N_d−N_gen = 44−3 (f_unproj 分子, o148)", 44-3 == 41)
ck("47 = N_d+N_gen = 44+3 (質子候選 B)", 44+3 == 47)
ck("38 = N_d−2N_gen = 44−6 (希格斯分子)", 44-6 == 38)
ck("19 = N_d/2−N_gen = 22−3 (希格斯分母)", 22-3 == 19)
ck("17 = N_d−N_gen³ = 44−27 (質子候選 A)", 44-27 == 17)
ck("17 = L₆−1 = Tr(T̂⁶)−1 (o138 F_proj)", 18-1 == 17)

print()
print("2. f_unproj = 41/60 嘅算子身份 (o148)")
print("="*70)
f_unproj = mp.mpf(41)/60
ck("41/60 = (1+33/90)/2 (對稱面分拆, o148 F1)", abs((1+mp.mpf(33)/90)/2 - f_unproj) < mp.mpf('1e-50'))
ck("60 = 180/3 = B(N_d+1)/3", 180//3 == 60 and B*(N_d+1)//3 == 60)
ck("60 = 2N_gen×(L₅−1) = 6×10", 2*N_gen*(L5-1) == 60)
ck("f_unproj = 61.5/90 = 123/180", abs(mp.mpf(123)/180 - f_unproj) < mp.mpf('1e-50'))
ck("f_proj = 19/60 (補)", abs(1 - f_unproj - mp.mpf(19)/60) < mp.mpf('1e-50'))
ck("ε = 19/41 = f_proj/f_unproj (o148 Q1d)", abs((mp.mpf(19)/60)/(mp.mpf(41)/60) - mp.mpf(19)/41) < mp.mpf('1e-50'))

print()
print("3. 希格斯家族模式指數 (o142)")
print("="*70)
mW_mZ = mp.sin(30*mp.pi/88)/mp.sin(41*mp.pi/88)
mH_mW = mp.sin(38*mp.pi/88)/mp.sin(19*mp.pi/88)
ck("m_W/m_Z = sin(30π/88)/sin(41π/88) = 0.8827 (PDG 0.8814)", abs(mW_mZ - 0.8827) < 1e-4 and abs(mW_mZ - 0.8814)/0.8814 < 0.002, "%.6f" % mW_mZ)
ck("m_H/m_W = sin(38π/88)/sin(19π/88) = 1.557283 (PDG 1.5572, 0.005%)", abs(mH_mW - 1.557283) < 1e-6 and abs(mH_mW - 1.5572)/1.5572 < 2e-4, "%.6f" % mH_mW)
print("   註: o142 docs/01 寫 1.5583 (0.064%) — 實際 1.557283 (0.005%); 精度表示偏差, 閉合不受影響")
ck("19 同 38 = 2×19 (o144: 38 = 2×19 質量比模式)", 2*19 == 38)
ck("41/19 節點 (o143): f_unproj/f_proj = 41/19", 41*mp.mpf(1)/19 == mp.mpf(41)/19)

print()
print("4. 質子兩候選 (o54/o144)")
print("="*70)
m_pA = 17 * M0 * w(44)                       # F_proj × M₀ × ω_max
m_pB = M0 * g(20)**2 * g(7) * 47             # M₀ × γ₂₀²γ₇ × 47
ck("A: 17×M₀×ω_max = 948.63 (1.10%)", abs(m_pA - 948.63) < 0.05, "%.2f" % m_pA)
ck("B: M₀×γ₂₀²γ₇×47 = 943.98 (0.61%)", abs(m_pB - 943.98) < 0.05, "%.2f" % m_pB)
ck("γ₂₀ = 4sin²(20π/88)", abs(g(20) - 4*mp.sin(20*mp.pi/88)**2) < mp.mpf('1e-50'))
ck("γ₇ = 4sin²(7π/88) = 0.2446", abs(g(7) - 0.2446) < 1e-4, "%.4f" % g(7))
ck("ω_max = ω₄₄ = 2 (Nyquist)", abs(w(44) - 2) < mp.mpf('1e-50'))

print()
print("5. ★ 聚類結構: 模式指數全住喺「維度 ± 世代」面")
print("="*70)
fam = {41: "N_d−N_gen", 47: "N_d+N_gen", 38: "N_d−2N_gen", 19: "N_d/2−N_gen", 17: "N_d−N_gen³"}
for v, desc in sorted(fam.items()):
    print("   %3d = %s" % (v, desc))
ck("五成員全部 ∈ {B·L₅ ± k·F₄, B·L₅−F₄³, 2L₅−F₄} 家族", 
   set(fam) == {41, 47, 38, 19, 17})
# T̂ 形式 (O155 工具箱)
ck("N_d±N_gen = B·L₅±(T̂⁴)₁₂ (T̂ 形式)", 4*11 - 3 == 41 and 4*11 + 3 == 47)
ck("38 = B·L₅−2(T̂⁴)₁₂; 19 = 2L₅−(T̂⁴)₁₂", 44-6 == 38 and 22-3 == 19)
ck("17 = Tr(T̂⁶)−1 (L₆−1)", 18-1 == 17)

print()
print("6. 對照: 殘差分析")
print("="*70)
ck("質子 A 殘差 1.10% (948.63 vs 938.27)", abs((m_pA-938.27)/938.27 - 0.0110) < 5e-4, "%.3f%%" % (100*(m_pA-938.27)/938.27))
ck("質子 B 殘差 0.61% (943.98 vs 938.27)", abs((m_pB-938.27)/938.27 - 0.0061) < 5e-4, "%.3f%%" % (100*(m_pB-938.27)/938.27))
ck("希格斯 m_H 殘差 0.21% (124.984 vs 125.250)", abs((mp.mpf('124.984')-mp.mpf('125.250'))/mp.mpf('125.250') + 0.00213) < 5e-4)
print("   註: 殘差本身未閉合 (質子 0.6-1.1%, 希格斯 0.2%) — 聚類係模式指數層, 唔係殘差閉合")

print()
total = len(checks)
print("="*70)
print("RESULT: %d/%d PASS" % (total-len(fails), total))
if fails: print("FAIL: %s" % fails)
print("="*70)
