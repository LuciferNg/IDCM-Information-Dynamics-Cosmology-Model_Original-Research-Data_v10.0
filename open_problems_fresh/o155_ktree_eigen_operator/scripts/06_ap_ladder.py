#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
06_ap_ladder.py — R4: AP {6,11,16,21} 作為 K_tree 不變量 (K_Tree 本徵算子化)
=============================================================================
問題 (O155 R4): AP {6, 11, 16, 21} 作為 K_tree 不變量 — 公差 5 = F₅ =
L₅−2N_gen = B²−L₅ 嘅算子來源; 下一項 21 = F₈ 嘅終止 (O152 R14 對照:
k-ladder 終止 F₁₀ = 55 > N_d−1 = 43)。

T̂ 算子讀法 (R1 延續):
  6  = 2N_gen = 2F₄ = 2(T̂⁴)₁₂            (種子 = 世代數 × 2)
  11 = L₅ = Tr(T̂⁵)                        (Lucas trace)
  16 = B² = Tr(T̂⁵) + (T̂⁵)₁₂ = 11 + 5     (分支平方 = trace + 離對角)
  21 = F₈ = Σ entries(T̂⁵) = F_{5+3}       (T̂⁵ 總和 = F₈)
公差 5 = F₅ = (T̂⁵)₁₂。

檢驗:
C1. {2N_gen, L₅, B², F₈} = {6,11,16,21} 等差, 公差 5 = F₅
C2. AP = {2F₄ + k·F₅, k=0..3}; 項數 = 4 = B
C3. T̂-形式: 6 = 2(T̂⁴)₁₂, 11 = Tr(T̂⁵), 16 = Tr(T̂⁵)+(T̂⁵)₁₂, 21 = Σ(T̂⁵)
C4. Pair 對稱: 6+21 = 11+16 = 27 = N_gen³; Σ = 54 = N_gen·L₆
C5. 乘積身份: 6·11 = 66 = 2K_tree; 11·16 = 176 = 2N; 11·21 = 231 = K_tree·L₄;
    6·21 = 126 = N_gen·N_d⁻
C6. 終止規則: 第 5 項 = 26 = 2F₇ (k_d Casimir 26β); F₉ = 34 = K_tree+1 封頂;
    O152 R14 對照 (F₁₀ = 55 > N_d−1 = 43)
C7. 5-step 嵌入 δ_CKM: 21 = B²+F₅ = F₈, 9 = N_gen²; δ_CKM = atan(ω₂₁/ω₉) = 66.399960°
"""
import mpmath as mp
mp.mp.dps = 50

def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def luc(n):
    return fib(n - 1) + fib(n + 1)

N, KTREE, B, Ngen, L5, Nd, Ndm = 88, 33, 4, 3, 11, 44, 42
F5, F7, F8, F9, F10 = fib(5), fib(7), fib(8), fib(9), fib(10)

passes = []
def check(name, cond, detail=""):
    passes.append(cond)
    print(f"   [{'PASS' if cond else 'FAIL'}] {name} {detail}")

print("C1) AP {2N_gen, L₅, B², F₈} = {6,11,16,21}")
a = [2 * Ngen, luc(5), B**2, fib(8)]
ok = a == [6, 11, 16, 21]
check("成員精確", ok, f"{a}")
diffs = [a[i+1] - a[i] for i in range(3)]
ok = diffs == [5, 5, 5]
check("公差 = 5 = F₅ = L₅−2N_gen = B²−L₅", ok, f"diffs={diffs}")

print("\nC2) AP = {2F₄ + k·F₅, k=0..3}, 項數 = 4 = B")
gen = [2 * fib(4) + k * fib(5) for k in range(4)]
ok = gen == a
check("k=0..3 生成, 4 = B 項", ok, f"{gen}")

print("\nC3) T̂-形式 (全部 = T̂ 量)")
ok1 = a[0] == 2 * fib(4)
ok2 = a[1] == luc(5)
ok3 = a[2] == luc(5) + fib(5)
ok4 = a[3] == fib(6) + 2 * fib(5) + fib(4)   # Σ entries T̂⁵
check("6 = 2(T̂⁴)₁₂ = 2F₄", ok1)
check("11 = Tr(T̂⁵) = L₅", ok2)
check("16 = Tr(T̂⁵)+(T̂⁵)₁₂ = L₅+F₅ = B²", ok3)
check("21 = Σ(T̂⁵) = F₈", ok4, f"8+5+5+3=21")

print("\nC4) Pair 對稱: 6+21 = 11+16 = 27 = N_gen³; Σ = 54 = N_gen·L₆")
ok1 = (a[0] + a[3]) == (a[1] + a[2]) == Ngen**3
check("6+21 = 11+16 = 27 = N_gen³", ok1, f"{a[0]+a[3]} = {a[1]+a[2]} = {Ngen**3}")
ok2 = sum(a) == Ngen * luc(6)
check("Σ AP = 54 = N_gen·L₆ (L₆ = 18)", ok2, f"Σ={sum(a)}, {Ngen}*{luc(6)}={Ngen*luc(6)}")

print("\nC5) 乘積身份")
ok1 = a[0] * a[1] == 66
check("6·11 = 66 = 2K_tree = Σλ_tree (R3)", ok1, f"{a[0]}*{a[1]}={a[0]*a[1]}")
ok2 = a[1] * a[2] == 176
check("11·16 = 176 = 2N (dual chain)", ok2, f"{a[1]}*{a[2]}={a[1]*a[2]}")
ok3 = a[1] * a[3] == KTREE * luc(4)
check("11·21 = 231 = K_tree·L₄ = δ+1 (R6)", ok3, f"{a[1]}*{a[3]}={a[1]*a[3]}")
ok4 = a[0] * a[3] == Ngen * Ndm
check("6·21 = 126 = N_gen·N_d⁻", ok4, f"{a[0]}*{a[3]}={a[0]*a[3]}")

print("\nC6) 終止規則")
n5 = a[3] + fib(5)
ok1 = n5 == 2 * F7
check("第 5 項 = 26 = 2F₇ (k_d Casimir 26β 係數)", ok1, f"{n5} = 2*{F7}")
ok2 = F9 == KTREE + 1
check("F₉ = 34 = K_tree+1 封頂 (首個 ≥ K_tree 嘅 Fib 項)", ok2)
ok3 = F10 > Nd - 1
check("O152 R14 對照: F₁₀ = 55 > N_d−1 = 43 (k-ladder 終止)", ok3,
      f"{F10} > {Nd-1}")
print(f"   → AP 最尾可容許 Fib 項 = F₈ = 21 < F₉ = 34 = K_tree+1")

print("\nC7) 5-step 嵌入 δ_CKM")
# CKM beat 慣例: ω_k = 2sin(kπ/176) (176-Laplacian 譜根, 同 scripts/02 一致)
omega = lambda k: 2 * mp.sin(k * mp.pi / 176)
d_ckm = mp.degrees(mp.atan(omega(21) / omega(9)))
ok1 = 21 == B**2 + F5 == F8 and 9 == Ngen**2
check("21 = B²+F₅ = F₈, 9 = N_gen²", ok1)
ok2 = mp.fabs(d_ckm - mp.mpf('66.3999600507')) < mp.mpf('1e-6')
check("δ_CKM = atan(ω₂₁/ω₉) = 66.399960°", ok2, f"={mp.nstr(d_ckm, 12)}°")

total = len(passes)
print(f"\nRESULT: {sum(passes)}/{total} PASS")
exit(0 if all(passes) else 1)
