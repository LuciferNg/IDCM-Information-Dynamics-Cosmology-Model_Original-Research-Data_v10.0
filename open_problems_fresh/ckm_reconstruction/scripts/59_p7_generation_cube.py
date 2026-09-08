#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ckm 59 — 世代立方形式: tanβ = N_gen³ + B/L₅ + 密度定理陳述
==============================================================
發現: B²+L₅ = 16+11 = 27 = N_gen³!
      tanβ = N_gen³ + B/L₅ = 27 + 4/11 — 世代立方 + 邊界密度
      v_u = N_gen⁵ + B·N_gen²/L₅ = 243 + 36/11 = 246.27
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
L5 = 11.0; L4 = 7.0

gams = [4*mp.sin(k*mp.pi/176)**2 for k in range(1, 89)]
tr1 = float(sum(gams)); so1 = float(sum(gams[k] for k in range(0, 88, 2)))
se1 = tr1 - so1

print("=" * 72)
print("C1. ★★ B²+L₅ = N_gen³ = 27 — 新純常數恆等式")
print("=" * 72)
chk("B²+L₅ = 16+11 = 27", B*B+L5, 27, 1e-9)
chk("★ B²+L₅ = N_gen³ = 3³", B*B+L5, N_gen**3, 1e-9, "← 世界內容 = 世代立方!")

print()
print("=" * 72)
print("C2. ★★★ tanβ = N_gen³ + B/L₅ = 27 + 4/11 (最簡形式)")
print("=" * 72)
chk("★ tanβ = N_gen³ + B/L₅", N_gen**3 + B/L5, 301/11, 1e-9,
    "← 世代立方 + 邊界分支密度")
chk("tanβ = B²+L₅+B/L₅ (v7 形式一致)", B*B+L5+B/L5, 301/11, 1e-9)
chk("tanβ = L₅ + (TrΔ+μ²)/L₅ (兩項形式一致)", L5+(tr1+mu2)/L5, 301/11, 1e-9)
chk("整數部分 27 = N_gen³, 分數部分 4/11 = B/L₅", 27+4/11, 301/11, 1e-9)

print()
print("=" * 72)
print("C3. ★★ v_u = N_gen⁵ + B·N_gen²/L₅ = 243 + 36/11")
print("=" * 72)
vd = N_gen**2
vu = vd*(N_gen**3 + B/L5)
chk("v_d = N_gen² = 9 EXACT", vd, 9, 1e-9)
chk("★ v_u = N_gen²·(N_gen³+B/L₅) = N_gen⁵ + B·N_gen²/L₅",
    N_gen**5 + B*N_gen**2/L5, vu, 1e-9, "= 243 + 36/11")
chk("★ v_u = 2L₅²+1 + B·N_gen²/L₅ (243 = 2·11²+1)", 2*L5**2+1+B*N_gen**2/L5, vu, 1e-9)
chk("v_u = 246.27 vs v·sinβ = 246.06: 0.088%", vu, 246.056, 0.002)

print()
print("=" * 72)
print("C4. ★ v_d = (L₅+L₄)/2 = 9 — Lucas 平均")
print("=" * 72)
chk("★ v_d = (L₅+L₄)/2 = (11+7)/2 = 9", (L5+L4)/2, 9, 1e-9,
    "← 連續 Lucas 跡平均")
chk("L₆ = L₅+L₄ = 18 (Lucas 遞歸)", L5+L4, 18, 1e-9)
chk("L₄ = B+N_gen = 7", L4, B+N_gen, 1e-9)
chk("v_d = (L₃²+μ²)/2 = (B²+μ²)/2 一致", (B*B+mu2)/2, 9, 1e-9)

print()
print("=" * 72)
print("C5. 301 多形式一致性")
print("=" * 72)
chk("301 = N_gen³·L₅ + B = 27×11+4", N_gen**3*L5+B, 301, 1e-9)
chk("301 = L₄·43 = 7×43", L4*43, 301, 1e-9)
chk("301 = B²L₅+L₅²+B = 176+121+4", B*B*L5+L5**2+B, 301, 1e-9)
chk("301 = TrΔ+L₁₀ = 178+123", tr1+123, 301, 1e-9)
chk("301 = (B+N_gen)(B·L₅−1) = 7×43", (B+N_gen)*(B*L5-1), 301, 1e-9)

print()
print("=" * 72)
print("C6. 密度定理陳述 (P7-T8)")
print("=" * 72)
print("  ★★★ tanβ = N_gen³ + B/L₅")
print("    = 世代立方 (世界內容: B²+L₅) + 邊界分支密度 (B/L₅)")
print("  v_d = N_gen² (世代平方)")
print("  v_u = N_gen⁵ + B·N_gen²/L₅ (世代五方 + 邊界×世代²/樹跡)")
print("  已證: 世代立方形式 (C1-C2); v_u 世代五方 (C3); Lucas 平均 v_d (C4);")
print("        301 五形式一致 (C5)")
print("  未證: 幾何強制 — 點解 VEV 比 = 世界內容 + 邊界密度")
print("  密度解讀: 一個樹跡單位 (L₅ = 11) 承載 N_gen³ 個世代立方單元")
print("            + 每樹跡單位嘅 B 個分支 — 即 v_u/v_d 係")
print("            「單位樹跡嘅世界生成內容」嘅密度比")
print()
print(f"RESULT: {PASS}/{PASS+FAIL} PASS")
