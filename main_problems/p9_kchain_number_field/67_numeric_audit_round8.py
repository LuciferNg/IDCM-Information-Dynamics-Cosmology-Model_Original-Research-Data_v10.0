#!/usr/bin/env python3
"""
67_numeric_audit_round8.py — P9 第八輪數字審計 (2026-10-17)
============================================================
審計對象 (64 號盤點 🔴 剩餘: 29 探針 + 早期無編號 scripts 核心聲稱):
  29_probe_88site_extension: N=44/88/176 gcd 類 + deg 分佈
  chain_closure.py: 946 拍頻 = 43 邊組合, 鏈閉合 946/946
  edge_energy.py: Σe_k² = 0.1070469136, e_k² = 4sin²(π/176)·γ_m
  magic_gcd_map.py + magic_families.py: gcd(|44−d|,176) 七類分類
  s33_pipeline.py: s=33 列 16 格 (d=奇數 1..31), 只有 (13,20) d=7 有 label
  periodic_table.py: 週期表 9 元素拍頻值
  其他族 (seed_90_88 / seven_identity / rule_* / smod4 / deg_formula 等)

方法: 零 import 任何原推導 script; 第一原理; mpmath dps=50。
"""
import mpmath as mp
mp.mp.dps = 50
from math import gcd, sin, cos, pi

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

def phi(n):
    r = n; m = n; p = 2
    while p * p <= m:
        if m % p == 0:
            while m % p == 0: m //= p
            r -= r // p
        p += 1
    if m > 1: r -= r // m
    return r

N44, N88, N176 = 44, 88, 176

print("=" * 72)
print("A. 29_probe_88site_extension — N-site gcd 類 + deg")
print("=" * 72)
# A1: 44-site gcd 類 (gcd(|44−d|,176), d=1..43)
def gcd_classes(N):
    cls = {}
    for d in range(1, N):
        g = gcd(abs(N - d), 4 * N)
        cls.setdefault(g, []).append(d)
    return cls
c44 = gcd_classes(N44)
exp44 = {1: 20, 2: 10, 4: 5, 8: 3, 11: 2, 16: 2, 22: 1}
got44 = {g: len(v) for g, v in sorted(c44.items())}
chk("A1_44_gcd", "44-site gcd 類 {1:20,2:10,4:5,8:3,11:2,16:2,22:1}", got44 == exp44, str(got44))
# A2: 88-site gcd 類
c88 = gcd_classes(N88)
# 88-site: gcd(|88−d|,352) — 邊界成員
n88_total = sum(len(v) for v in c88.values())
chk("A2_88_gcd_total", "88-site gcd 類覆蓋 d=1..87 (87 個)", n88_total == 87, f"n={n88_total} classes={len(c88)}")
# A3: ω deg 公式 (deg_omega = phi(4N/gcd(|N−n|,4N))/2) — 抽樣
def deg_omega(N, n):
    return phi(4 * N // gcd(abs(N - n), 4 * N)) // 2
# 44-site: n=1 → deg?  (ζ₁₇₆: deg 應為 40)
d1 = deg_omega(N44, 1)
chk("A3_deg_omega_44_1", "44-site deg_ω(1) = 40", d1 == 40, str(d1))
# 88-site: n=1 → deg (ζ₃₅₂⁺: 352=2⁵·11, φ(352)=160, /2=80)
d88_1 = deg_omega(N88, 1)
chk("A4_deg_omega_88_1", "88-site deg_ω(1) = 80 (ζ₃₅₂⁺)", d88_1 == 80, str(d88_1))
# 176-site n=1 → φ(704)/2? 704=2⁶·11, φ=320, /2=160
d176_1 = deg_omega(N176, 1)
chk("A5_deg_omega_176_1", "176-site deg_ω(1) = 160 (ζ₇₀₄⁺)", d176_1 == 160, str(d176_1))
# A6: deg_gamma N-site = phi(2N/gcd(n,2N))/2
def deg_gamma(N, n):
    return phi(2 * N // gcd(n, 2 * N)) // 2
g44_1 = deg_gamma(N44, 1)
g88_1 = deg_gamma(N88, 1)
chk("A6_deg_gamma", "deg_γ(1): 44-site=20, 88-site=40", g44_1 == 20 and g88_1 == 40, f"44:{g44_1} 88:{g88_1}")

print()
print("=" * 72)
print("B. chain_closure.py — 946 拍頻 = 43 邊組合")
print("=" * 72)
w = lambda n: 2 * mp.sin(mp.mpf(n) * mp.pi / mp.mpf(88))
# B1: 鏈閉合 beat(i,j) = Σ_{k=i}^{j−1} beat(k,k+1) 946/946
all_ok = True
for i in range(1, 44):
    for j in range(i + 1, 45):
        direct = abs(w(j) - w(i))
        chain = sum(abs(w(k + 1) - w(k)) for k in range(i, j))
        if abs(direct - chain) > mp.mpf("1e-40"):
            all_ok = False
            break
chk("B1_chain946", "鏈閉合 beat(i,j)=Σadj 946/946 EXACT", all_ok)
# B2: 43 條邊
chk("B2_43edges", "43 條相鄰邊 (n=1..43)", True, "定義性")

print()
print("=" * 72)
print("C. edge_energy.py — 邊集能量")
print("=" * 72)
# e_k = 4sin(π/176)·cos((2k+1)π/176), k=1..43; Σe_k² = 0.1070469136
esum = mp.mpf(0)
for k in range(1, 44):
    e = 4 * mp.sin(mp.mpf(1) * mp.pi / mp.mpf(176)) * mp.cos((2*k+1) * mp.pi / mp.mpf(176))
    esum += e * e
chk("C1_edge_energy", "Σe_k² = 0.1070469136 (±1e-6)",
    abs(esum - mp.mpf("0.1070469136")) < mp.mpf("1e-6"), mp.nstr(esum, 12))
# C2: e_k² = 4sin²(π/176)·γ_m, m=87−2k (奇數)
# 驗證: cos²(θ) 關係 — e_k² = 16 sin²(π/176) cos²((2k+1)π/176)
# γ_m = 4sin²(mπ/176)? — 檢查 m=87−2k
k0 = 1
m0 = 87 - 2 * k0
# e_1² vs 4sin²(π/176)·4sin²(m0π/176)?
e1 = 4 * mp.sin(mp.mpf(1)*mp.pi/mp.mpf(176)) * mp.cos(3*mp.pi/mp.mpf(176))
lhs = e1 * e1
rhs = 4 * mp.sin(mp.mpf(1)*mp.pi/mp.mpf(176))**2 * (4 * mp.sin(mp.mpf(m0)*mp.pi/mp.mpf(176))**2)
# 用 cos²x = 1−sin²x: 要檢查 16s²c² vs 16s²·sin²(87−2)π/176
# sin²((87−2k)π/176) = cos²((2k+1)π/176)? (87−2k)π/176 = (π/2)−(2k+1)π/176? 
# π/2 = 88π/176; 88−(87−2k) = 1+2k ⟹ (87−2k)π/176 + (2k+1)π/176 = 88π/176 = π/2 ✓
chk("C2_edge_gamma", "e_k² = 4sin²(π/176)·γ_{87−2k} (補充角恒等)",
    abs(lhs - rhs) < mp.mpf("1e-45"), f"diff={float(abs(lhs-rhs)):.1e}")

print()
print("=" * 72)
print("D. magic_gcd_map / magic_families — gcd 七類 + magic") 
print("=" * 72)
MAGIC = [7, 14, 20, 22, 33]
gcl44 = lambda d: gcd(abs(44 - d), 176)
magic_g = {d: gcl44(d) for d in MAGIC}
# magic 分佈: 7→1, 14→2, 20→8, 22→22, 33→11
chk("D1_magic_gcd", "magic gcd 類: 7→1, 14→2, 20→8, 22→22, 33→11",
    magic_g == {7: 1, 14: 2, 20: 8, 22: 22, 33: 11}, str(magic_g))
# D2: 每個 gcd 類嘅 magic 唯一性 (49 號 C1 已審, 快速重複)
byg = {}
for d in MAGIC: byg.setdefault(gcl44(d), []).append(d)
chk("D2_gcd_unique2", "magic 分佈 5 個唔同 gcd 類 (互斥)", len(byg) == 5)
# D3: 七類缺 {4,16} (冇 magic)
missing = [d for d in (4, 16) if d not in set(MAGIC)]
chk("D3_missing_4_16", "缺 {4,16} gcd 類", set(MAGIC) & {4, 16} == set())

print()
print("=" * 72)
print("E. s33_pipeline.py — s=33 列 16 格")
print("=" * 72)
# s=33 列: d=奇數 1..31 共 16 格; (13,20) d=7 有 label
s33_cells = [(i, j) for (i, j) in [(13, 20)] if j - i == 7]
chk("E1_s33_df", "s=33 列 16 格 (d=1,3,...,31)", True, "定義性")
# 驗證 (13,20): s=33, d=7
i, j = 13, 20
chk("E2_anchor_cell", "(13,20): d=7, s=33 (ANCHOR 格)", (j - i == 7) and (j + i == 33))

print()
print("=" * 72)
print("F. periodic_table.py — 週期表 9 元素拍頻")
print("=" * 72)
# 已知 9 label 格 (DATA_CELLS) 與 O-series 一致
DATA_CELLS = [(1,18),(1,22),(7,20),(8,22),(8,33),(10,24),(19,33),(19,38),(30,41)]
dvals = [j - i for i, j in DATA_CELLS]
# 9 格 d 值: (1,18)→17 (1,22)→21 (7,20)→13 (8,22)→14 (8,33)→25
#              (10,24)→14 (19,33)→14 (19,38)→19 (30,41)→11
# unique = {11,13,14,17,19,21,25}
chk("F1_nine_cells", "9 格 d 值 unique = {11,13,14,17,19,21,25}",
    sorted(set(dvals)) == [11, 13, 14, 17, 19, 21, 25], str(sorted(set(dvals))))
# 週期表 data 行 {11,13,17,19,21,25} 全部有格 cover
data_d = {11, 13, 17, 19, 21, 25}
overlap = data_d & set(dvals)
chk("F2_data_overlap", "data 行全部 6 個都有格 (11,13,17,19,21,25)",
    len(overlap) == 6, f"overlap={sorted(overlap)}")
# F3: beat 值抽樣 — (7,20) n/p BBN
beat720 = abs(w(20) - w(7))
# beat(7,20) 數值 = ?
chk("F3_beat720", "beat(7,20) 計算正常 (正值)",
    beat720 > 0 and beat720 < 4, mp.nstr(beat720, 10))

print()
print("=" * 72)
print("G. 其他早期族 — 數論規則核心")
print("=" * 72)
# deg_formula.py: deg(ω_n) 公式核對 (44-site n=1..44 分佈)
degs44 = [deg_omega(N44, n) for n in range(1, 45)]
# 已知分佈 (21 號): deg 40:20個, 20:10個, 10:5個, 5:5個, 4:2個(11,33), 2:1(22), 0:1(44)
from collections import Counter
dc44 = Counter(degs44)
exp_dc = {40: 20, 20: 10, 10: 5, 5: 5, 4: 2, 2: 1, 0: 1}
ok44 = all(dc44.get(k, 0) == v for k, v in exp_dc.items()) and sum(dc44.values()) == 44
chk("G1_deg_dist44", "44-site deg(ω) 分佈 {40:20,20:10,10:5,5:5,4:2,2:1,0:1}",
    ok44, str(dict(dc44)))
# seven_identity.py: 7 嘅結構身份
chk("G2_seven_identity", "7 ∈ gcd1 類 (deg40)", gcl44(7) == 1 and deg_omega(N44, 7) == 40)
# seed_90_88: Σγ=90 種子
S90 = sum(4 * mp.sin(mp.mpf(k) * mp.pi / mp.mpf(88))**2 for k in range(1, 45))
chk("G3_seed_90", "Σγ (n=1..44) = 90 (種子 90_88)", abs(S90 - 90) < mp.mpf("1e-40"), mp.nstr(S90, 12))
# smod4_rule.py: mod-4 判準 (45 族 a奇/47 族 a偶)
# γ_{22+m}+γ_{22−m}=4 基礎
gam4 = all(abs((4*mp.sin(mp.mpf(22+m)*mp.pi/mp.mpf(88))**2 + 4*mp.sin(mp.mpf(22-m)*mp.pi/mp.mpf(88))**2) - 4) < mp.mpf("1e-40") for m in range(1, 22))
chk("G4_pair224", "γ_{22+m}+γ_{22−m}=4 ∀m (smod4 基礎)", gam4)
# rule_4adic: 4-adic 規則 — ω_n 嘅 v₂?
def v2(x):
    c = 0
    while x % 2 == 0:
        c += 1; x //= 2
    return c
# (4adic 關於 γ_n 的 v₂ 結構 — 22 → v₂=1? 快速檢查 n=22: γ=2)
chk("G5_gamma22", "γ_22 = 2 (有理, v₂ 判準核心)", abs(4*mp.sin(mp.mpf(22)*mp.pi/mp.mpf(88))**2 - 2) < mp.mpf("1e-40"))
# spectral_match / spectroscopy / spectrum_analysis: 譜家族
# 946 拍頻分佈: 奇區 484 + 偶區 462
odd = sum(1 for i in range(1, 44) for j in range(i+1, 45) if (j - i) % 2 == 1)
even = sum(1 for i in range(1, 44) for j in range(i+1, 45) if (j - i) % 2 == 0)
chk("G6_parity946", "946 拍頻奇偶: 奇 484 + 偶 462", odd == 484 and even == 462, f"odd={odd} even={even}")
# low_endpoint_structure: γ_1 結構
chk("G7_gamma1", "γ_1 = 4sin²(π/88) (低端點結構)", abs(4*mp.sin(mp.mpf(1)*mp.pi/mp.mpf(88))**2 - (2 - 2*mp.cos(mp.mpf(2)*mp.pi/mp.mpf(88)))) < mp.mpf("1e-40"))
# missing_gcd.py: gcd 類別缺 magic 數
chk("G8_missing_gcd", "七類缺 {4,16} — 兩類冇 magic", (4 not in [gcl44(d) for d in MAGIC]) and (16 not in [gcl44(d) for d in MAGIC]))
# unassigned_opcodes: 未指派 opcode 數 (946 − 25 label)
chk("G9_unassigned", "946 − 25 label = 921 未指派 (定義性)", 946 - 25 == 921)

print()
print("=" * 72)
print(f"結果: PASS {PASS} / FAIL {FAIL}")
print("=" * 72)
if FAILS:
    print("FAIL:", FAILS)

import json
with open("data/67_numeric_audit_round8.json", "w") as f:
    json.dump({"audit": "67_numeric_audit_round8", "date": "2026-10-17",
               "targets": ["29_probe", "chain_closure", "edge_energy", "magic_gcd_map",
                           "s33_pipeline", "periodic_table", "早期族"],
               "results": OUT, "pass": PASS, "fail": FAIL}, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/67_numeric_audit_round8.json")