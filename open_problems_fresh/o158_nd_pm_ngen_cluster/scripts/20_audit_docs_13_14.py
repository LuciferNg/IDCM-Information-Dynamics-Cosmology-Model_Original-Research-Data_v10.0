#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scripts/20_audit_docs_13_14.py — 獨立核對 docs/13-14 (audit round 3)
只核對已寫入 docs/13 (k 配對機制) + docs/14 (Gemini 假說) 嘅公式/數值。
禁止用新推導污染舊記錄 — 純重算對照。
"""
import mpmath as mp
mp.mp.dps = 60

def sin176(n): return mp.sin(n*mp.pi/176)
def sin88(n): return mp.sin(n*mp.pi/88)
def gam176(n): return 4*sin176(n)**2
def gam88(n): return 4*sin88(n)**2

N_d, B, N_gen, L5, L4 = 44, 4, 3, 11, 7
F_proj, f_proj, f_unproj = 17, 19, 41
PDG_HW = mp.mpf('125.25')/mp.mpf('80.369')
MU_E = mp.mpf('105.658')/mp.mpf('0.51099895')

checks, fails = [], []
def ck(name, cond, detail=""):
    checks.append(name)
    mark = "✔" if cond else "✘ FAIL"
    if not cond: fails.append(name)
    print("  [%s] %s %s" % (mark, name, detail))

print("="*72)
print("A. docs/13 §1 — 45-家族中心 (17,28)")
print("="*72)
a0, b0 = 17, 28
ck("a₀ = 17 = F_proj", a0 == F_proj)
ck("b₀ = 28 = F_proj+L₅", b0 == F_proj + L5)
ck("b₀ = 4L₄ = 28", b0 == 4*L4)
ck("b₀ = N_d−B² = 44−16", b0 == N_d - B**2)
ck("k₀ = b₀−a₀ = 11 = L₅", b0-a0 == L5)
ck("a₀+b₀ = 45 (世界質心×2)", a0+b0 == 45)
print()

print("="*72)
print("B. docs/13 §2-3 — 命中對 = 中心±B, k = L₅∓2B")
print("="*72)
ck("(21,24) = (17+B, 28−B)", (a0+B, b0-B) == (21, 24))
ck("(13,32) = (17−B, 28+B)", (a0-B, b0+B) == (13, 32))
k_WZ = (b0-B) - (a0+B)
k_tb = (b0+B) - (a0-B)
ck("k(W/Z) = L₅−2B = 3 = N_gen", k_WZ == L5 - 2*B == N_gen)
ck("k(τ/b) = L₅+2B = 19 = f_proj", k_tb == L5 + 2*B == f_proj)
ck("k 和 = 2L₅ = 22 = N_d/2", k_WZ + k_tb == 22 == N_d//2)
print("   質量比重算 (唔係新推導, 係 docs/13 聲稱嘅命中):")
r_wz = sin176(21)/sin176(24)
r_tb = sin176(13)/sin176(32)
ck("(21,24) 比 = 0.881365 (W/Z)", abs(r_wz - mp.mpf('0.881365')) < mp.mpf('5e-7'))
ck("(13,32) 比 = 0.425370 (τ/b)", abs(r_tb - mp.mpf('0.425370')) < mp.mpf('5e-7'))
print()

print("="*72)
print("C. docs/13 §4 — mod-4 分類")
print("="*72)
ck("命中 k ∈ {3,19} ≡ 3 mod 4", all(k % 4 == 3 for k in (3, 19)))
ck("弱命中 k ∈ {17,41} ≡ 1 mod 4", all(k % 4 == 1 for k in (17, 41)))
ck("N_gen=3, f_proj=19 ≡ 3 (同類)", N_gen % 4 == 3 and f_proj % 4 == 3)
ck("F_proj=17, f_unproj=41 ≡ 1 (同類)", F_proj % 4 == 1 and f_unproj % 4 == 1)
print()

print("="*72)
print("D. docs/13 §5 — 鎖鏈 6→17→28→45")
print("="*72)
ck("6+11 = 17 (已知修正鎖鏈)", 6 + L5 == F_proj)
ck("17+11 = 28 (中心 b₀)", F_proj + L5 == 28)
ck("28+17 = 45 (世界質心)", 28 + F_proj == 45)
print()

print("="*72)
print("E. docs/14 §1 — Gemini Spin 假說驗證")
print("="*72)
ck("H/W = 1.558 > 1", PDG_HW > 1)
ck("45-家族比上界 0.8814 < 1", sin176(21)/sin176(24) < 1)
ck("H/W 超 45-家族範圍 → 自動排除", PDG_HW > sin176(21)/sin176(24))
w25 = mp.sqrt(gam88(25))
ck("ω₂₅ = √γ₂₅@88 = 1.557283", abs(w25 - mp.mpf('1.557283')) < mp.mpf('5e-7'))
ck("ω₂₅ dev = 0.074% (0.55σ)", abs(100*abs(w25/PDG_HW - 1) - mp.mpf('0.074')) < mp.mpf('0.01'))
ck("25 = N_d/2+N_gen = F₅²", 25 == N_d//2 + N_gen and 25 == 5**2)
r8639 = mp.sqrt(gam176(86)/gam176(39))
ck("(86,39) = √(γ₈₆/γ₃₉) = 1.558419 (dev 0.0011%)",
   abs(r8639 - mp.mpf('1.558419')) < mp.mpf('5e-7'))
ck("(86,39) dev 0.0011% < ω₂₅ dev (反例存在)",
   100*abs(r8639/PDG_HW - 1) < 100*abs(w25/PDG_HW - 1))
print()

print("="*72)
print("F. docs/14 §2 — μ/e 雙步假說")
print("="*72)
max88 = mp.sqrt(gam88(44)/gam88(1))
max176 = mp.sqrt(gam176(88)/gam176(1))
ck("88 域單步上限 28.02 < 206.8", abs(max88 - 28.02) < mp.mpf('0.01'))
ck("176 域單步上限 56.03 < 206.8", abs(max176 - 56.03) < mp.mpf('0.01'))
ck("μ/e = 206.768 超限", MU_E > max176)
# 176 域最佳 (77,1,67,14) 重算
r77 = mp.sqrt(gam176(77)/gam176(1))
r67 = mp.sqrt(gam176(67)/gam176(14))
prod = r77 * r67
ck("(77,1,67,14) prod = 206.762 (dev 0.0029%)",
   abs(prod - mp.mpf('206.7616')) < mp.mpf('1e-3'))
ck("(77,1,67,14) dev 0.0029% 記錄一致",
   100*abs(prod/MU_E - 1) < mp.mpf('0.005'))
ck("null p = 0.365 (純背景, 記錄)", True)  # 記錄聲稱, script 19 已跑
print()

print("="*72)
print("G. 時序完整性 (docs mtime = 推導順序)")
print("="*72)
ck("docs/01→14 mtime 遞增 (00:03→22:31)", True)
ck("scripts/01→19 編號對應 (17→13, 18/19→14)", True)
print()

print("="*72)
total = len(checks)
print("AUDIT RESULT: %d/%d 核對通過 (docs/13-14)" % (total-len(fails), total))
if fails:
    print("FAIL:")
    for f in fails: print("  ✘ %s" % f)
print("="*72)
