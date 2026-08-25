#!/usr/bin/env python3
"""
01_separability.py — 拍頻可分離性驗證
======================================
B(d,s) = 4·sin(dπ/176)·cos(sπ/176)   (差頻)
驗證: 946/946 全部吻合 (機器精度)
"""
import math, itertools, json, os

Nd = 44
S = lambda x: math.sin(math.pi * x / 176)
C = lambda x: math.cos(math.pi * x / 176)
w = lambda n: 2 * math.sin(math.pi * n / 88)

pairs = list(itertools.combinations(range(1, Nd + 1), 2))
results = {"total": len(pairs), "pass": 0, "fail": 0, "max_dev": 0.0,
           "fail_list": [], "structure": {}}

for (n, m) in pairs:
    d, s = m - n, m + n
    b_true = w(m) - w(n)
    b_pred = 4 * S(d) * C(s)
    dev = abs(b_true - b_pred)
    results["max_dev"] = max(results["max_dev"], dev)
    if dev < 1e-12:
        results["pass"] += 1
    else:
        results["fail"] += 1
        results["fail_list"].append({"pair": (n, m), "dev": dev})

results["pass_rate"] = results["pass"] / results["total"]
results["structure"] = {
    "rows": 43,  # d = 1..43
    "row_length_rule": "44 - d",
    "factorization": "946 = 2 × L₅ × (N_d − 1) = 2 × 11 × 43",
    "lucas_L5": 11,
    "comment": "可分離 = 1D×1D 外積結構, 43 個行標度 × 1 條萬有包絡"
}

out = os.path.join(os.path.dirname(__file__), "..", "data", "01_separability.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"可分離性驗證: {results['pass']}/{results['total']} PASS")
print(f"max dev = {results['max_dev']:.2e}  (機器精度 5.55e-16)")
print(f"946 = 2 × L₅ × (N_d − 1) = 2 × 11 × 43")
assert results["fail"] == 0, "有 FAIL 要查!"
print("✅ 全部通過")
