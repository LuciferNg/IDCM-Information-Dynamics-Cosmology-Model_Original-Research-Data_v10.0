#!/usr/bin/env python3
"""
O88/PD — 三階異常係數之第一性原理計算（全整數，取締一切擬合閉式）
==================================================================
背景: `scripts/03_verifier.py:75-76` 用擬合閉式
        A(Λ⁴) = (N-3)(N-6)(N-10)/6        -> N=12 給 18
        A(Λ⁵) = (N-3)(N-6)(N-10)(N-15)/24 -> N=12 給 −14
      docs/03 更正為 48 / 42 —— 但該更正本身亦係（上一次）擬合之產物。
      本腳本**唔用任何閉式**，由權重結構直接決定真值。

修訂記錄
   v1（`logs/09_anomaly_first_principles.v1_superseded.py`，sha256 e489747064a0a9b3…）
      用 Fraction 逐元素計權重；Pyright 抓到 tuple 相減 & ntr 未綁定兩處 bug，且太慢（>7 min）。
   v2.1（本檔）空洞修復: `consensus_A` 對空權重集改為 **raise**；
      REPS 迴圈對 `dim == 0`（唔存在之 rep，如 Λ⁶(SU(5))）明確跳過。
      ★ 觸發源: 遲到背景通知（proc_dc340220815c）之 v1 traceback —— v1 在此位置
        IndexError crash，v2 曾靜靜回 `A = 0`（更差之 silent 行為）。
   v2（logs/09_anomaly_first_principles.v2_superseded.py）關鍵簡化：t^μ_a := μ_a − μ_{a+1} ∈ ℤ
      （基本權重 ν_i = e_i − (1/N)·1 ⟹ t^{ν_i}_a = δ_{ia} − δ_{i,a+1} ∈ {−1,0,1}）
      ⟹ 全整數運算，無 Fraction，快 ~10³ 倍。

原理（精確，無擬合）
--------------------
SU(N) 之三階異常: Tr_R(T^a {T^b,T^c}) = A(R)·d^{abc}, 正規化 A(fund) = 1。
取 a,b,c 全為 Cartan 指標 (H_a = E_aa − E_{a+1,a+1})：
    Tr_R(H_a{H_b,H_c}) = 2 Tr_R(H_aH_bH_c) = 2 Σ_μ m_μ · t^μ_a t^μ_b t^μ_c
    d^{abc}            = 2 Σ_{ν∈fund} t^ν_a t^ν_b t^ν_c
⟹  ★ A(R) = [Σ_μ m_μ t^μ_a t^μ_b t^μ_c] / [Σ_{ν∈fund} t^ν_a t^ν_b t^ν_c]

權重（純組合）: Λ^k = k-子集之和（重數 1）；Sym^k = k-可重組合之和（重數 1）；
               Adj = {ν_i − ν_j} ∪ {0 之重數 N−1}。

★ 自檢（強交叉驗證）: A(R) 必須對**所有** (a,b,c) 三重（分母 ≠ 0 者）給同一值 ——
   「共識」即係驗證，唔係「揀到啱嘅 triple」。

執行: /usr/bin/python3 scripts/09_anomaly_first_principles.py
"""

import os, json, math
from fractions import Fraction as F
from itertools import combinations, combinations_with_replacement

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE, "logs"); DATA_DIR = os.path.join(BASE, "data")
os.makedirs(LOG_DIR, exist_ok=True); os.makedirs(DATA_DIR, exist_ok=True)

RESULTS = []
def check(name, cond, detail=""):
    RESULTS.append({"id": name, "pass": bool(cond), "detail": detail})
    print("  [%s] %s %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)

print("=" * 78)
print("O88 — 三階異常係數之第一性原理計算（全整數）")
print("=" * 78)

# ---------------------------------------------------------------
def tvec_from_subset(N, S):
    """t_a = #{a∈S} − #{a+1∈S}, a = 0..N−2"""
    cnt = [0] * N
    for i in S: cnt[i] += 1
    return tuple(cnt[a] - cnt[a + 1] for a in range(N - 1))

def tvecs_alt(N, k):
    return [tvec_from_subset(N, S) for S in combinations(range(N), k)]

def tvecs_sym(N, k):
    return [tvec_from_subset(N, S) for S in combinations_with_replacement(range(N), k)]

def tvecs_adj(N):
    out = []
    for i in range(N):
        for j in range(N):
            out.append(tuple((1 if a == i else 0) - (1 if a + 1 == i else 0)
                             - ((1 if a == j else 0) - (1 if a + 1 == j else 0))
                             for a in range(N - 1)))
    out.remove(tuple([0] * (N - 1)))      # adjoint 之 0 重數 = N−1
    return out

def tvecs_fund(N):
    return [tuple((1 if a == i else 0) - (1 if a + 1 == i else 0) for a in range(N - 1))
            for i in range(N)]

Df_cache = {}
def denom_table(N):
    if N not in Df_cache:
        tf = tvecs_fund(N)
        Df_cache[N] = {(a, b, c): sum(t[a] * t[b] * t[c] for t in tf)
                       for a in range(N - 1) for b in range(N - 1) for c in range(N - 1)}
    return Df_cache[N]

def consensus_A(tvecs, N):
    # ★ 2026-10-02 空洞修復: 空權重集 = 該 N 之下 rep 唔存在，**唔可以**靜靜回 A = 0。
    #   （v1 在此位置 IndexError crash；v2 曾靜靜回 0 ⟹ silent 缺陷，由遲到背景通知之
    #    v1 traceback 揭示；見 docs/08 §8）
    if not tvecs:
        raise ValueError("consensus_A: 空權重集（該 N 之下 rep 唔存在）—— 呼叫者須自行跳過")
    Df = denom_table(N)
    vals = set(); ntr = 0
    for key, den in Df.items():
        if den == 0: continue
        num = sum(t[key[0]] * t[key[1]] * t[key[2]] for t in tvecs)
        vals.add(F(num, den)); ntr += 1
    return vals, ntr

REPS = [
    ("12",   lambda N: tvecs_alt(N, 1),  lambda N: math.comb(N, 1)),
    ("66",   lambda N: tvecs_alt(N, 2),  lambda N: math.comb(N, 2)),
    ("220",  lambda N: tvecs_alt(N, 3),  lambda N: math.comb(N, 3)),
    ("495",  lambda N: tvecs_alt(N, 4),  lambda N: math.comb(N, 4)),
    ("792",  lambda N: tvecs_alt(N, 5),  lambda N: math.comb(N, 5)),
    ("924",  lambda N: tvecs_alt(N, 6),  lambda N: math.comb(N, 6)),
    ("78",   lambda N: tvecs_sym(N, 2),  lambda N: math.comb(N + 1, 2)),
    ("364",  lambda N: tvecs_sym(N, 3),  lambda N: math.comb(N + 2, 3)),
    ("143",  lambda N: tvecs_adj(N),     lambda N: N * N - 1),
]

# ============================================================
print("\nSECTION 1: 方法自驗（known values 來自標準結果，非本腳本擬合）")
print("-" * 78)
KNOWN = {
    ("12", 12): 1, ("66", 12): 8, ("78", 12): 16, ("143", 12): 0, ("924", 12): 0,
    ("66", 5): 1, ("78", 5): 9, ("220", 6): 0, ("220", 7): 2, ("66", 7): 3,
    ("143", 7): 0, ("78", 6): 10, ("143", 5): 0,
}
NS = (5, 6, 7, 8, 10, 12, 13)
computed = {}
print("  %-6s %-5s %-10s %-11s %s" % ("rep", "N", "A(R)", "共識triple", "對照 known"))
skipped = []
for name, wfun, dfun in REPS:
    for NN in NS:
        if dfun(NN) == 0:                      # ★ rep 唔存在（如 Λ⁶(SU(5)): C(5,6)=0）
            skipped.append((name, NN)); continue
        tv = wfun(NN)
        if len(tv) != dfun(NN):
            print("  [FAIL] %s N=%d dim %d != %d" % (name, NN, len(tv), dfun(NN))); continue
        vals, ntr = consensus_A(tv, NN)
        if len(vals) == 1:
            a = vals.pop(); computed[(name, NN)] = a
            if (name, NN) in KNOWN:
                exp = KNOWN[(name, NN)]; ok = (a == exp)
                print("  %-6s %-5d %-10s %-11d %s" % (name, NN, str(a), ntr,
                      "OK" if ok else "*** MISMATCH known=%s ***" % exp))
                RESULTS.append({"id": "A(%s,N=%d) vs known" % (name, NN), "pass": ok,
                                "detail": "%s vs %s" % (a, exp)})
        else:
            print("  [FAIL] %s N=%d 共識失敗: %s" % (name, NN, sorted(map(str, vals))))

# 空洞修復之實質檢查（唔可以恆真）
_expected_skip = sorted([(n, NN) for n, _, df in REPS for NN in NS if df(NN) == 0])
try:
    consensus_A([], 5); _raised = False
except ValueError:
    _raised = True
check("S0  ★★ 空洞修復: ① consensus_A([]) 改為 raise %s；② 唔存在之 rep 明確跳過 %s（期望 %s）"
      % ("✓" if _raised else "✗", skipped, _expected_skip),
      _raised and sorted(skipped) == _expected_skip,
      "skipped=%s ; expected=%s ; raise=%s" % (skipped, _expected_skip, _raised))

kn = [r for r in RESULTS if "vs known" in r["id"]]
check("S1  方法自驗: 全部 known values 命中（%d 項）" % len(kn),
      all(r["pass"] for r in kn) and len(kn) == len(KNOWN), "n=%d/%d" % (len(kn), len(KNOWN)))

# ============================================================
print("\nSECTION 2: 交叉驗證 —— A(R) 對所有 (a,b,c) 三重一致")
print("-" * 78)
allcons = True; ntr_max = 0
for name, wfun, dfun in REPS:
    for NN in (12, 13):
        tv = wfun(NN); vals, ntr = consensus_A(tv, NN)
        ntr_max = max(ntr_max, ntr)
        if len(vals) != 1:
            allcons = False; print("   [FAIL] %s N=%d: %d 個值" % (name, NN, len(vals)))
check("S2  ★ 全部 rep 之 A(R) 對最多 %d 個 (a,b,c) 三重一致（共識）" % ntr_max, allcons)

# ============================================================
print("\nSECTION 3: ★★ N=12 之真值 vs 現行記錄")
print("-" * 78)
OLD = {"66": 8, "78": 16, "143": 0, "220": 27,
       "495": (12 - 3) * (12 - 6) * (12 - 10) // 6,
       "792": (12 - 3) * (12 - 6) * (12 - 10) * (12 - 15) // 24, "924": 0}
DOC03 = {"495": 48, "792": 42}
print("  %-8s %-8s %-14s %-13s %s" % ("rep", "dim", "03_verifier", "docs/03更正", "★第一性原理"))
for name, wfun, dfun in REPS:
    tv = wfun(12); vals, ntr = consensus_A(tv, 12)
    a = list(vals)[0] if len(vals) == 1 else "?"
    print("  %-8s %-8d %-14s %-13s %s" % (name, len(tv), OLD.get(name, "—"), DOC03.get(name, "—"), a))
    if len(vals) == 1: computed[(name, 12)] = a

a495 = computed[("495", 12)]; a792 = computed[("792", 12)]
check("S3  ★ A(Λ³)=A(220) = 27（現行記錄正確）", computed[("220", 12)] == 27,
      "got %s" % computed[("220", 12)])
check("S4  ★ A(Λ⁶)=A(924) = 0（自對偶 ⟹ A = −A 之唯一整數解）", computed[("924", 12)] == 0,
      "got %s" % computed[("924", 12)])

ext = {}
for k in (7, 8, 9, 10, 11):
    v, _ = consensus_A(tvecs_alt(12, k), 12)
    ext["Λ^%d" % k] = list(v)[0] if len(v) == 1 else "?"
print("\n  延伸: " + "  ".join("%s=%s" % (k, v) for k, v in ext.items()))
check("S5  ★ 對偶律 A(Λ^k) = −A(Λ^{N−k})（N=12, k=4..11）",
      ext["Λ^8"] == -a495 and ext["Λ^7"] == -a792
      and ext["Λ^9"] == -computed[("220", 12)] and ext["Λ^10"] == -computed[("66", 12)]
      and ext["Λ^11"] == -computed[("12", 12)],
      "Λ⁸=%s vs −Λ⁴=%s ; Λ⁷=%s vs −Λ⁵=%s ; Λ⁹=%s vs −Λ³=%s ; Λ^10=%s vs −Λ²=%s ; Λ^11=%s vs −Λ¹=%s"
      % (ext["Λ^8"], -a495, ext["Λ^7"], -a792, ext["Λ^9"], -computed[("220", 12)],
         ext["Λ^10"], -computed[("66", 12)], ext["Λ^11"], -computed[("12", 12)]))

# ============================================================
print("\nSECTION 4: 閉式候選之跨 N 檢定（N=5..13 × k=1..5，非單點擬合）")
print("-" * 78)
def cand(N, k):
    if k - 1 > N - 3 or (N - k - 1) <= 0: return None
    v = F(math.comb(N - 3, k - 1) * (N - 2 * k), N - k - 1)
    return int(v) if v.denominator == 1 else v

bad = []; table = {}; outside = []
for k in range(1, 6):
    row = []
    for NN in range(5, 14):
        tv = tvecs_alt(NN, k)
        if len(tv) > 3000: continue
        vals, _ = consensus_A(tv, NN)
        a = list(vals)[0] if len(vals) == 1 else None
        c = cand(NN, k)
        table["k=%d,N=%d" % (k, NN)] = str(a)
        row.append((NN, a, c))
        if c is None:
            outside.append((k, NN, str(a)))     # 候選閉式定義域外（非值不符）
        elif a != c:
            bad.append((k, NN, str(a), str(c)))
    print("  Λ^%d : " % k + "  ".join("N=%d:%s%s" % (n, a, "" if a == c else "(候選%s✗)" % c)
                                      for n, a, c in row))
check("S6  ★ 候選閉式 C(N−3,k−1)·(N−2k)/(N−k−1) 於其定義域內全中（%d 點）" % (len(table) - len(outside)),
      not bad, "值不符=%s ; 定義域外=%s" % (bad[:6], outside))
print("  ⚠️ 候選閉式**定義域受限**（%s 等點無定義）⟹ 唔可用作核對器；核對器須用第一性原理。"
      % outside)

print("\n  ── 現行 03_verifier 閉式之檢定（A(Λ⁴)）──")
for NN in (7, 8, 10, 12, 13):
    v4, _ = consensus_A(tvecs_alt(NN, 4), NN); a4 = list(v4)[0]
    old4 = (NN - 3) * (NN - 6) * (NN - 10) // 6
    print("     N=%-3d 真值=%-5s 現行閉式=%-5s %s" % (NN, a4, old4, "OK" if a4 == old4 else "✗"))
    if NN == 12:
        RESULTS.append({"id": "★ 現行 03_verifier Λ⁴ 閉式缺陷確認", "pass": (a4 != old4),
                        "detail": "N=12 真值 %s vs 現行 %s" % (a4, old4)})

# ============================================================
print("\n" + "=" * 78)
npass = sum(1 for r in RESULTS if r["pass"])
print("結果: %d/%d PASS" % (npass, len(RESULTS)))
for r in RESULTS:
    if not r["pass"]: print("   FAIL - %s : %s" % (r["id"], r["detail"]))
print("=" * 78)

out = {
    "script": "09_anomaly_first_principles.py", "version": "v2.1-int-holefix", "date": "2026-10-02",
    "supersedes": {"file": "logs/09_anomaly_first_principles.v1_superseded.py",
                   "sha256_prefix": "e489747064a0a9b3"},
    "purpose": "三階異常係數之第一性原理計算（全整數，取締擬合閉式）",
    "method": "A(R) = Sum_mu m_mu t_a t_b t_c / Sum_fund t_a t_b t_c,  t_a = mu_a - mu_{a+1} (integer)",
    "N12": {n: str(computed.get((n, 12))) for n, _, _ in REPS},
    "nonexistent_reps_skipped": [list(x) for x in skipped],
    "N12_extended": ext,
    "verdict_495": str(a495), "verdict_792": str(a792),
    "old_03verifier": {"495": OLD["495"], "792": OLD["792"]},
    "doc03_correction": DOC03,
    "closed_form_candidate": "A(Lambda^k) = C(N-3,k-1)*(N-2k)/(N-k-1)",
    "closed_form_mismatches": bad, "closed_form_outside_domain": outside, "table": table,
    "checks": RESULTS, "n_pass": npass, "n_total": len(RESULTS),
}
with open(os.path.join(DATA_DIR, "09_anomaly_first_principles.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=2, ensure_ascii=False, default=str)
print("\n已寫入: data/09_anomaly_first_principles.json")
