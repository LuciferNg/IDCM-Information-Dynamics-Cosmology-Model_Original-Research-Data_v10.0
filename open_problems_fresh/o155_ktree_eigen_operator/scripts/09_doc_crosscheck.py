#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
09_doc_crosscheck.py — 獨立文檔核對 (O153 審計模式)
====================================================
從零重算 docs/00-06 嘅 headline 公式/數值 (mpmath 50 dps), 唔依賴 scripts/03-08 輸出。
目的: 捉 doc 入面嘅錯 (包括自己寫錯嘅)。

C1.  docs/01: T̂³³ 條目 + mod-33 同餘族 [[25,13],[13,12]], L₃₃≡4, F₃₆≡30
C2.  docs/01: K_tree = F₄·L₅ = 33; F₉−1 = 33; 176 = 11·16; 231 = 33·7 = 11·21; 126 = 3·42
C3.  docs/02: 1+...+33 = 561 = 33·17; mean = 17; 1/33 + 32/33 = 1
C4.  docs/03: Σ_{k=1}^{33} 4sin²(kπ/68) = 66; Tr(Dir)−Tr(Neu) = 2; Σγ_even = 90, Σγ_odd = 88
C5.  docs/04: AP diffs = 5; 6+21 = 11+16 = 27; Σ = 54; 乘積 66/176/231/126
C6.  docs/05: tan((β+1/33)/(1−β/33)) 形式 = (33+φ)/(33φ−1); ε·32/33 = 0.14982642
C7.  docs/06: δ = (33+13)(11−6) = 230; (34−1+13)·5 = 230; 11·21−1 = 230; 176+54 = 230;
    J_CP(結構角度, δ=230°) = 0.0255 vs 0.0254 (0.4%)
"""
import mpmath as mp
import math
mp.mp.dps = 50

passes = []
def check(name, cond, detail=""):
    passes.append(cond)
    print(f"   [{'PASS' if cond else 'FAIL'}] {name} {detail}")

def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def luc(n):
    return fib(n - 1) + fib(n + 1)

phi = (1 + mp.sqrt(5)) / 2
beta = 1 / phi

print("C1) docs/01: T̂³³ 同餘族")
F32, F33, F34 = fib(32), fib(33), fib(34)
r = (F34 % 33, F33 % 33, F33 % 33, F32 % 33)
check("T̂³³ mod 33 = (25,13,13,12)", r == (25, 13, 13, 12), f"{r}")
check("25 = F₅², 13 = F₇, 12 = L₅+1", (25, 13, 12) == (fib(5)**2, fib(7), luc(5)+1))
check("L₃₃ mod 33 = 4 = B", luc(33) % 33 == 4, f"{luc(33) % 33}")
check("F₃₆ mod 33 = 30", fib(36) % 33 == 30, f"{fib(36) % 33}")

print("\nC2) docs/01: tree 常數乘積")
check("K_tree = F₄·L₅ = 33", fib(4)*luc(5) == 33, f"{fib(4)}*{luc(5)}={fib(4)*luc(5)}")
check("K_tree = F₉−1 = 33", fib(9)-1 == 33)
check("L₅·B² = 176", luc(5)*16 == 176)
check("L₅·F₈ = K_tree·L₄ = 231", luc(5)*fib(8) == 231 == 33*luc(4))
check("2N_gen·F₈ = 126 = 3·42", 2*3*fib(8) == 126 == 3*42)

print("\nC3) docs/02: height operator")
s = sum(range(1, 34))
check("Σ1..33 = 561 = 33·17", s == 561 == 33*17, f"{s}")
check("mean = 17", s/33 == 17.0)
check("1/33+32/33 = 1", mp.mpf(1)/33 + mp.mpf(32)/33 == 1)

print("\nC4) docs/03: Laplacian")
sm = mp.nsum(lambda k: 4*mp.sin(mp.pi*k/68)**2, [1, 33])
check("Σ4sin²(kπ/68) = 66", mp.fabs(sm-66) < mp.mpf('1e-30'), f"{mp.nstr(sm,15)}")
sE = sum(4*mp.sin(mp.pi*k/176)**2 for k in range(2, 89, 2))
sO = sum(4*mp.sin(mp.pi*k/176)**2 for k in range(1, 88, 2))
check("Σγ_even = 90, Σγ_odd = 88", mp.fabs(sE-90) < 1e-30 and mp.fabs(sO-88) < 1e-30,
      f"E={mp.nstr(sE,12)}, O={mp.nstr(sO,12)}")
check("E−O = 2 = 66−64", mp.fabs((sE-sO)-2) < 1e-30 and mp.fabs((sE-sO)-(66-64)) < 1e-30)

print("\nC5) docs/04: AP")
a = [2*3, luc(5), 16, fib(8)]
check("AP diffs = 5", [a[i+1]-a[i] for i in range(3)] == [5, 5, 5])
check("6+21 = 11+16 = 27", a[0]+a[3] == a[1]+a[2] == 27)
check("Σ = 54 = 3·18", sum(a) == 54 == 3*luc(6))
check("乘積 66/176/231/126", a[0]*a[1] == 66 and a[1]*a[2] == 176 and a[1]*a[3] == 231 and a[0]*a[3] == 126)

print("\nC6) docs/05: channel")
lhs = mp.atan((33+phi)/(33*phi-1))
rhs = mp.atan(beta) + mp.atan(mp.mpf(1)/33)
check("atan((33+φ)/(33φ−1)) = atan(β)+atan(1/33)", mp.fabs(lhs-rhs) < mp.mpf('1e-40'))
tadd = (beta + mp.mpf(1)/33) / (1 - beta/33)
check("tan 加法 = (33+φ)/(33φ−1)", mp.fabs(tadd - (33+phi)/(33*phi-1)) < mp.mpf('1e-40'))
e = beta/4
check("ε·32/33 = 0.1498264215", mp.fabs(e*mp.mpf(32)/33 - mp.mpf('0.14982642151513')) < mp.mpf('1e-12'))

print("\nC7) docs/06: δ = 230°")
check("(33+13)(11−6) = 230", (33+13)*(11-6) == 230)
check("(34−1+13)·5 = 230", (34-1+13)*5 == 230)
check("11·21−1 = 230", 11*21-1 == 230)
check("33·7−1 = 230", 33*7-1 == 230)
check("176+54 = 230", 176+54 == 230)
# J_CP: 結構角度 + δ=230°
omega = lambda k: 2*math.sin(k*math.pi/88)
bf = (math.sqrt(5)-1)/2
t12 = math.degrees(math.atan(bf)) + math.degrees(math.atan(1/33))
t23 = math.degrees(math.atan(omega(7)/omega(6)))
t13 = math.degrees(math.asin((bf/4)*(32/33)))
s1, s2, s3 = map(lambda x: math.sin(math.radians(x)), (t12, t23, t13))
c1, c2, c3 = map(lambda x: math.cos(math.radians(x)), (t12, t23, t13))
J = s1*s2*s3*c1*c2*c3*c3*math.sin(math.radians(230))
rel = abs(abs(J) - 0.0254)/0.0254
check("J_CP = 0.0255 (0.4%)", rel < 0.01, f"J_CP={abs(J):.4f}, Δ={rel*100:.1f}%")

total = len(passes)
print(f"\nRESULT: {sum(passes)}/{total} PASS")
exit(0 if all(passes) else 1)
