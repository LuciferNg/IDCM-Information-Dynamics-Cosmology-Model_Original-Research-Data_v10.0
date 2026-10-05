#!/usr/bin/env python3
"""
03_magic_rows.py — 魔術行 + 世代座標
======================================
- 魔術行: d=7 (m_7 錨點), d=14 (世代規則), d=20 (轉移矩陣), d=22 (半節點), d=33 (K_tree)
- 世代三重奏: u/d=(10,24), c/s=(8,22), t/b=(19,33) 全部 d=14
"""
import math, itertools, json, os

Nd = 44
S = lambda x: math.sin(math.pi * x / 176)
C = lambda x: math.cos(math.pi * x / 176)
w = lambda n: 2 * math.sin(math.pi * n / 88)

pairs = list(itertools.combinations(range(1, Nd + 1), 2))
rows = {}
for (n, m) in pairs:
    d, s = m - n, m + n
    rows.setdefault(d, []).append((s, n, m, w(m) - w(n)))

magic = {
    7: "m_7 錨點: √γ₇/2 = sin(7π/88) = 0.247307; Δn=7 → sin(7π/88)/2 → m_7 DM 質量 13.8 MeV",
    14: "★世代規則 Δn = B²−2 = 14 (O34 scripts/19)",
    20: "轉移矩陣 T(s→d) = 2n_u = 20 (O35 scripts/11)",
    22: "半節點基線 44/2 = 22 (O20 EE 極化峰)",
    33: "K_tree 尺度維 (B=4, L₅=11 → K_tree 33)",
}

res = {"magic_rows": {}, "generation_triplet": {}, "checks": {}}
for d, label in magic.items():
    vals = [b for (s, n, m, b) in rows[d]]
    res["magic_rows"][str(d)] = {
        "members": len(rows[d]),
        "S_d": S(d),
        "label": label,
        "min": min(vals), "max": max(vals),
    }

# 世代三重奏
gen = {(10, 24): "u/d", (8, 22): "c/s", (19, 33): "t/b"}
triplet = {}
for (n, m), name in gen.items():
    d, s = m - n, m + n
    triplet[name] = {"pair": [n, m], "d": d, "s": s, "row": f"行{d}", "col": f"列{s}"}
    assert d == 14, f"世代 {name} 唔喺行 14!"
res["generation_triplet"] = {
    "row": 14,
    "rule": "全部世代配對 Δn=14 = B²−2",
    "members": triplet,
    "s_spacing": {"34−30": 4, "rule": "4 = B (MERA 分支因子)"},
}

# 魔術行驗證
res["checks"]["all_magic_rows_present"] = all(d in rows for d in magic)
res["checks"]["generation_all_d14"] = all(v["d"] == 14 for v in triplet.values())
res["checks"]["s_spacing_B"] = (triplet["c/s"]["s"] == 30 and
                                triplet["u/d"]["s"] == 34 and
                                triplet["t/b"]["s"] == 52)

# 額外: Δn=14 行全部 30 個成員
res["checks"]["d14_members"] = len(rows[14]) == 30

out = os.path.join(os.path.dirname(__file__), "..", "data", "03_magic_rows.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w") as f:
    json.dump(res, f, indent=2, ensure_ascii=False)

print("魔術行:")
for d, v in res["magic_rows"].items():
    print(f"  d={d:>2}: {v['members']:>2} 成員 | S(d)={v['S_d']:.6f} | {v['label']}")
print(f"\n世代三重奏 (全部行 14):")
for name, v in triplet.items():
    print(f"  {name}: {v['pair']} → {v['row']} × {v['col']}")
print(f"\n驗證: {res['checks']}")
assert all(res["checks"].values()), "魔術行驗證 FAIL!"
print("✅ 全部通過")
