#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ckm 58 — 純常數表閉環: B/L/μ² 語言完整表格 + 世界質心連接 + 投影定理 v7
==============================================================
發現: Σγ_even = 2(BL₅+1) = 2×45 = 2×世界質心 (O158)
      B²L₅+B = TrΔ+μ² = 180 — 世界+B = 鏈跡+邊界
      tanβ = L₅ + (TrΔ+μ²)/L₅ — 三層坍縮為兩項
"""
import mpmath as mp
mp.mp.dps = 60

PASS = FAIL = 0
def chk(name, val, target, tol, note=""):
    global PASS, FAIL
    val_f = float(val); tgt = float(target)
    dev = abs(val_f-tgt)/abs(tgt)*100 if abs(tgt) > 1e-30 else abs(val_f-tgt)*100
    ok = abs(val_f - tgt) <= tol * max(1.0, abs(tgt)) if abs(tgt) > 1e-30 else abs(val_f) <= tol
    if ok:
        PASS += 1
        print(f"  [✔] {name} = {val_f:.9f}  (dev {dev:+.4f}%) {note}")
    else:
        FAIL += 1
        print(f"  [✘] {name} = {val_f:.9f} vs {tgt}  (dev {dev:+.4f}%) {note}")

N_d, N_gen, B, K_tree, mu2 = 44, 3, 4, 33, 2.0
L5 = 11.0

gams = [4*mp.sin(k*mp.pi/176)**2 for k in range(1, 89)]
odd  = [gams[k] for k in range(0, 88, 2)]
even = [gams[k] for k in range(1, 88, 2)]
tr1 = float(sum(gams)); so1 = float(sum(odd)); se1 = float(sum(even))
det_odd  = float(mp.e**sum(mp.log(g) for g in odd))
det_even = float(mp.e**sum(mp.log(g) for g in even))

print("=" * 72)
print("C1. ★★ 純常數表 — 全鏈/樹量喺 {B, L₅, μ²} 語言")
print("=" * 72)
chk("Σγ_odd  = 2B·L₅ = 2×44 = 88", so1, 2*B*L5, 1e-9)
chk("Σγ_even = 2B·L₅+μ² = 88+2 = 90", se1, 2*B*L5+mu2, 1e-9)
chk("TrΔ = B²·L₅+μ² = 176+2 = 178", tr1, B*B*L5+mu2, 1e-9)
chk("det_even = B²·L₅ = 176", det_even, B*B*L5, 1e-6)
chk("det_odd = μ² = 2", det_odd, mu2, 1e-6)
chk("L₁₀ = L₅²+μ² = 121+2 (Lucas 倍角)", 123, L5**2+mu2, 1e-9)
chk("301 = B²L₅+L₅²+B = 176+121+4", B*B*L5+L5**2+B, 301, 1e-9)

print()
print("=" * 72)
print("C2. ★★ 世界質心連接: 45 = B·L₅+1 = C(10,2) (O158)")
print("=" * 72)
chk("★ 45 = B·L₅+1 = 44+1 (世界質心 O158)", B*L5+1, 45, 1e-9)
chk("★ 45 = C(2F₅,2) = C(10,2)", 10*9//2, 45, 0)
chk("★ Σγ_even = 2(B·L₅+1) = 2×45 = 2×世界質心", se1, 2*(B*L5+1), 1e-9)
chk("Σγ_odd = 2B·L₅ = 2×44 (質心−1)", so1, 2*(B*L5+1)-2, 1e-9)

print()
print("=" * 72)
print("C3. ★★ B²L₅+B = TrΔ+μ² = 180 — 世界+B = 鏈跡+邊界")
print("=" * 72)
chk("★ B²L₅+B = B(BL₅+1) = 4×45 = 180", B*(B*L5+1), 180, 1e-9)
chk("★ B²L₅+B = TrΔ+μ² = 178+2 = 180", B*B*L5+B, tr1+mu2, 1e-9)
chk("★ 2Σγ_even = TrΔ+μ² = 180", 2*se1, tr1+mu2, 1e-9)
chk("★ 180 = 2×90 = 2Σγ_even", 2*se1, 180, 1e-9)

print()
print("=" * 72)
print("C4. ★ tanβ 兩項形式: L₅ + (TrΔ+μ²)/L₅ = 11 + 180/11")
print("=" * 72)
chk("★ tanβ = L₅ + (TrΔ+μ²)/L₅ = 11+180/11", L5+(tr1+mu2)/L5, 301/11, 1e-9,
    "← 樹跡 + 全鏈跡(含邊界)/樹跡")
chk("tanβ = L₅ + 2Σγ_even/L₅ = 11+180/11", L5+2*se1/L5, 301/11, 1e-9,
    "← 樹跡 + 2×世界譜和/樹跡")
chk("tanβ = (B²L₅+L₅²+B)/L₅ (v7 純常數)", (B*B*L5+L5**2+B)/L5, 301/11, 1e-9)

print()
print("=" * 72)
print("C5. m_t/m_b B-形式一致性 (form-grade)")
print("=" * 72)
chk("m_t/m_b ≈ BL₅−N_gen+½ = 44−3+0.5 = 41.5 (0.048%)", 41.5, 41.4802, 0.02,
    "form-grade — B/L 語言一致但唔宣稱")
chk("m_t/m_b = 83/2, 83 = 2BL₅−2N_gen+1", 2*B*L5-2*N_gen+1, 83, 1e-9)

print()
print("=" * 72)
print("C6. 投影定理 v7 — 兩項形式陳述")
print("=" * 72)
print("  ★★ 核心: tanβ = L₅ + (TrΔ+μ²)/L₅")
print("    = 樹跡 + (世界譜和 + 觀察者譜和 + 邊界成本)/樹跡")
print("    = 樹跡 + (2×世界質心×2)/樹跡  [2Σγ_even = 4×45]")
print("  已證: 純常數表閉環 (C1); 世界質心連接 (C2); 180 四重身份 (C3);")
print("        兩項形式 (C4); m_t/m_b B-語言一致 (C5)")
print("  未證: 幾何強制 — 點解 VEV 比 = 樹跡 + 全鏈跡/樹跡")
print()
print(f"RESULT: {PASS}/{PASS+FAIL} PASS")
