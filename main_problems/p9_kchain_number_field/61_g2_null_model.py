#!/usr/bin/env python3
"""
61_g2_null_model.py — G2 NULL MODEL: 隨機 k 命中 O-series 身份基準 (2026-10-17)
==============================================================================
53-55 號:「R5 輸出 6/6 有身份」 — 未問隨機基準!
48 號教訓: 統計檢查必須喺閉合論證之前
k=46 (對照) 都中 ⟹ 需要知領域命中率

方法:
  O-series 身份判準 (同 53-55 一致): sin(kπ/176) 或 4sin²(kπ/176)
  (或 gcd 化簡後) 出現喺 O-series 已閉合 md/scripts
  全量掃描 k=1..87 — 唔止 R5 輸出, 係全部 (零 import)
  然後: R5 輸出 6/6 vs 隨機基準命中率 → 統計比較
"""
import subprocess, json, math
from math import gcd

def sin_form(k):
    # 產生 sin(kπ/176) 嘅書寫變體, 加 gcd 化簡後嘅變體
    g = gcd(k, 176)
    forms = [f"sin({k}π/176)", f"sin({k} π/176)"]
    # 化簡: sin(kπ/176) = sin((k/g)π/(176/g))
    if g > 1:
        forms.append(f"sin({k//g}π/{176//g})")
    return forms

def has_identity(k):
    """grep O-series md+py: sin(kπ/176) 或 4sin² 出現 (唔包 p9/p13/o246)"""
    forms = sin_form(k)
    for f in forms:
        r = subprocess.run(
            ["grep", "-rE", f.replace("(", "\\(").replace(")", "\\)"),
             "--include=*.md", "--include=*.py",
             "main_problems", "open_problems_fresh"],
            capture_output=True, text=True,
            cwd="/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat", timeout=30)
        hits = [l for l in r.stdout.splitlines()
                if "p9_kchain" not in l and "p13_beat" not in l and "o246" not in l]
        if hits:
            return True, hits[0][:80]
    return False, ""

# 全量掃描 k=1..87
print("=== 全量掃描 k=1..87 (grep 真係會慢 — 88 個 subprocess) ===")
results = {}
for k in range(1, 88):
    hit, src = has_identity(k)
    results[k] = hit
    if k % 10 == 0 or k in (7, 14, 20, 22, 28, 33, 44, 46, 55, 68, 74, 81, 52, 59, 82, 84, 86, 54, 67, 75, 80, 83):
        print(f"  k={k:>2}: {'✅' if hit else '❌'} {src[:60]}")

hits = [k for k in range(1, 88) if results[k]]
n_k = 87
n_hit = len(hits)
print(f"\n  全 87 個 k: {n_hit} 命中 = {n_hit/n_k:.1%} 領域基準命中率")

R5_out = [7, 14, 22, 28, 33, 44]
r5_hits = [k for k in R5_out if results[k]]
r5_miss = [k for k in R5_out if not results[k]]
print(f"\n  R5 輸出 {R5_out}: 命中 {len(r5_hits)}/6 = {len(r5_hits)/6:.1%}")
print(f"    命中: {r5_hits}")
print(f"    未命中: {r5_miss}")
# 超幾何: 87 揀 6, 領域命中 n_hit, 觀察 6 揀 6 (或 r5_hits)
from math import comb
def hyper_p(k_success, n_sample, pop_hit, pop):
    # P(X >= k_success) 超幾何單側
    s = 0.0
    for x in range(k_success, n_sample + 1):
        if x <= pop_hit and n_sample - x <= pop - pop_hit:
            s += comb(pop_hit, x) * comb(pop - pop_hit, n_sample - x)
    return s / comb(pop, n_sample)

for ks in (6, len(r5_hits)):
    p = hyper_p(ks, 6, n_hit, n_k)
    print(f"  P(6 個抽中 ≥{ks} 命中 | 領域 {n_hit}/{n_k} = {n_hit/n_k:.1%}) = {p:.4f}")

res = {"test": "61_g2_null_model",
       "k_hits": [k for k in range(1, 88) if results[k]],
       "n_hit": n_hit, "n_k": n_k, "base_rate": round(n_hit / n_k, 4),
       "R5_out": R5_out, "R5_hits": r5_hits, "R5_miss": r5_miss,
       "p_hypergeo_6of6": hyper_p(6, 6, n_hit, n_k),
       "note": "領域命中率 = 隨機 k 命中 O-series 身份嘅機率"}
with open("data/61_g2_null_model.json", "w") as f:
    json.dump(res, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/61_g2_null_model.json")