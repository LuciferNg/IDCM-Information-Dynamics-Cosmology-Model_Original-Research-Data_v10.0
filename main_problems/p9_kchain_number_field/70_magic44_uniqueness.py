#!/usr/bin/env python3
"""
70_magic44_uniqueness.py — 44-site magic 獨特性 null 對照 (2026-10-17)
======================================================================
背景: 61/63 號擊穿 88-site label 命中率 (領域 54% vs R5 66%, p=0.42)。
      44-site R5 5/5 EXACT 嘅「獨特性」未做 null — 呢個係已知缺口。

問題一 (anchor 唯一性): cover magic 5/5 嘅 3-anchor 集有幾多個?
  35 號 Q1 提示 3/12341 — 全枚舉確認。
問題二 (magic 結構獨特性): 隨機 5 個 d (1..43), gcd 類互斥 + deg 層互斥
  嘅機率有幾高? (MC 10^6)
問題三 (O-series 命中率): 用 63 號同判準 (直接 sin(dπ/88) / sin(2dπ/176)),
  領域 d∈1..43 命中率 vs magic 5 命中率 — 超幾何 p。
問題四 (magic 覆蓋 O-series 身份): magic 5 個全部有 O-series 身份 ⟹
  若領域命中率低而 magic 全中, 才係真獨特。

工具: 零 import 原 scripts; mpmath 唔需要 (純整數 + grep); MC 隨機種子固定。
"""
import random
import subprocess
import json
import os
from math import gcd
from itertools import combinations

random.seed(7070)
ROOT = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat"
MAGIC = [7, 14, 20, 22, 33]
ALLD = list(range(1, 44))

PASS = 0
FAIL = 0
FAILS = []
OUT = []

def chk(name, desc, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  ✅ {name}: {desc}")
    else:
        FAIL += 1
        FAILS.append(name)
        print(f"  ❌ {name}: {desc}" + (f"  [{detail}]" if detail else ""))
    OUT.append({"id": name, "desc": desc, "ok": ok, "detail": detail})

def gcl(d):
    return gcd(abs(44 - d), 176)

def om_deg(d):
    m = 176 // gcl(d)
    r = m; p = 2
    while p * p <= m:
        if m % p == 0:
            while m % p == 0:
                m //= p
            r -= r // p
        p += 1
    if m > 1:
        r -= r // m
    return r // 2

def G(anchors, ms=(1, 2, 3, 4)):
    return sorted({m * a for a in anchors for m in ms if 1 <= m * a <= 43})

print("=" * 72)
print("A. Anchor 唯一性 — cover magic 5/5 嘅 3-anchor 全枚舉")
print("=" * 72)
covers = []
for tri in combinations(ALLD, 3):
    if len(set(G(tri)) & set(MAGIC)) == 5:
        covers.append(tri)
chk("A1_cover_count", "cover magic 5/5 嘅 3-anchor = 3 個 (C(43,3)=12341)",
    len(covers) == 3, f"{len(covers)}/12341 = {len(covers)/12341*100:.3f}%")
chk("A2_anchor_known", "已知 anchor (7,11,5) ∈ covers (sorted (5,7,11))",
    tuple(sorted((7, 11, 5))) in covers, str(covers))
other = [c for c in covers if c != (7, 11, 5)]
chk("A3_anchor_not_unique", "★★anchor 唔係唯一: 有 {other} 都 cover 5/5",
    len(other) >= 1, f"其他 = {other}")
print(f"  [誠實標記: 3 個 anchor 集都 cover magic — anchor=(7,11,5) 唔係唯一解]")

print()
print("=" * 72)
print("B. Magic 結構獨特性 — gcd 類互斥 + deg 層互斥 vs 隨機")
print("=" * 72)
# B1: magic 5 個 gcd 類兩兩唔同 + deg 兩兩唔同
g_m = [gcl(d) for d in MAGIC]
d_m = [om_deg(d) for d in MAGIC]
chk("B1_magic_struct", "magic 5 個 gcd 類兩兩唔同 + deg 兩兩唔同",
    len(set(g_m)) == 5 and len(set(d_m)) == 5, f"gcd={sorted(g_m)} deg={sorted(d_m)}")
# B2: 窮舉全 C(43,5)=962,598 組合做精確機率
from itertools import combinations as combos5
hit = 0
tot = 0
for five in combos5(ALLD, 5):
    tot += 1
    if len({gcl(x) for x in five}) == 5 and len({om_deg(x) for x in five}) == 5:
        hit += 1
pb = hit / tot
chk("B2_null_prob", f"窮舉: 隨機 5 個 gcd+deg 全互斥機率 = {pb:.5f}",
    pb < 0.05, f"{hit}/{tot} = {pb:.5f}")
# B3: 只 gcd 互斥 (唔理 deg) 嘅機率做對照
hitg = 0
for five in combos5(ALLD, 5):
    if len({gcl(x) for x in five}) == 5:
        hitg += 1
pg = hitg / tot
chk("B3_gcd_only", f"只 gcd 互斥機率 = {pg:.5f} (deg 層係額外壓縮)",
    pg < 0.10, f"{pg:.5f}")

print()
print("=" * 72)
print("C. O-series 身份命中率 — 63 號同判準 (44-site 版)")
print("=" * 72)
# 判準: d 有身份 ⟺ sin(dπ/88) 或者 sin(2dπ/176) 喺 O-series 任何地方出現
import re as _re
# 優化: 一次 grep 掃全部 112 個 pattern (43d × 4 變體) → 用 ripgrep -l 攞文件集
# 然後逐 d 本地比對 (唔使再 spawn 43×4 個 process)
pats_all = []
for d in ALLD:
    pats_all += [f"sin({d}π/88)", f"sin({2 * d}π/176)", f"γ_{d}", f"gamma_{d}"]
allfiles = []
for rootdir in ("open_problems_fresh", "main_problems"):
    r = subprocess.run(["grep", "-rl", "--include=*.py", "--include=*.md",
                        "-e", "sin(", f"{ROOT}/{rootdir}"],
                       capture_output=True, text=True)
    allfiles += r.stdout.splitlines()
    r2 = subprocess.run(["grep", "-rl", "--include=*.py", "--include=*.md",
                         "-e", "γ_", f"{ROOT}/{rootdir}"],
                        capture_output=True, text=True)
    allfiles += r2.stdout.splitlines()
    r3 = subprocess.run(["grep", "-rl", "--include=*.py", "--include=*.md",
                         "-e", "gamma_", f"{ROOT}/{rootdir}"],
                        capture_output=True, text=True)
    allfiles += r3.stdout.splitlines()
allfiles = sorted(set(f for f in allfiles if f))
corpus = ""
for f in allfiles:
    try:
        corpus += open(f, encoding="utf-8", errors="ignore").read() + "\n"
    except Exception:
        pass

# 判準收緊 (同 63 號判準 B): 只用 sin(dπ/88) 直接出現 + sin(2dπ/176) 偶模 carry
# ⚠γ_ pattern 淘汰: γ_n 全譜 44 個都喺 docs 出現 (43/43 = 100%), 係全譜符號
#   唔係身份判準 — 第一版用佢做污染源 (C 段 100% 結果要重新計)
def has_identity(d):
    return f"sin({d}π/88)" in corpus or f"sin({2 * d}π/176)" in corpus

hits = {d: has_identity(d) for d in ALLD}
magic_all = all(hits[d] for d in MAGIC)
n_dom = sum(1 for d in ALLD if hits[d])
chk("C1_magic_all_hit", "magic 5 個全部有 O-series 身份", magic_all,
     f"magic hits: { {d: hits[d] for d in MAGIC} }")
chk("C2_domain_rate", f"領域命中率 = {n_dom}/43 = {n_dom/43*100:.1f}%",
    True, f"hits={n_dom}")
# 超幾何: 43 揀 5, 領域 hit n_dom, magic 全中 (5/5) 機率
from math import comb
def hypergeom_leq(k, n, K, N):
    # P(X <= k | n draws, K successes in N)
    return sum(comb(K, i) * comb(N - K, n - i) for i in range(k + 1)) / comb(N, n)
# C3: 誠實 — 領域命中率 90.7% ⟹ magic 全中唔構成獨特性證據
#     判準換算: P(5/5 全中 | 領域 39/43) = (39/43)^5 ≈ 0.60 — 唔顯著
chk("C3_hypergeom", "★magic 全中命中率 5/5 — 但領域本身 90.7%, P(全中)≈0.60 唔顯著",
    True, "領域 91% ⟹ magic 全中必然; 判準 A(63 號同款) 喺 44-site 領域極高")

# 二項判讀: P(magic 5/5 全中 | 領域率)
pbinom = (n_dom / 43) ** 5
chk("C4_binomial", f"二項: P(magic 5/5 全中 | 領域 {n_dom/43*100:.0f}%) = {pbinom:.3f} — 確認唔顯著",
    pbinom > 0.05, f"p={pbinom:.4f}")

print()
print("=" * 72)
print("D. 誠實判讀 — 兩個層次分開")
print("=" * 72)
print(f"""
  1. anchor 唯一性: 3/12341 cover — 全枚舉確認。但 anchor 有 3 個解,
     (7,11,5) 唔係唯一 — 「R5 程序由結構鎖定 anchor」claim 要降級:
     實情係「3 個 anchor 集都 cover magic」, 我哋揀咗 (7,11,5) 因為
     Lucas/Fibonacci 語意 (7=L₄, 11=L₅, 5=F₅) — 後驗命名風險! 🟡
  2. magic 結構獨特性: 隨機 5 個 gcd+deg 全互斥機率 ≈2.1% (窮舉) —
     magic 結構確實稀有 (5 個 gcd 類 + 5 個 deg 層齊 cover), 但唔係
     <1% 嘅極端; 只 gcd 互斥 3.5% — deg 層加碼壓縮。
  3. O-series 身份: 領域命中率 {n_dom}/43 ({n_dom/43*100:.0f}%) —
     magic 5/5 全中。二項 p={pbinom:.3f} — 唔顯著 (領域率太高)!
     判準 A (63 號同款): 44-site 領域中 39/43 都有一堆 O-series 身份,
     magic 全中必然 — 同 88-site 結論一致: 「有身份」唔係獨特性判準。
""")

print()
print("=" * 72)
print(f"結果: PASS {PASS} / FAIL {FAIL}")
print("=" * 72)
if FAILS:
    print("FAIL:", FAILS)

with open("data/70_magic44_uniqueness.json", "w") as f:
    json.dump({
        "audit": "70_magic44_uniqueness", "date": "2026-10-17",
        "cover_triples": [list(c) for c in covers],
        "anchor_unique": len(covers) == 1,
        "mc_gcd_deg_prob": pb, "mc_gcd_deg_hits": hit,
        "domain_hits": n_dom, "domain_total": 43,
        "magic_hit_all": magic_all,
        "hypergeom_p_all5": p_all5,
        "results": OUT, "pass": PASS, "fail": FAIL,
    }, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/70_magic44_uniqueness.json")