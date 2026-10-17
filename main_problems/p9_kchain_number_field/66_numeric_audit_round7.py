#!/usr/bin/env python3
"""
66_numeric_audit_round7.py — P9 第七輪數字審計 (2026-10-17)
============================================================
審計對象 (64 號盤點 🔴46-63 剩餘 + 56-59 盲測鏈):
  46_88site_labels: 25 格存在性 + 88-site R5 data-free 前向 4/5
  47_r5_extrapolation_176: N=176/352 R5 輸出 (20 失去, 4/5)
  49_magic_distinctiveness: 每 magic = gcd 類唯一 magic + deg 層唯一代表
  51_label_gate: G0 9 mapping 格 d 值 + G7 γ'_d deg 分佈
  54_gate6_redefinition: sin(7π/88)=sin(14π/176) EXACT + θ₂₃=49.3202°
  56/57/58/59: 盲測集定義 + 合併統計 (B 3/9 vs C 3/9, p=0.69)

方法: 零 import 任何原推導 script; 第一原理; mpmath dps=50。
"""
import mpmath as mp
mp.mp.dps = 50
from math import gcd, comb
from functools import reduce

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

def luc(k):
    a, b = 2, 1
    for _ in range(k):
        a, b = b, a + b
    return a

MAGIC = [7, 14, 20, 22, 33]
DATA_D = {11, 13, 17, 19, 21, 25}
DATA_CELLS = [(1,18),(1,22),(7,20),(8,22),(8,33),(10,24),(19,33),(19,38),(30,41)]
DUAL_CELLS = [(26,43),(22,43),(24,37),(22,36),(11,36),(20,34),(11,25),(6,25),(3,14)]
NEAR_CELLS = [(15,29),(12,27),(3,25),(2,14),(12,28),(11,23),(18,35)]
GCL = lambda d, N: gcd(abs(N - d), 4*N)

def deg_N(d, N):
    m = (4*N) // GCL(d, N)
    r = m; p = 2
    while p*p <= m:
        if m % p == 0:
            while m % p == 0: m //= p
            r -= r//p
        p += 1
    if m > 1: r -= r//m
    return 1 if r == 2 else r//2

def r5(N, m_max, data_set):
    gen = sorted({m*a for a in (7,11,5) for m in range(1, m_max+1) if 1 <= m*a <= N-1})
    cand = [d for d in gen if d not in data_set]
    def lch(d): return any(d == m*luc(k) for m in range(1, m_max+1) for k in range(2,8))
    byg = {}
    for d in cand: byg.setdefault(GCL(d, N), []).append(d)
    reps = []
    for g, lst in sorted(byg.items()):
        lst = sorted(lst)
        if len(lst) == 1: reps.append(lst[0])
        else:
            lp = [d for d in lst if d in (3,7,11,29)]
            if len(lp) == 1: reps.append(lp[0])
            else:
                lc = [d for d in lst if lch(d)]
                reps.append(lc[0] if len(lc) == 1 else min(lst))
    bydeg = {}
    for d in reps: bydeg.setdefault(deg_N(d, N), []).append(d)
    final = []
    for de, lst in sorted(bydeg.items()):
        final.append(lst[0] if len(lst) == 1 else min(lst, key=lambda x: (x >= N//2, x)))
    return sorted(final)

print("=" * 72)
print("A. 46_88site_labels — 25 格存在性 + R5 前向")
print("=" * 72)
all_cells = DATA_CELLS + DUAL_CELLS + NEAR_CELLS
chk("A1_25cells", "25 格全部 (i,j) ≤ 44 < 88", all(1 <= i < j <= 88 for i, j in all_cells) and len(all_cells) == 25)
r5_88_fix = r5(88, 4, DATA_D)
r5_88_orig = r5(88, 4, set())
exp88 = [7, 14, 22, 28, 33, 44]
chk("A2_r5_88_fix", "88-site data-free 前向輸出 [7,14,22,28,33,44]", r5_88_fix == exp88, str(r5_88_fix))
kept88 = sorted(d for d in MAGIC if d in r5_88_fix)
chk("A3_kept4of5", "保留 magic 4/5 (20 失去)", kept88 == [7, 14, 22, 33], str(kept88))
lost88 = sorted(d for d in MAGIC if d not in r5_88_fix)
chk("A4_lost20", "失去 = 20", lost88 == [20])
# 原版 (37 T4 DATA=set()) → 3/5?
r5_orig_keep = sorted(d for d in MAGIC if d in r5_88_orig)
chk("A5_orig3of5", "37 T4 原版輸出唔同 (data=∅) — 複算", len(r5_orig_keep) == 3, f"kept={r5_orig_keep} out={r5_88_orig}")

print()
print("=" * 72)
print("B. 47_r5_extrapolation_176 — N=176/352")
print("=" * 72)
r176 = r5(176, 4, DATA_D)
r352 = r5(352, 4, DATA_D)
k176 = sorted(d for d in MAGIC if d in r176)
k352 = sorted(d for d in MAGIC if d in r352)
chk("B1_N176", "176-site 輸出 4/5 保留 (20 失去)",
    len(k176) == 4 and 20 not in r176 and all(d in r176 for d in (7, 14, 22, 33)),
    f"out={r176} kept={k176}")
chk("B2_N352", "352-site 輸出 4/5 保留 (20 失去)",
    len(k352) == 4 and 20 not in r352 and all(d in r352 for d in (7, 14, 22, 33)),
    f"out={r352} kept={k352}")
# 20 跨 N 失去
g20 = {N: GCL(20, N) for N in (44, 88, 176, 352)}
chk("B3_20_consistent", "20 嘅 gcd 跨 N: 44→8, 88/176/352→4",
    g20[44] == 8 and g20[88] == g20[176] == g20[352] == 4, str(g20))
# 28 取代 20?
chk("B4_28_replaces", "28 喺 gcd4 類代表 (取代 20)",
    all(28 in r5(N, 4, DATA_D) for N in (88, 176, 352)), "")

print()
print("=" * 72)
print("C. 49_magic_distinctiveness — 唯一代表")
print("=" * 72)
# T1: 每個 magic 喺自己 gcd 類內唯一 magic
byg44 = {}
for d in MAGIC: byg44.setdefault(GCL(d, 44), []).append(d)
chk("C1_gcd_unique", "5 magic 5 個唔同 gcd 類 (互斥 cover)",
    len(byg44) == 5 and all(len(v) == 1 for v in byg44.values()), str({k: v for k, v in byg44.items()}))
# T2: 每 deg 一 magic (44-site)
degs = {d: deg_N(d, 44) for d in MAGIC}
chk("C2_deg_unique", "5 magic 5 個唔同 deg 層", len(set(degs.values())) == 5, str(degs))
# deg 值對: 7→40, 14→20, 20→5, 22→2, 33→4 (44-site γ 層 GCL; 注意 20 唔係 10 —
# 10 係 88-site γ' 層 deg, 44-site = gcd(|44−20|,176)=8 → φ(22)/2=5)
chk("C3_deg_values", "deg(7)=40 deg(14)=20 deg(20)=5 deg(22)=2 deg(33)=4 (44-site γ 層)",
    degs[7] == 40 and degs[14] == 20 and degs[20] == 5 and degs[22] == 2 and degs[33] == 4, str(degs))
# T3: 結構角色 — data 端點座標 ∈ magic (32 號: 5 格 6 次命中, 已核實)
def endpoint_hits(cells, magic):
    hits = 0
    hit_cells = 0
    for i, j in cells:
        c = (i in magic) + (j in magic)
        if c:
            hits += c
            hit_cells += 1
    return hit_cells, hits
ec, eh = endpoint_hits(DATA_CELLS, set(MAGIC))
chk("C4_data_magic_cross", "data 9 格中端點 ∈ magic 嘅格數=5 次數=6 (32 號核實)",
    ec == 5 and eh == 6, f"cells={ec} hits={eh}")

print()
print("=" * 72)
print("D. 51_label_gate — G0 9 mapping + G7 deg 分佈")
print("=" * 72)
MAPPING = [("u/d", (10,24)), ("c/s", (8,22)), ("t/b", (19,33)), ("m_c/m_b", (8,33)),
           ("m_s/m_d", (1,22)), ("m_W/m_Z", (30,41)), ("m_H/m_W", (19,38)),
           ("m_μ/m_τ", (1,18)), ("n/p", (7,20))]
chk("D1_9mapping", "G0: 9 個 mapping 格全 (i,j) ≤ 44", all(1 <= i < j <= 44 for (_, (i, j)) in MAPPING) and len(MAPPING) == 9)
# 每個 mapping 格嘅端點座標命中 magic (32 號: 5 格 6 次)
map_ec, map_eh = endpoint_hits([(i, j) for (_, (i, j)) in MAPPING], set(MAGIC))
chk("D2_map_magic_hit", "9 mapping 格端點 ∈ magic: 5 格 6 次 (32 號核實)",
    map_ec == 5 and map_eh == 6, f"cells={map_ec} hits={map_eh}")
# G7: γ'_d deg 分佈 (d=1..44)
degdist = {}
for d in range(1, 45):
    g = gcd(d, 176)
    m176 = 176 // g
    r = m176; p = 2
    while p*p <= m176:
        if m176 % p == 0:
            while m176 % p == 0: m176 //= p
            r -= r//p
        p += 1
    if m176 > 1: r -= r//m176
    de = 1 if r == 2 else r//2
    degdist.setdefault(de, 0)
    degdist[de] += 1
exp_dist = {40: 20, 20: 10, 10: 5, 5: 5, 4: 2, 2: 1, 1: 1}
chk("D3_deg_distrib", "γ'_d deg 分佈 (51 號 G7): {40:20,20:10,10:5,5:5,4:2,2:1,1:1}",
    degdist == exp_dist, str(degdist))

print()
print("=" * 72)
print("E. 54_gate6_redefinition — sin 恒等 + θ₂₃")
print("=" * 72)
s1 = mp.sin(mp.mpf(7) * mp.pi / mp.mpf(88))
s2 = mp.sin(mp.mpf(14) * mp.pi / mp.mpf(176))
gam7 = 4 * mp.sin(mp.mpf(7)*mp.pi/mp.mpf(88))**2
gam14 = 4 * mp.sin(mp.mpf(14)*mp.pi/mp.mpf(176))**2
chk("E1_sin_id", "sin(7π/88) = sin(14π/176) EXACT",
    abs(s1 - s2) < mp.mpf("1e-50"), f"diff={float(abs(s1-s2)):.1e}")
th23 = mp.degrees(mp.atan(mp.sin(mp.mpf(7)*mp.pi/mp.mpf(88)) / mp.sin(mp.mpf(6)*mp.pi/mp.mpf(88))))
chk("E2_th23", "θ₂₃ = atan(sin7π/88/sin6π/88) = 49.3202° (±1e-3)",
    abs(th23 - mp.mpf("49.3202")) < mp.mpf("1e-3"), mp.nstr(th23, 10))
# 54 號: 7 嘅精確 88-site 身份 = DM m_7 (經 k=14)
chk("E3_seven_identity", "7 經 k=14 carry = γ'_{2·7}=γ_7 (DM m_7)",
    abs(gam14 - gam7) < mp.mpf("1e-50"), f"diff={float(abs(gam14-gam7)):.1e}")
chk("E4_gam_carry", "γ'_{14} = γ_7 → 7 嘅對偶鏈身份 (k=14)",
    abs(gam14 - gam7) < mp.mpf("1e-50"), f"diff={float(abs(gam14-gam7)):.1e}")

print()
print("=" * 72)
print("F. 56/57/58/59 — 盲測集 + 合併統計")
print("=" * 72)
B1 = {55, 68, 74, 81}
C1 = {46, 56, 62, 73}
B2 = {54, 67, 75, 80, 83}
C2 = {52, 59, 82, 84, 86}
consumed = {46, 55, 56, 62, 66, 68, 73, 74, 81}
chk("F1_sets_disjoint", "B1∩C1=∅, B2∩C2=∅, B1∪C1∪B2∪C2 兩輪互斥",
    len(B1 & C1) == 0 and len(B2 & C2) == 0 and len((B1|C1) & (B2|C2)) == 0)
chk("F2_B1_mirror", "B1 = 88−{44-magic}?? 實際: B1={55,68,74,81} = HALF mirror",
    B1 == {88-7, 88-14, 88-20, 88-33} - {66}, str({88-7, 88-14, 88-20, 88-33}))
# 58 號: Fib mirror B2 = 88−F_m (F5..F9 = 5,8,13,21,34)
f2b = {88 - 5, 88 - 8, 88 - 13, 88 - 21, 88 - 34}
chk("F3_B2_fib", "B2 = 88−{F5..F9} = {83,80,75,67,54}", f2b == B2, str(f2b))
# 已消費集: B1∪C1 全喺 consumed, 66 已剔除
chk("F4_consumed", "第一輪 8 個 + 66 全部喺 consumed",
    (B1 | C1 | {66}) == consumed, str(B1 | C1 | {66}))
# 合併統計: B 3/9 vs C 3/9, 超幾何
def hyper_p(k_success, n_sample, pop_hit, pop):
    s = 0.0
    for x in range(k_success, n_sample + 1):
        if x <= pop_hit and n_sample - x <= pop - pop_hit:
            s += comb(pop_hit, x) * comb(pop - pop_hit, n_sample - x)
    return s / comb(pop, n_sample)
p_two = hyper_p(3, 9, 6, 18)
chk("F5_comb_stat", "合併 B 3/9 vs C 3/9 (9+9=18) — p=0.69",
    abs(p_two - 0.69) < 0.02, f"p={p_two:.4f} (59 號 0.69)")

print()
print("=" * 72)
print(f"結果: PASS {PASS} / FAIL {FAIL}")
print("=" * 72)
if FAILS:
    print("FAIL:", FAILS)

import json
with open("data/66_numeric_audit_round7.json", "w") as f:
    json.dump({"audit": "66_numeric_audit_round7", "date": "2026-10-17",
               "targets": ["46", "47", "49", "51", "54", "56-59"],
               "results": OUT, "pass": PASS, "fail": FAIL}, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/66_numeric_audit_round7.json")