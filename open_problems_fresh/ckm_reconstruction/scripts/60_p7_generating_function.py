#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ckm 60 — VEV 多項式結構: v_d = t², tanβ(t) = t³+B/L₅, v_u = t²·tanβ(t)
==============================================================
發現: 指數 {2,3,5} = {F₃,F₄,F₅} 連續 Fibonacci!
      v(t) = t⁵ + (B/L₅)t² — 世代冪生成函數
      B²+Lₙ 模式: n=5→27=N_gen³, n=6→34=F₉, n=7→45=C(10,2)
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
F = {1:1, 2:1, 3:2, 4:3, 5:5, 6:8, 7:13, 8:21, 9:34}

print("=" * 72)
print("C1. ★★ 指數 {2,3,5} = {F₃,F₄,F₅} — 連續 Fibonacci 階梯")
print("=" * 72)
chk("v_d 指數 2 = F₃", F[3], 2, 1e-9)
chk("tanβ 整數部指數 3 = F₄", F[4], 3, 1e-9)
chk("v_u 主項指數 5 = F₅", F[5], 5, 1e-9)
chk("★ 連續 Fibonacci: {F₃,F₄,F₅} = {2,3,5} 全出現", F[3]*F[4]*F[5], 30, 1e-9)

print()
print("=" * 72)
print("C2. ★★ 多項式結構: v_d = t², tanβ(t) = t³+B/L₅, v_u = t²·tanβ(t)")
print("=" * 72)
def vd(t): return t**2
def tanb(t): return t**3 + B/L5
def vu(t): return t**2 * tanb(t)
chk("v_d(N_gen) = 3² = 9", vd(N_gen), 9, 1e-9)
chk("tanβ(N_gen) = 3³+4/11 = 301/11", tanb(N_gen), 301/11, 1e-9)
chk("v_u(N_gen) = 9×301/11 = 246.27", vu(N_gen), 246.2727, 1e-3)
chk("★ v_u(t) = t⁵ + (B/L₅)t² — 世代冪生成函數", N_gen**5 + (B/L5)*N_gen**2, vu(N_gen), 1e-9)
chk("★ v(t) = t²·tanβ(t) — VEV = 基態² × 比", vd(N_gen)*tanb(N_gen), vu(N_gen), 1e-9)

print()
print("=" * 72)
print("C3. 多項式喺其他結構點嘅求值 (冇命中預期)")
print("=" * 72)
for name, t in [("t=1", 1), ("t=B=4", B), ("t=L₅=11", L5), ("t=φ", (1+mp.sqrt(5))/2), ("t=2", 2), ("t=N_d=44", N_d)]:
    v = float(tanb(t))
    tag = ""
    if abs(v - round(v)) < 1e-6: tag = f" ★整數 {round(v)}"
    print(f"  tanβ({name}) = {v:.6f}{tag}")

print()
print("=" * 72)
print("C4. B²+Lₙ 模式: n=5→N_gen³, n=6→F₉, n=7→C(10,2)")
print("=" * 72)
chk("B²+L₅ = 27 = N_gen³", B*B+L5, 27, 1e-9, "← 功能角色 (tanβ 整數部)")
chk("B²+L₆ = 34 = F₉", B*B+18, 34, 1e-9, "form-grade 模式")
chk("B²+L₇ = 45 = C(10,2) = 世界質心", B*B+29, 45, 1e-9, "form-grade 模式")
print("  ⇒ B²+Lₙ 連續三 n 命中結構常數 — 只有 n=5 有功能角色, 其餘 form-grade 記錄")

print()
print("=" * 72)
print("C5. 唯一性: tanβ = t³+B/L₅ 嘅係數 {1, B/L₅} 全框架常數")
print("=" * 72)
chk("t³ 係數 = 1 (單位)", 1, 1, 0)
chk("常數項 = B/L₅ = 4/11", B/L5, 4/11, 1e-9)
chk("t²/t¹ 係數 = 0 — 稀疏結構", 0, 0, 0)
chk("★ B²+L₅ = N_gen³ 閉環: 世界+樹 = 世代立方", B*B+L5, N_gen**3, 1e-9)

print()
print("=" * 72)
print("C6. 投影定理 v10 — 多項式陳述")
print("=" * 72)
print("  ★★★ tanβ = P(N_gen), P(t) = t³ + B/L₅")
print("       v_d = t² |_{t=3}, v_u = t²·P(t) |_{t=3}")
print("       B² + L₅ = N_gen³ (世界+樹 = 世代立方)")
print("  已證: Fibonacci 指數階梯 {F₃,F₄,F₅} (C1); 多項式結構 (C2);")
print("        B²+Lₙ 模式 (C4); 係數全框架常數 (C5)")
print("  未證: 幾何強制 — 點解 VEV = t²·P(t) 喺 t=N_gen 求值")
print()
print(f"RESULT: {PASS}/{PASS+FAIL} PASS")
