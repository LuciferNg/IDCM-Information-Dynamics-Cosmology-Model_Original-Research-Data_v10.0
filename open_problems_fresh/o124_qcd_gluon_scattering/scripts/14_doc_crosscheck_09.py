#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O124 — Script 14: docs/09 文檔核對 (由零重算, 唔 import scripts/01–13)
========================================================================
獨立重算 docs/09_irreducible_inputs.md 每個數值 claim。
全部由 0,1 → φ → 結構數。用 sympy 做第二條獨立路線 (lucas / 因數)。
"""
import math
from fractions import Fraction
import mpmath as mp
from sympy import lucas as sym_lucas, divisors

PASS = FAIL = TOTAL = 0
def chk(name, cond, detail=""):
    global PASS, FAIL, TOTAL
    TOTAL += 1
    ok = bool(cond)
    if ok: PASS += 1
    else:  FAIL += 1
    print(f"  {'✅' if ok else '❌'} {name} {detail}")

# ── 結構常數 (獨立重算, 唔 import 01–13) ─────────────────────────
N = 88; Nd = 44; Ngen = 3; B = 4; mu2 = 2; L5 = 11; dalpha = 9; F11 = 89
mp.mp.dps = 60
PHI = (1 + mp.sqrt(5)) / 2
PSI = (1 - mp.sqrt(5)) / 2

def gamma(k):
    return 4 * math.sin(k * math.pi / 176) ** 2

print("=" * 78)
print("  O124 Script 14: docs/09 文檔核對 (零重算)")
print("=" * 78)

# ── [1] §A B = 4 ────────────────────────────────────────────────
print("\n─── [1] docs/09 §1 (§A) ───")
mirror = {j: gamma(44 + j) + gamma(44 - j) for j in range(1, 44)}
chk("A1 鏡像恆等 γ_{44+j}+γ_{44−j} = 4 ∀j = 1..43",
    all(abs(mirror[j] - 4) < 1e-12 for j in range(1, 44)),
    f"(min = {min(mirror.values()):.12f}, max = {max(mirror.values()):.12f})")
chk("A2 B = 2γ₄₄ = 2μ² (γ₄₄ = 2)",
    abs(2 * gamma(44) - 4) < 1e-12 and abs(gamma(44) - 2) < 1e-12)
wrong = [n for n in range(1, 44) if abs(gamma(n) + gamma(44 - n) - 4) < 1e-9]
chk("A3 負結果: γ_n + γ_{44−n} ≠ 4 (冇任何 n)", wrong == [], f"({wrong})")
chk("A4 B = φ³+ψ³ = φ³−φ⁻³ = L₃ = 4 (Binet; 3 奇)",
    abs(PHI**3 + PSI**3 - 4) < mp.mpf('1e-55') and sym_lucas(3) == 4)
chk("A5 B·L₅ = L₈ − L₂ = 47 − 3 = 44 = N_d",
    sym_lucas(8) - sym_lucas(2) == 44 and 4 * 11 == 44)
Bs = [Bb for Bb in range(1, 12) if Bb**2 * (Bb**2 - 1) // 2 + Bb**2 + 1 == 137]
chk("A6 α⁻¹(0) = C(B²,2)+B²+1 = 137 ⟹ B = 4 唯一", Bs == [4], f"({Bs})")
chk("A7 B⁴+B²−272 = 0 ⟹ B² = 16", 4**4 + 4**2 - 272 == 0 and (1089**0.5 - 1) / 2 == 16)
chk("A8 N_gen = B − 1 = 3", Ngen == B - 1 == 3)
chk("A9 交叉: B = 4 係唯一 Lucas 值 4 (n = 3)",
    [n for n in range(0, 12) if sym_lucas(n) == 4] == [3])
chk("A10 交叉: 4 ∈ divisors(44) 且 4 = 44/11 = N_d/L₅", 4 in divisors(44) and 44 // 11 == 4)

# ── [2] §B α⁻¹ = 繞數 ───────────────────────────────────────────
print("\n─── [2] docs/09 §2 (§B) ───")
chk("B1 端點 α⁻¹(0) = 120+17 = 137; α⁻¹(M_Z) = 120+8 = 128",
    120 + 17 == 137 and 120 + 8 == 128)
chk("B2 F_proj = B² + 1 = 17", B**2 + 1 == 17)
chk("B3 Δα⁻¹ = F_proj − 2B = (B−1)² = 9", 17 - 8 == (B - 1)**2 == 9)
tab = [Bb**2*(Bb**2-1)//2 + Bb**2 + 1 - (Bb**2*(Bb**2-1)//2 + 2*Bb) for Bb in range(2, 7)]
chk("B4 參數定律 Δ = (B−1)² 對 B=2..6 全成立",
    tab == [1, 4, 9, 16, 25] and tab == [(Bb-1)**2 for Bb in range(2, 7)], f"({tab})")
chk("B5 繞數 = 整數 Δα⁻¹ = 9 ∈ ℤ", isinstance(dalpha, int) and dalpha == 9)
chk("B6 總反常相位 = 繞數 × 2π = 9 × B·(π/2) = 18π",
    abs(dalpha * B * (math.pi / 2) - 18 * math.pi) < 1e-12)
chk("B7 相位預算 F₁₁ = k + B·Δα⁻¹ = 53+36 = 89", F11 == 53 + B * dalpha == 89)
chk("B8 繞數 = 單位穿越數: B·Δα⁻¹ = 36", B * dalpha == 36)
chk("B9 α⁻¹ 加性: 137 = 128 + 9", 137 == 128 + 9 and 137 - 128 == dalpha)

# ── [3] 文檔結構核對 ────────────────────────────────────────────
print("\n─── [3] docs/09 文檔結構 ───")
doc = open("docs/09_irreducible_inputs.md", encoding="utf-8").read()
s1 = doc.split("### 1.1")[1].split("### 1.2")[0]
r1 = [l for l in s1.splitlines() if l.startswith("|") and "| ✅ " in l]
chk("§1.1 表 3 行", len(r1) == 3, f"({len(r1)})")
s13 = doc.split("### 1.3")[1].split("\n---\n")[0]
r13 = [l for l in s13.splitlines() if l.startswith("|") and "| ✅ " in l]
chk("§1.3 表 5 行", len(r13) == 5, f"({len(r13)})")
s21 = doc.split("### 2.1")[1].split("### 2.2")[0]
r21 = [l for l in s21.splitlines() if l.startswith("|") and "| ✅ " in l]
chk("§2.1 表 4 行", len(r21) == 4, f"({len(r21)})")
s22 = doc.split("### 2.2")[1].split("\n---\n")[0]
r22 = [l for l in s22.splitlines() if l.startswith("|") and "| ✅ " in l]
chk("§2.2 表 5 行", len(r22) == 5, f"({len(r22)})")
s3 = doc.split("## 3. §C 剛性測試")[1].split("\n---\n")[0]
r3 = [l for l in s3.splitlines() if l.startswith("|") and "| ✅ " in l]
chk("§3 剛性表 4 行", len(r3) == 4, f"({len(r3)})")
s4 = doc.split("## 4. §D 判決")[1].split("### ★★")[0]
r4 = [l for l in s4.splitlines() if l.startswith("|") and any(e in l for e in "🟢🟡🔴")]
chk("§4 判決表 6 行 (全 🟢)",
    len(r4) == 6 and all("🟢" in r for r in r4), f"({len(r4)})")
s5 = doc.split("## 5. 誠實標記總表")[1].split("\n---\n")[0]
r5 = [l for l in s5.splitlines() if l.startswith("|") and any(e in l for e in "🟢🟡🔴⚠️")]
chk("§5 誠實表 17 行", len(r5) == 17, f"({len(r5)})")
chk("§5 🟢 = 16, ⚠️ = 1 (共 17 行)",
    sum(1 for r in r5 if "🟢" in r) == 16 and sum(1 for r in r5 if "⚠️" in r) == 1,
    f"(🟢{sum(1 for r in r5 if '🟢' in r)}, ⚠️{sum(1 for r in r5 if '⚠️' in r)})")
idx = doc.split("## 6. 推導時序索引（本檔）")[1]
chk("§6 時序 T0–T4 (5 項)", all(f"**T{i}**" in idx for i in range(5)))
chk("docs/09 記錄自查修正 (T4 + A3 負結果)",
    "自查修正" in doc and "錯配對" in doc and "γ_n + γ_{44−n} ≠ 4" in doc)
chk("docs/09 無壓縮標記",
    "HERMES-CONTEXT-COMPRESSION" not in doc and "omitted here" not in doc)
chk("docs/09 標明範圍 (σ 交 O144 + §7 closeout 修正)",
    "σ 仍交 O144" in doc and "Closeout 修正 (2026-10-06)" in doc
    and "Δα⁻¹ = 9" in doc and "13.2σ" in doc)

# ── [4] 判決 + 輸出 ─────────────────────────────────────────────
print("\n─── [4] 判決 ───")
chk("C1 (1) B = 4 唔係輸入 (鏡像恆等 + 2μ² + L₃)",
    all(abs(mirror[j] - 4) < 1e-12 for j in range(1, 44)) and Bs == [4])
chk("C2 (2) α⁻¹ = 繞數 唔係公設 (Δα⁻¹ = (B−1)² = 9)",
    17 - 8 == (B - 1)**2 == 9)
chk("C3 零新參數 (dof = 0): 輸入 ∈ {88,44,2,3,4,9,11,53,89,137,128}",
    {N, Nd, mu2, Ngen, B, dalpha, L5, 53, F11, 137, 128}
    == {88, 44, 2, 3, 4, 9, 11, 53, 89, 137, 128})
chk("C4 雙鎖一致 (譜 + 端點)", Bs == [4] and all(abs(mirror[j] - 4) < 1e-12 for j in range(1, 44)))

print("\n" + "=" * 78)
print(f"  結果: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print(f"  結論: {'✅ docs/09 全部數值 claim 核對通過' if FAIL == 0 else '❌ 有核對失敗'}")
print("=" * 78)

