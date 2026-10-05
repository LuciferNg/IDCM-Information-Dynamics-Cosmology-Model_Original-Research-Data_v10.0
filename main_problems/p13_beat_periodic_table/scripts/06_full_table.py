#!/usr/bin/env python3
"""
06_full_table.py — 完整拍頻周期表輸出
=====================================
輸出:
- data/beat_table_full.csv   (946 差頻 + 946 和頻, 完整座標)
- data/beat_table_rows.json  (43 行 × 列結構, 含魔術行標記)
- data/periodic_summary.json (周期表摘要: 行/列/族/週期)
"""
import math, itertools, json, os, csv

Nd = 44
S = lambda x: math.sin(math.pi * x / 176)
C = lambda x: math.cos(math.pi * x / 176)
w = lambda n: 2 * math.sin(math.pi * n / 88)
B = lambda d, s: 4 * S(d) * C(s)
Bp = lambda d, s: 4 * S(s) * C(d)

pairs = list(itertools.combinations(range(1, Nd + 1), 2))
data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(data_dir, exist_ok=True)

# ===== 完整 CSV (差頻) =====
with open(os.path.join(data_dir, "beat_table_full.csv"), "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["n", "m", "d", "s", "type", "value", "S_d", "C_s", "reduced"])
    for (n, m) in pairs:
        d, s = m - n, m + n
        val = B(d, s)
        writer.writerow([n, m, d, s, "difference", f"{val:.12f}", f"{S(d):.12f}",
                         f"{C(s):.12f}", f"{val/S(d):.12f}"])
    for (n, m) in pairs:
        d, s = m - n, m + n
        val = Bp(d, s)  # 和頻
        writer.writerow([n, m, d, s, "sum", f"{val:.12f}", f"{S(s):.12f}",
                         f"{C(d):.12f}", f"{val/S(s):.12f}"])

# ===== 43 行結構 =====
rows_out = {}
for d in range(1, 44):
    members = [(s, B(d, s)) for (n, m) in pairs if m - n == d]
    members.sort()
    rows_out[str(d)] = {
        "row_length": len(members),
        "S_d": S(d),
        "S_d_label": f"sin({d}π/176)",
        "members": [[s, round(v, 12)] for s, v in members],
    }

# ===== 周期表摘要 =====
magic_rows = {
    7: "m_7 錨點 √γ₇/2", 14: "★世代規則 B²−2", 20: "轉移矩陣 2n_u",
    22: "半節點 44/2", 33: "K_tree 33",
}
summary = {
    "title": "拍頻周期表 (Beat Periodic Table)",
    "structure": "43 行 (d=1..43, 模態間距) × 87 列 (s=3..87, 模態和)",
    "formula_difference": "B(d,s) = 4·sin(dπ/176)·cos(sπ/176)",
    "formula_sum": "B'(d,s) = 4·sin(sπ/176)·cos(dπ/176) (轉置對偶)",
    "total_beats": 946,
    "total_pairs": 1892,
    "row_rule": "行長 = 44 − d (三角表)",
    "column_rule": "s 由 d+2 到 88−d, 步長 2 (同奇偶)",
    "periodicity": "列方向: s → s+88 → cos 值週期重現 (半圈); 行方向: d → 88−d → sin↔cos 互補",
    "magic_rows": {str(k): v for k, v in magic_rows.items()},
    "hypotenuse": "斜邊 (m=44) = 88-site 對偶鏈譜 4sin²(dπ/176)",
    "generations": "行14 × 列{30,34,52}: c/s, u/d, t/b",
    "duality": "和頻表 = 差頻表轉置 (O54 反物質對偶)",
    "moseley": "每行÷S(d) → 萬有包絡 4cos(sπ/176) (946/946 零例外)",
    "irrationality": "全部 946 個無理 (代數次數 ≥ 4; 分層見 05)",
}

with open(os.path.join(data_dir, "periodic_summary.json"), "w") as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)
with open(os.path.join(data_dir, "beat_table_rows.json"), "w") as f:
    json.dump(rows_out, f, indent=2, ensure_ascii=False)

print(f"✅ 完整表輸出完成:")
print(f"  beat_table_full.csv: 1892 行 (946 差頻 + 946 和頻)")
print(f"  beat_table_rows.json: 43 行 × 列結構")
print(f"  periodic_summary.json: 周期表摘要")
print(f"\n週期表摘要:")
for k, v in summary.items():
    print(f"  {k}: {v}")
