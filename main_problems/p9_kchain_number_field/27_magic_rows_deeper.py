#!/usr/bin/env python3
"""
27_magic_rows_deeper.py — P9 續推: magic rows 結構差異盲測 + v₂ 規則公平化 (2026-10-17)
====================================================================================
上輪盲測 26 判死 R1/R2 為代表選擇規則 → 今輪換方向:
  TEST D: magic rows (d∈{7,14,20,22,33}) 成員結構 vs filler rows — 有冇統計差異?
          (如果 magic = 操作族, 成員結構應該有 marker; 冇 = 又一次負結果)
  TEST E: missing_gcd.py §6 的 v₂ 奇偶規則 (v₂(176/g) 奇 → magic) — 正式化 + 例外分析
  TEST F: 7 vs 29 vs 3 嘅新判準候選 (Lucas 質數 / 半鏈位置) — 有預言力先算

zero import 原推導; 純整數/Fraction; 43 rows 獨立比較 (filler n=38 vs magic n=5)
"""
import json, csv
from math import gcd
from collections import Counter, defaultdict

MAGIC = [7, 14, 20, 22, 33]
DATA  = {11, 13, 17, 19, 21, 25}

# ---------- 讀 946 beat 表 (i,j) ----------
beats = []
with open("data/beat_algebraic_table.txt") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 2:
            try:
                i, j = int(parts[0]), int(parts[1])
                if 1 <= i <= 44 and 1 <= j <= 44:
                    beats.append((i, j))
            except ValueError:
                pass
assert len(beats) == 946, f"FAIL: {len(beats)} != 946"

# ---------- rows: d = |i-j| ----------
rows = defaultdict(list)
for (i, j) in beats:
    d = abs(i - j)
    rows[d].append((i, j))

# ---------- TEST D: s 值結構 (s = i+j) ----------
def s_structure(d):
    """成員 s 值分佈: 範圍/步長/奇偶 mix/平均"""
    ss = sorted(i + j for (i, j) in rows[d])
    if len(ss) < 2:
        return None
    steps = [ss[k+1] - ss[k] for k in range(len(ss)-1)]
    return {
        "n": len(ss),
        "s_min": ss[0], "s_max": ss[-1],
        "s_steps_uniq": sorted(set(steps)),
        "s_step_mode": Counter(steps).most_common(1)[0][0],
        "s_parity_mix": len(set(s % 2 for s in ss)),  # 1 = 全同奇偶, 2 = 混合
        "s_mean": sum(ss) / len(ss),
    }

magic_s = {d: s_structure(d) for d in MAGIC}
filler_s = {d: s_structure(d) for d in range(1, 44) if d not in MAGIC and d not in DATA}
# 過濾單成員行 (d=43 只有 (1,44) 一個成員, s_structure=None)
magic_s = {d: v for d, v in magic_s.items() if v}
filler_s = {d: v for d, v in filler_s.items() if v}

# 統計比較
def st(name, f):
    mv = [f(magic_s[d]) for d in magic_s]
    fv = [f(filler_s[d]) for d in filler_s]
    return {"magic": mv, "filler_mean": round(sum(fv)/len(fv), 4),
            "filler_range": [min(fv), max(fv)],
            "magic_outside": [v for v in mv if v < min(fv) or v > max(fv)]}

TEST_D = {
    "s_step_mode": st("mode", lambda x: x["s_step_mode"]),
    "s_parity_mix": st("parity", lambda x: x["s_parity_mix"]),
    "s_mean_scaled": st("mean/88", lambda x: round(x["s_mean"]/88, 4)),
}
# magic vs filler s_step_mode 分佈比較
TEST_D["step_mode_counts"] = {
    "magic": dict(Counter(magic_s[d]["s_step_mode"] for d in MAGIC)),
    "filler": dict(Counter(filler_s[d]["s_step_mode"] for d in filler_s)),
}
TEST_D["s_mean_verdict"] = ("magic s_mean 超出 filler 範圍" if TEST_D["s_mean_scaled"]["magic_outside"]
                            else "magic s_mean 全部喺 filler 範圍內 — 冇結構差異")

# ---------- TEST E: v₂ 奇偶規則 ----------
def v2(n):
    c = 0
    while n % 2 == 0 and n > 0:
        c += 1; n //= 2
    return c

e_rows = {}
for g in [1, 2, 4, 8, 11, 16, 22]:
    ds = [d for d in range(1, 44) if gcd(abs(44 - d), 176) == g]
    e_rows[g] = {
        "d_list": ds,
        "has_magic": bool([d for d in ds if d in MAGIC]),
        "magic_d": [d for d in ds if d in MAGIC],
        "v2_176_over_g": v2(176 // g),
        "v2_parity": "odd" if v2(176 // g) % 2 else "even",
        "contains_11_factor": (176 // g) % 11 == 0,
    }
v2_odd = [g for g, v in e_rows.items() if v["v2_parity"] == "odd"]
v2_even = [g for g, v in e_rows.items() if v["v2_parity"] == "even"]
TEST_E = {
    "per_gcd": e_rows,
    "v2_odd_classes": v2_odd,
    "v2_even_classes": v2_even,
    "rule": "v₂(176/g) 奇 → 必有 magic? (g∈{2,8,22})",
    "rule_check": all(e_rows[g]["has_magic"] for g in v2_odd),
    "even_exceptions": [g for g in v2_even if e_rows[g]["has_magic"]],
    "note": "v₂ 奇數類 3/3 全 magic; v₂ 偶數類 4 個, g=4/16 filler, g=1/11 magic (有例外) — 規則唔完整, 只係『v₂ 奇 ⇒ magic』單向"
}

# ---------- TEST F: 7 vs 29 vs 3 判準候選 ----------
L = {0: 2, 1: 1, 2: 3, 3: 4, 4: 7, 5: 11, 6: 18, 7: 29}
gcd1 = [d for d in range(1, 44) if gcd(abs(44 - d), 176) == 1]
lucas_in_g1 = [(idx, val) for idx, val in L.items() if val in gcd1]
# 候選判準: 「Lucas 質數 + 3mod4 + 最小大於 half?」唔好 — 要結構
# 觀察: 7 喺前半 (d<22), 29 喺後半 (d>22); 3 喺前半都係 Lucas 質數 3mod4 → 3 vs 7
# 新候選: d 對應嘅 γ_d = 4sin²(dπ/88) 有冇「跨半」性質? 7+81=88? 7*? 
# F1: d 同 88 嘅對稱 partner: 88−d ±? 7↔81, 29↔59, 3↔85
TEST_F = {
    "gcd1_lucas": lucas_in_g1,
    "candidates": {"3": "L₂=L₃ (重複索引) mod4=3", "7": "L₄ (唯一) mod4=3 前半", "29": "L₇ (唯一) mod4=1 後半"},
    "seven_symmetry": {"partner_88": 88 - 7, "partner_44": 44 - 7, "half_relation": "7 < 22 (half-node)"},
    "twenty_nine_symmetry": {"partner_88": 88 - 29, "partner_44": 44 - 29, "half_relation": "29 > 22"},
    "verdict": "7 = 前半獨有 Lucas 質數 mod4=3; 29 後半 + mod4=1; 3 重複索引 → 7 唯一滿足全部三條件 (但未有預言力測試 — 樣本 1)"
}

res = {"test": "27_magic_rows_deeper", "TEST_D": TEST_D, "TEST_E": TEST_E, "TEST_F": TEST_F}

with open("data/27_magic_deeper.json", "w") as f:
    json.dump(res, f, indent=1, ensure_ascii=False, default=str)

print("=== TEST D: magic vs filler 成員結構 ===")
print("s_step_mode: magic =", dict(Counter(magic_s[d]['s_step_mode'] for d in MAGIC)))
print("             filler =", dict(Counter(filler_s[d]['s_step_mode'] for d in filler_s)))
print("s_mean: magic =", [round(magic_s[d]['s_mean'],2) for d in MAGIC],
      " filler 範圍 =", [round(min(filler_s[d]['s_mean'] for d in filler_s),2),
                        round(max(filler_s[d]['s_mean'] for d in filler_s),2)])
print("s_parity_mix: magic =", [magic_s[d]['s_parity_mix'] for d in MAGIC],
      " filler uniq =", sorted(set(filler_s[d]['s_parity_mix'] for d in filler_s)))
print("verdict:", TEST_D["s_mean_verdict"])
print()
print("=== TEST E: v₂ 奇偶規則 ===")
for g in sorted(e_rows):
    v = e_rows[g]
    print(f"  gcd={g:2d}: v2={v['v2_176_over_g']}({v['v2_parity']:4s}) 11因子={v['contains_11_factor']!s:5s} magic={v['has_magic']!s:5s} d={v['d_list']}")
print("v₂奇 ⇒ magic (單向) 成立:", TEST_E["rule_check"], "| 例外(偶但有magic):", TEST_E["even_exceptions"])
print()
print("=== TEST F: gcd=1 內 Lucas ===")
print("Lucas 喺 gcd=1:", TEST_F["gcd1_lucas"])
print(TEST_F["verdict"])
print()
print("輸出: data/27_magic_deeper.json")