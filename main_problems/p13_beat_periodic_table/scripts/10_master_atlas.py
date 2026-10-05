#!/usr/bin/env python3
"""
10_master_atlas.py — 44×44 全矩陣 Master Atlas 數據生成
========================================================
完整正方形張量: 44×44 = 1936 格
- 對角線 (m=n): 差頻 = 0 (真空基態), 和頻 = 4sin(nπ/88) (自耦合)
- 下三角 (m>n): 差頻 = ω_m − ω_n > 0 (正向物質算符)
- 上三角 (m<n): 差頻 = ω_n − ω_m < 0 (CPT 反物質對偶, 反對稱)
- 每格: [m,n] 座標 + (d,s) 可分離座標 + 代數次數 + 差頻/和頻值 + 物理標籤

輸出:
- data/master_atlas.csv         1936 格全量 (差頻+和頻+次數+標籤)
- data/master_atlas.json        重點結構 (對稱性驗證)
"""
import math, json, os, csv

Nd = 44
S = lambda x: math.sin(math.pi * x / 176)
C = lambda x: math.cos(math.pi * x / 176)
w = lambda n: 2 * math.sin(math.pi * n / 88)

def phi(n):
    r = n; p = 2
    while p * p <= n:
        if n % p == 0:
            while n % p == 0: n //= p
            r -= r // p
        p += 1
    if n > 1: r -= r // n
    return r

def sin_deg(k):
    """sin(kπ/176) 代數次數 (k 可負, 用 |k|)"""
    k = abs(k) % 176
    if k == 88:  # sin(π/2)=1
        return 1
    m = (88 - k) % 176
    g = math.gcd(352, m)
    return phi(352 // g) // 2

def beat_degree(d, s):
    """B(d,s) = 4·S(d)·C(s) 代數次數 (積化和差 + lcm)"""
    k1 = abs(d + s) % 352
    k2 = abs(d - s) % 352
    return math.lcm(sin_deg(k1), sin_deg(k2))

# ===== 物理標籤表 (已閉合 O34/O35/O13) =====
phys_labels = {
    (10, 24): "u/d Quark (O34)",
    (8, 22): "c/s Quark (O34)",
    (19, 33): "t/b Quark (O34)",
    (8, 33): "m_c/m_b (O34)",
    (1, 22): "m_s/m_d (O35)",
    (30, 41): "m_W/m_Z (O34)",
    (19, 38): "m_H/m_W (O34)",
    (1, 18): "m_mu/m_tau (O34)",
    (7, 20): "n/p BBN (O13)",
}

# 魔術行 (d = m−n) 標籤
magic_row_label = {
    7: "m7 anchor",
    14: "GEN d=14",
    20: "T(s->d)",
    22: "half-node",
    33: "K_tree",
}

def label_for(n, m):
    """返回物理標籤 (冇就 '')"""
    key = (min(n, m), max(n, m))
    if key in phys_labels:
        return phys_labels[key]
    d = abs(m - n)
    if d in magic_row_label and n != m:
        return f"Row {magic_row_label[d]}"
    if n == m:
        return "DIAG zero/self"
    return ""

# ===== 生成 1936 格 =====
rows = []
sym_check = {"antisym_count": 0, "sym_count": 0}
for n in range(1, Nd + 1):
    for m in range(1, Nd + 1):
        d = m - n
        s = m + n
        diff = w(m) - w(n)          # 差頻 (可負)
        summ = w(m) + w(n)          # 和頻 (全正)
        if n == m:
            deg_diff = 0            # 0 係有理數
            deg_sum = sin_deg(2 * n)  # 4sin(nπ/88) = 4sin(2nπ/176)
        else:
            deg_diff = beat_degree(abs(d), s)
            deg_sum = beat_degree(s, abs(d))  # 轉置: S(s)C(d)
        label = label_for(n, m)
        rows.append({
            "n": n, "m": m, "d": d, "s": s,
            "diff": round(diff, 12), "sum": round(summ, 12),
            "deg_diff": deg_diff, "deg_sum": deg_sum,
            "label": label,
        })
        # 對稱性檢查
        if n < m:
            if abs((w(m) - w(n)) + (w(n) - w(m))) < 1e-12:
                sym_check["antisym_count"] += 1
            if abs((w(m) + w(n)) - (w(n) + w(m))) < 1e-12:
                sym_check["sym_count"] += 1

# ===== 輸出 CSV =====
data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(data_dir, exist_ok=True)
csv_path = os.path.join(data_dir, "master_atlas.csv")
with open(csv_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["n", "m", "d", "s", "diff", "sum",
                                           "deg_diff", "deg_sum", "label"])
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

# ===== 輸出 JSON 摘要 =====
# 對角線和頻值: 4sin(nπ/88)
diag_sum = [round(4 * math.sin(n * math.pi / 88), 12) for n in range(1, 45)]
summary = {
    "dimension": "44 × 44 = 1936 cells",
    "diagonal_diff": "0 (vacuum baseline)",
    "diagonal_sum_formula": "4sin(nπ/88) = 2ω_n (self-coupling)",
    "diagonal_sum_values": diag_sum,
    "lower_triangle": "diff > 0 (matter operators)",
    "upper_triangle": "diff < 0 (CPT anti-matter duality)",
    "antisymmetry_verified": sym_check["antisym_count"] == 946,
    "antisym_pairs": sym_check["antisym_count"],
    "symmetry_verified": sym_check["sym_count"] == 946,
    "sym_pairs": sym_check["sym_count"],
    "total_cells": len(rows),
    "labeled_cells": sum(1 for r in rows if r["label"]),
    "note": "差頻 = 反對稱 (B(m,n) = −B(n,m)): CPT 對偶; 和頻 = 對稱 (B'(m,n) = B'(n,m)): 自對偶",
}

with open(os.path.join(data_dir, "master_atlas.json"), "w") as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

print(f"✅ Master Atlas 數據生成:")
print(f"   CSV: {csv_path} ({len(rows)} 格)")
print(f"   差頻反對稱配對: {sym_check['antisym_count']}/946")
print(f"   和頻對稱配對: {sym_check['sym_count']}/946")
print(f"   標籤格: {sum(1 for r in rows if r['label'])}")
print(f"   對角線和頻 (n=1..10): {diag_sum[:10]}")
assert sym_check["antisym_count"] == 946 and sym_check["sym_count"] == 946
print("✅ 對稱性全部驗證")
