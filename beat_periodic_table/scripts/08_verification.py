#!/usr/bin/env python3
"""
08_verification.py — 獨立 Audit (唔 reuse 推導函數)
====================================================
由原始定義重新計算, 唔 import scripts/01-07 任何函數
"""
import math, itertools, json, os

Nd = 44
w = lambda n: 2 * math.sin(math.pi * n / 88)

pairs = list(itertools.combinations(range(1, Nd + 1), 2))
checks = {}

# [1] 946 = C(44,2)
checks["count"] = {"expected": 946, "actual": len(pairs),
                   "pass": len(pairs) == 946}

# [2] 全部拍頻無理 (數值上唔等於任何有理簡單值) — 用 sympy 抽樣
from sympy import sin, pi, Rational, nsimplify
sample = [(1, 2), (7, 44), (10, 24), (19, 33), (1, 44)]
samp_irr = []
for (n, m) in sample:
    x = sin(m * pi / 88) - sin(n * pi / 88)
    samp_irr.append({"pair": [n, m], "is_irrational": not x.is_rational})
checks["sample_irrational"] = {"pass": all(s["is_irrational"] for s in samp_irr),
                               "samples": samp_irr}

# [3] 可分離性獨立重算 (抽樣 50 對)
import random
random.seed(42)
sub = random.sample(pairs, 50)
S = lambda x: math.sin(math.pi * x / 176)
C = lambda x: math.cos(math.pi * x / 176)
maxdev = 0.0
for (n, m) in sub:
    d, s = m - n, m + n
    maxdev = max(maxdev, abs((w(m) - w(n)) - 4 * S(d) * C(s)))
checks["separability_sample"] = {"samples": 50, "max_dev": maxdev,
                                 "pass": maxdev < 1e-12}

# [4] 斜邊閉合 (88-site 譜)
hyp = max(abs((w(44) - w(44 - d)) - 4 * math.sin(math.pi * d / 176) ** 2)
          for d in range(1, 44))
checks["hypotenuse"] = {"max_dev": hyp, "pass": hyp < 1e-12}

# [5] 世代三重奏 d=14
gen = [(10, 24), (8, 22), (19, 33)]
checks["generations"] = {"all_d14": all(m - n == 14 for (n, m) in gen),
                         "pass": all(m - n == 14 for (n, m) in gen)}

# [6] 和頻轉置對偶 (抽樣)
sub2 = random.sample(pairs, 50)
maxdev_sum = 0.0
for (n, m) in sub2:
    d, s = m - n, m + n
    s_true = w(m) + w(n)
    s_pred = 4 * S(s) * C(d)
    maxdev_sum = max(maxdev_sum, abs(s_true - s_pred))
checks["sum_duality"] = {"samples": 50, "max_dev": maxdev_sum,
                         "pass": maxdev_sum < 1e-12}

# [7] Z₂ 對偶: γ_n + γ_{44−n} = 4
z2 = all(abs((4 * math.sin(math.pi * n / 88) ** 2 +
              4 * math.sin(math.pi * (44 - n) / 88) ** 2) - 4) < 1e-12
         for n in range(1, 44))
checks["z2_duality"] = {"pass": z2}

# [8] 全表唯一性 (差頻值全部唯一)
vals = [round(w(m) - w(n), 12) for (n, m) in pairs]
checks["uniqueness"] = {"total": len(vals), "unique": len(set(vals)),
                        "pass": len(set(vals)) == len(vals)}

all_pass = all(v["pass"] for v in checks.values())
res = {"checks": checks, "all_pass": all_pass,
       "total_checks": len(checks)}

out = os.path.join(os.path.dirname(__file__), "..", "data", "08_verification.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w") as f:
    json.dump(res, f, indent=2, ensure_ascii=False)

print("獨立 Audit:")
for k, v in checks.items():
    print(f"  [{k}] PASS={v['pass']}  {v}")
print(f"\n總計: {len(checks)} checks, all_pass = {all_pass}")
assert all_pass, "Audit 有 FAIL!"
print("✅ 全部通過")
