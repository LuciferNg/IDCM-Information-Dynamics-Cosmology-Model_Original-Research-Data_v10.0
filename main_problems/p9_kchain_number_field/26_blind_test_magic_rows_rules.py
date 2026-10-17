#!/usr/bin/env python3
"""
26_blind_test_magic_rows_rules.py — P9 Magic rows 規則盲測 (2026-10-17)
====================================================================
預註冊規則 (25_magic_rows_open 已 locked, 唔准事後改):
  R1 data-free:  magic 代表 ∉ data rows {11,13,17,19,21,25}
  R2 Lucas-chain: magic 代表 ∈ L* = {L_k, 2L_k, 3L_k}, L_k∈{1,2,3,4,7,11,18,29}
  R3 deg-cover:   magic 覆蓋 deg {40,20,5,2,4}, 缺 deg=10

TEST A: null 概率 (closed-form + MC 10^6 雙軌)
  A1: P(5/5 magic 隨機揀全非 data)
  A2: P(5/5 magic 隨機揀全喺 L*)
  A3: deg-cover 係咪 gcd 類結構必然 (唔係巧合)?
TEST B: P13 master_atlas 一致性 (Row label d 集 = magic 集?)
TEST C: 辨識力 — R1+R2 篩完, 每 gcd 類仲剩幾多候選? 規則唯唔唯一鎖定 7?
zero import 原推導; 純整數/Fraction; MC 用 random 固定 seed 可重現
"""
import csv, json, random
from math import gcd, comb
from collections import Counter

random.seed(20261017)
MAGIC = [7, 14, 20, 22, 33]
DATA  = {11, 13, 17, 19, 21, 25}
LUCAS = {1, 2, 3, 4, 7, 11, 18, 29}
LSTAR = set()
for L in LUCAS:
    for m in (1, 2, 3):
        v = m * L
        if v <= 43:
            LSTAR.add(v)

def gcd_class(d):
    return gcd(abs(44 - d), 176)

# d 候選按 gcd 類
d_by_g = {}
for d in range(1, 44):
    d_by_g.setdefault(gcd_class(d), []).append(d)

# deg 按 gcd 類
def phi_deg(g_):
    e = 176 // g_
    ph = e; p = 2; ee = e
    while p * p <= ee:
        if ee % p == 0:
            while ee % p == 0: ee //= p
            ph -= ph // p
        p += 1
    if ee > 1: ph -= ph // ee
    if ph <= 2: return 1
    return ph // 2
deg_of_g = {g: phi_deg(g) for g in d_by_g}
# deg 覆蓋真係單射? gcd=8 同 gcd=16 都係 deg=5 → 唔係單射!
deg_hist = Counter(deg_of_g.values())

res = {"test": "26_blind_test_magic_rows_rules", "rules": {"R1": "data-free", "R2": "Lucas-chain", "R3": "deg-cover"}}

# ---------- TEST A: null ----------
# 隨機嘅「一組代表」= 每 gcd 類隨機揀 1 個 (5 類 → 5 代表)
classes5 = sorted(d_by_g.keys())  # 7 類; magic 落喺 5 類 {1,2,8,11,22}
MC = 1_000_000
cnt_r1 = cnt_r2 = cnt_r3 = cnt_all5 = 0
for _ in range(MC):
    reps = []
    for g in classes5:
        reps.append(random.choice(d_by_g[g]))
    cnt_r1 += all(r not in DATA for r in reps)
    cnt_r2 += all(r in LSTAR for r in reps)
    cnt_r3 += len({deg_of_g[gcd_class(r)] for r in reps}) == 5
    cnt_all5 += len({gcd_class(r) for r in reps}) == 5

# closed-form A1 (唔使 MC): 每類非 data 比例乘積
p1_closed = 1.0
per_class_r1 = {}
for g in classes5:
    p = sum(1 for d in d_by_g[g] if d not in DATA) / len(d_by_g[g])
    per_class_r1[str(g)] = p
    p1_closed *= p

# closed-form A2: 每類 L* 比例乘積
p2_closed = 1.0
per_class_r2 = {}
for g in classes5:
    p = sum(1 for d in d_by_g[g] if d in LSTAR) / len(d_by_g[g])
    per_class_r2[str(g)] = p
    p2_closed *= p

# A3: deg-cover — 每 gcd 類 deg 唔重複? (gcd=8/16 都 deg5 → 唔係)
deg_unique = len(set(deg_of_g.values())) == len(deg_of_g)
# 真正問題: 隨機 5 個 d (無類別限制) 落喺 5 個唔同 gcd 類概率
p3_mc = cnt_r3 / MC
p_distinct_gcd_mc = cnt_all5 / MC

res["TEST_A"] = {
    "A1_data_free_null": {"closed_form": round(p1_closed, 6), "mc_1e6": round(cnt_r1/MC, 6),
                           "per_class": per_class_r1,
                           "verdict": "PASS" if p1_closed < 0.01 else "FAIL 唔顯著 (data 只塞喺 gcd=1/11 類, 巧合機會高)"},
    "A2_lucas_null": {"closed_form": round(p2_closed, 6), "mc_1e6": round(cnt_r2/MC, 6),
                       "per_class": per_class_r2, "LSTAR": sorted(LSTAR),
                       "verdict": "PASS(5σ)" if p2_closed < 3.0e-7 else ("邊緣" if p2_closed < 0.05 else "FAIL")},
    "A3_deg_cover": {"deg_per_gcd_unique": deg_unique, "deg_hist": {str(k): v for k, v in deg_hist.items()},
                      "mc_P_5distinct_gcd": round(p3_mc, 6),
                      "note": "gcd→deg 唔係單射 (gcd=8/16 都 deg5); 『缺 deg10』只啱一半 — gcd=4 係 deg10 唯一來源 (deg10 全缺), 但 gcd=16 缺係『同一 deg5 嘅第二 gcd 來源冇代表』, 唔係 deg 缺",
                      "verdict": "R3 表述修正: 缺 = gcd 類缺 {4,16}, 唔係 deg 缺 (deg5 仍有 gcd=8 代表)"},
}

# ---------- TEST B: P13 master_atlas 一致性 ----------
atlas_path = "../p13_beat_periodic_table/data/master_atlas.csv"
row_label_d = {}  # d -> label (第一遇到嘅 Row label)
physics_d = {}
try:
    with open(atlas_path, newline='', encoding='utf-8-sig') as f:
        rd = csv.DictReader(f)
        for r in rd:
            d = int(r['d']); lb = (r['label'] or '').strip()
            if lb and not lb.replace('.','').replace('e-','').replace('-','').isdigit():
                # 逐 cell label (d 唔夠) — 用 n,m 定位
                pass
    # 重新讀: label 喺特定 (n,m,d) cell; 抽 Row label 靠 text 匹配
    with open(atlas_path, newline='', encoding='utf-8-sig') as f:
        rd = csv.DictReader(f)
        for r in rd:
            lb = (r['label'] or '').strip()
            if not lb: continue
            if any(k in lb for k in ("Row", "anchor", "GEN", "half", "K_tree", "T(s->d)")):
                key = int(r['d'])
                row_label_d.setdefault(key, lb)
            elif lb[0].isalpha():
                key = int(r['d'])
                physics_d.setdefault(key, lb)
except FileNotFoundError:
    res["TEST_B"] = {"error": "atlas 唔喺預期路徑，跳過"}

p13_magic_d = sorted(set(d for d in row_label_d if d > 0)) if row_label_d else []
label_match = (p13_magic_d == MAGIC)
res["TEST_B"] = {
    "P13_row_label_d": p13_magic_d,
    "P9_magic": MAGIC,
    "exact_match": label_match,
    "row_labels": {str(k): v for k, v in sorted(row_label_d.items())},
    "physics_labels_sample": {str(k): v for k, v in sorted(physics_d.items())[:12]},
    "verdict": "✅ 一致" if label_match else "⚠️ 不一致",
    "note": "P13 label 同 p9 分類同源 (唔係獨立盲測), 只做一致性命題 (非預言證據)"
}

# ---------- TEST C: 辨識力 ----------
ident = {}
for g in classes5:
    cand = d_by_g[g]
    ok = [d for d in cand if d not in DATA and d in LSTAR]
    ident[str(g)] = {"candidates": cand, "R1R2_survivors": ok,
                     "actual_magic": [d for d in MAGIC if gcd_class(d) == g]}
survivor_all = sum(len(v["R1R2_survivors"]) for v in ident.values())
res["TEST_C"] = {"per_class": ident, "total_survivors_5classes": survivor_all,
    "unique_lock": (survivor_all == 5),
    "verdict": "✅ 唯一鎖定" if survivor_all == 5 else "❌ 唔唯一 — R1+R2 只係必要條件, 唔係充分預言規則",
    "detail": "gcd=1 類仲有幾個 Lucas 候選 (1/3/7/29) → 7 需要額外判準 (未預註冊, 唔可以後驗加入)"}

print(json.dumps(res, indent=1, ensure_ascii=False))
with open("data/26_blind_test.json", "w") as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
print("\n輸出: data/26_blind_test.json")