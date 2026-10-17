#!/usr/bin/env python3
"""
63_g2_null_model_v2.py — G2 NULL MODEL 修正版: 三判準全量 (2026-10-17)
=====================================================================
61 號 (判準 B direct grep per-k) work: 領域 42.5%, R5 3/6 p=0.51 — 唔顯著
62 號 grep_all + parse 壞咗 (過濾後空) — 修正: 用 grep -oE 提取全部 d

三判準:
  B: sin(kπ/176) 直接出現喺 O-series (k∈[1,87])
  C: sin(nπ/88) 出現 (n∈[1,44]) — 44-site 領域
  A = B ∪ carry(k=2n, n∈C∩[1,43])
"""
import subprocess, json, re
from math import comb

repo = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat"

def grep_o(pattern):
    """grep -oE 提取全部 match, 排除 p9/p13/o246 檔案"""
    r = subprocess.run(
        ["grep", "-rE", pattern, "-o", "--include=*.md", "--include=*.py",
         "main_problems", "open_problems_fresh"],
        capture_output=True, text=True, cwd=repo, timeout=90)
    out = []
    for line in r.stdout.splitlines():
        fname = line.split(":", 1)[0]
        if any(x in fname for x in ("p9_kchain", "p13_beat", "o246")):
            continue
        m = re.search(pattern, line)
        if m:
            out.append(m.group(0))
    return out

print("=== 提取 sin(dπ/176) 全部出現 ===")
hits176 = grep_o(r"sin\([0-9]+π/176\)")
d176 = set()
for h in hits176:
    m = re.match(r"sin\(([0-9]+)π/176\)", h)
    if m:
        d176.add(int(m.group(1)))
print(f"  176 分母出現 ({len(hits176)} raw, {len(d176)} unique d): {sorted(d176)}")

print()
print("=== 提取 sin(nπ/88) 全部出現 (44-site) ===")
hits88 = grep_o(r"sin\([0-9]+π/88\)")
d88 = set()
for h in hits88:
    m = re.match(r"sin\(([0-9]+)π/88\)", h)
    if m:
        n = int(m.group(1))
        if 1 <= n <= 44:
            d88.add(n)
print(f"  88 分母出現 n=1..44 ({len(d88)} unique): {sorted(d88)}")

# 判準 B: k∈[1,87], sin(kπ/176) 直接
B = set(k for k in range(1, 88) if k in d176)
# 判準 A: B ∪ carry (k=2n, n∈d88)
A = set(B)
for n in d88:
    if 2 * n <= 87:
        A.add(2 * n)
# carry 反向: 如果 odd k 嘅 2k 有身份 (唔適用 — 唔好亂加)

print()
print(f"  ★判準 B (直接 176):      {len(B)}/87 = {len(B)/87:.1%}")
print(f"  ★判準 A (B∪偶模 carry): {len(A)}/87 = {len(A)/87:.1%}")
print(f"  A 新增 (carry): {sorted(A - B) if len(A-B) < 40 else len(A-B)}")
print(f"  88-site 本身 d176 集: {sorted(d176)}")

R5 = [7, 14, 22, 28, 33, 44]
print()
for name, S in (("B", B), ("A", A)):
    hits = [k for k in R5 if k in S]
    miss = [k for k in R5 if k not in S]
    print(f"  R5 vs 判準 {name}: {len(hits)}/6 ({len(hits)/6:.1%}) 命中 {hits} 未中 {miss}")

def hyper_p(k_success, n_sample, pop_hit, pop):
    s = 0.0
    for x in range(k_success, n_sample + 1):
        if x <= pop_hit and n_sample - x <= pop - pop_hit:
            s += comb(pop_hit, x) * comb(pop - pop_hit, n_sample - x)
    return s / comb(pop, n_sample)

print()
for name, S in (("B", B), ("A", A)):
    hits = len([k for k in R5 if k in S])
    p = hyper_p(hits, 6, len(S), 87)
    print(f"  P(6 抽 ≥{hits} | {name} 領域 {len(S)/87:.1%}) = {p:.4f}  {'✅ 顯著' if p < 0.05 else '❌ 唔顯著'}")

res = {"test": "63_g2_null_model_v2",
       "d176": sorted(d176), "d88": sorted(d88),
       "B": sorted(B), "A": sorted(A),
       "base_B": round(len(B)/87, 4), "base_A": round(len(A)/87, 4),
       "R5": R5,
       "R5_B": [k for k in R5 if k in B],
       "R5_A": [k for k in R5 if k in A]}
with open("data/63_g2_null_model_v2.json", "w") as f:
    json.dump(res, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/63_g2_null_model_v2.json")