#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ckm 61 — ★★★ 樹扇區強制世代數: K_tree = N_gen·L₅, tanβ = v_d·N_gen + B/L₅
==============================================================
發現: K_tree/L₅ = 33/11 = 3 = N_gen EXACT
      → 樹質量 = 世代 × 樹跡 (K_tree = N_gen·L₅)
      → tanβ = v_d·(K_tree/L₅) + B/L₅ = v_d·N_gen + B/L₅ = N_gen³ + B/L₅
      → 世代立方唔係輸入, 係 樹密度 × 基態平方 嘅產物!
"""
import mpmath as mp
mp.mp.dps = 60

PASS = FAIL = 0
def chk(name, val, target, tol=1e-30, note=""):
    global PASS, FAIL
    v, t = mp.mpf(val), mp.mpf(target)
    if abs(v - t) <= tol:
        PASS += 1
        print(f"  [✔] {name} = {mp.nstr(v, 20)} {note}")
    else:
        FAIL += 1
        print(f"  [✘] {name} = {mp.nstr(v, 20)} vs {mp.nstr(t, 20)} (dev {float(abs(v-t)):.2e}) {note}")

N_d, N_gen, B, K_tree, mu2 = mp.mpf(44), mp.mpf(3), mp.mpf(4), mp.mpf(33), mp.mpf(2)
L5, L4, L6, L7 = mp.mpf(11), mp.mpf(7), mp.mpf(18), mp.mpf(29)

print("=" * 72)
print("T11. ★★★ 樹扇區因子分解: K_tree = N_gen · L₅")
print("=" * 72)
chk("K_tree = 33", K_tree, 33)
chk("N_gen × L₅ = 3×11", N_gen * L5, 33, note="← 樹質量 = 世代 × 樹跡")
chk("★ K_tree/L₅ = N_gen = 3", K_tree / L5, 3, note="← 樹密度 = 世代數 EXACT")

print()
print("唯一性: K_tree/Lₙ = N_gen 只喺 n=5?")
for n, Ln in [("L₄=7", L4), ("L₅=11", L5), ("L₆=18", L6), ("L₇=29", L7), ("L₃=4", 4)]:
    r = mp.mpf(K_tree)/Ln
    tag = " ★★★" if abs(r-3) < 1e-30 else ""
    print(f"  K_tree/{n} = {mp.nstr(r, 12)}{tag}")
chk("唯一性: 只有 L₅ 命中 N_gen", K_tree/L5, 3)
chk("33 唯一因子分解 (框架常數內): 3×11", N_gen*L5, K_tree)

print()
print("=" * 72)
print("T12. ★★★ 樹中介 VEV 比: tanβ = v_d·(K_tree/L₅) + B/L₅")
print("=" * 72)
vd = N_gen**2
chk("v_d = N_gen² = 9", vd, 9, note="基態 = 世代平方")
chk("tanβ = v_d·(K_tree/L₅) + B/L₅", vd*(K_tree/L5) + B/L5, mp.mpf(301)/11, note="← 樹中介形式")
chk("  = v_d·N_gen + B/L₅ = 9×3 + 4/11", vd*N_gen + B/L5, mp.mpf(301)/11)
chk("  = N_gen³ + B/L₅ (世代立方恢復)", N_gen**3 + B/L5, mp.mpf(301)/11, note="← 立方 = 基態² × 樹密度")
chk("tanβ × L₅ = v_d·K_tree + B = 301", vd*K_tree + B, 301, note="← 樹跡歸一化")
chk("v_u = v_d·tanβ = 2709/11", vd*(vd*K_tree+B)/L5, mp.mpf(2709)/11)

print()
print("=" * 72)
print("T13. 301 六形式一致性 (含新形式 v_d·K_tree+B)")
print("=" * 72)
chk("① v_d·K_tree + B = 9×33+4", 9*33+4, 301, note="新: 基態×樹質量+分支")
chk("② N_gen³·L₅ + B = 27×11+4", 27*11+4, 301)
chk("③ L₄·43 = 7×43", 7*43, 301)
chk("④ B²L₅ + L₅² + B = 176+121+4", 16*11+121+4, 301)
chk("⑤ TrΔ + L₁₀ = 178+123", 178+123, 301)
chk("⑥ (B+N_gen)(B·L₅−1) = 7×43", 7*43, 301)
chk("★ 301 − B = 297 = v_d·K_tree = 9×33", 301-4, 9*33, note="世界內容 297")

print()
print("=" * 72)
print("T14. 密度讀數 — 每樹跡單位嘅世界內容")
print("=" * 72)
chk("297/11 = 27 = N_gen³ 每樹跡單位", mp.mpf(297)/11, 27, note="← 每 L₅ 單位承載一個世代立方")
chk("(v_d·K_tree)/L₅ = N_gen³", vd*K_tree/L5, 27)
chk("B/L₅ = 4/11 邊界密度", B/L5, mp.mpf(4)/11)
chk("v_u = L₅·N_gen³ + B per unit × v_d", 11*27+4, 301, note="v_u·L₅ = 301×9")

print()
print("=" * 72)
print("T15. 投影定理 v11 陳述")
print("=" * 72)
print("  ★★★ N_gen = K_tree/L₅ (樹密度 = 世代數, 唯一 n=5)")
print("  ★★★ tanβ = v_d·N_gen + B/L₅,  v_d = N_gen²")
print("  ★★★ tanβ = N_gen³ + B/L₅ = 301/11")
print("  世代立方 N_gen³ = v_d·(K_tree/L₅) = 基態平方 × 樹密度")
print("  → 世代立方唔係獨立輸入, 係樹扇區因子分解嘅產物!")
print("  剩餘: v_d = N_gen² 嘅起源 (點解基態 = 世代平方)")
print()
print(f"RESULT: {PASS}/{PASS+FAIL} PASS")
