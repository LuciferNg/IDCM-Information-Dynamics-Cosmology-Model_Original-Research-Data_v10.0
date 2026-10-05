#!/usr/bin/env python3
"""
04_moseley_collapse.py — Moseley 律塌縮驗證
==========================================
每行除以自己嘅 sin 標度 S(d) → 946 個點全部塌縮到同一條萬有包絡 4·cos(sπ/176)
(Moseley 律類比: √ν ∝ Z — 週期表嘅「列規律」)
"""
import math, itertools, json, os

Nd = 44
S = lambda x: math.sin(math.pi * x / 176)
C = lambda x: math.cos(math.pi * x / 176)
w = lambda n: 2 * math.sin(math.pi * n / 88)

pairs = list(itertools.combinations(range(1, Nd + 1), 2))
res = {"total": 0, "pass": 0, "fail": 0, "max_dev": 0.0,
       "envelope": "4·cos(sπ/176)", "fail_list": []}

for (n, m) in pairs:
    d, s = m - n, m + n
    b = w(m) - w(n)
    reduced = b / S(d)          # 行歸一化
    env = 4 * C(s)
    dev = abs(reduced - env)
    res["total"] += 1
    res["max_dev"] = max(res["max_dev"], dev)
    if dev < 1e-12:
        res["pass"] += 1
    else:
        res["fail"] += 1
        res["fail_list"].append({"pair": (n, m), "dev": dev})

res["pass_rate"] = res["pass"] / res["total"]
res["meaning"] = ("946 個無理數嘅資訊量 = 43 個行標度 S(d) × 1 條萬有包絡 C(s) — "
                  "Mendeleev/Moseley 式結構: 元素周期表有例外, 呢張表 946/946 零例外!")

out = os.path.join(os.path.dirname(__file__), "..", "data", "04_moseley_collapse.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w") as f:
    json.dump(res, f, indent=2, ensure_ascii=False)

print(f"Moseley 塌縮: {res['pass']}/{res['total']} PASS, max dev = {res['max_dev']:.2e}")
print(f"946 個點 → 單一包絡 {res['envelope']}")
assert res["fail"] == 0, "Moseley 塌縮有 FAIL!"
print("✅ 全部通過")
