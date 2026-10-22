#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
03_t_operator_algebra.py — R1: T̂ 算子代數 (K_Tree 本徵算子化)
================================================================
問題 (O155 R1): T̂ 譜 {phi, -1/phi} <-> 33-level tree 嘅算子身份。
T̂^33 = ? Fibonacci at depth 33; Lucas/Fibonacci 階梯 (O142) 喺 T̂ 表示嘅封閉形式。

檢驗:
C1. T̂^n = [[F_{n+1}, F_n], [F_n, F_{n-1}]]  n=1..40 (精確整數)
C2. T̂^33 條目: F_34=5702887, F_33=3524578, F_32=2178309
C3. Lucas 階梯: L_n = Tr(T̂^n); L_4=7, L_5=11, L_6=18, L_7=29, L_8=47 (O142 慣例)
C4. Binet 閉合形式: F_n = (phi^n - (-phi)^-n)/sqrt(5), L_n = phi^n + (-phi)^-n
C5. K_tree = (T̂^9)_12 - 1 = F_9 - 1 = 33  (9 = N_gen^2 = 3^2)
C6. K_tree = (T̂^4)_12 * Tr(T̂^5) = 3 * 11 = 33  (F_4 = N_gen)
C7. Depth-33 同餘 (mod K_tree=33): T̂^33 ≡ [[F_5^2, F_7],[F_7, L_5+1]] = [[25,13],[13,12]]
    Tr(T̂^33) ≡ 4 = B;  sum(T̂^33) ≡ 30 = 2N_gen * F_5
C8. Sum entries T̂^n = F_{n+3}  n=1..20
C9. 跨維度乘積: L_5*B^2 = 176 = 2N (dual chain); 2N_gen*L_5 = 66 = 2K_tree; L_5*F_8 = 231 = K_tree*L_4
C10. F_33 = F_11*(L_11^2+1)  (模算術分解一致性)
"""
import mpmath as mp
mp.mp.dps = 50

def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def luc(n):                     # L_n = F_{n-1} + F_{n+1} (O142: L0=2, L1=1)
    return fib(n - 1) + fib(n + 1)

phi = (1 + mp.sqrt(5)) / 2
N, KTREE, B, Ngen, L5 = 88, 33, 4, 3, 11

passes = []
def check(name, cond, detail=""):
    passes.append(cond)
    print(f"   [{'PASS' if cond else 'FAIL'}] {name} {detail}")

print("C1) T̂^n = [[F_{n+1},F_n],[F_n,F_{n-1}]]  n=1..40")
ok = True
for n in range(1, 41):
    M = [[fib(n + 1), fib(n)], [fib(n), fib(n - 1)]]
    if M != [[1, 1], [1, 0]] and n == 1:
        pass
    # 直接用矩陣乘法驗證
    T = [[1, 1], [1, 0]]
    Mn = [[1, 0], [0, 1]]
    for _ in range(n):
        Mn = [[Mn[0][0]*T[0][0]+Mn[0][1]*T[1][0], Mn[0][0]*T[0][1]+Mn[0][1]*T[1][1]],
              [Mn[1][0]*T[0][0]+Mn[1][1]*T[1][0], Mn[1][0]*T[0][1]+Mn[1][1]*T[1][1]]]
    if Mn != M:
        ok = False
        break
check("n=1..40", ok)
print(f"   T̂^5 = [[F_6,F_5],[F_5,F_4]] = [[{fib(6)},{fib(5)}],[{fib(5)},{fib(4)}]]  sum={fib(6)+2*fib(5)+fib(4)}")

print("\nC2) T̂^33 條目 (深度 = K_tree)")
e = [fib(34), fib(33), fib(33), fib(32)]
ok = e == [5702887, 3524578, 3524578, 2178309]
check("T̂^33 = [[5702887,3524578],[3524578,2178309]]", ok)

print("\nC3) Lucas 階梯 L_n = Tr(T̂^n)")
ok = all(luc(n) == fib(n - 1) + fib(n + 1) and luc(n) == fib(n+1) + fib(n-1) for n in range(1, 41))
L = {n: luc(n) for n in [4, 5, 6, 7, 8]}
ok2 = L[4] == 7 and L[5] == 11 and L[6] == 18 and L[7] == 29 and L[8] == 47
check("L_n = F_{n-1}+F_{n+1} n=1..40", ok)
check("L_4=7 L_5=11 L_6=18 L_7=29 L_8=47", ok2, f"L={L}")

print("\nC4) Binet 閉合形式 (mpmath 50 dps)")
ok = True
for n in range(1, 41):
    Fb = (phi**n - (-phi)**(-n)) / mp.sqrt(5)
    Lb = phi**n + (-phi)**(-n)
    if mp.fabs(Fb - fib(n)) > mp.mpf('1e-40') or mp.fabs(Lb - luc(n)) > mp.mpf('1e-40'):
        ok = False
        break
check("F_n, L_n Binet 50-dps 閉合形式", ok)

print("\nC5) K_tree = (T̂^9)_12 - 1 = F_9 - 1 = 33  (9 = N_gen^2)")
ok = (fib(9) - 1) == KTREE and (fib(Ngen**2) - 1) == KTREE
check("F_9 - 1 = 33", ok, f"F_9={fib(9)}, 9=N_gen^2={Ngen**2}")

print("\nC6) K_tree = (T̂^4)_12 * Tr(T̂^5) = 3 * 11 = 33")
ok = (fib(4) * luc(5)) == KTREE
check("F_4 * L_5 = 33", ok, f"F_4={fib(4)}=N_gen, L_5={luc(5)}")

print("\nC7) Depth-33 同餘 mod K_tree = 33")
r34, r33, r32 = fib(34) % 33, fib(33) % 33, fib(32) % 33
ok1 = (r34, r33, r33, r32) == (25, 13, 13, 12)
check("T̂^33 mod 33 = [[25,13],[13,12]]", ok1,
      f"= [[F_5^2={fib(5)**2}, F_7={fib(7)}],[F_7, L_5+1={luc(5)+1}]]")
ok2 = luc(33) % 33 == 4
check("Tr(T̂^33) mod 33 = 4 = B", ok2, f"L_33={luc(33)} mod 33 = {luc(33) % 33}")
ok3 = (sum([r34, r33, r33, r32])) % 33 == 30
check("sum(T̂^33) mod 33 = 30 = 2N_gen*F_5", ok3,
      f"F_36={fib(36)} mod 33 = {fib(36) % 33}")

print("\nC8) Sum entries T̂^n = F_{n+3}")
ok = all((fib(n + 1) + 2 * fib(n) + fib(n - 1)) == fib(n + 3) for n in range(1, 21))
check("n=1..20", ok)

print("\nC9) 跨維度乘積 (tree 常數 -> chain 維度)")
ok1 = (luc(5) * B**2) == 176
check("L_5 * B^2 = 176 = 2N", ok1, f"{luc(5)}*{B**2}={luc(5)*B**2}")
ok2 = (2 * Ngen * luc(5)) == 66
check("2N_gen * L_5 = 66 = 2K_tree", ok2, f"2*{Ngen}*{luc(5)}={2*Ngen*luc(5)}")
ok3 = (luc(5) * fib(8)) == 231 == (KTREE * luc(4))
check("L_5 * F_8 = K_tree * L_4 = 231 = δ+1", ok3,
      f"{luc(5)}*{fib(8)}={luc(5)*fib(8)}, {KTREE}*{luc(4)}={KTREE*luc(4)}")
ok4 = (2 * Ngen * fib(8)) == 126 == (Ngen * 42)
check("2N_gen * F_8 = 126 = N_gen*N_d⁻", ok4, f"2*{Ngen}*{fib(8)}={2*Ngen*fib(8)}")

print("\nC10) F_33 = F_11 * (L_11^2 + 1)  (模算術分解)")
ok = fib(33) == fib(11) * (luc(11)**2 + 1)
check("F_33 = 89*(199^2+1)", ok, f"F_33={fib(33)}, F_11={fib(11)}, L_11={luc(11)}")
print(f"   F_33 mod 33 = {fib(33) % 33} = F_7 = {fib(7)}  (C7 同餘來源)")

total = len(passes)
print(f"\nRESULT: {sum(passes)}/{total} PASS")
exit(0 if all(passes) else 1)
