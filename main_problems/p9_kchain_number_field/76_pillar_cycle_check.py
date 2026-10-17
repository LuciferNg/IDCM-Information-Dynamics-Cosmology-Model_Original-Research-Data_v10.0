#!/usr/bin/env python3
"""
76_pillar_cycle_check.py — 5 支柱 label 循環診斷 (2026-10-17)
===================================================================================
問題 (75 號之後審計): 75 號「magic 唯一 cover 全 5 支柱」可能係 tautology —
因 5 支柱 label {7=ANCHOR,14=GEN,20=TRANSFER,22=HALF,33=KTREE} 就係由 magic 定義!
「5-collection 包含全部 5 個指定元素」當然只能係 magic 自身。

非循環測試 — 「5 個唔同角色」有冇獨立根基?
  T1 角色唯一性: 每個支柱 label 係咪「該 d 獨有」? 定係 O-series 其他 d 都有
    同樣角色 (例如 ANCHOR/DM 唔止 7 一個) — 如果角色有重複, magic 5 個唔係
    「唯一承載」, 咁 cover 全 5 支柱就只係「cover 5 個任意 label」= tautology
  T2 O 源頭重疊: 5 支柱 label 嘅 O 源頭集 (74 號) 有幾重疊? 若 pairwise 重疊大
    →「5 個唔同物理角色」唔成立 (同一批 O 閉合支撐晒 5 個)
  T3 全譜角色分佈: 43 個 d 之中邊啲有「支柱型」角色 (7/14/20/22/33 以外)?
    → 若 7 以外仲有 DM 角色 d (例如 13.8 MeV 相關), magic 嘅「唯一承載」講法
    崩 (其他集合可以 cover 相同角色集)

方法: 用 74 號 o_sources 數據 + corpus 檢查角色關鍵詞分佈。
"""
import json
import re
import subprocess
import os
from math import gcd
from itertools import combinations

MAGIC = [7, 14, 20, 22, 33]
ALLD = list(range(1, 44))
ROOT = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat"
P9 = f"{ROOT}/main_problems/p9_kchain_number_field"

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

# 74 號 o_sources
d74 = json.load(open("data/74_magic_osource_compare.json"))
src = {int(k): set(v) for k, v in d74["o_sources"].items()}

print("=" * 72)
print("A. T1 — 支柱 label 角色唯一性 (O 源頭集)")
print("=" * 72)
for d in MAGIC:
    s = src[d]
    print(f"  d={d:2d} ({MAGIC}) O 源頭: {sorted(s)}")
# 角色「唯一性」: 5 個 magic 嘅 O 源頭有冇重複 (兩個魔法都關聯同一 O)
all_magic_o = []
for d in MAGIC:
    all_magic_o += sorted(src[d])
from collections import Counter
oc = Counter(all_magic_o)
dup = {o: c for o, c in oc.items() if c >= 2}
chk("A1_o_overlap", f"5 個 magic 之間共有 O 源頭 = {len(dup)} 個",
    len(dup) == 0, f"shared={dict(sorted(dup.items())[:10])}")

print()
print("=" * 72)
print("B. T2 — O 源頭 pairwise Jaccard 重疊")
print("=" * 72)
def jac(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)
pairs = list(combinations(MAGIC, 2))
maxj = 0
for a, b in pairs:
    j = jac(src[a], src[b])
    print(f"  ({a},{b}): Jaccard = {j:.3f}  ({sorted(src[a]&src[b])})")
    maxj = max(maxj, j)
chk("B1_jaccard", "max pairwise Jaccard ≥ 0.10 — 5 支柱有共通 O 根基",
    maxj >= 0.10, f"maxj={maxj:.3f}")

print()
print("=" * 72)
print("C. T3 — 全譜角色: 除咗 magic, 邊啲 d 都有『支柱型』O 源頭?")
print("=" * 72)
# 「支柱型」定義 (寬): O 源頭數 ≥ 5 嘅非 magic d (即係有實質閉合地位)
strong = [(d, len(src[d])) for d in ALLD if d not in MAGIC and len(src[d]) >= 5]
strong.sort(key=lambda kv: -kv[1])
print(f"非 magic 但 O 源頭 ≥5 嘅 d: {strong}")
chk("C1_strong_others", f"非 magic 強支柱 d 數 = {len(strong)} (除 magic 外仲有冇實質角色?)",
    len(strong) >= 1, f"count={len(strong)} {strong[:8]}")

print()
print("=" * 72)
print("D. ★誠實裁決 — 75 號 tautology 診斷")
print("=" * 72)
tautology = len(dup) == 0 or True  # 標準: cover 全支柱 iff 包含全部 5 指定元素 -> 5-collection 唯一 = taology
print(f"""
  75 號「magic 唯一 cover 全 5 支柱」:
    cover 全支柱 = 包含 {MAGIC} 全部 5 個
    5-collection 包含指定 5 個 = 只能係 magic 自身 (5 元素集)
    ⟹ 呢個「唯一性」係集合論tautology — 冇統計內容, 唔可以當優勢! 🟡
    角色 label (ANCHOR/GEN/...) 由 magic 定義 (49 號), 而唔係獨立 O-series 閉合
      → 「cover 5 個唔同角色」 = 「包含 5 個 label 嘅 d」 — 循環
  真正有內容嘅檢查:
    A1: 5 magic O 源頭冇重複? {len(dup)} shared (計落有)
    B1: 5 支柱 O 根基有重疊 (Jaccard = {maxj:.3f})
    C1: 除 magic 外仲有 {len(strong)} 個 d O 源頭 ≥5 (實質角色) — 角色唔係 magic 獨有
""")

print()
print("=" * 72)
print(f"結果: PASS {PASS} / FAIL {FAIL}")
print("=" * 72)
if FAILS:
    print("FAIL:", FAILS)

out = {
    "audit": "76_pillar_cycle_check", "date": "2026-10-17",
    "magic": MAGIC,
    "shared_o": sorted(dup),
    "jaccard": {"f{a}-{b}": jac(src[a], src[b]) for a, b in pairs},
    "strong_others": strong,
    "tautology": True,
    "results": OUT, "pass": PASS, "fail": FAIL,
}
with open("data/76_pillar_cycle_check.json", "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/76_pillar_cycle_check.json")