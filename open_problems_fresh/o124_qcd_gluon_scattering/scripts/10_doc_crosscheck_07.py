#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O124 — Script 10: docs/07 文檔核對 (由零重算, 唔 import scripts/01–09)
========================================================================
獨立重算 docs/07_beta_mechanism.md 每個數值 claim。全部由 0,1 → φ → 結構數。
"""
import itertools
import math

PASS = FAIL = TOTAL = 0
def chk(name, cond, detail=""):
    global PASS, FAIL, TOTAL
    TOTAL += 1
    ok = bool(cond)
    if ok: PASS += 1
    else:  FAIL += 1
    print(f"  {'✅' if ok else '❌'} {name} {detail}")

N = 88; B = 4; Ngen = 3; Nf = 6; Nd = 44; mu2 = 2; L5 = 11; L6 = 18
dalpha = 9; F11 = 89; k = 53; j0 = 18
PHI = (1 + 5**0.5)/2
def Tpow(n):
    R = [[1, 0], [0, 1]]; M = [[1, 1], [1, 0]]
    for _ in range(n):
        R = [[R[0][0]*M[0][0] + R[0][1]*M[1][0], R[0][0]*M[0][1] + R[0][1]*M[1][1]],
             [R[1][0]*M[0][0] + R[1][1]*M[1][0], R[1][0]*M[0][1] + R[1][1]*M[1][1]]]
    return R
L = {n: Tpow(n)[0][0] + Tpow(n)[1][1] for n in range(1, 13)}
F = {n: Tpow(n)[0][1] for n in range(1, 13)}

print("=" * 78)
print("  O124 Script 10: docs/07 文檔核對 (零重算)")
print("=" * 78)

# ── [1] §1 相位/繞數結構 ────────────────────────────────────────
print("\n─── [1] docs/07 §1 (A) ───")
chk("A1 Σkπ/88 = 44.5π = F₁₁(π/2)",
    abs(sum(kk*math.pi/88 for kk in range(1, N+1)) - 44.5*math.pi) < 1e-12)
chk("A2 88 = B·22; 22 = 2L₅", N == B*22 and 22 == 2*L5)
chk("A3 B(π/2) = 2π; B = 2μ²", abs(B*(math.pi/2) - 2*math.pi) < 1e-12 and B == 2*mu2)
chk("A4 Δα⁻¹ = 9 = N_gen²; 反常 = 18π = L₆π", dalpha == Ngen**2 and L6 == 18)
chk("A5 通道相位 = 26.5π = 53(π/2)", abs((44.5-18)*math.pi - k*(math.pi/2)) < 1e-12)
sol = [(kk, jj) for kk in range(1, N+1) for jj in range(1, N+1) if kk*(2*jj+kk-1) == 4664]
chk("A6 相位方程 k(2j+k−1) = 4664 唯一解 (53,18)", sol == [(53, 18)], f"({sol})")
wsum = sum(range(j0, j0+k))
chk("A7 窗口 {18..70} Σsite = 2332 = k·N_d", wsum == 2332 and wsum == k*Nd,
    f"({wsum})")
chk("A8 補集 35 sites 相位 = 18π", N-k == 35 and abs((sum(range(1, N+1))-wsum)/88 - 18) < 1e-12)
chk("A9 F₁₁ = k + 4N_gen² = 89", F11 == k + 4*Ngen**2 == 89)

# ── [2] §2 b₀ = Tr(T̂^B) ─────────────────────────────────────────
print("\n─── [2] docs/07 §2 (B) ───")
chk("B2 Tr(T̂^B) = L_B = 7", L[B] == 7)
chk("B3 φ^B + φ^{−B} = 7", abs(PHI**B + PHI**(-B) - 7) < 1e-12,
    f"({PHI**B + PHI**(-B):.9f})")
chk("B4 L_n = 7 唯一解 n = 4", [n for n in range(1, 13) if L[n] == 7] == [4])
chk("B5 N_gen = B−1 = 3", Ngen == B-1 == 3)
chk("B6 2B−1 = F₆−1 = N_gen+B = L₅−L₃ = L₄ = 7",
    2*B-1 == 7 and F[6]-1 == 7 and Ngen+B == 7 and L[5]-L[3] == 7 and L[4] == 7)
chk("B7 11 − 2N_f/3 = 7 且 N_f = 2N_gen = 6", abs(11 - 2*Nf/3 - 7) < 1e-12 and Nf == 6)

# ── [3] §3 b₁ = 通道半寬 ────────────────────────────────────────
print("\n─── [3] docs/07 §3 (C) ───")
chk("C1 (k−1)/2 = 26", (k-1)//2 == 26)
chk("C2 2F₇ = 26", 2*F[7] == 26)
chk("C3 44 ± 26 = {18,70}, 中心 44", Nd-2*F[7] == 18 and Nd+2*F[7] == 70
    and (18+70)//2 == Nd)
chk("C4 L₈ − F₈ = 47 − 21 = 26", L[8] - F[8] == 26)
chk("C5 L_n − F_n = 2F_{n−1} (n=2..12)",
    all(L[n]-F[n] == 2*F[n-1] for n in range(2, 13)))
chk("C6 半寬由 k=53 唯一解決定", sol == [(53, 18)] and (k-1)//2 == 26)

# ── [4] §4 舊 justification 審計 ────────────────────────────────
print("\n─── [4] docs/07 §4 (D) ───")
chk("D1 標準 b₁ = 102 − 76 = 26", abs(102 - 38*Nf/3 - 26) < 1e-12)
CA = 3.0; TF = 0.5; CF = 4/3
chk("D2 (34/3)C_A² − (20/3)C_A T_F N_f − 4C_F T_F N_f = 102 − 60 − 16 = 26",
    abs((34/3)*CA**2 - 102) < 1e-12 and abs((20/3)*CA*TF*Nf - 60) < 1e-12
    and abs(4*CF*TF*Nf - 16) < 1e-12 and abs(102-60-16 - 26) < 1e-12)
chk("D3 102 = 2K_tree + 2L₆ = 2·33 + 2·18", 2*33 + 2*L6 == 102)
chk("D4 φ⁹−φ⁻⁹ = L₉ = 76 (唔係 F₉); F₉ = 34",
    abs(PHI**9 - PHI**(-9) - 76) < 1e-6 and L[9] == 76 and F[9] == 34,
    f"(L₉ = {L[9]}, F₉ = {F[9]})")
pool = {"L3": L[3], "L4": L[4], "L5": L[5], "L6": L[6], "L7": L[7], "L8": L[8], "L9": L[9],
        "F5": F[5], "F6": F[6], "F7": F[7], "F8": F[8], "F9": F[9], "F10": F[10],
        "B": B, "Ngen": Ngen, "Nf": Nf, "Ktree": 33, "Nd": Nd, "2Nd": 2*Nd,
        "CB2": 120, "Fproj": 17, "dalpha": dalpha, "mu2": mu2, "Sg": 90, "Sl": 176,
        "F11": F11, "k": k}
names = list(pool)
exprs = set()
for r in (1, 2, 3):
    for combo in itertools.combinations(names, r):
        for coefs in itertools.product([1, 2, 3], repeat=r):
            for signs in itertools.product([1, -1], repeat=r):
                if sum(s*c*pool[nm] for s, c, nm in zip(signs, coefs, combo)) == 26:
                    exprs.add(tuple(sorted((nm, s*c) for nm, s, c in zip(combo, signs, coefs))))
chk("D5 組合出 26 嘅獨立表達式 ≥ 1000 (非唯一)", len(exprs) >= 1000,
    f"({len(exprs)} 個)")

# ── [5] §5/§6 表 + §7 時序 ──────────────────────────────────────
print("\n─── [5] docs/07 §5/§6/§7 ───")
doc = open("docs/07_beta_mechanism.md", encoding="utf-8").read()
tbl6 = doc.split("## 6. 誠實標記總表")[1].split("## 7.")[0]
r6 = [l for l in tbl6.splitlines() if l.startswith("|") and any(e in l for e in "🟢🟡🔴")]
chk("§6 誠實表 14 行", len(r6) == 14, f"({len(r6)})")
chk("§6 🟢 = 11", sum(1 for r in r6 if "🟢" in r) == 11, f"({sum(1 for r in r6 if '🟢' in r)})")
chk("§6 🔴 = 1", sum(1 for r in r6 if "🔴" in r) == 1)
chk("§6 🟡 = 2", sum(1 for r in r6 if "🟡" in r) == 2)
tbl5 = doc.split("## 5. §E 判決")[1].split("### ★★")[0]
r5 = [l for l in tbl5.splitlines() if l.startswith("|") and any(e in l for e in "🟢🟡🔴")]
chk("§5 判決表 8 行 (含 emoji)", len(r5) == 8, f"({len(r5)})")
idx = doc.split("## 7. 推導時序索引（本檔）")[1]
chk("§7 時序 T0–T4 (5 項)", all(f"**T{i}**" in idx for i in range(5)))
chk("docs/07 無壓縮標記",
    "HERMES-CONTEXT-COMPRESSION" not in doc and "omitted here" not in doc)
chk("docs/07 標明範圍 (σ 交 O144)",
    "σ 交 O144" in doc and "只處理" in doc)

print("\n" + "=" * 78)
print(f"  結果: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print(f"  結論: {'✅ docs/07 全部數值 claim 核對通過' if FAIL == 0 else '❌ 有核對失敗'}")
print("=" * 78)
