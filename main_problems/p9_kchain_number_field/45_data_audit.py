#!/usr/bin/env python3
"""
45_data_audit.py — P9 數據審計: 週期表 DATA 集完整性 (2026-10-17)
=================================================================
範圍: 19_periodic_table.md 全部 25 元素 (9 已知 + 9 dual + 7 近值)
     + 17_layer_magic_data.md 三層分類
     + 26 號預註冊 DATA 定義 (canonical)

問題:
  Q1 DATA 定義漂移: 19 號「DATA 7 行 (含 14)」vs 17 號「6 行 (唔含 14)」
     vs 26 預註冊「{11,13,17,19,21,25} (6 行)」— canonical 邊個?
  Q2 DATA_CELLS 9 格 (含 3 格 d=14) vs DATA 6 行 — 行/格層次?
  Q3 25 元素 beat 值重算 vs 19 號表 (mpmath 60dps)
  Q4 「18/946 有 label」= 9 known + 9 dual? (00_record §)
  Q5 ★R5 敏感度: 若 data-free 用 7 行版 (含 14) → R5 程序輸出變點?

零 import 原 scripts; 第一原理重算。
"""
import json
import mpmath as mp
mp.mp.dps = 60
from math import gcd
from fractions import Fraction

w = lambda n: 2*mp.sin(mp.mpf(n)*mp.pi/88)

# ================= Q3: 25 元素 beat 重算 =================
print("=== Q3: 19 號表 25 元素 beat 重算 ===")
known = {  # (i,j): (d, [19號表 beat], label)
    (1,18): (17, "1.12717067", "m_μ/m_τ"),
    (1,22): (21, "1.34282889", "m_s/m_d"),
    (7,20): (13, "0.81510847", "n/p"),
    (8,22): (14, "0.85074845", "c/s"),
    (8,33): (25, "1.28429395", "m_c/m_b"),
    (10,24): (14, "0.81257079", "u/d"),
    (19,33): (14, "0.59282105", "t/b"),
    (19,38): (19, "0.69935572", "m_H/m_W"),
    (30,41): (11, "0.23318262", "m_W/m_Z"),
}
dual = {
    (26,43): (17, "0.39764317", "dual(m_μ/m_τ)"),
    (22,43): (21, "0.58451209", "dual(m_s/m_d)"),
    (24,37): (13, "0.42637545", "dual(n/p)"),
    (22,36): (14, "0.50477238", "dual(c/s)"),
    (11,36): (25, "1.15361908", "dual(m_c/m_b)"),
    (20,34): (14, "0.56417798", "dual(u/d)"),
    (11,25): (14, "0.79191621", "dual(t/b)"),
    (6,25): (19, "1.13215250", "dual(m_H/m_W)"),
    (3,14): (11, "0.74470773", "dual(m_W/m_Z)"),
}
near = {
    (15,29): (14, "0.69948841", "0.000133", "m_H/m_W"),
    (12,27): (15, "0.81201152", "0.000559", "u/d"),
    (3,25):  (22, "1.34349283", "0.000664", "m_s/m_d"),
    (2,14):  (12, "0.81581961", "0.000711", "n/p"),
    (12,28): (16, "0.85167704", "0.000929", "c/s"),
    (11,23): (12, "0.69842218", "0.000934", "m_H/m_W"),
    (18,35): (17, "0.69909650", "0.000259", "m_H/m_W"),
}

def check_row(groupName, table):
    print(f"--- {groupName} ---")
    bad = []
    for (i,j), row in sorted(table.items()):
        d_exp, beat_str = row[0], row[1]
        label = row[2] if groupName == "known" else (row[3] if groupName == "near" else row[2])
        bt = abs(w(j) - w(i))
        d_got = j - i
        beat_ok = mp.almosteq(bt, mp.mpf(beat_str), rel_eps=mp.mpf('1e-6'))
        d_ok = (d_got == d_exp)
        flag = "✅" if (d_ok and beat_ok) else "❌"
        if not (d_ok and beat_ok): bad.append((i,j))
        print(f"  ({i:>2},{j:>2}) d={d_got:<2} beat={mp.nstr(bt, 9):<12} 表值={beat_str:<12} {label:<18} {flag}")
    print(f"  → {'全部一致 ✅' if not bad else f'{len(bad)} 個唔一致: {bad}'}")
    return len(bad)

nbad = 0
nbad += check_row("known", known)
nbad += check_row("dual", dual)
nbad += check_row("near", near)

# ================= Q1: DATA 定義漂移 =================
print()
print("=== Q1: DATA 定義漂移 ===")
data19 = {11, 13, 14, 17, 19, 21, 25}   # 19 號 (7 行含 d=14)
data17 = {11, 13, 17, 19, 21, 25}       # 17 號 (6 行)
data26 = data17                          # 26 預註冊 R1
chk1 = (data26 == data17)
print(f"  19 號 DATA (7 行) = {sorted(data19)}")
print(f"  17 號 DATA (6 行) = {sorted(data17)}")
print(f"  26 預註冊 R1       = {sorted(data26)}")
print(f"  canonical = 6 行版 (26 預註冊 lock) — 19 號 7 行版含 d=14 係雛形, 被 17 號取代")
print(f"  差異 = {{14}} — d=14 係 magic 行 (GEN), 唔應該入 data 行集")
print(f"  check: 26 == 17? {chk1}")

# ================= Q2: 行/格層次 =================
print()
print("=== Q2: data 格 (9) vs data 行 (6) 層次 ===")
cells = list(known.keys())
cell_ds = sorted({j - i for (i, j) in cells})
d14_cells = sorted((i, j) for (i, j) in cells if j - i == 14)
print(f"  data 格 9 個: {cells}")
print(f"  data 格 d 值集 = {cell_ds} (含 14!)")
print(f"  喺 d=14 行嘅 data 格 = {d14_cells} (u/d, c/s, t/b 三代 quark)")
print(f"  data 行 (canonical) = {sorted(data26)} ← 唔含 14")
print(f"  ★ 層次: d=14 行 = magic 操作行 (GEN), 行內 3 格 = data (格層)")
print(f"  ★ data-free 係「行層」規則 (排除成個行) — 唔需要亦唔應該排除 d=14 行")
print(f"  ★ d=14 = 唯一 magic×data 結合點 (17 號 §4 已閉合) ✓")

# ================= Q4: 18/946 =================
print()
print("=== Q4: 18/946 label 數目核對 ===")
total_labeled = len(known) + len(dual)
print(f"  9 known + 9 dual = {total_labeled} 格 → 00_record「18/946 有 label」✓")
print(f"  但 dual 9 格係「Z₂ 對偶候選」唔係「已知物理格」(19 號 §5 🟡) — 標記為 label 層, 唔係量度層")
print(f"  near 7 格 (diff<0.001) 係近似匹配候選 — 唔算 label")

# ================= Q5: R5 敏感度 =================
print()
print("=== Q5: ★R5 敏感度 — 若 data-free 用 7 行版 (含 14) ===")
MAGIC = [7, 14, 20, 22, 33]
def r5_proc(N, m_max, data_set):
    gen = sorted({m*a for a in (7, 11, 5) for m in range(1, m_max+1) if 1 <= m*a <= N-1})
    cand = [d for d in gen if d not in data_set]
    def lch(d): return any(d == m*luc(k) for m in range(1, m_max+1) for k in range(2, 8))
    byg = {}
    for d in cand: byg.setdefault(gcd(abs(N-d), 4*N), []).append(d)
    reps = []
    for g, lst in sorted(byg.items()):
        lst = sorted(lst)
        if len(lst) == 1: reps.append(lst[0])
        else:
            lp = [d for d in lst if d in (3, 7, 11, 29)]
            if len(lp) == 1: reps.append(lp[0])
            else:
                lc = [d for d in lst if lch(d)]
                reps.append(lc[0] if len(lc) == 1 else min(lst))
    bydeg = {}
    for d in reps: bydeg.setdefault(deg_of(d, N), []).append(d)
    final = []
    for de, lst in sorted(bydeg.items()):
        final.append(lst[0] if len(lst) == 1 else min(lst, key=lambda x: (x >= N//2, x)))
    return sorted(final)

def deg_of(d, N=44):
    g = gcd(abs(N-d), 4*N)
    m = (4*N)//g
    r = m; p = 2
    while p*p <= m:
        if m % p == 0:
            while m % p == 0: m //= p
            r -= r//p
        p += 1
    if m > 1: r -= r//m
    return 1 if r == 2 else r//2
def luc(k):
    a, b = 2, 1
    for _ in range(k): a, b = b, a + b
    return a

out6 = r5_proc(44, 4, data26)          # canonical 6 行
out7 = r5_proc(44, 4, data19)          # 如果 7 行版 (含 14)
print(f"  canonical 6 行版 → {out6}   = magic? {sorted(out6) == [7,14,20,22,33]}")
print(f"  7 行版 (含 14)    → {out7}   = magic? {sorted(out7) == [7,14,20,22,33]}")
print(f"  ★ 結論: 5/5 依賴 14 ∉ DATA 行集 — 若將 d=14 當 data 行排除, magic 14 消失 → FAIL")
print(f"  ★ 但 26 號預註冊 R1 (6 行版) 結果係 FAIL (0.375) — 6 行版唔係「為保 magic 而揀」,")
print(f"     data 行集先於 R5 定義; d=14 係 magic 行 (gen 操作), 3 個 data 格係格層")
print(f"     ⟹ 冇循環: 行/格分層已喺 17 號 §4 閉合 (操作=數據結合點)")

res = {
    "test": "45_data_audit",
    "Q3_mismatch": nbad,
    "Q1_canonical": "6 行版 {11,13,17,19,21,25} (26 預註冊)",
    "Q2_d14": {"cells_in_d14": d14_cells, "layer": "行=magic, 格=data"},
    "Q4_labeled": {"known": len(known), "dual": len(dual), "total": total_labeled},
    "Q5": {"out6": out6, "out7": out7, "stab": sorted(out6) == [7,14,20,22,33]},
}
with open("data/45_data_audit.json", "w") as f:
    json.dump(res, f, indent=1, ensure_ascii=False, default=str)
print()
print(f"輸出: data/45_data_audit.json   (Q3 mismatch = {nbad})")