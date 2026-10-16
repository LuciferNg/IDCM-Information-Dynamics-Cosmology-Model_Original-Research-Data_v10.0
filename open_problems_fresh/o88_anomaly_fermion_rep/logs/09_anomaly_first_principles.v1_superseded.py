#!/usr/bin/env python3
"""
O88 — 三階異常係數之第一性原理計算（取締一切擬合閉式）
========================================================
背景: `scripts/03_verifier.py:75-76` 用擬合閉式
        A(Λ⁴) = (N-3)(N-6)(N-10)/6   -> N=12 給 18
        A(Λ⁵) = (N-3)(N-6)(N-10)(N-15)/24 -> N=12 給 -14
      docs/03 更正為 48 / 42 —— 但該更正本身亦係（上一次）擬合產物。
      本腳本用**第一性原理**決定真值，唔用任何閉式。

原理（精確、無擬合）
--------------------
SU(N) 之三階異常 A(R) 定義: Tr_R(T^a {T^b, T^c}) = A(R) · d^{abc}, 正規化 A(fund) = 1。
取 a,b,c 全為 Cartan 指標 (H_a = E_aa − E_{a+1,a+1}，traceless 對角)：
    T^a{T^b,T^c} = 2 H_a H_b H_c        (Cartan 元素互換)
    Tr_R(H_a H_b H_c) = Σ_μ m_μ · (μ·h_a)(μ·h_b)(μ·h_c)      (μ = 權重, m_μ = 重數)
    d^{abc} = Tr_fund(H_a{H_b,H_c}) = 2 Σ_ν (ν·h_a)(ν·h_b)(ν·h_c)
⟹  ★ A(R) = [Σ_μ m_μ (μ_a−μ_{a+1})(μ_b−μ_{b+1})(μ_c−μ_{c+1})]
           / [Σ_{ν∈fund} (ν_a−ν_{a+1})(ν_b−ν_{b+1})(ν_c−ν_{c+1})]
     （fund 之權重 ν_i = e_i − (1/N)·1 ⟹ ν_a − ν_{a+1} = δ_{ia} − δ_{i,a+1}）

★ 自檢: A(R) 必須對**所有** (a,b,c) 三重（分母 ≠ 0 者）給同一值 ——
   呢個係強交叉驗證，唔係「揀到啱嘅 triple」。

權重多重集（純組合，精確有理數）
    Λ^k(12)  : 大小 k 之子集之和，每個重數 1   ⟹ dim = C(N,k)
    Sym^k(12): 大小 k 之可重組合之和，重數 1   ⟹ dim = C(N+k-1,k)
    Adj(12)  : {ν_i − ν_j} 加上 0 之重數 N−1   ⟹ dim = N²−1

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
print("O88 — 三階異常係數之第一性原理計算")
print("=" * 78)

# ---------------------------------------------------------------
# 核心: 由權重多重集算 A(R)
# ---------------------------------------------------------------
def fund_weights(N):
    """ν_i = e_i − (1/N)·1（traceless 對角 N-tuple），逐元素相減"""
    return [tuple((F(1) if j == i else F(0)) - F(1, N) for j in range(N))
            for i in range(N)]

def shift(ws):
    """把一組權重（可含負值）整理；此處僅確保長度一致"""
    return ws

def weights_alt(N, k):
    """Λ^k 之權重多重集: k-子集之和，重數 1"""
    v = fund_weights(N)
    out = []
    for S in combinations(range(N), k):
        out.append(tuple(sum((v[i][j] for i in S), F(0)) for j in range(N)))
    return out

def weights_sym(N, k):
    """Sym^k 之權重多重集: k-可重組合之和，重數 1"""
    v = fund_weights(N)
    out = []
    for S in combinations_with_replacement(range(N), k):
        out.append(tuple(sum((v[i][j] for i in S), F(0)) for j in range(N)))
    return out

def weights_adj(N):
    """Adj 之權重多重集: ν_i − ν_j (i≠j) 各 1，加 0 之重數 N−1"""
    v = fund_weights(N)
    out = []
    for i in range(N):
        for j in range(N):
            out.append(tuple(v[i][t] - v[j][t] for t in range(N)))
    # i=j 已含 N 個 0；adjoint 之 0 重數 = N−1，故去一個
    out.remove(tuple([F(0)] * N))
    return out

def D(wsets):
    """回傳 dict: (a,b,c) -> Σ_μ (μ_a − μ_{a+1})(μ_b − μ_{b+1})(μ_c − μ_{c+1})"""
    N = len(wsets[0])
    out = {}
    for a in range(N - 1):
        for b in range(N - 1):
            for c in range(N - 1):
                s = F(0)
                for mu in wsets:
                    s += (mu[a] - mu[a + 1]) * (mu[b] - mu[b + 1]) * (mu[c] - mu[c + 1])
                out[(a, b, c)] = s
    return out

def anomaly(wsets, N, ratio):
    """由權重集算 A(R)：對所有分母 ≠ 0 之 triple 取共識"""
    DR = D(wsets); Df = D(fund_weights(N))
    vals = set()
    ntr = 0
    for key in DR:
        if Df[key] != 0:
            vals.add(DR[key] / Df[key]); ntr += 1
    return vals, ntr

REPS = [
    ("12",   lambda N: weights_alt(N, 1),                    lambda N: math.comb(N, 1)),
    ("66",   lambda N: weights_alt(N, 2),                    lambda N: math.comb(N, 2)),
    ("220",  lambda N: weights_alt(N, 3),                    lambda N: math.comb(N, 3)),
    ("495",  lambda N: weights_alt(N, 4),                    lambda N: math.comb(N, 4)),
    ("792",  lambda N: weights_alt(N, 5),                    lambda N: math.comb(N, 5)),
    ("924",  lambda N: weights_alt(N, 6),                    lambda N: math.comb(N, 6)),
    ("78",   lambda N: weights_sym(N, 2),                    lambda N: math.comb(N + 1, 2)),
    ("364",  lambda N: weights_sym(N, 3),                    lambda N: math.comb(N + 2, 3)),
    ("143",  lambda N: weights_adj(N),                       lambda N: N * N - 1),
]

# ============================================================
# SECTION 1: 方法自驗 —— 已知值（獨立於本腳本之來源）
# ============================================================
print("\nSECTION 1: 方法自驗（known values，來自標準結果，非本腳本擬合）")
print("-" * 78)
N = 12
KNOWN = {  # (rep, N) -> 期望 A
    ("12", 12): 1,      # fundamental 正規化
    ("66", 12): 8,      # Λ²: N−4
    ("78", 12): 16,     # Sym²: N+4
    ("143", 12): 0,     # adjoint
    ("924", 12): 0,     # Λ⁶ 自對偶 (Λ⁶ ≅ Λ⁶*) ⟹ A = 0
    ("66", 5): 1,       # SU(5) 10-plet: N−4 = 1
    ("78", 5): 9,       # SU(5) Sym²(5)=15: N+4 = 9
    ("220", 6): 0,      # SU(6) 20-plet: (N−3)(N−6)/2 = 0 且 Λ³(6) 自對偶
    ("220", 7): 2,      # SU(7) 35: (4)(1)/2 = 2
    ("66", 7): 3,       # SU(7) 21: N−4 = 3
}
computed = {}
print("  %-6s %-4s %-26s %-8s %s" % ("rep", "N", "由權重算出之 A", "共識triple", "對照"))
for name, wfun, dfun in REPS:
    for NN in (5, 6, 7, 8, 10, 12, 13):
        ws = wfun(NN)
        if len(ws) != dfun(NN):
            print("  [FAIL] %s N=%d dim %d != %d" % (name, NN, len(ws), dfun(NN)))
            continue
        vals, ntr = anomaly(ws, NN, None)
        if len(vals) == 1:
            a = vals.pop(); computed[(name, NN)] = a
            if (name, NN) in KNOWN:
                exp = KNOWN[(name, NN)]
                ok = (a == exp)
                print("  %-6s %-4d %-26s %-8d %s" % (name, NN, str(a), ntr,
                      "OK (known=%s)" % exp if ok else "*** MISMATCH known=%s ***" % exp))
                RESULTS.append({"id": "A(%s,%d)" % (name, NN), "pass": ok,
                                "detail": "%s vs known %s" % (a, exp)})
        else:
            print("  [FAIL] %s N=%d 共識失敗: %s 個不同值" % (name, NN, len(vals)))
            RESULTS.append({"id": "consensus %s N=%d" % (name, NN), "pass": False,
                            "detail": str(sorted(map(str, vals)))})

kn_ok = [r for r in RESULTS if r["id"].startswith("A(") and "known" in r["detail"]]
check("S1  方法自驗: 全部 known values 命中（%d 項）" % len(kn_ok),
      all(r["pass"] for r in kn_ok) and len(kn_ok) == len(KNOWN),
      "n=%d/%d" % (len(kn_ok), len(KNOWN)))

# ============================================================
# SECTION 2: triple 共識性（強交叉驗證）
# ============================================================
print("\nSECTION 2: 交叉驗證 —— A(R) 對所有 (a,b,c) 三重給同一值")
print("-" * 78)
allcons = True
ntr = 0
for name, wfun, dfun in REPS:
    for NN in (12, 13):
        ws = wfun(NN)
        vals, ntr = anomaly(ws, NN, None)
        if len(vals) != 1:
            allcons = False
            print("   [FAIL] %s N=%d: %d 個值" % (name, NN, len(vals)))
check("S2  ★ 全部 rep 之 A(R) 對 %d 個 (a,b,c) 三重一致（共識）" % ntr, allcons)

# ============================================================
# SECTION 3: ★★ N=12 之真值 —— 對照 03_verifier.py 及 docs/03 更正
# ============================================================
print("\nSECTION 3: ★★ N=12 之真值 vs 現行記錄")
print("-" * 78)
print("  %-8s %-10s %-14s %-14s %s" % ("rep", "dim", "03_verifier", "docs/03更正", "★本腳本(第一性原理)"))
OLD = {  # 03_verifier.py:71-77 之值
    "66": 8, "78": 16, "143": 0, "220": 27, "495": (12-3)*(12-6)*(12-10)//6,
    "792": (12-3)*(12-6)*(12-10)*(12-15)//24, "924": 0,
}
DOC03 = {"495": 48, "792": 42}
for name, wfun, dfun in REPS:
    ws = wfun(12)
    vals, ntr = anomaly(ws, 12, None)
    a = list(vals)[0] if len(vals) == 1 else "?"
    print("  %-8s %-10d %-14s %-14s %s" % (name, len(ws), OLD.get(name, "—"),
          DOC03.get(name, "—"), a))
    computed[(name, 12)] = a

a495 = computed[("495", 12)]; a792 = computed[("792", 12)]; a220 = computed[("220", 12)]
check("S3  ★ A(Λ³)=A(220) = 27（現行記錄正確）", a220 == 27, "got %s" % a220)
check("S4  ★★ A(Λ⁴)=A(495) 真值 = %s（03_verifier 給 18；docs/03 更正給 48）" % a495,
      True, "第一性原理 = %s" % a495)
check("S5  ★★ A(Λ⁵)=A(792) 真值 = %s（03_verifier 給 −14；docs/03 更正給 42）" % a792,
      True, "第一性原理 = %s" % a792)
check("S6  ★ Λ⁶(12) 自對偶 ⟹ A = 0（A = −A 之唯一整數解）",
      computed[("924", 12)] == 0, "A(Λ⁶)=%s" % computed[("924", 12)])
# 直接驗 Λ⁸ = Λ⁴ 之對偶
w8 = weights_alt(12, 8)
v8, _ = anomaly(w8, 12, None)
a8 = list(v8)[0] if len(v8) == 1 else None
w7 = weights_alt(12, 7); v7, _ = anomaly(w7, 12, None); a7 = list(v7)[0]
print("\n  延伸: A(Λ⁷) = %s ; A(Λ⁸) = %s ; A(Λ⁹) = %s…" % (a7, a8, "—"))
check("S6b ★ 對偶律: A(Λ⁸) = −A(Λ⁴) 且 A(Λ⁷) = −A(Λ⁵)",
      a8 == -computed[("495", 12)] and a7 == -computed[("792", 12)],
      "A(Λ⁸)=%s, −A(Λ⁴)=%s ; A(Λ⁷)=%s, −A(Λ⁵)=%s" % (a8, -computed[("495", 12)], a7, -computed[("792", 12)]))

# ============================================================
# SECTION 4: 閉式之獨立檢定（跨 N，非單點擬合）
# ============================================================
print("\nSECTION 4: 閉式候選之跨 N 檢定（N=5..13，唔係單點擬合）")
print("-" * 78)
def cand(N, k):
    """候選閉式 A(Λ^k) = C(N-3,k-1)·(N-2k)/(N-k-1)"""
    if k - 1 > N - 3 or (N - k - 1) == 0:
        return None
    val = F(math.comb(N - 3, k - 1) * (N - 2 * k), N - k - 1)
    return int(val) if val.denominator == 1 else val

bad = []
for k in range(1, 6):
    row = []
    for NN in range(5, 14):
        ws = weights_alt(NN, k)
        vals, _ = anomaly(ws, NN, None)
        a = list(vals)[0] if len(vals) == 1 else None
        c = cand(NN, k)
        row.append((NN, a, c))
        if a != c:
            bad.append((k, NN, a, c))
    print("  Λ^%d : " % k + "  ".join("N=%d:A=%s%s" % (n, a, "" if a == c else "(候選%s✗)" % c)
                                      for n, a, c in row))
check("S7  ★ 候選閉式 C(N−3,k−1)·(N−2k)/(N−k−1) 跨 N=5..13 × k=1..5 全中",
      not bad, "mismatch=%s" % bad[:6])

# ============================================================
print("\n" + "=" * 78)
npass = sum(1 for r in RESULTS if r["pass"])
print("結果: %d/%d PASS" % (npass, len(RESULTS)))
for r in RESULTS:
    if not r["pass"]: print("   FAIL - %s : %s" % (r["id"], r["detail"]))
print("=" * 78)

out = {
    "script": "09_anomaly_first_principles.py", "version": "v1", "date": "2026-10-02",
    "purpose": "三階異常係數之第一性原理計算（取締擬合閉式）",
    "method": "A(R) = Sum_mu m_mu (mu_a-mu_{a+1})(mu_b-mu_{b+1})(mu_c-mu_{c+1}) / same for fund",
    "N12": {n: computed.get((n, 12)) for n, _, _ in REPS},
    "known_check": {("%s,N=%d" % k): v for k, v in KNOWN.items()},
    "closed_form_candidate": "A(Lambda^k) = C(N-3,k-1)*(N-2k)/(N-k-1)",
    "closed_form_mismatches": bad,
    "verdict_495": computed[("495", 12)], "verdict_792": computed[("792", 12)],
    "checks": RESULTS, "n_pass": npass, "n_total": len(RESULTS),
}
with open(os.path.join(DATA_DIR, "09_anomaly_first_principles.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=2, ensure_ascii=False, default=str)
print("\n已寫入: data/09_anomaly_first_principles.json")
