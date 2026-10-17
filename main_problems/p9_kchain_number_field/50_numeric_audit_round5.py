#!/usr/bin/env python3
"""
50_numeric_audit_round5.py — 第五輪審計: 30-32 號 (2026-10-17)
==============================================================
範圍: 30_mirror_exclusion / 31_matrix_fixed_point / 32_column_isomorph_contact
紀律: 零 import 原 scripts; 第一原理重算; §4.7 有罪推定 (check bug 優先);
      整數/Fraction 精確; 全部真工具輸出。

審計靶 (md 聲明):
A (30): A1 gcl 七類; A2 鏡像流向; A3 R4a 出走/缺類; A4 R4c 鎖7 FAIL;
        A5 盲測 P=0.6999; A6 33↔11 / 20↔24 / 22 自鏡像
B (31): B1 operator 固定表 (T1-T7, 22 唯一); B2 Galois {1,87} + 87 奇數;
        B3 gcd_shift k={43}; B4 ★md/script Galois 條件一致性
C (32): C1 deg 層分佈; C2 data 端點×magic; C3 7 位置; C4 14 冇端點
"""
import json
from math import gcd
from collections import Counter

OUT = {}
FAILS = []

def norm_key(o):
    """轉 tuple keys 做 str (JSON dump 需要)"""
    if isinstance(o, dict):
        return {str(k): norm_key(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [norm_key(x) for x in o]
    return o

def check(name, got, exp, desc):
    ok = (got == exp)
    OUT[name] = {"got": norm_key(got), "exp": norm_key(exp), "ok": ok}
    if not ok:
        FAILS.append(name)
    print(f"  [{'✅' if ok else '❌'}] {name}: {desc}  got={got} exp={exp}")
    return ok

def gcl(d): return gcd(abs(44 - d), 176)
MAGIC = [7, 14, 20, 22, 33]
DATA = {11, 13, 17, 19, 21, 25}

# ============ A: 30_mirror_exclusion ============
print("=== A: 30_mirror_exclusion ===")
classes = {}
for d in range(1, 44): classes.setdefault(gcl(d), []).append(d)
A1exp = {1: 20, 2: 10, 4: 5, 8: 3, 11: 2, 16: 2, 22: 1}
check("A1_class_sizes", {g: len(v) for g, v in sorted(classes.items())}, A1exp,
      "gcd 七類大小 (1:20,2:10,4:5,8:3,11:2,16:2,22:1)")

mirror = lambda d: 44 - d
flow = {}
for g in sorted(classes):
    targets = Counter(gcl(mirror(d)) for d in classes[g])
    flow[g] = dict(targets)
no_magic_g = [g for g in sorted(classes) if not any(d in MAGIC for d in classes[g])]
all_exit_g = [g for g in sorted(classes) if all(gcl(mirror(d)) != g for d in classes[g])]
has_magic_all_exit = [g for g in sorted(classes) if all(gcl(mirror(d)) != g for d in classes[g])
                      and any(d in MAGIC for d in classes[g])]
check("A2_flow_gcd4", flow.get(4), {8: 3, 16: 2}, "gcd4 鏡像流向 gcd8:3+gcd16:2")
check("A2_flow_gcd16", flow.get(16), {4: 2}, "gcd16 → gcd4:2")
check("A2_flow_gcd8", flow.get(8), {4: 3}, "gcd8 → gcd4:3")
check("A3_no_magic", no_magic_g, [4, 16], "冇 magic 類 = [4,16]")
check("A3_all_exit", all_exit_g, [4, 8, 16], "全出走類 = [4,8,16]")
check("A3_exit_but_magic", has_magic_all_exit, [8], "出走但有 magic = [8] (反例 R4a 必要唔充要)")

# A4: R4c 鎖 7 — gcd1 Lucas 質數候選 {3,7,29} 鏡像伴侶角色
g1 = classes[1]
role = lambda x: "magic" if x in MAGIC else ("data" if x in DATA else "filler")
cand = [3, 7, 29]
partner_roles = {d: role(mirror(d)) for d in cand}
check("A4_partner_roles", partner_roles, {3: "filler", 7: "filler", 29: "filler"},
      "3/7/29 伴侶全 filler → R4c 分唔開")
check("A4_7_mirror_is_37", mirror(7), 37, "7 ↔ 37")

# A5: 盲測 P (10^6, seed 20261017)
import random
random.seed(20261017)
N = 10**6
cnt = 0
for _ in range(N):
    d_ = random.choice(g1)
    if role(mirror(d_)) == "filler":
        cnt += 1
p = cnt / N
print(f"  [{'✅' if abs(p-0.7)<0.01 else '⚠️'}] A5_blind: P={p:.4f} (exp ≈0.6999)")
OUT["A5_blind"] = {"p": round(p, 5), "exp": 0.6999, "ok": abs(p - 0.6999) < 0.01}
if abs(p - 0.6999) >= 0.01: FAILS.append("A5_blind")

# A6: 33↔11, 20↔24, 22 自鏡像
check("A6_33_mirror_11", mirror(33), 11, "33 ↔ 11 (magic↔data)")
check("A6_20_mirror_24", mirror(20), 24, "20 ↔ 24")
check("A6_22_self", mirror(22), 22, "22 自鏡像")
check("A6_22_gcl", gcl(22), 22, "22 gcd=22")

# ============ B: 31_matrix_fixed_point ============
print()
print("=== B: 31_matrix_fixed_point ===")

def P(d):
    return frozenset((i, j) for i in range(1, 45) for j in range(i + 1, 45) if j - i == d)

def norm(pair, mod=44):
    i, j = pair
    return ((i % mod) if (i % mod) else 44, (j % mod) if (j % mod) else 44)

def apply_op(Pset, op, mod=44):
    out = set()
    for (i, j) in Pset:
        ni, nj = op(i, j)
        a, b = norm((ni, nj), mod)
        out.add((min(a, b), max(a, b)))
    return frozenset(out)

ops = {
    "T1_transpose": lambda i, j: (j, i),
    "T2_mirror44": lambda i, j: (44 - i, 44 - j),
    "T3_mirror88": lambda i, j: (88 - i, 88 - j),
    "T4_neg_left": lambda i, j: (44 - i, j),
    "T4_neg_right": lambda i, j: (i, 44 - j),
    "T5_diag_shift1": lambda i, j: (i + 1, j + 1),
    "T6_diag_shift2": lambda i, j: (i + 2, j + 2),
    "T7_antidiag_s1": lambda i, j: (i + 1, j - 1),
}
# md 表 (31 號): op → (d7 fixed, magic 內唯一固定, 全 43 行 fixed 數)
md_tab = {
    "T1_transpose": (True, None, 43),
    "T2_mirror44": (False, [22], 1),
    "T3_mirror88": (False, [22], 1),
    "T4_neg_left": (False, None, 0),
    "T4_neg_right": (False, None, 1),
    "T5_diag_shift1": (False, [22], 1),
    "T6_diag_shift2": (False, [22], 1),
    "T7_antidiag_s1": (False, None, 1),
}
for name, op in ops.items():
    all_fixed = [d for d in range(1, 44) if apply_op(P(d), op, 44) == P(d)]
    fd = set(all_fixed)
    uniq = [d for d in MAGIC if d in fd and all((d2 not in fd) for d2 in MAGIC if d2 != d)]
    exp7, expu, expn = md_tab[name]
    ok = (7 in fd) == exp7 and uniq == (expu or []) and len(all_fixed) == expn
    OUT[f"B1_{name}"] = {"d7_fixed": 7 in fd, "unique_magic": uniq, "n_fixed": len(all_fixed), "ok": ok}
    if not ok: FAILS.append(f"B1_{name}")
    print(f"  [{'✅' if ok else '❌'}] B1_{name}: d7={7 in fd!s:5s} 唯一magic={uniq!s:12s} fixed數={len(all_fixed):2d}  (md: {exp7}, {expu}, {expn})")

# B2: Galois — md 聲明 σ_a(ω_d)=ω_d ⟺ a·d≡d (mod 176) 或 d(a+1)≡88 (mod 176)
#     d=3/7/29 → {1,87}; σ_87 固定所有奇數
print()
def galois_fixed_correct(d):
    out = []
    for a in range(1, 176):
        if gcd(a, 176) != 1: continue
        if (a * d) % 176 == d % 176 or (d * (a + 1)) % 176 == 88 % 176:
            out.append(a)
    return out
g37 = galois_fixed_correct(7)
g3 = galois_fixed_correct(3)
g29 = galois_fixed_correct(29)
check("B2_galois_7", g37, [1, 87], "d=7 → {1,87}")
check("B2_galois_3", g3, [1, 87], "d=3 → {1,87}")
check("B2_galois_29", g29, [1, 87], "d=29 → {1,87}")
# σ_87 固定所有奇數 d?
odd_fixed = all(87 in galois_fixed_correct(d) for d in range(1, 44, 2))
even_fixed = all(87 not in galois_fixed_correct(d) for d in range(2, 44, 2))
check("B2_sigma87_odds", [odd_fixed, even_fixed], [True, True], "σ_87 固定全部奇數, 唔固定任何偶數")
# ★ B4: script 用嘅條件 (a*d)%176 in (d, 176−d) 係咪等價於正確條件?
script_cond = []
for d in [3, 7, 29]:
    s = [a for a in range(1, 176) if gcd(a, 176) == 1 and (a * d) % 176 in (d % 176, (176 - d) % 176)]
    script_cond.append((d, s))
print(f"  [{'✅' if all(v[1]==[1,175] for v in script_cond) else '⚠️'}] B4_script_cond: script 條件 (a·d ≡ ±d) 得出 {[v[1] for v in script_cond]} — 同正確 {[1,87]} 唔同!!")
OUT["B4_script_cond"] = {"script_gives": [v[1] for v in script_cond], "correct": [[1, 87]] * 3,
                         "ok": False, "note": "31 script 用 (176−d) = −d 條件 (σ=± 鏡像), 正確固定條件係 d(a+1)≡88; 但 run 出嚟 md 寫 {1,87} — script 同 md 唔一致, 需查原 JSON"}
FAILS.append("B4_script_cond")
# 檢查原 JSON 有咩
try:
    j31 = json.load(open("data/31_matrix_fixed_point.json"))
    g_orig = j31.get("galois", {})
    print(f"  → 原 JSON galois: {json.dumps(g_orig, default=str)[:200]}")
except Exception as e:
    print(f"  → 原 JSON 讀唔到: {e}")

# B3: gcd_shift — 保持 gcd1 全體嘅 k
gshift_keepers = []
for k in range(1, 44):
    d2 = lambda d: (d + k - 1) % 43 + 1
    if all(gcl(d2(d)) == gcl(d) for d in range(1, 44)):
        gshift_keepers.append(k)
check("B3_gcd_shift_keepers", gshift_keepers, [43], "非平凡 k 只有 43 (trivial mod43 恆等)")

# ============ C: 32_column_isomorph_contact ============
print()
print("=== C: 32_column_isomorph_contact ===")
phi = lambda n: sum(1 for k in range(1, n + 1) if gcd(k, n) == 1)
def om_deg(n): return phi(176 // gcl(n)) // 2
deg_classes = {}
for n in range(1, 45): deg_classes.setdefault(om_deg(n), []).append(n)
# C1 正確期望: n 面 (1..44) 包括 n=44 (ω₄₄=2 唯一有理, gcl=176, om_deg=0)
C1exp = {40: 20, 20: 10, 10: 5, 5: 5, 4: 2, 2: 1, 0: 1}
check("C1_deg_distrib", {de: len(v) for de, v in sorted(deg_classes.items(), reverse=True)}, C1exp,
      "deg 分佈 (n 面 1..44, 含 ω₄₄ deg0:1) — 32 md 表省略 deg0, 附件更正")
for de, v in sorted(deg_classes.items(), reverse=True):
    m_in = [x for x in v if x in MAGIC]
    d_in = [x for x in v if x in DATA]
    print(f"    deg={de:>2}: n={v}  magic={m_in}  data={d_in}")
# 每 deg 層一 magic (除 deg10)
# 每 deg 層一 magic (除 deg10; deg0=44 冇 magic 唔算層缺)
magic_by_deg = {de: [x for x in v if x in MAGIC] for de, v in deg_classes.items()}
okC1b = all(len(m) == 1 for de, m in magic_by_deg.items() if de not in (10, 0)) and magic_by_deg.get(10) == [] and magic_by_deg.get(0) == []
OUT["C1b_per_layer"] = {"by_deg": {de: m for de, m in magic_by_deg.items()}, "ok": okC1b}
if not okC1b: FAILS.append("C1b_per_layer")
print(f"  [{'✅' if okC1b else '❌'}] C1b: 每 deg 層一 magic (deg10 缺, deg0=44 冇 magic): {magic_by_deg}")

# C2: data 格端點 × magic
data_cells = [(30, 41), (7, 20), (8, 22), (10, 24), (19, 33), (1, 18), (19, 38), (1, 22), (8, 33)]
hits = []
for (i, j) in data_cells:
    me = sorted(x for x in (i, j) if x in MAGIC)
    hits.append(((i, j), me))
C2exp = {  # 5 格有 magic 端點: (7,20)[7,20] 2次 + (8,22)[22] (19,33)[33] (1,22)[22] (8,33)[33] 各1 = 6 次命中
    (30, 41): [], (7, 20): [7, 20], (8, 22): [22], (10, 24): [], (19, 33): [33],
    (1, 18): [], (19, 38): [], (1, 22): [22], (8, 33): [33],
}
got_h = {c: m for c, m in hits}
check("C2_data_endpoint_magic", got_h, C2exp, "data 格端點×magic (5/9 格, 6 次命中)")
n_hit_cells = sum(1 for m in got_h.values() if m)
check("C2_n_hit_cells", n_hit_cells, 5, "5/9 格有 magic 端點 ← 32 md 寫 6 格 7 次係真 doc 錯!")
check("C2_anchor_transfer", got_h[(7, 20)], [7, 20], "(7,20) 唯一雙 magic 端點")
check("C2_14_no_endpoint", [x for x in MAGIC if not any(x in m for m in got_h.values())], [14],
      "Magic 只有 14 冇做 data 端點")

# C3: deg40 層 7 嘅位置
g40 = sorted(deg_classes[40])
pos7 = g40.index(7) + 1
check("C3_pos7", [pos7, len(g40)], [4, 20], "7 = 第 4/20 位")
first_lp = min(x for x in g40 if x in {3, 7, 29})
check("C3_first_lucas_prime", first_lp, 3, "第一 Lucas 質數 = 3 (唔係 7)")

print()
print(f"=== 結果: {len(OUT)-len(FAILS)}/{len(OUT)} PASS, {len(FAILS)} FAIL ===")
for f in FAILS:
    print(f"  FAIL: {f}")
with open("data/50_numeric_audit_round5.json", "w") as f:
    json.dump(OUT, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/50_numeric_audit_round5.json")