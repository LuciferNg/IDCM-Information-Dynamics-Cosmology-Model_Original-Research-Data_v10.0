#!/usr/bin/env python3
"""
02_boundary_closure.py — 邊界閉合驗證
======================================
- 斜邊 (m=44): B(d, 88−d) = 4sin²(dπ/176) = 88-site 對偶鏈譜 γ'_k
- 左邊 (n=1): 全部模式同模式 1 嘅耦合
- 頂行 (d=1): 相鄰模態間隔, 零點 n=43.5 (半整數 = 觀察者通道)
"""
import math, json, os

Nd = 44
S = lambda x: math.sin(math.pi * x / 176)
C = lambda x: math.cos(math.pi * x / 176)
w = lambda n: 2 * math.sin(math.pi * n / 88)

res = {"hypotenuse": {}, "left_edge": {}, "top_row": {}}

# 斜邊: pair (44−d, 44), s = 88−d
hyp = []
for d in range(1, 44):
    n, m = 44 - d, 44
    b_true = w(m) - w(n)
    b_pred = 4 * S(d) * S(d)          # C(88−d) = sin(dπ/176)
    g88 = 4 * math.sin(math.pi * d / 176) ** 2   # 88-site 對偶譜
    hyp.append(abs(b_true - g88))
res["hypotenuse"] = {
    "rule": "B(d,88−d) = 4sin²(dπ/176) = 88-site 對偶鏈譜 γ'_d",
    "checks": len(hyp), "max_dev": max(hyp),
    "pass": max(hyp) < 1e-12,
    "significance": "拍頻表斜邊 = O34 對偶鏈 (88-site) 頭 43 個模態 — 表內含母譜!"
}

# 左邊: pair (1, d+1), s = d+2
lft = []
for d in range(1, 44):
    n, m = 1, d + 1
    b_true = w(m) - w(1)
    b_pred = 4 * S(d) * C(d + 2)
    lft.append(abs(b_true - b_pred))
res["left_edge"] = {
    "rule": "B(d,d+2) = 4·S(d)·C(d+2) (n=1 行)",
    "checks": len(lft), "max_dev": max(lft),
    "pass": max(lft) < 1e-12,
}

# 頂行: d=1, pair (n, n+1), s = 2n+1
top = []
for n in range(1, 44):
    m = n + 1
    b_true = w(m) - w(n)
    b_pred = 4 * S(1) * C(2 * n + 1)
    top.append(abs(b_true - b_pred))
# 零點: cos((2n+1)π/176) = 0 → 2n+1 = 88 → n = 43.5 (半整數)
zero_check = abs(math.cos((2 * 43.5 + 1) * math.pi / 176)) < 1e-12
res["top_row"] = {
    "rule": "B(1,2n+1) = 4·S(1)·C(2n+1) (相鄰間隔)",
    "checks": len(top), "max_dev": max(top),
    "pass": max(top) < 1e-12,
    "zero_point": "n=43.5 (半整數 = 觀察者子空間, O36)",
    "zero_verified": zero_check,
}

all_pass = all(v["pass"] for v in res.values()) and zero_check
out = os.path.join(os.path.dirname(__file__), "..", "data", "02_boundary_closure.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w") as f:
    json.dump(res, f, indent=2, ensure_ascii=False)

print("邊界閉合驗證:")
for k, v in res.items():
    print(f"  {k}: {v['checks']} checks, max dev = {v['max_dev']:.2e}, PASS={v['pass']}")
print(f"  斜邊意義: {res['hypotenuse']['significance']}")
print(f"  頂行零點: {res['top_row']['zero_point']} (驗證 {res['top_row']['zero_verified']})")
assert all_pass, "邊界閉合有 FAIL!"
print("✅ 全部通過")
