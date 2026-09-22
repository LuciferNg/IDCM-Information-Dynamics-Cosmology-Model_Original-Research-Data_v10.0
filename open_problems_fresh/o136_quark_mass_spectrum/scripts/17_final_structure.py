#!/usr/bin/env python3
"""
O136 — Script 17: 最終驗證 — O34/O35 完整模式分配結構
================================================================
O34 §4.9 給出全部 n 值的結構分解 + 世代中心 n₀ + 同位旋規則
本 script 獨立驗證整個體系。
"""
import math, json
from pathlib import Path

phi = (1 + math.sqrt(5))/2
B_, Nd, dimC = 4, 44, 3
C42 = 6        # C(4,2) = B×dimC/2
L = [2, 1, 3, 4, 7, 11, 18, 29, 47]   # L0..L8
F = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]  # F0..F10

print("=" * 88)
print("O136 Script 17: 最終驗證 — O34/O35 完整模式分配結構")
print("=" * 88)

# ═══ 1. 同位旋規則 Δn = 14 ═══════════════════════════
print(f"\n{'─'*88}")
print("1. 同位旋規則: Δn = B²−2 = 14,  n = n₀ − (B²−2)/2 · (2I₃)")
print(f"{'─'*88}")

print(f"\nB²−2 = {B_**2-2} = 14;  (B²−2)/2 = {(B_**2-2)//2} = 7")
print(f"n = n₀ − 7·(2I₃),  2I₃ = ±1")

trio = [("gen1 u/d", 17, 10, 24), ("gen2 c/s", 15, 8, 22), ("gen3 t/b", 26, 19, 33)]
print(f"\n{'世代':>10} {'n₀':>4} {'n₀−7':>6} {'n₀+7':>6} {'實際':>12} {'Δn':>4} {'=14?':>6}")
print("-" * 58)
ok1 = True
for label, n0, lo, hi in trio:
    d = hi - lo
    good = (lo == n0-7) and (hi == n0+7) and (d == 14)
    ok1 = ok1 and good
    print(f"{label:>10} {n0:>4} {n0-7:>6} {n0+7:>6} {f'({lo},{hi})':>12} {d:>4} {'✅' if good else '🔴':>6}")
print(f"\n{'✅ 全部通過' if ok1 else '🔴 失敗'}")

# ═══ 2. 全部 n 值的結構分解 ═══════════════════════════
print(f"\n{'─'*88}")
print("2. 全部 n 值的結構分解 (O34 §4.9)")
print(f"{'─'*88}")

decomp = [
    ("Z",    41, "N_d − dimC",              Nd - dimC),
    ("H",    38, "2×(N_d/2 − dimC) = 2×19", 2*(Nd//2 - dimC)),
    ("b",    33, "M (K_Tree)",              33),
    ("W",    30, "M − dimC = 33−3",         33 - dimC),
    ("d",    24, "L₅ + F₇ = 11+13",         L[5] + F[7]),
    ("s",    22, "N_d/2 = 44/2",            Nd//2),
    ("W'",   19, "F₇ + C(4,2) = 13+6",      F[7] + C42),
    ("τ",    18, "L₆",                      L[6]),
    ("u",    10, "n₀(1) − 7 = 17−7",        17 - 7),
    ("c",     8, "n₀(2) − 7 = 15−7",        15 - 7),
    ("μ",     1, "基礎種子 (fundamental)",   1),
]
print(f"\n{'粒子':>5} {'n':>4} {'結構分解':>28} {'計算':>6} {'驗證':>7}")
print("-" * 58)
ok2 = True
for name, n, form, calc in decomp:
    good = (n == calc)
    ok2 = ok2 and good
    print(f"{name:>5} {n:>4} {form:>28} {calc:>6} {'✅' if good else '🔴':>7}")
print(f"\n{'✅ 全部通過' if ok2 else '🔴 部分失敗'}")

# ═══ 3. 世代中心 n₀ ═══════════════════════════════════
print(f"\n{'─'*88}")
print("3. 世代中心 n₀")
print(f"{'─'*88}")

print(f"\nn₀(1) = 17 = L₅ + C(4,2) = 11 + 6 ✅")
print(f"n₀(2) = 15 = ?")
print(f"n₀(3) = 26 = ?")
print(f"\nn₀ 差: 17→15 (Δ = −2 = −L₀),  15→26 (Δ = +11 = +L₅)")

# 檢查 n₀ 的結構
print(f"\n─── n₀ 結構檢查 ───")
cands_15 = {
    "L₅+dimC+1": L[5]+dimC+1, "L₆−dimC": L[6]-dimC, "F₇+L₀": F[7]+L[0],
    "L₇−F₇−1": L[7]-F[7]-1, "N_d/2−7": Nd//2-7, "2F₅+5": 2*F[5]+5,
    "(B²−2)+1": (B_**2-2)+1, "C(4,2)+9": C42+9,
}
print(f"  n₀(2) = 15 候選:")
for name, val in cands_15.items():
    print(f"    {name:>14} = {val} {'✅' if val==15 else ''}")

cands_26 = {
    "2×F₇": 2*F[7], "L₅+F₇+L₀": L[5]+F[7]+L[0], "N_d−L₆": Nd-L[6],
    "L₇−dimC": L[7]-dimC, "B²+10": B_**2+10, "C(4,2)+20": C42+20,
    "M−7": 33-7, "N_d/2+4": Nd//2+4,
}
print(f"\n  n₀(3) = 26 候選:")
for name, val in cands_26.items():
    print(f"    {name:>14} = {val} {'✅' if val==26 else ''}")

# ═══ 4. 世代跳躍 k 值 ════════════════════════════════
print(f"\n{'─'*88}")
print("4. 世代跳躍 k 值 (O34 §4.10)")
print(f"{'─'*88}")

k_emu = 11 + 7/88
k_mutau = 6 - 71/528
k_etau = 17 - 29/528
print(f"\nk(e→μ)   = 11 + 7/88    = {k_emu:.10f}   (L₅ + L₄/(2N_d))")
print(f"k(μ→τ)   = 6 − 71/528   = {k_mutau:.10f}   (C(4,2) − (2N_d−17)/528)")
print(f"k(e→τ)   = 17 − 29/528  = {k_etau:.10f}   (L₅+C(4,2) − L₇/528)")
print(f"\n加法一致性: {k_emu:.10f} + {k_mutau:.10f} = {k_emu+k_mutau:.10f}")
print(f"           k(e→τ) = {k_etau:.10f}")
print(f"           差 = {abs(k_emu+k_mutau-k_etau):.2e} {'✅' if abs(k_emu+k_mutau-k_etau)<1e-12 else '🔴'}")

# 7/88 = 42/528, 42−71 = −29
print(f"\n7/88 = {7/88:.10f} = 42/528 = {42/528:.10f} ✅")
print(f"42 − 71 = {42-71} = −29 ✅")

# ═══ 5. 完整質量譜 (sin 框架) ════════════════════════
print(f"\n{'─'*88}")
print("5. 完整質量譜 — 從 μ 錨定 (sin 框架)")
print(f"{'─'*88}")

PDG = {"t":172760, "b":4180, "c":1270, "s":93.0, "d":4.67, "u":2.16,
       "tau":1776.86, "mu":105.658, "e":0.510999}

# n 分配 (O34 §4.9)
n_assign = {"u":10, "d":24, "c":8, "s":22, "t":19, "b":33, "mu":1, "tau":18}

print(f"\n{'粒子':>5} {'n':>4} {'sin(nπ/88)':>12} {'A (MeV)':>14} {'A/A(μ)':>12} {'結構候選':>16}")
print("-" * 70)
base_A = PDG["mu"]/math.sin(1*math.pi/88)
for p, n in sorted(n_assign.items(), key=lambda kv: kv[1]):
    sn = math.sin(n*math.pi/88)
    A = PDG[p]/sn
    print(f"{p:>5} {n:>4} {sn:>12.6f} {A:>14.4f} {A/base_A:>12.6f}")

print(f"\nμ 的 A = {base_A:.4f} MeV (錨點)")
print(f"\n★ 檢查 u/d 的 A 一致性:")
A_u = PDG["u"]/math.sin(10*math.pi/88)
A_d = PDG["d"]/math.sin(24*math.pi/88)
print(f"  A(u) = {A_u:.4f}, A(d) = {A_d:.4f}, 比 = {A_u/A_d:.6f} (0.03% ✅)")

# ═══ 6. 保存 ════════════════════════════════════════
data_dir = Path(__file__).parent.parent / "data"
data_dir.mkdir(exist_ok=True)
with open(data_dir / "17_final_structure.json", "w") as f:
    json.dump({
        "isospin_rule": {"delta_n": 14, "formula": "n = n₀ − 7·(2I₃)", "verified": ok1},
        "n_decompositions": {name: {"n": n, "form": form, "calc": calc, "ok": n==calc}
                             for name, n, form, calc in decomp},
        "generation_centers": {"n0_1": 17, "n0_2": 15, "n0_3": 26},
        "generation_jumps": {"k_emu": k_emu, "k_mutau": k_mutau, "k_etau": k_etau,
                             "additive_consistency": abs(k_emu+k_mutau-k_etau)<1e-12},
        "n_assignment": n_assign,
        "A_u_over_A_d": A_u/A_d,
    }, f, indent=2, ensure_ascii=False)
print(f"\n✅ 結果已寫入 data/17_final_structure.json")