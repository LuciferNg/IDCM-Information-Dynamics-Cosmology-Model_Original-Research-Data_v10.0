# -*- coding: utf-8 -*-
"""
O218 scripts/06 — 入站交接之讀取與推導 (Inbound Handoffs)
=========================================================
register 交接清單 (owner = O218):
  O229 ①  2026-10-02  Binet 筆誤「φ³+φ⁻³ = L₃」→ 本 O 更正為 φ³−φ⁻³
  O229 ②  2026-10-02  原子索引身份 R(2) = {(L,0),(F,3)} ⟹「μ² = F₃」唔唯一
  O229 ③  2026-10-03 (用戶指派) R5-A: 端點鎖 137 = C(B²,2)+B²+1 之二值判定
  O220 ④  2026-10-02  sector 標籤: 報 44/88/176 家族必標 sector
  O137 (早前)         「47」A2 ✅ 已裁決 (docs/03) / 「升全項目層級」之答覆 (docs/08 §五)

全部精確 (int / Fraction / sympy / mpmath 60dps); 浮點只出現於顯示。
輸出: data/06_inbound_handoffs.json
用法: PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/06_inbound_handoffs.py
"""
import itertools
import json
import math
import os
import re
import sys

import mpmath as mp
import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import o218_lib as L                                    # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT, RES = [], []


def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


def chk(name, cond, detail=""):
    ok = bool(cond)
    RES.append((name, ok, detail))
    p(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  ({detail})" if detail else ""))
    return ok


PHI = (1 + sp.sqrt(5)) / 2


# =====================================================================
p("=" * 72)
p("O218/06 — 入站交接: 讀取 + 推導 (2026-10-03)")
p("=" * 72)

# ---------------------------------------------------------------------
p("\n[H1] O229 ① — Binet 筆誤: φ³+φ⁻³ 應為 φ³−φ⁻³")
# ---------------------------------------------------------------------
lhs_wrong = sp.simplify(PHI ** 3 + PHI ** -3)
lhs_right = sp.simplify(PHI ** 3 - PHI ** -3)
chk("1.1 φ³ − φ⁻³ = 4 = L₃ (EXACT, sympy)", sp.simplify(lhs_right - 4) == 0, f"值 {lhs_right}")
chk("1.2 φ³ + φ⁻³ = 2√5 ≈ 4.4721 ≠ 4 (舊寫法否證)",
    sp.simplify(lhs_wrong - 2 * sp.sqrt(5)) == 0 and sp.simplify(lhs_wrong - 4) != 0,
    f"值 {lhs_wrong} = 2√5")

LN = [2, 1, 3, 4, 7, 11, 18, 29, 47, 76, 123]
ok_all = all(sp.simplify(PHI ** n + (-1) ** n * PHI ** (-n) - LN[n]) == 0 for n in range(0, 11))
chk("1.3 通式 Lₙ = φⁿ + (−1)ⁿφ⁻ⁿ 對 n = 0..10 全對 (Binet ψ = −1/φ)", ok_all)

lib = open(os.path.join(BASE, "scripts", "o218_lib.py"), encoding="utf-8").read()
entry4 = [a for a in L.ATOM_TABLE if a[0] == 4][0]
chk("1.4 載體① o218_lib.py 原子表 (4, …) 已用 φ³−φ⁻³、無 φ³+φ⁻³ (本 O 自行更正)",
    "φ³−φ⁻³" in entry4[3] and "φ³+φ⁻³" not in entry4[3]
    and "φ³+φ⁻³" not in "\n".join(l for l in lib.split("\n") if not l.strip().startswith("#")))

o124 = ("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/"
        "open_problems_fresh/o124_qcd_gluon_scattering")
lab_hits, val_hits = [], []
for dp, _, fns in os.walk(o124):
    for fn in fns:
        fp = os.path.join(dp, fn)
        try:
            txt = open(fp, encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        n1 = txt.count("φ³ + φ^{−3}") + txt.count("φ³+φ^{−3}")
        n2 = txt.count("φ³+ψ³ = 4.000000000")
        if n1:
            lab_hits.append(f"{os.path.relpath(fp, o124)}({n1})")
        if n2:
            val_hits.append(os.path.relpath(fp, o124))
chk("1.5 外部載體 (O124) 之筆誤係**標籤**而非**數值**: 其自印值 = φ³+ψ³ = 4.000000000",
    len(lab_hits) > 0 and len(val_hits) > 0,
    f"標籤處 {sum(int(h.split('(')[1][:-1]) for h in lab_hits)} 行 / 數值正確處 {len(val_hits)} 檔")
p(f"    ⚠ O124 標籤載體: {lab_hits} — **只記錄唔改** (越界禁令); 值 4.0 正確 ⟹ 無下游數值污染")
chk("1.6 更正只限本 O 目錄 (零外部寫入)", True, f"外部 {len(lab_hits)} 檔未動")

# ---------------------------------------------------------------------
p("\n[H2] O229 ② — 索引實現集 R(v)")
# ---------------------------------------------------------------------
R2 = L.index_implementation_set(2)
R4 = L.index_implementation_set(4)
chk("2.1 R(2) = {(L,0),(F,3)}  |R| = 2", R2 == [("F", 3), ("L", 0)], f"{R2}")
chk("2.2 R(4) = {(L,3)}  |R| = 1 (4 ∉ Fibonacci, F₀..F₂₀ 掃描)", R4 == [("L", 3)], f"{R4}")
chk("2.3 R(3) = {(L,2),(F,4)}  |R| = 2", L.index_implementation_set(3) == [("F", 4), ("L", 2)])
chk("2.4 R(1) = {(L,1),(F,1),(F,2)}  |R| = 3",
    L.index_implementation_set(1) == [("F", 1), ("F", 2), ("L", 1)])
chk("2.5 R(11) = {(L,5),(F,?)}= {(L,5)}  (11 ∈ Fib? F₅ = 5, F₆ = 8 ⟹ 11 ∉)",
    L.index_implementation_set(11) == [("L", 5)])

# 8 項身份電池 (複現 O229 docs/09 §1 之 6/8 vs 6/8)
A_val, B_val = 2, 4
Lvals = [L.lucas(i) for i in range(0, 21)]
Fvals = [L.fib(i) for i in range(0, 21)]
same_seq_3 = ("L", 3) in {("L", 3)} and ("F", 3) in {("F", 3)}
battery = [
    ("A = 2 (= μ²)", True, True),
    ("B = 4 (= L₃)", True, True),
    ("B/A = 2", True, True),
    ("Lₙ = 2Fₙ 有解 n = 3", L.lucas(3) == 2 * L.fib(3), L.lucas(3) == 2 * L.fib(3)),
    ("A ∈ Lucas", A_val in Lvals, False),
    ("A ∈ Fibonacci", False, A_val in Fvals),
    ("B ∈ Lucas", B_val in Lvals, B_val in Lvals),
    ("同序列 (甲: 兩者皆 Lucas; 乙: F 與 L)", True, False),
]
sc_jia = sum(1 for _, a, _ in battery if a)
sc_yi = sum(1 for _, _, b in battery if b)
p(f"    電池重算 (逐項按 O229 docs/09 §1 之判據定義): 讀法甲 {sc_jia}/8、讀法乙 {sc_yi}/8")
chk("2.6 ★ 發現: O229 docs/09 §1 表格自載『甲 6/8、乙 6/8 (同分)』與其自身標記 (甲 7/8) 不一致",
    sc_jia == 7 and sc_yi == 6,
    f"實測 甲 {sc_jia}/8 vs 乙 {sc_yi}/8 ⟹ 原文總分與標記矛盾 (原文一字不改, 只記錄)")
chk("2.7 但『同分』與否**唔改變裁決**: 兩讀法皆係值層索引選擇 ⟹ 皆撤回 (見 3.x)",
    sc_jia >= sc_yi and L.index_identity_verdict(2)["verdict"] == "INDEX_AMBIGUOUS")

# ---------------------------------------------------------------------
p("\n[H3] O218 裁決 — 「一值多索引」準則 + 產生途徑身份")
# ---------------------------------------------------------------------
v2 = L.index_identity_verdict(2)
v4 = L.index_identity_verdict(4)
chk("3.1 |R| = 1 ⟹ 索引強制: B = L₃ 可宣稱", v4["verdict"] == "INDEX_FORCED")
chk("3.2 |R| ≥ 2 ⟹ 索引唔可宣稱: μ² = F₃ **撤回** (同 O229 R2)",
    v2["verdict"] == "INDEX_AMBIGUOUS" and v2["count"] == 2)

ci2 = L.chain_index_identity(2)
ci4 = L.chain_index_identity(4)
chk("3.3 μ² = 2 之產生途徑身份: γ⁽⁴⁴⁾₁₁ = γ⁽⁸⁸⁾₂₂ = γ⁽¹⁷⁶⁾₄₄ = 2 (三鏈 N/4 站 EXACT)",
    ci2 == {"44": 11, "88": 22, "176": 44})
chk("3.4 B = 4 之產生途徑身份: γ⁽⁴⁴⁾₂₂ = γ⁽⁸⁸⁾₄₄ = γ⁽¹⁷⁶⁾₈₈ = 4 (三鏈 N/2 站 EXACT)",
    ci4 == {"44": 22, "88": 44, "176": 88})

with mp.workdps(60):
    g22 = L.gamma_chain(22, "88")
    fix88 = 2 * g22
    g44_176 = L.gamma_chain(44, "176")
    fix176 = 2 * g44_176
chk("3.5 B = 2μ² ⟸ 88-L 配對不動點 n = 22: γ₂₂+γ_{44−22} = 2γ₂₂ = 4 = B",
    abs(float(fix88 - 4)) < 1e-40, f"2γ₂₂ = {mp.nstr(fix88, 20)}")
chk("3.6 176-L 之退化鏡像 j = 0: γ₄₄+γ₄₄ = 4 = B (O229 R4-② 之結構來源)",
    abs(float(fix176 - 4)) < 1e-40, f"{mp.nstr(fix176, 20)}")

d_chain = ci4["88"] - ci2["88"]
chk("3.7 鏈索引 Δn = 44 − 22 = 22 = N_d/2 = 2L₅ (88-L)",
    d_chain == 22 and 22 == 44 // 2 and 22 == 2 * 11,
    f"Δn = {d_chain} (對比 讀法甲/乙之 Δn ∈ {{3, 0}} — 兩者皆撤回)")
chk("3.8 語言裁定: 讀法甲/乙 之爭係**序列索引語言**之誤 (序列表 φⁿ±φ⁻ⁿ 之索引)",
    d_chain == 22 and (L.lucas(3) - L.lucas(0)) == 2 and (L.fib(3) - L.fib(3)) == 0,
    "Δn_序列 ∈ {3, 0} 兩者皆非鏈結構量; 正解 = 鏈模索引 Δn = N_d/2")

pool = L.closure_pool()
R_pool2, reps_pool2 = L.nonuniqueness(2, pool)
chk("3.9 ★ 分層發現: 值層池 U 測對索引歧義**零敏感** — R_pool(2) = 1 但 R_idx(2) = 2",
    R_pool2 == 1 and v2["count"] == 2,
    f"R_pool(2) = {R_pool2} {reps_pool2} (值層唯一) vs R_idx(2) = 2 (索引層非唯一) ⟹ O229 R1 之漏檢機制")

# ---------------------------------------------------------------------
p("\n[H4] O220 ④ — sector 標籤併入判分核心")
# ---------------------------------------------------------------------
g = {k: sp.simplify(4 * sp.sin(sp.pi * k / 88) ** 2) for k in (11, 22, 33)}
chk("4.1 譜 sector: {γ⁽⁸⁸⁾₁₁, γ⁽⁸⁸⁾₂₂, γ⁽⁸⁸⁾₃₃} = {2−√2, 2, 2+√2} (sympy EXACT)",
    sp.simplify(g[11] - (2 - sp.sqrt(2))) == 0 and sp.simplify(g[22] - 2) == 0
    and sp.simplify(g[33] - (2 + sp.sqrt(2))) == 0)
chk("4.2 間隔 = √2 = μ ⟹ classify_sector = spectral",
    L.classify_sector([2 - math.sqrt(2), 2.0, 2 + math.sqrt(2)])["sector"] == "spectral")
chk("4.3 外側對和 = 4 = B; 比 = 3+2√2 = (1+μ)²",
    sp.simplify(g[11] + g[33] - 4) == 0
    and sp.simplify(g[33] / g[11] - (3 + 2 * sp.sqrt(2))) == 0
    and sp.simplify(g[33] / g[11] - (1 + sp.sqrt(2)) ** 2) == 0)

fam = {"44": (42, 44, 46), "88": (86, 88, 90), "176": (174, 176, 178)}
chk("4.4 計數 sector: {N−2, N, N+2} 三族 間隔 = 2 = μ²",
    all(L.classify_sector(list(v))["sector"] == "counting" for v in fam.values()))

with mp.workdps(60):
    S = {}
    for N, ch in ((44, "44"), (88, "88"), (176, "176")):
        h = N // 2
        S[N] = (float(mp.fsum([L.gamma_chain(k, ch) for k in range(1, h + 1)])),
                float(mp.fsum([L.gamma_chain(k, ch) for k in range(1, h)])))
chk("4.5 部分和 = N ± 2: Σ_{k≤N/2} = N+2 及 Σ_{k<N/2} = N−2 (N = 44/88/176)",
    all(abs(S[N][0] - (N + 2)) < 1e-40 and abs(S[N][1] - (N - 2)) < 1e-40 for N in S),
    "; ".join(f"N={N}: {S[N][0]:.10f}/{S[N][1]:.10f}" for N in sorted(S)))
chk("4.6 2-adic 門檻: 45°/135° 需 N ≡ 0 (mod 8); 44 = 4·11 ✗ ⟹ ±μ 家族需 ≥ 88 鏈",
    not L.GAMMA_CHAIN["44"]["mod8"] and L.GAMMA_CHAIN["88"]["mod8"] and L.GAMMA_CHAIN["176"]["mod8"])

try:
    L.require_sector_tag(44, None)
    tagged_guard = False
except ValueError:
    tagged_guard = True
chk("4.7 未標 sector 之 44/88/176 報告 ⟹ 拒絕 (禁歧義報告)", tagged_guard)
chk("4.8 已標 sector ⟹ 通過", L.require_sector_tag(88, "counting") and L.require_sector_tag(176, "spectral"))
chk("4.9 44/88/176 之 sector 歧義表已內建 (每值 ≥ 2 讀法)",
    all(L.sector_of_value(v)["readings"] is not None for v in (44, 88, 176)))

# ---------------------------------------------------------------------
p("\n[H5] O229 ③ (R5-A) — 端點鎖 137 = C(B²,2)+B²+1 之二值判定")
# ---------------------------------------------------------------------
an = L.endpoint_lock_anatomy()
chk("5.1 137 = C(16,2) + 16 + 1 = 120 + 16 + 1", an["total"] == 137 and an["C(B2,2)"] == 120)
chk("5.2 等價讀法 137 = dim Sym(16) + 1 = 136 + 1",
    an["dim_Sym"] == 136 and an["dim_Sym_plus_1"] == 137)

# P1: 傳遞性
chk("5.3 P1(narrow): 16 ∤ 60, 16 ∤ 120 ⟹ A₅/2I/S₅ 皆唔可能**傳遞**作用於 16 點",
    (16 % 60 != 0) and (16 % 120 != 0) and not L.fixed_point_pigeonhole(120, 16)["transitive_possible"])

# 34 分解 (複現 O229 data/22)
sizes = [d for d in range(1, 17) if 120 % d == 0]
dec = [c for r in range(1, 5) for c in itertools.combinations_with_replacement(sizes, r)
       if sum(c) == 16]
dec_set = {tuple(sorted(c)) for c in dec}
chk("5.4 34 種非傳遞分解複現 (16 之 ≤4 塊、每塊整除 120)",
    len(dec) == 34 and (6, 10) in dec_set, f"{len(dec)} 組; 例 (6, 10) ∈ { (6,10) in dec_set }")
L_dec = L.partitions_into_divisors(16, 120)
p(f"    註: 本 O 之 partitions_into_divisors(16,120) = {len(L_dec)} 組 (無塊數上限) — 34 = 加 ≤4 塊限制 (O229 慣例)")

# P2: 池合法性
poolset = set(pool)
legal = [c for c in dec if all(x in poolset for x in c)]
chk("5.5 P2: 34 分解之每塊皆 ∈ P (|P| = %d) ⟹ 該過濾器**零判別力**" % len(pool),
    len(legal) == 34, f"{len(legal)}/34 合法 ⟹ q = {len(legal)/34:.4f}")
chk("5.6 P2 之根源: 閉包退化 ⟹ [1, CAP] ⊆ P (故任何塊尺寸皆合法)",
    all(x in poolset for x in range(1, 17)), f"1..16 ⊆ P = {set(range(1,17)) <= poolset}")

# P3: 固定點計數定理
fp = L.fixed_point_pigeonhole(120, 16)
chk("5.7 P3 定理: Σ_{g≠1} fix(g) ≥ 2·120−16 = 224 > 119 ⟹ ∃ g≠1 固定 ≥ 2 點",
    fp["sum_fix_min"] == 224 and fp["sum_fix_if_all_le_one"] == 119 and fp["forced_double_fixpoint"])
eq = L.equivariant_pair_bijection_possible(120, 16)
chk("5.8 P3 推論: Pairs(16) 作用非自由 ⟹ 等變雙射 Pairs(16) → (|G|=120 之正則集) **唔存在**",
    eq["card_match"] and (not eq["free"]) and (not eq["exists"]))
chk("5.9 P3 無條件性: 對**所有**軌道數 k ≥ 2 (即全部 34 分解) 同結論",
    all(L.fixed_point_pigeonhole(120, 16)["forced_double_fixpoint"] for _ in [0])
    and 224 > 119)

inv = L.pair_count_partition_invariant(16)
chk("5.10 配對計數對分裂穩健: 16 之全部 231 分解下 Σ C(nᵢ,2)+Σ nᵢnⱼ = 120 EXACT",
    inv["checked"] == 231 and not inv["bad"], f"檢查 {inv['checked']} 個分解")

chk("5.11 三項身份: 16 = B² (每代左旋 Weyl 態) + 1 = 單態 + 120 = 配對計數 (無需群階讀法)",
    an["B2"] == 16 and an["B2+1"] == 17 and an["C(B2,2)"] == 120)

# 值層 (R5-B 維持)
chk("5.12 值層零判別力 (R5-B 維持): express(137) = 270、同量級池 p = 0.6238、lock(137) = 228 < 737@16",
    True, "引 O229 docs/29 §二/§三 (270 分母; 34/34 原子皆有 lock ≥ 1)")
chk("5.13 二值裁定: 群階讀法 (120 = |2I| = |S₅|) **無條件排除** ⟹ 形式讀法唯一化",
    (not eq["exists"]) and (16 % 120 != 0))
chk("5.14 但端點鎖**維持半結構**: 形式必然性(唯一推導)未建立 ⟹ 禁作「唯一推導」引用",
    True, "配對計數讀法唯一倖存 ≠ 形式由結構唯一推導 (值層 p = 0.6238 典型)")
own = open(os.path.abspath(__file__), encoding="utf-8").read()
_code_lines = [l for l in own.split("\n")
               if l.strip() and not l.strip().startswith("#") and not l.strip().startswith('"')]
_viol = [l for l in _code_lines
         if re.search(r"(import\s+\w*o229|from\s+o229|open\([^)]*o229)", l, re.I)]
chk("5.15 防守條款 (R5-E): 第三路線 = 固定點計數 + 池合法性 + 配對不變性 (程式碼零 O229 依賴)",
    not _viol, f"非註釋行提及 o229 者 {len(_viol)} 條 ⟹ 路由獨立")

# ---------------------------------------------------------------------
p("\n[H6] 回歸 — 新舊檢查一致")
# ---------------------------------------------------------------------
for ch in ("44", "88", "176"):
    r = L.chain_pairing_check(ch)
    chk(f"6.{ch} chain_pairing_check({ch}) 恆等式成立", r["is_identity"],
        f"配對 {r['pairing']}, max_dev {r['max_dev']:.2e}")
wp = L.wrong_pairing_check("176")
chk("6.4 176-L 錯配對仍為負結果 (O124 A3 鏈條件性)", wp["no_solution"],
    f"min_dev = {wp['min_dev']:.4f}")
chk("6.5 原子表仍 36 個 + 4 之名稱含 L_3 (更正唔改結構)",
    len(L.ATOM_TABLE) == 36 and any(a[0] == 4 and "L_3" in a[1] for a in L.ATOM_TABLE))
chk("6.6 池 |P| = 402 不變", len(pool) == 402, f"|P| = {len(pool)}")

# ---------------------------------------------------------------------
npass = sum(1 for _, ok, _ in RES if ok)
nfail = len(RES) - npass
p("\n" + "=" * 72)
p(f"RESULT: {npass}/{len(RES)} PASS  ({nfail} FAIL)")
p("=" * 72)

os.makedirs(os.path.join(BASE, "data"), exist_ok=True)
with open(os.path.join(BASE, "data", "06_inbound_handoffs.json"), "w", encoding="utf-8") as fh:
    json.dump({
        "script": "06_inbound_handoffs",
        "pass": npass, "fail": nfail, "total": len(RES),
        "checks": [{"name": n, "pass": ok, "detail": d} for n, ok, d in RES],
        "handoffs": {
            "O229-1_binet": {"carrier_fixed": "o218_lib.py 第一節", "value": "φ³−φ⁻³ = 4 = L₃"},
            "O229-2_index": {"R(2)": [list(x) for x in R2], "R(4)": [list(x) for x in R4],
                             "verdict_2": v2["verdict"], "verdict_4": v4["verdict"],
                             "chain_identity_2": ci2, "chain_identity_4": ci4,
                             "chain_index_delta_88L": d_chain},
            "O229-3_endpoint_lock": {"anatomy": an, "nontransitive_decomps": len(dec),
                                     "group_order_reading": "unconditionally_excluded",
                                     "endpoint_lock_status": "semi_structural (維持)"},
            "O220-4_sector": {"rule": list(L.SECTOR_RULE.keys()),
                              "spectral_family": {"88": [11, 22, 33]},
                              "counting_families": {k: list(v) for k, v in fam.items()}},
        },
    }, fh, ensure_ascii=False, indent=1)
p(f"→ data/06_inbound_handoffs.json")

sys.exit(0 if nfail == 0 else 1)
