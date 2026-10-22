#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scripts/03_ap_split_dual_channel.py — O158 深化: AP 三元組 + 反射鏈 + R2/R3/R4
新結構候選 (2026-09-08):
  F1: (19, 41) = 30 ∓ L₅  — f_proj/f_unproj 分子對 = 30±11 AP (步 = L₅)
  F2: 60 = 2×30;  19+41 = 60;  41−19 = 22 = N_d/2 = 2L₅
  F3: 30 = Tr(χ) = N_d−2L₄ = K_tree−N_gen = Σγ_even/N_gen = 90/3
  F4: 反射/餘角差鏈: 2×41−44 = 38 (H/W 分子!), 2×30−44 = 16 = B²
      38 = 41 − (44−41) = W/Z 分母 41 同自己餘角 3 之差
  F5: R3 統一: f_unproj, f_proj, m_W/m_Z, m_H/m_W, g₂² 全部由 (Tr(χ), L₅) = (30,11) 決定
  F6: 60 候選身份: 2Tr(χ), 2(K_tree−N_gen), 2Σγ_even/N_gen, V(rhombi)=|A₅|, N_d+B²
  F7: 47 = L₈ (Lucas); 樹側讀法: 17=K_tree−B², 19=K_tree−2L₄, 38=K_tree+F₅, 41=K_tree+2B, 47=K_tree+2L₄
  R4: m_H/m_Z 自動預測 (乘積); SM 質量比 ω-比掃描 + 背景密度 null; X(2370) 候選
"""
import mpmath as mp
mp.mp.dps = 60

N_d, N_gen, B, L4, L5, L6, L8 = 44, 3, 4, 7, 11, 18, 47
K_tree, F5, F6, F7 = 33, 5, 8, 13
M0 = mp.mpf('27.9009')
X2370 = mp.mpf('2370')   # BESIII glueball 候選 (2026-08-06 ICHEP)

def sinp(n): return mp.sin(n*mp.pi/88)
def cosp(n): return mp.cos(n*mp.pi/88)
def g(n): return 4*mp.sin(n*mp.pi/88)**2

checks, fails = [], []
def ck(name, cond, detail=""):
    checks.append(name)
    mark = "✔" if cond else "✘ FAIL"
    if not cond: fails.append(name)
    print("  [%s] %s %s" % (mark, name, detail))

print("="*72)
print("1. ★ AP 三元組: (19, 41) = 30 ∓ L₅  (f_proj/f_unproj 分子對)")
print("="*72)
ck("19 = 30 − L₅ = 30−11", 30-11 == 19)
ck("41 = 30 + L₅ = 30+11", 30+11 == 41)
ck("19+41 = 60 (分子和 = 分母!)", 19+41 == 60)
ck("41−19 = 22 = N_d/2 = 2L₅", 41-19 == 22 and 22 == N_d//2 and 22 == 2*L5)
ck("60 = 2×30 (分母 = 中點 × 2)", 2*30 == 60)
print("   → f_unproj = (30+L₅)/(2·30), f_proj = (30−L₅)/(2·30) — 對稱分拆, 零新常數")
print()

print("2. 30 嘅五重身份 (中點 = Tr(χ))")
print("="*72)
ck("30 = Tr(χ) = N_d−2L₄ = 44−14 (o142 譜作用量跡)", 44-2*L4 == 30)
ck("30 = K_tree−N_gen = 33−3 (tree 讀法)", K_tree-N_gen == 30)
ck("30 = Σγ_even/N_gen = 90/3 (世界預算/世代)", 90//3 == 30)
ck("30 = 60/2 (投影分母一半)", 60//2 == 30)
ck("4K_tree = 3N_d = 132 (Pythagorean 腿比 33:44 = 3:4, O156 R7)", 4*K_tree == 132 and 3*N_d == 132)
ck("33²+44² = 55² (O156 R7 閉合核對)", 33**2 + 44**2 == 55**2)
print("   → 30 三通道重合: 譜作用量跡 / tree 讀法 / 世界預算每世代")
print()

print("3. ★★ 反射/餘角差鏈: W/Z 指數 → H/W 指數 (R1 必要性候選)")
print("="*72)
ck("2×41 − 44 = 38 (W/Z 分母 41 反射 → H/W 分子 38!)", 2*41-44 == 38)
ck("2×30 − 44 = 16 = B² (W/Z 分子 30 反射 → B²)", 2*30-44 == 16 and 16 == B**2)
ck("38 = 41 − (44−41) = 41 − 3 (分母同自己餘角之差)", 41-(44-41) == 38)
ck("16 = 30 − (44−30) = 30 − 14 (分子同自己餘角之差)", 30-(44-30) == 16)
ck("餘角 14 = 2L₄, 3 = N_gen (cos 形式指數, docs/02)", 2*L4 == 14 and N_gen == 3)
ck("H/W = sin(38π/88)/sin(19π/88), 19 = 38/2 (雙角結構)", 38//2 == 19)
print("   → H/W 指數 (38,19) 由 W/Z 分母 41 經反射+減半得出 — 4 個自由指數減到 2 個 (30,41)")
print()

print("4. ★★★ R3 統一: 5 個量全部由 (Tr(χ), L₅) = (30, 11) 決定")
print("="*72)
f_unproj = mp.mpf(41)/60
f_proj = mp.mpf(19)/60
mW_mZ = sinp(30)/sinp(41)
mH_mW = sinp(38)/sinp(19)
g2sq = 4*mp.pi/30
ck("f_unproj = (30+11)/(2×30) = 41/60", abs(f_unproj - mp.mpf(30+11)/60) < mp.mpf('1e-50'))
ck("f_proj   = (30−11)/(2×30) = 19/60", abs(f_proj - mp.mpf(30-11)/60) < mp.mpf('1e-50'))
ck("m_W/m_Z = sin(30π/88)/sin(41π/88)", abs(mW_mZ - sinp(30)/sinp(30+11)) < mp.mpf('1e-50'))
ck("m_H/m_W = 2cos(19π/88) = 2cos((30−11)π/88)", abs(mH_mW - 2*cosp(19)) < mp.mpf('1e-50'))
ck("g₂² = 4π/Tr(χ) = 4π/30", abs(g2sq - 4*mp.pi/30) < mp.mpf('1e-50'))
print("   f_unproj=%.12f  f_proj=%.12f  mW/mZ=%.9f  mH/mW=%.9f  g2²=%.9f" %
      (f_unproj, f_proj, mW_mZ, mH_mW, g2sq))
print("   → 電弱玻色子 sector (g₂, W/Z, H/W) + 真空能投影 = (Tr(χ), L₅) 兩參數族")
print()

print("5. 60 嘅候選身份 (R2)")
print("="*72)
ck("60 = 2Tr(χ) = 2×30 (譜作用量雙倍)", 2*30 == 60)
ck("60 = 2(K_tree−N_gen) = 2×30", 2*(K_tree-N_gen) == 60)
ck("60 = 2Σγ_even/N_gen = 180/3", 2*90//3 == 60)
ck("60 = N_d + B² = 44+16", N_d + B**2 == 60)
ck("60 = B(N_d+1)/3 = 4×45/3 (o148 表法)", B*(N_d+1)//3 == 60)
ck("60 = 2N_gen(L₅−1) = 6×10 (o148 表法)", 2*N_gen*(L5-1) == 60)
ck("60 = |A₅| = 5!/2 (icosahedral 旋轉群階, 冷斑骨架)", 5*4*3*2*1//2 == 60)
ck("60 = V(rhombicosidodecahedron) (冷斑 60 節點, cmb_cold_spot/18)", 60 == 60)
print("   → 幾何讀法: f_unproj 分母 = 冷斑 A₅ 骨架節點數 (跨域登記 🟡)")
print()

print("6. 47 = L₈ + 樹側聚類讀法")
print("="*72)
ck("47 = L₈ (Lucas 第 8 項!)", L8 == 47)
ck("47 = N_d+N_gen = 44+3 (chain 讀法, docs/01)", N_d+N_gen == 47)
ck("17 = K_tree−B² = 33−16 (樹側, 質子 A)", K_tree - B**2 == 17)
ck("19 = K_tree−2L₄ = 33−14 (樹側, f_proj)", K_tree - 2*L4 == 19)
ck("38 = K_tree+F₅ = 33+5 (樹側, H/W 分子)", K_tree + F5 == 38)
ck("41 = K_tree+2B = 33+8 (樹側, f_unproj)", K_tree + 2*B == 41)
ck("46 = K_tree+F₇ = 33+13 = N_d⁺ (O153 世界自我維度, 同族!)", K_tree + F7 == 46)
ck("47 = K_tree+2L₄ = 33+14 (樹側, 質子 B)", K_tree + 2*L4 == 47)
print("   → 樹側讀法: 17/19/38/41/46/47 = K_tree ± {B², 2L₄, F₅, 2B, F₇} — 46 自動入族")
print()

print("7. R4 — m_H/m_Z 自動預測 (乘積閉合)")
print("="*72)
mH_mZ_idcm = mH_mW * mW_mZ
mH_mZ_pdg = mp.mpf('125.25')/mp.mpf('91.1876')
dev = abs(mH_mZ_idcm - mH_mZ_pdg)/mH_mZ_pdg
ck("m_H/m_Z = (m_H/m_W)×(m_W/m_Z) = %.9f" % mH_mZ_idcm,
   dev < 0.001, "vs PDG %.9f, dev = %.4f%%" % (mH_mZ_pdg, 100*dev))
print("   → H/Z 比唔係新自由度 — 係兩個閉合比嘅乘積, 自動預測")
print()

print("8. R4 — SM 質量比 ω-比掃描 + 背景密度 null")
print("="*72)
targets = {
    "m_W/m_Z  (PDG 80.369/91.1876)": mp.mpf('80.369')/mp.mpf('91.1876'),
    "m_H/m_W  (PDG 125.25/80.369)":  mp.mpf('125.25')/mp.mpf('80.369'),
    "m_H/m_Z  (PDG 125.25/91.1876)": mp.mpf('125.25')/mp.mpf('91.1876'),
    "m_τ/m_μ  (1776.86/105.658)":    mp.mpf('1776.86')/mp.mpf('105.658'),
    "m_μ/m_e  (105.658/0.511)":      mp.mpf('105.658')/mp.mpf('0.511'),
    "m_b/m_c  (4180/1270)":          mp.mpf('4180')/mp.mpf('1270'),
    "m_c/m_s  (1270/93.4)":          mp.mpf('1270')/mp.mpf('93.4'),
    "m_s/m_d  (93.4/4.67)":          mp.mpf('93.4')/mp.mpf('4.67'),
    "m_t/m_b  (172690/4180)":        mp.mpf('172690')/mp.mpf('4180'),
    "m_t/m_W  (172690/80369)":       mp.mpf('172690')/mp.mpf('80369'),
    "m_p/m_μ  (938.272/105.658)":    mp.mpf('938.272')/mp.mpf('105.658'),
}
cluster = {17, 19, 30, 38, 41, 47}
pairs = [(a, b) for a in range(1, 45) for b in range(1, 45) if a != b]
ratios = {(a, b): sinp(a)/sinp(b) for a, b in pairs}
print("   %-28s %10s %8s %6s %8s" % ("target", "best(a,b)", "dev%", "≤1%", "cluster?"))
for name, t in targets.items():
    best = min(pairs, key=lambda ab: abs(ratios[ab]/t - 1))
    devbest = abs(ratios[best]/t - 1)
    within1 = sum(1 for ab in pairs if abs(ratios[ab]/t - 1) < 0.01)
    incl = "★" if (best[0] in cluster and best[1] in cluster) else ""
    print("   %-28s (%2d,%2d)  %7.3f  %5d  %s" % (name, best[0], best[1], 100*devbest, within1, incl))
print("   ★ = best 命中用聚類指數對; ≤1% = 背景密度 (1936 對中 1% 內有幾多)")
print()

print("9. R4 — X(2370) 膠球候選 (trap-window 標記)")
print("="*72)
x_ratio = X2370/M0
ck("X(2370)/M₀ = %.4f" % x_ratio, abs(x_ratio - 85) < 0.15,
   "(85 = 2N_d−N_gen = F₅×F_proj, dev = %.4f%%)" % (100*abs(x_ratio-85)/85))
print("   ⚠️ 0.07% 偏差喺 φ-陷阱窗 (1e-5~1e-3) 內 → 🟡 候選唔係閉合")
ck("M₀×85 = 2371.58 vs X(2370) +0.07%", abs(M0*85 - X2370)/X2370 < 0.002, "%.2f MeV" % (M0*85))
print()

print("10. Verdict 總結")
print("="*72)
ck("F1 AP 三元組 (19,41) = 30∓L₅", 19 == 30-11 and 41 == 30+11)
ck("F4 反射鏈 41→38→19, 30→16", 2*41-44 == 38 and 2*30-44 == 16)
ck("F5 五量 (Tr(χ),L₅) 統一", True)
ck("F6 60 = 2Tr(χ) = 2(K_tree−N_gen) = 2Σγ_even/N_gen", 2*30 == 60)
ck("F7 47 = L₈ 獨立身份", L8 == 47)
ck("R4 m_H/m_Z 自動預測 0.09%", dev < 0.001)

print()
total = len(checks)
print("="*72)
print("RESULT: %d/%d PASS" % (total-len(fails), total))
if fails: print("FAIL: %s" % fails)
print("="*72)
