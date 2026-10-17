#!/usr/bin/env python3
"""
28_numeric_audit_round3.py — P9 第三輪數字審計 (2026-10-17)
===========================================================
審計對象: 25_magic_rows_open / 26_blind_test_magic_rows_rules / 27_magic_rows_deeper
方法: 零 import 原推導 scripts — 由第一原理 (ω_n=2sin(πn/88), γ_n=4sin²(πn/88),
      gcd(|44-n|,176), deg=φ(176/gcd)/2, Lucas) 重算全部 headline 數字。
      MC: 同 seed 複現 + 唔同 seed 確認。

段 A: 數論地基 (gcd 七類 / deg 分佈 / d 候選數)
段 B: magic rows 覆蓋 (25號: 七揀五缺 {4,16} / deg 覆蓋)
段 C: 盲測 26 A1 data-free null (closed-form + MC)
段 D: 盲測 26 A2 Lucas null (closed-form + MC multi-seed)
段 E: 盲測 26 A3 deg_hist + TEST C 候選集
段 F: 深推 27 TEST D (s 步長/均值) + TEST E (v₂ 規則) + TEST F (Lucas 對)
段 G: register/附註核對 (docs 數字 vs 本審計)

高精度: 純整數/Fraction/精確算術; MC 用固定 seed。
"""
import json, random
from math import gcd
from fractions import Fraction
from collections import Counter, defaultdict

PASS, FAIL = "PASS", "FAIL"
results = []
def chk(name, got, exp, desc):
    ok = (got == exp)
    results.append((name, ok, got, exp, desc))
    print(f"[{PASS if ok else FAIL}] {name}: got={got} exp={exp} — {desc}")

# ---------- 第一原理數域 ----------
# ω_n = 2sin(πn/88), n=1..44; beat d = |i-j| -> gcd(|44-d|,176)
MAGIC = [7, 14, 20, 22, 33]
DATA = {11, 13, 17, 19, 21, 25}

# 段 A: gcd 七類
gcd_classes = {}
for g in [1, 2, 4, 8, 11, 16, 22]:
    ds = [d for d in range(1, 44) if gcd(abs(44 - d), 176) == g]
    gcd_classes[g] = ds
cnts = {g: len(ds) for g, ds in gcd_classes.items()}
chk("A1 gcd七類候選數", cnts, {1: 20, 2: 10, 4: 5, 8: 3, 11: 2, 16: 2, 22: 1}, "25號 d 候選數 (gcd: {1:20,2:10,4:5,8:3,11:2,16:2,22:1})")
# 七類並集 = 1..43 全部
all_d = sorted(set().union(*gcd_classes.values()))
chk("A2 七類並集=1..43", len(all_d), 43, "全部 d=1..43 覆蓋一次")
chk("A3 無重疊", sum(cnts.values()), 43, "七類總數=43 ⟹ 互斥覆蓋")
# d 面 deg 分佈 (第一原理重算)
def phi_small(n):
    """精確 φ(n): 第一原理"""
    r = n
    m = n
    p = 2
    while p * p <= m:
        if m % p == 0:
            while m % p == 0:
                m //= p
            r -= r // p
        p += 1
    if m > 1:
        r -= r // m
    return r

def deg_of(d):
    g = gcd(abs(44 - d), 176)
    return phi_small(176 // g) // 2

def v2(n):
    c = 0
    while n % 2 == 0:
        c += 1; n //= 2
    return c

deg_hist_d = Counter(deg_of(d) for d in range(1, 44))
chk("A4 d面deg分佈", dict(deg_hist_d), {40: 20, 20: 10, 10: 5, 5: 5, 4: 2, 2: 1}, "d=1..43 面 deg 分佈 (gcd1→40×20, gcd2→20×10, gcd4→10×5, gcd8/16→5×5, gcd11→4×2, gcd22→2×1)")
chk("A5 分佈加總=43", sum(deg_hist_d.values()), 43, "對帳")

# 段 B: magic 覆蓋
m_gcd = {d: gcd(abs(44 - d), 176) for d in MAGIC}
chk("B1 magic gcd覆蓋", set(m_gcd.values()), {1, 2, 8, 11, 22}, "七揀五: magic 覆蓋 {1,2,8,11,22}")
chk("B2 缺 {4,16}", set(gcd_classes) - set(m_gcd.values()), {4, 16}, "缺 gcd 類 {4,16}")
# 每一 gcd 類 magic 數
for g in [1, 2, 4, 8, 11, 16, 22]:
    n_m = sum(1 for d in MAGIC if gcd(abs(44 - d), 176) == g)
    chk(f"B3 gcd{g} magic數", n_m, 1 if g in {1, 2, 8, 11, 22} else 0, f"每類 1 代表 (7 揀 5)")
# deg 覆蓋
m_deg = {d: deg_of(d) for d in MAGIC}
chk("B4 magic deg覆蓋", set(m_deg.values()), {40, 20, 5, 2, 4}, "magic deg: {40,20,5,2,4} (缺 deg=10)")
chk("B5 deg10來源", {d: deg_of(d) for d in gcd_classes[4]}, {d: 10 for d in gcd_classes[4]}, "gcd=4 係 deg10 唯一來源 (5 個全 deg10 都冇 magic 代表)")

# 段 C: 盲測 26 A1 data-free null — closed-form + MC
# ★ null model (26 號定義, 已讀 script 核實): 「一組代表」= 每 gcd 類隨機揀 1 個 d (7 類 → 7 代表)
#    A1 = P(全部 7 代表都非 data) = ∏_g (類內非 data 數 / 類大小)
#    (唔係「43 揀 5 無類別限制」!)
from math import comb
p1_cf = Fraction(1, 1)
per_class_r1 = {}
for g in gcd_classes:
    p = Fraction(sum(1 for d in gcd_classes[g] if d not in DATA), len(gcd_classes[g]))
    per_class_r1[g] = p
    p1_cf *= p
chk("C1 A1 closed-form", float(p1_cf), 0.375, f"data-free null = ∏每類非data比例 = {float(p1_cf):.6f} (26 號: 0.375; gcd1=15/20, gcd11=1/2)")
random.seed(20261017)
N = 10**6
cnt = 0
for _ in range(N):
    reps = [random.choice(gcd_classes[g]) for g in sorted(gcd_classes)]
    cnt += all(r not in DATA for r in reps)
p1_mc = cnt / N
chk("C2 A1 MC 同seed", round(p1_mc, 5), 0.37504, f"MC 10^6 seed=20261017: {p1_mc:.5f} (26 號: 0.375039)")
random.seed(777)
cnt = 0
for _ in range(N):
    reps = [random.choice(gcd_classes[g]) for g in sorted(gcd_classes)]
    cnt += all(r not in DATA for r in reps)
p1_mc2 = cnt / N
assert abs(p1_mc2 - 0.375) < 0.003, f"唔同 seed 超出 MC 誤差: {p1_mc2}"
chk("C3 A1 MC 唔同seed (tolerance)", True, True, f"seed=777: {p1_mc2:.4f} vs 0.375, |Δ|={abs(p1_mc2-0.375):.5f} — MC 誤差內一致 (assert 已過)")

# 段 D: 盲測 26 A2 Lucas null — 同一「每類代表」model
# A2 = P(全部 7 代表都喺 L* = {m·L_k: m∈{1,2,3}, k=0..7}) = ∏_g (類內 L* 比例)
L = {0: 2, 1: 1, 2: 3, 3: 4, 4: 7, 5: 11, 6: 18, 7: 29}
lstar = sorted({m * Lk for Lk in L.values() for m in (1, 2, 3) if 1 <= m * Lk <= 43})
p2_cf = Fraction(1, 1)
per_class_r2 = {}
for g in gcd_classes:
    p = Fraction(sum(1 for d in gcd_classes[g] if d in lstar), len(gcd_classes[g]))
    per_class_r2[g] = p
    p2_cf *= p
chk("D1 A2 closed-form", float(p2_cf), 0.008, f"Lucas null = ∏每類L*比例 = {float(p2_cf):.6f} (26 號: 0.008; gcd1=6/20,gcd2=4/10,gcd4=1/5,gcd8=2/3,gcd11=2/2,gcd16=1/2,gcd22=1/1)")
random.seed(20261017)
cnt = 0
for _ in range(N):
    reps = [random.choice(gcd_classes[g]) for g in sorted(gcd_classes)]
    cnt += all(r in lstar for r in reps)
p2_mc = cnt / N
chk("D2 A2 MC 同seed", round(p2_mc, 6), 0.008288, f"MC 10^6: {p2_mc:.6f} (26 號: 0.008288)")
random.seed(314159)
cnt = 0
for _ in range(N):
    reps = [random.choice(gcd_classes[g]) for g in sorted(gcd_classes)]
    cnt += all(r in lstar for r in reps)
p2_mc2 = cnt / N
assert abs(p2_mc2 - 0.008) < 0.0015, f"唔同 seed 超出 MC 誤差: {p2_mc2}"
chk("D3 A2 MC 唔同seed (tolerance)", True, True, f"seed=314159: {p2_mc2:.5f} vs 0.008, |Δ|={abs(p2_mc2-0.008):.5f} — MC 誤差內一致 (assert 已過)")

# 段 E: A3 deg_hist + TEST C 候選
# A3: gcd→deg 唔係單射: gcd8 & gcd16 都 deg5
g8 = gcd_classes[8]; g16 = gcd_classes[16]
chk("E1 gcd8 deg5", set(deg_of(d) for d in g8), {5}, "gcd8 → deg5")
chk("E2 gcd16 deg5", set(deg_of(d) for d in g16), {5}, "gcd16 → deg5")
chk("E3 gcd→deg非單射", deg_of(g8[0]) == deg_of(g16[0]), True, "gcd8/16 撞 deg5 ⟹ 唔係單射 (26 號修正)")
# TEST C: R1+R2 篩剩候選
# ★ 26 號定義: R1 (data-free) + R2 (Lucas-chain) 篩完, 喺非 data 候選入面仲剩幾多 L* 成員
# L* = {m·L_k: m∈{1,2,3}, k=0..7} 喺 1..43
lc_full = sorted({m * Lk for Lk in L.values() for m in (1, 2, 3) if 1 <= m * Lk <= 43})
lc_no_data = [d for d in lc_full if d not in DATA]
chk("E4 TEST C 候選集", lc_no_data, [1, 2, 3, 4, 6, 7, 8, 9, 12, 14, 18, 22, 29, 33, 36], f"R1+R2 篩剩 15 個: {lc_no_data} (26 號 TEST C: gcd1{{1,3,7,9,29}} gcd2{{2,6,14,18}} gcd8{{4,36}} gcd11{{33}} gcd22{{22}} = 15)")
# E5: magic 落喺候選集幾多? 候選 15 個 ≫ magic 5 個 ⟹ 唔唯一鎖定
overlap = [d for d in MAGIC if d in lc_no_data]
chk("E5 magic∩候選", sorted(overlap), [7, 14, 22, 33], f"magic 中符合 R1+R2 者 {sorted(overlap)} (20 例外) — 但候選集 15 個遠大於 magic 5 個 = 唔唯一鎖定 (26 號判語)")

# 段 F: 深推 27 TEST D/E/F
# 讀 946 beat 表 (i,j)
beats = []
with open("data/beat_algebraic_table.txt") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 2:
            try:
                i, j = int(parts[0]), int(parts[1])
                if 1 <= i <= 44 and 1 <= j <= 44:
                    beats.append((i, j))
            except ValueError:
                pass
chk("F1 946 beats", len(beats), 946, "beat 表行數 (完整性)")
rows = defaultdict(list)
for (i, j) in beats:
    rows[abs(i - j)].append((i, j))
# TEST D: 每個 row 嘅 s=i+j 步長
def s_stats(d):
    ss = sorted(i + j for (i, j) in rows[d])
    steps = sorted({ss[k+1] - ss[k] for k in range(len(ss)-1)})
    return steps, round(sum(ss)/len(ss), 4)
magic_steps = {d: s_stats(d)[0] for d in MAGIC}
magic_means = {d: s_stats(d)[1] for d in MAGIC}
chk("F2 magic s步長全2", all(v == [2] for v in magic_steps.values()), True, f"magic rows s-step 全 [2]: {magic_steps}")
chk("F3 magic s_mean全45", set(magic_means.values()), {45.0}, f"magic s_mean 全 45.0: {magic_means}")
# filler (非 magic 非 data)
filler_steps = []
filler_means = []
for d in range(1, 44):
    if d in MAGIC or d in DATA:
        continue
    if len(rows[d]) < 2:
        continue
    st, mn = s_stats(d)
    filler_steps.append(st); filler_means.append(mn)
chk("F4 filler s步長全2", all(v == [2] for v in filler_steps), True, "filler 31/31 s-step 全 [2] — magic/filler 零差異")
chk("F5 filler s_mean全45", set(filler_means), {45.0}, f"filler s_mean 全 45.0 — 零差異 ({len(filler_means)} rows)")
# TEST E: v₂ 奇 ⇒ magic
v2_odd = [g for g in [1, 2, 4, 8, 11, 16, 22] if v2(176 // g) % 2 == 1]
v2_even = [g for g in [1, 2, 4, 8, 11, 16, 22] if v2(176 // g) % 2 == 0]
chk("F6 v₂奇類", v2_odd, [2, 8, 22], f"v₂(176/g) 奇: {v2_odd} (176/2=88 v2=3, 176/8=22 v2=1, 176/22=8 v2=3)")
chk("F7 v₂奇⇒magic 3/3", all(any(d in MAGIC for d in gcd_classes[g]) for g in v2_odd), True, "v₂ 奇類全部有 magic")
chk("F8 v₂偶例外", [g for g in v2_even if any(d in MAGIC for d in gcd_classes[g])], [1, 11], "v₂ 偶但有 magic: g=1,11 — 規則唔充要 (27 號)")
# TEST F: Lucas pair
chk("F9 7=L4 14=2L4 22=2L5 33=3L5", {7: L[4], 14: 2 * L[4], 22: 2 * L[5], 33: 3 * L[5]}, {7: 7, 14: 14, 22: 22, 33: 33}, "L₄/L₅ 對生成 4/5 magic")
chk("F10 20 冇Lucas鏈", 20 in {m * Lk for Lk in L.values() for m in (1, 2, 3)}, False, "20 唔可 m·Lₖ 表示 (唯一冇鏈)")
# 7 vs 29 vs 3
g1 = gcd_classes[1]
chk("F11 7/29∈gcd1", all(d in g1 for d in [7, 29]), True, "gcd=1 類含 7,29")
chk("F12 29>22 後半", 29 > 22 and 7 < 22, True, "7 前半, 29 後半 (half-node 22)")

# 段 G: 讀 JSON 產物對帳 (25/26/27)
with open("data/25_magic_open.json") as f:
    j25 = json.load(f)
# 25 JSON: Q2_magic_d_deg = {"7": {"gcd":1,"deg":40}, ...}
magic_in_j25 = set(int(k) for k in j25.get("Q2_magic_d_deg", {}))
chk("G1 25 JSON magic", magic_in_j25, set(MAGIC), f"25 JSON Q2_magic_d_deg keys={sorted(magic_in_j25)}")
# gcd 分佈核實
j25_gcd = {int(k): v["gcd"] for k, v in j25["Q2_magic_d_deg"].items()}
chk("G1b 25 JSON gcd一致", set(j25_gcd.values()), {1, 2, 8, 11, 22}, f"25 JSON magic gcd: {j25_gcd}")
with open("data/26_blind_test.json") as f:
    j26 = json.load(f)
def deep_find(o, key):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == key:
                return v
            r = deep_find(v, key)
            if r is not None:
                return r
    elif isinstance(o, list):
        for v in o:
            r = deep_find(v, key)
            if r is not None:
                return r
    return None
a1 = deep_find(j26, "A1") or {}
vals = json.dumps(j26)
chk("G2 26 JSON 含0.375", "0.375" in vals, True, "26 JSON 記 A1 ≈0.375")
chk("G3 26 JSON 含0.008", "0.008" in vals, True, "26 JSON 記 A2 ≈0.008")
with open("data/27_magic_deeper.json") as f:
    j27 = json.load(f)
rule27 = j27.get("TEST_E", {}).get("rule", "")
chk("G4 27 JSON v2規則", "必有 magic" in rule27, True, f"27 JSON TEST_E.rule='{rule27}'")
chk("G5 27 JSON v2奇類", j27.get("TEST_E", {}).get("v2_odd_classes"), [2, 8, 22], "27 JSON v2_odd_classes")
chk("G6 27 JSON TEST_D 零差異", "冇結構差異" in json.dumps(j27.get("TEST_D", {}), ensure_ascii=False), True, "27 JSON TEST_D 記錄零差異判語")

n_pass = sum(1 for _, ok, _, _, _ in results if ok)
n_fail = sum(1 for _, ok, _, _, _ in results if not ok)
print(f"\nRESULT: {n_pass}/{len(results)} PASS ({n_fail} FAIL)")
if n_fail:
    print("FAIL 清單:")
    for name, ok, got, exp, desc in results:
        if not ok:
            print(f"  {name}: got={got} exp={exp} — {desc}")
    import sys
    sys.exit(1)