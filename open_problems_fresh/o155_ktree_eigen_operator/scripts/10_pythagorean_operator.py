#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
10_pythagorean_operator.py — R7: 33-44-55 Pythagorean 閉合 (納入 O156 結果)
============================================================================
O156 (θ₂₃ 尺度流) 發現: 33² + 44² = 55² EXACT — (N_gen, B, F₅) = (3,4,5)
primitive Pythagorean ×L₅ → (K_tree, N_d, F₁₀)。O156 只做尺度層, 算子化交 O155。

本 script: O155 算子級驗證 + 與 R1-R6 交叉連接。

檢驗:
C1. 原始三元組 (N_gen, B, F₅) = (3,4,5): 3²+4² = 5², gcd = 1 (primitive)
C2. ×L₅: (K_tree, N_d, F₁₀) = (33, 44, 55); 33²+44² = 55² EXACT
C3. T̂ 形式: F₄ = N_gen, F₅ = (T̂⁵)₁₂, F₁₀ = (T̂¹⁰)₁₂ = 55; K_tree = F₄·L₅ (R1 一致);
    10 = L₅−1 = 2F₅
C4. AP 讀法: (33, 44, 55) = K_tree + k·L₅ (k=0,1,2) — Pythagorean 三元組 = L₅-step AP
C5. 尺度塔: {176, 88, 55, 44, 33, 22, 11} = L₅×{16, 8, 5, 4, 3, 2, 1}
C6. θ₂₃ home = 55 (O156): θ(55) = atan(sin(7π/55)/sin(6π/55)) = 49.1966° vs NuFIT 49.1980°
    (0.003%); θ(88) = 49.3202° (0.25%) — 86× 改善
C7. Sector 分離: CKM 留 88 (δ_CKM(55) = 62.18° 破壞 1e-9); 質量留 88 (γ₇(55) = 0.6061
    破壞 m_μ 0.13%) — 55 只係 θ₂₃ 嘅家
C8. 終止幾何 (O152 R14 升級): k-ladder 終止 F₁₀ = 55 > 43 = N_d−1; 55 = √(K_tree²+N_d²)
    — ladder 頂 = tree×world 維度嘅幾何斜邊
C9. 55 雙重身份: F₁₀ = (T̂¹⁰)₁₂ = C(L₅,2) = N_d+L₅ (O152 T7) = √(K_tree²+N_d²) (O156)
C10. R4 連接: 原始斜邊 5 = F₅ = (T̂⁵)₁₂ = AP 公差 (R4) — AP 階梯同 Pythagorean 共享 5
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

import math
KTREE, Nd, L5, Ngen, B = 33, 44, 11, 3, 4
F4, F5, F8, F9, F10 = fib(4), fib(5), fib(8), fib(9), fib(10)

passes = []
def check(name, cond, detail=""):
    passes.append(cond)
    print(f"   [{'PASS' if cond else 'FAIL'}] {name} {detail}")

print("C1) 原始三元組 (N_gen, B, F₅) = (3,4,5)")
ok1 = 3**2 + 4**2 == 5**2
ok2 = math.gcd(3, 4) == 1 and math.gcd(3, 5) == 1
check("3²+4² = 5²", ok1)
check("gcd(3,4,5) = 1 (primitive)", ok2)
check("成員 = (F₄, B, F₅)", (F4, B, F5) == (3, 4, 5), f"F₄={F4}, B={B}, F₅={F5}")

print("\nC2) ×L₅ → (K_tree, N_d, F₁₀) = (33, 44, 55)")
ok1 = (Ngen * L5, B * L5, F5 * L5) == (33, 44, 55)
check("(N_gen, B, F₅)·L₅ = (33,44,55)", ok1)
ok2 = 33**2 + 44**2 == 55**2
check("33²+44² = 55² EXACT", ok2, f"{33**2}+{44**2}={33**2+44**2}={55**2}")
ok3 = KTREE == F4 * L5 and Nd == B * L5 and F10 == F5 * L5
check("K_tree = F₄·L₅ (R1), N_d = B·L₅, F₁₀ = F₅·L₅", ok3)

print("\nC3) T̂ 形式")
ok1 = F10 == fib(10) and 10 == L5 - 1 and 10 == 2 * F5
check("F₁₀ = (T̂¹⁰)₁₂ = 55; index 10 = L₅−1 = 2F₅", ok1, f"F₁₀={F10}")
ok2 = KTREE == F4 * luc(5)
check("K_tree = (T̂⁴)₁₂·Tr(T̂⁵) = 33 (R1 一致)", ok2)

print("\nC4) AP 讀法: (33,44,55) = K_tree + k·L₅, k=0,1,2")
gen = [KTREE + k * L5 for k in range(3)]
check("(33, 44, 55) = 33 + {0,1,2}·11", gen == [33, 44, 55], f"{gen}")
check("AP 差 = 11 = L₅", gen[1]-gen[0] == gen[2]-gen[1] == L5)

print("\nC5) 尺度塔 = L₅×{16,8,5,4,3,2,1}")
tower = {176: 16, 88: 8, 55: 5, 44: 4, 33: 3, 22: 2, 11: 1}
ok = all(N == m * L5 for N, m in tower.items())
check("176/88/55/44/33/22/11 全部 = L₅ 倍數", ok)
check("{3,4,5} = Pythagorean, {1,2,4,8,16} = 2 冪", tower[33] == 3 and tower[44] == 4 and tower[55] == 5)

print("\nC6) θ₂₃ home = 55 (O156 co-closure)")
def th(N):
    return math.degrees(math.atan(math.sin(7*math.pi/N) / math.sin(6*math.pi/N)))
t55, t88 = th(55), th(88)
t_nufit = 49.1980
ok1 = abs(t55 - t_nufit) < 0.005
check("θ(55) = 49.1966° vs 49.1980° (0.003%)", ok1, f"θ(55)={t55:.4f}°, Δ={abs(t55-t_nufit):.4f}°")
ok2 = abs(t88 - t_nufit) > abs(t55 - t_nufit) * 50
check("θ(88) = 49.3202° 86× 遠", ok2, f"θ(88)={t88:.4f}°, Δ={abs(t88-t_nufit):.4f}°")
# sin²θ₂₃
s55 = math.sin(math.radians(t55))**2
s_nf = math.sin(math.radians(t_nufit))**2
check("sin²θ₂₃(55) = 0.57298 vs NuFIT 0.57301 (0.004%)", abs(s55 - s_nf)/s_nf < 0.0001,
      f"sin²={s55:.6f}, Δ={abs(s55-s_nf)/s_nf*100:.3f}%")

print("\nC7) Sector 分離: 55 只係 θ₂₃ 嘅家")
# CKM δ 必須留 88: ω_k = 2sin(kπ/176) (176-Laplacian beat, scripts/02/06 慣例)
d88 = math.degrees(math.atan(math.sin(21*math.pi/176) / math.sin(9*math.pi/176)))
d55 = math.degrees(math.atan(math.sin(21*math.pi/55) / math.sin(9*math.pi/55)))   # N=55 直接 (O156 慣例)
ok1 = abs(d88 - 66.3999600507) < 1e-6
check("δ_CKM(88) = 66.399960° EXACT", ok1, f"{d88:.6f}°")
ok2 = abs(d55 - d88) > 1.0
check("δ_CKM(55) = 62.18° — 破壞 1e-9 閉合", ok2, f"{d55:.2f}°")
# 質量必須留 88
g7_88 = 4 * math.sin(7*math.pi/88)**2
g7_55 = 4 * math.sin(7*math.pi/55)**2
ok3 = g7_55 / g7_88 > 2.0
check("γ₇(55)/γ₇(88) = 2.48× — 質量公式破壞 (m_μ 留 88)", ok3,
      f"γ₇(88)={g7_88:.4f}, γ₇(55)={g7_55:.4f}")

print("\nC8) 終止幾何: k-ladder 頂 = 幾何斜邊 (O152 R14 升級讀法)")
ok1 = F10 == 55 and F10 > Nd - 1
check("F₁₀ = 55 > 43 = N_d−1 (O152 R14)", ok1)
ok2 = F10 == math.isqrt(33*33 + 44*44)
check("55 = √(K_tree²+N_d²) — tree×world 維度幾何閉合", ok2)
print("   → 讀法: ladder 喺 tree/world 維度幾何閉合點終止 (詮釋級 🟡)")

print("\nC9) 55 雙重身份")
ok1 = F10 == fib(10) and F10 == math.comb(L5, 2) and F10 == Nd + L5
check("55 = F₁₀ = C(L₅,2) = N_d+L₅ (O152 T7) = √(K_tree²+N_d²)", ok1,
      f"C(11,2)={math.comb(L5,2)}, {Nd}+{L5}={Nd+L5}")

print("\nC10) R4 連接: 原始斜邊 5 = AP 公差")
ok1 = F5 == 5 and F5 == L5 - 2 * Ngen and F5 == B**2 - L5
check("5 = F₅ = L₅−2N_gen = B²−L₅ (R4 AP 公差)", ok1)
ok2 = F5 == math.isqrt(3*3 + 4*4)
check("5 = √(N_gen²+B²) — primitive 斜邊 = AP 公差", ok2)
print("   → AP 階梯 (R4) 同 Pythagorean 三元組共享 5 = F₅")

total = len(passes)
print(f"\nRESULT: {sum(passes)}/{total} PASS")
exit(0 if all(passes) else 1)
