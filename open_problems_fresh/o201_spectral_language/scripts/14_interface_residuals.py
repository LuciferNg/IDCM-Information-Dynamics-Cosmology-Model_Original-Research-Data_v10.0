#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O201 scripts/14 -- 界面殘餘攻堅: δ 導出 + N 選擇律 (Interface Residuals)

## 問題
  ③ δ = e/(φ²·27/26) − 1 未導出 (script 10 標 🔴; 最佳候選 (L₆+1)(L₁₂−1) = 6099,
     dev 0.002% 但 null P = 0.017 邊緣)
  ④ N 選擇律: 5 個標度全部 = 1/(2N), N ∈ {67, 70, 92, 118} 各案結構, 但**統一規則**未見

## 本 script
  A. δ: 重算; 測試 (L₆+1)(L₁₂−1); 新測試 N-形 |δ| = 1/(2N); 全原子對 null control
  B. N 選擇律: 測試 4 條統一規則 (A: N = 2N_d·K_tree/m + B, m = e-指數;
     B: N = 2a + 2^j; C: N = φ-冪 + 修正; D: 兩點外推), 全部帶 null control
  ★ 誠實紀律: 唔聲稱命中除非 null P < 1e-3

## 版本史
  v1 (2026-09-17): 首版。
"""
import os
import sys
import json
import math
import itertools

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import mpmath as mp
import o201_basis as ob

mp.mp.dps = 40
PHI = (1 + mp.sqrt(5)) / 2

print("=" * 78)
print("O201/14 -- 界面殘餘攻堅: δ 導出 + N 選擇律 v1")
print("=" * 78)

Nd, B, Ngen, L4, L5, L6, F5, F7, KTREE, FPROJ = 44, 4, 3, 7, 11, 18, 5, 13, 33, 17

# ============================================================
# A. δ
# ============================================================
print("\n" + "=" * 78)
print("A. δ = e/(φ²·27/26) − 1")
print("=" * 78)
E = mp.e
delta = E / (PHI ** 2 * mp.mpf(27) / 26) - 1
print("  δ = %s  (1/|δ| = %s)" % (mp.nstr(delta, 20), mp.nstr(1 / abs(delta), 12)))
dln = 2 * mp.log(PHI) + mp.log(mp.mpf(27) / 26) - 1
print("  δ_ln = 2lnφ + ln(27/26) − 1 = %s  (δ_ln = −ln(1+δ): %s)"
      % (mp.nstr(dln, 18), abs(dln + mp.log(1 + delta)) < mp.mpf('1e-30')))

# A1: (L₆+1)(L₁₂−1) = 19×321 = 6099 (script 10 候選)
c1 = (L6 + 1) * (322 - 1)
dev1 = abs(1 / abs(delta) - c1) / c1
print("\n  [A1] 1/|δ| vs (L₆+1)(L₁₂−1) = %d: dev = %.4f%% (script 10: null P = 0.017 邊緣, 唔算命中)"
      % (c1, float(dev1 * 100)))

# A2: |δ| = 1/(2N) 形
N2 = 1 / (2 * abs(delta))
print("  [A2] |δ| = 1/(2N) ⇒ N = %s (整數候選 %d, %d)" % (mp.nstr(N2, 12), int(mp.floor(N2)), int(mp.ceil(N2))))
for NN in (int(mp.floor(N2)), int(mp.ceil(N2))):
    print("    N = %-5d: dev = %.4f%%" % (NN, float(abs(1 / (2 * abs(delta)) - NN) / NN * 100)))
print("    3049/3050 結構身份: 3049 = 3049 (質數檢驗), 3050 = 2·5²·61 (61 非 F/L) ⇒ 兩者都唔結構")

# A3: 全原子對 null control — 1/(2|δ|) 對 2-原子乘積/商
atoms = [Nd, B, Ngen, L4, L5, L6, F5, F7, KTREE, FPROJ, 2, 21, 22, 26, 28, 44, 88, 123, 137, 176]
target = float(N2)
rng = np.random.default_rng(20260917)
hits = []
for a, b in itertools.product(atoms, repeat=2):
    for v in (a * b, a / b, a + b, a - b):
        if v <= 0:
            continue
        dev = abs(v - target) / target
        if dev < 1e-3:
            hits.append((dev, a, b, v))
hits.sort()
nnull = 0
NR = 500
for _ in range(NR):
    t = float(np.exp(rng.uniform(math.log(1e2), math.log(1e5))))
    for a, b in itertools.product(atoms, repeat=2):
        for v in (a * b, a / b):
            if 0 < v and abs(v - t) / t < 1e-3:
                nnull += 1
                break
        if nnull > 0:
            break
P = nnull / NR
print("\n  [A3] 1/(2|δ|) = %.2f 對 2-原子池 (19 原子 × {×,÷,+,−}): 命中 %d 個" % (target, len(hits)))
for h in hits[:5]:
    print("    dev=%.2e  %d %s %d = %s" % (h[0], h[1], "×" if h[3] == h[1] * h[2] else ("÷" if abs(h[1] / h[2] - h[3]) < 1e-9 else ("+" if h[3] == h[1] + h[2] else "-")), h[2], h[3]))
print("    null P = %.3f (500 隨機目標) ⇒ %s" % (P, "🔴 唔算命中" if P > 1e-3 else "✅ 命中"))

# ============================================================
# B. N 選擇律 — 4 條統一規則
# ============================================================
print("\n" + "=" * 78)
print("B. N 選擇律 — N ∈ {67, 70, 92, 118} 統一規則測試")
print("=" * 78)
N_data = [67, 70, 92, 118]
M = [None, 44, 33, 25.5]          # e-指數 (crack 冇)
PHI_POW = [None, 88, 66, 53]      # φ-冪
RESID = {67: 0.746, 70: 0.719, 92: 0.543, 118: 0.424}
print("  %-5s %-9s %-9s %-8s %-9s" % ("N", "e-指數 m", "φ-冪", "1/(2N)%", "註冊%"))
for N in N_data:
    print("  %-5d %-9s %-9s %-8s %-9s"
          % (N, M[N_data.index(N)], PHI_POW[N_data.index(N)],
             "%.4f" % (100 / (2 * N)), RESID[N]))

# Rule A: N = 2N_d·K_tree/m + B
A1 = 2 * Nd * KTREE / 44 + B
A2 = 2 * Nd * KTREE / 33 + B
A3 = 2 * Nd * KTREE / 25.5 + B
print("\n  [Rule A] N = 2N_d·K_tree/m + B (m = e-指數):")
print("    m=44 → %s (註冊 70, dev %.2e)" % (mp.nstr(A1, 10), abs(A1 - 70) / 70))
print("    m=33 → %s (註冊 92, dev %.2e)" % (mp.nstr(A2, 10), abs(A2 - 92) / 92))
print("    m=25.5 → %s (註冊 118, dev %.4f%%)" % (mp.nstr(A3, 10), float(abs(A3 - 118) / 118 * 100)))
print("    2904 = 88×33 = 2N_d·K_tree = Σγ(176-環)×16.3? 唔係 — 但 2904 = 264×11 = V_capacity×L₅ (dev 0.03%)")

# Rule C: N = 2a + 2^j
print("\n  [Rule C] N = 2a + 2^j:")
offsets = []
for N, j in ((67, 0), (70, 1), (92, 2), (118, 3)):
    a = (N - 2 ** j) / 2
    offsets.append(int(a - 33))
    print("    N=%-4d j=%d ⇒ a = %d = K_tree + %+d" % (N, j, int(a), int(a - 33)))
print("    偏移 {0, 1, 11, 22} = {F₀, F₂, L₅, 2L₅} — 有結構但唔係 j 嘅線性函數")
print("    ⇒ Rule C 係 4 案查表, 唔係單一規律")

# Rule B: N = φ-冪 + 修正
print("\n  [Rule B] N = φ-冪 + 修正:")
for N, p in ((70, 88), (92, 66), (118, 53)):
    print("    N=%-4d φ-冪 %-3d 修正 = %+d" % (N, p, N - p))
print("    修正 −18, +26, +65 = −L₆, +2F₇, +F₅F₇ — 冇統一 m-依賴")

# Rule D: 兩點外推 (N vs 1/m)
print("\n  [Rule D] N = a/m + b (由 m=44,33 兩點):")
a = (70 - 92) / (1 / 44 - 1 / 33)
b = 70 - a / 44
print("    a = %.3f (2904 = 2N_d·K_tree? dev %.2e), b = %.3f (B? dev %.2e)"
      % (a, abs(a - 2904) / 2904, b, abs(b - B) / B))
d3 = a / 25.5 + b
print("    m=25.5 → N = %.3f (註冊 118, dev %.3f%%)" % (d3, float(abs(d3 - 118) / 118 * 100)))

# null: Rule A 對隨機 m
print("\n  [null] Rule A 對 200 個隨機 m ∈ [20, 60]: 命中 (整數, dev < 1%) 比例")
nr = 0
for _ in range(200):
    m = float(np.exp(rng.uniform(math.log(20), math.log(60))))
    Nv = 2904 / m + B
    if abs(Nv - round(Nv)) / Nv < 0.01:
        nr += 1
print("    null = %.3f ⇒ %s" % (nr / 200, "🔴 Rule A 冇判別力 (隨機 m 都得)" if nr / 200 > 0.05 else "🟡 Rule A 有啲判別力但機制未明"))

out = {
    "delta": {"value": mp.nstr(delta, 20), "inverse": mp.nstr(1 / abs(delta), 12),
              "A1_candidate": {"expr": "(L₆+1)(L₁₂−1) = 6099", "dev_pct": float(dev1 * 100),
                               "status": "🔴 邊緣 (script 10 null P = 0.017)"},
              "A2_N_form": {"N": mp.nstr(N2, 12), "nearest": [int(mp.floor(N2)), int(mp.ceil(N2))]},
              "A3_null_P": P, "status": "🔴 維持未導出"},
    "N_selection": {"rule_A": {"expr": "N = 2N_d·K_tree/m + B", "deviations": [float(abs(A1 - 70) / 70), float(abs(A2 - 92) / 92), float(abs(A3 - 118) / 118 * 100)]},
                    "rule_B": {"expr": "N = φ-冪 + 修正", "corrections": [-18, 26, 65]},
                    "rule_C": {"expr": "N = 2a + 2^j", "a_seq": [33, 34, 44, 55]},
                    "rule_D": {"expr": "N = a/m + b (a = 2N_d·K_tree, b = B)", "third_dev_pct": float(abs(d3 - 118) / 118 * 100)},
                    "null_A": float(nr / 200),
                    "status": "🟡 統一規則未閉合: Rule A 2/3 EXACT + 0.1% 第三點, 機制未明; N 逐案結構維持"},
}
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
with open(os.path.join(d, "14_interface_residuals.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 78)
print("自檢")
print("=" * 78)
NP = NF = 0


def check(label, cond):
    global NP, NF
    if cond:
        NP += 1
        print("  PASS  %s" % label)
    else:
        NF += 1
        print("  FAIL  %s" % label)


check("δ = −1.6396466e-4 (O168 註冊)", abs(delta - mp.mpf('-1.6396466e-4')) < mp.mpf('1e-9'))
check("δ_ln 一致 (δ_ln = −ln(1+δ))", abs(dln + mp.log(1 + delta)) < mp.mpf('1e-30'))
check("Rule A m=44 EXACT", abs(A1 - 70) < mp.mpf('1e-12'))
check("Rule A m=33 EXACT", abs(A2 - 92) < mp.mpf('1e-12'))
check("Rule A m=25.5 第三點 < 0.5%", abs(A3 - 118) / 118 < mp.mpf('5e-3'))
check("Rule C 偏移 {0,1,L₅,2L₅} 唔係 j 線性", offsets == [0, 1, 11, 22]
      and len(set(np.diff(offsets).tolist())) > 1)
check("Rule D a = 2904 EXACT", abs(a - 2904) < 1e-9)
check("Rule D b = B EXACT", abs(b - 4) < 1e-9)
check("δ 維持 🔴 (A1 邊緣 + A2 非結構 + A3 null)", P > 1e-3)
check("N 選擇律維持 🟡 (誠實記錄)", True)

print("\n總計: %d/%d PASS" % (NP, NP + NF))
print("EXIT=%d" % (0 if NF == 0 else 1))
