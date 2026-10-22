#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
08_delta_operator.py — R6: δ_PMNS = 230° 算子表述 (K_Tree 本徵算子化)
====================================================================
問題 (O155 R6): δ_PMNS = (K_tree+F₇)(L₅−2N_gen) 嘅算子表述 — F₇ = 13,
46 = K_tree+F₇ 喺 T̂ 語言。

T̂ 算子形式 (R1/R4 延續):
  K_tree = (T̂⁹)₁₂ − 1 = F₉−1 (9 = N_gen²)
  F₇ = (T̂⁷)₁₂ = (T̂³³ mod K_tree)₁₂   ← R1 C7: F₃₃ ≡ F₇ (mod 33) — tree-depth 殘餘
  5  = F₅ = (T̂⁵)₁₂ = L₅−2N_gen = Tr(T̂⁵)−2(T̂⁴)₁₂
  δ = ((T̂⁹)₁₂ − 1 + (T̂⁷)₁₂) · (T̂⁵)₁₂ = 46 × 5 = 230.00° EXACT

檢驗:
C1. δ = (K_tree+F₇)(L₅−2N_gen) = 46×5 = 230.000000 EXACT
C2. T̂ 形式: δ = ((T̂⁹)₁₂−1+(T̂⁷)₁₂)·(T̂⁵)₁₂ = 230
C3. 同餘: F₃₃ ≡ F₇ (mod K_tree); 46 = K_tree + (T̂³³ mod 33)₁₂
C4. 46 = L₈−1 = Tr(T̂⁸)−1; δ = (Tr(T̂⁸)−1)·(T̂⁵)₁₂
C5. 其他精確形式一致: L₅·F₈−1 = 230; K_tree·L₄−1 = 230; 2N+ΣAP = 230
C6. J_CP(230°) = 0.0255 vs NuFIT 0.0254 (0.4%) — 標準參數化重算
C7. 雙重選擇規則: mod-5 ∧ J_CP 於 {72,144,216,230,232} 唯一鎖定 230
C8. Chain 讀法: 46 = Σγ(k≡0 mod 4, k=4..88) = 46.000000 = N_d⁻+B (O153) — 雙重身份
C9. 誠實: ≥6 個精確分解存在; tree-pure 46×5 被雙重規則選擇; 機制開 🔴
"""
import mpmath as mp
import math
mp.mp.dps = 50

def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def luc(n):
    return fib(n - 1) + fib(n + 1)

N, KTREE, B, Ngen, L5, Nd, Ndm = 88, 33, 4, 3, 11, 44, 42
F5, F7, F8, F9 = fib(5), fib(7), fib(8), fib(9)

passes = []
def check(name, cond, detail=""):
    passes.append(cond)
    print(f"   [{'PASS' if cond else 'FAIL'}] {name} {detail}")

print("C1) δ = (K_tree+F₇)(L₅−2N_gen) = 46×5 = 230 EXACT")
d = (KTREE + F7) * (L5 - 2 * Ngen)
check("46×5 = 230.000000", d == 230, f"({KTREE}+{F7})({L5}−{2*Ngen}) = {d}")

print("\nC2) T̂ 形式: δ = ((T̂⁹)₁₂−1+(T̂⁷)₁₂)·(T̂⁵)₁₂")
d2 = (fib(9) - 1 + fib(7)) * fib(5)
check("= 230", d2 == 230, f"({fib(9)}−1+{fib(7)})·{fib(5)} = {d2}")

print("\nC3) 同餘: F₃₃ ≡ F₇ (mod K_tree) — δ 嘅 F₇ = tree-depth 殘餘")
r33 = fib(33) % 33
ok1 = r33 == F7
check("F₃₃ mod 33 = 13 = F₇", ok1, f"{fib(33)} mod 33 = {r33}")
ok2 = KTREE + r33 == 46
check("46 = K_tree + (T̂³³ mod 33)₁₂", ok2, f"{KTREE}+{r33}={KTREE+r33}")

print("\nC4) 46 = L₈−1 = Tr(T̂⁸)−1")
ok1 = luc(8) - 1 == 46
check("L₈−1 = 47−1 = 46", ok1)
d4 = (luc(8) - 1) * fib(5)
check("δ = (Tr(T̂⁸)−1)·(T̂⁵)₁₂ = 46·5", d4 == 230, f"{luc(8)-1}·{fib(5)}={d4}")

print("\nC5) 其他精確形式一致")
ok1 = L5 * F8 - 1 == 230
check("L₅·F₈−1 = 11·21−1 = 230", ok1)
ok2 = KTREE * luc(4) - 1 == 230
check("K_tree·L₄−1 = 33·7−1 = 230", ok2)
ok3 = 2 * N + (2*Ngen + L5 + B**2 + F8) == 230
check("2N+ΣAP = 176+54 = 230", ok3)

print("\nC6) J_CP(230°) vs NuFIT — 用結構角度 (docs/09 §11 慣例)")
# 結構角度: θ₁₂ = atan(β)+atan(1/33), θ₂₃ = atan(ω₇/ω₆), θ₁₃ = arcsin(ε·32/33)
# ω 慣例: ω_k = 2sin(kπ/88) (44-mode chain 譜根, docs/09 §4 一致)
omega = lambda k: 2 * math.sin(k * math.pi / 88)
beta_f = (math.sqrt(5) - 1) / 2
t12_s = math.degrees(math.atan(beta_f)) + math.degrees(math.atan(1/33))
t23_s = math.degrees(math.atan(omega(7) / omega(6)))
t13_s = math.degrees(math.asin((beta_f / 4) * (32/33)))
for nm, v in [("θ₁₂", t12_s), ("θ₂₃", t23_s), ("θ₁₃", t13_s)]:
    print(f"   {nm} = {v:.4f}°")
s1, s2, s3 = (math.sin(math.radians(t12_s)), math.sin(math.radians(t23_s)),
              math.sin(math.radians(t13_s)))
c1, c2, c3 = (math.cos(math.radians(t12_s)), math.cos(math.radians(t23_s)),
              math.cos(math.radians(t13_s)))
d_ = math.radians(230.0)
J = s1*s2*s3*c1*c2*(c3**2)*math.sin(d_)      # J = s₁₂c₁₂s₂₃c₂₃s₁₃c₁₃² sinδ
target = 0.0254
rel = abs(abs(J) - target) / target
ok = rel < 0.01
check("J_CP = 0.0255 vs 0.0254 (0.4%)", ok, f"J_CP={abs(J):.4f}, Δ={rel*100:.1f}%")

print("\nC7) 雙重選擇規則 (mod-5 ∧ J_CP)")
cands = {"72": 72, "144": 144, "216": 216, "230": 230, "232": 232}
surv = [k for k, v in cands.items() if v % 5 == 0]
ok1 = surv == ["230"]
check("mod-5 唯一: 230", ok1, f"倖存: {surv}")
best = None
for k, v in cands.items():
    Jv = s1*s2*s3*c1*c2*(c3**2)*abs(math.sin(math.radians(v)))
    relv = abs(Jv - target) / target
    if best is None or relv < best[1]:
        best = (k, relv)
ok2 = best[0] == "230"
check("J_CP 最細殘差: 230", ok2, f"best={best[0]} ({best[1]*100:.1f}%)")

print("\nC8) Chain 讀法: 46 = Σγ(k≡0 mod 4, k=4..88) (O153)")
s = sum(4 * mp.sin(k * mp.pi / 176)**2 for k in range(4, 89, 4))
ok1 = mp.fabs(s - 46) < mp.mpf('1e-9')
check("Σγ(class-0) = 46.000000", ok1, f"={mp.nstr(s, 12)}")
ok2 = 46 == Ndm + B
check("46 = N_d⁻+B = 42+4 (chain 讀法) — 同 tree 讀法 33+13 雙重身份", ok2)

print("\nC9) 誠實標記")
print("   δ = 46×5 tree-pure 形式: 🟢 值閉合 (0 參數, 雙重選擇規則)")
print("   ≥6 個精確分解存在 (5×46, 144+90−4, 360−88−42, 180+44+6, L₅·F₈−1, 2N+ΣAP)")
print("   → tree-pure 46×5 係被 mod-5 ∧ J_CP 選擇嘅最簡形式; 機制 (點解 5×46) 🔴 開")

total = len(passes)
print(f"\nRESULT: {sum(passes)}/{total} PASS")
exit(0 if all(passes) else 1)
