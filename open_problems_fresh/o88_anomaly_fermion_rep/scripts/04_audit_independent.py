#!/usr/bin/env python3
"""
O88 — scripts/04_audit_independent.py   (獨立審計器 / INDEPENDENT AUDITOR)
=========================================================================
目的：唔 import scripts/01–03 任何一行，用**唔同演算法**由原始定義重算 O88
      所有 headline 數字，並對已記錄值逐項核對。

獨立演算法（權重法 / weight method）—— 與 scripts/01 的「封閉式公式」路線不同：
  SU(N) 嘅立方異常係數（normalized A(□) = 1）等於
        A(R) = [ Σ_{λ∈R} Σ_{i=1..N} λ_i³ ] / [ Σ_{λ∈□} Σ_i λ_i³ ]
  其中 λ 取標準正交歸一化權重（Σ_i λ_i = 0）。
  對 fundamental：Σ_{λ∈□}Σλ³ = (N−1)(N−2)/N。
  對 Λ^k：λ 為 k 個 1 與 N−k 個 0 減去 k/N：
        Σλ³ = k((N−k)/N)³ + (N−k)(−k/N)³
  ⟹ A(Λ^k) = C(N,k)·k(N−k)(N−2k) / [N(N−1)(N−2)]

⚠️ 本檢查為「審計員有罪推定」：FAIL 先懷疑 check 設計，後懷疑 doc。
⚠️ 唔准 import 01/02/03。零共享函數 = 零共享 bug。
"""

import math
import os
import json
from fractions import Fraction as F

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "data", "04_audit_independent.json")

N = 12
B, N_gen, K_tree, N_d, L_5 = 4, 3, 33, 44, 11

results = []
def chk(tag, claim, got, want, tol=None):
    """tol=None ⟹ 精確比較（int/rational）；否則絕對容差。"""
    if tol is None:
        ok = (got == want)
    else:
        ok = abs(float(got) - float(want)) <= tol
    results.append({"tag": tag, "claim": claim, "got": str(got),
                    "want": str(want), "pass": bool(ok),
                    "vacuous": False})
    print("  [%s] %-10s %s  (got=%s want=%s)" % (
        "PASS" if ok else "FAIL", tag, claim, got, want))
    return ok


# ============================================================
# 段 A — SU(N) 立方異常係數（權重法，獨立於封閉式）
# ============================================================
print("=" * 74)
print("段 A — SU(N) 立方異常係數：權重法（獨立演算法）")
print("=" * 74)

def sum_cube_per_weight(ones, N):
    """權重 λ = (1...1 [k 個], 0...0) − (k/N)(1,...,1)；回傳 Σ_i λ_i³。"""
    k = ones
    pos = (1 - F(k, N)) ** 3          # k 個分量
    neg = (-F(k, N)) ** 3             # N−k 個分量
    return F(k) * pos + F(N - k) * neg

def A_fund_denom(N):
    """Σ_{λ∈□} Σ_i λ_i³ = (N−1)(N−2)/N。"""
    return F((N - 1) * (N - 2), N)

def A_weight_method(k, N):
    """A(Λ^k) 由權重法直接求和（唔用 C(N,k)·k(N−k)(N−2k)/[N(N−1)(N−2)] 封閉式）。"""
    s = sum_cube_per_weight(k, N)
    return F(math.comb(N, k)) * s / A_fund_denom(N)

def A_closed(k, N):
    """權重法推導出嘅封閉式（A2 交叉核用）。"""
    return F(math.comb(N, k) * k * (N - k) * (N - 2 * k), N * (N - 1) * (N - 2))

print("\n  權重法 vs 封閉式（雙路徑互證）:")
for k in range(1, 6):
    a1, a2 = A_weight_method(k, N), A_closed(k, N)
    print("    Λ^%-2d  weight=%s  closed=%s  %s" % (k, a1, a2, "OK" if a1 == a2 else "MISMATCH"))
    assert a1 == a2

print("\n  A(□) 歸一化檢查（權重法必須給 1）:", A_weight_method(1, N))
chk("A0", "A(fund) = 1（歸一化自洽）", A_weight_method(1, N), F(1))

# 已記錄值（scripts/01 + data/01 + docs）
REC_A = {
    "12":   (1, "fundamental"),
    "12bar": (-1, "anti-fundamental"),
    "66":   (8, "Lambda^2"),
    "78":   (16, "Sym^2"),
    "143":  (0, "adjoint"),
    "220":  (27, "Lambda^3"),
    "495":  (18, "Lambda^4"),      # ← 記錄值
    "792":  (-14, "Lambda^5"),     # ← 記錄值
    "924":  (0, "Lambda^6 (self-dual)"),
}

print("\n  === 逐項核對：記錄值 vs 權重法 ===")
mismatch = []
# 12 / 12bar
chk("A1", "A(12) = 1", A_weight_method(1, N), F(REC_A["12"][0]))
chk("A2", "A(12bar) = -1", -A_weight_method(1, N), F(REC_A["12bar"][0]))
# 66 = Λ²
chk("A3", "A(66)=A(Λ²) = 8", A_weight_method(2, N), F(REC_A["66"][0]))
# 220 = Λ³
chk("A4", "A(220)=A(Λ³) = 27", A_weight_method(3, N), F(REC_A["220"][0]))
# 924 = Λ⁶
chk("A5", "A(924)=A(Λ⁶) = 0", A_weight_method(6, N), F(REC_A["924"][0]))
# 495 = Λ⁴  ← 關鍵
got4 = A_weight_method(4, N)
ok4 = chk("A6", "A(495)=A(Λ⁴) 記錄 18", got4, F(REC_A["495"][0]))
if not ok4:
    mismatch.append(("495 / Λ4", REC_A["495"][0], int(got4)))
# 792 = Λ⁵  ← 關鍵
got5 = A_weight_method(5, N)
ok5 = chk("A7", "A(792)=A(Λ⁵) 記錄 -14", got5, F(REC_A["792"][0]))
if not ok5:
    mismatch.append(("792 / Λ5", REC_A["792"][0], int(got5)))

print("\n  === -c 校正 tag：記錄值錯之兩項，改斷言權重法正解 ===")
chk("A6c", "A(495)=A(Λ⁴) = 48（正解，取代記錄 18）", A_weight_method(4, N), F(48))
chk("A7c", "A(792)=A(Λ⁵) = 42（正解，取代記錄 -14）", A_weight_method(5, N), F(42))

print("\n  === 對稱性 A(Λ^k) = −A(Λ^(N−k))（獨立恆等式核）===")
for k in range(1, 6):
    lhs, rhs = A_weight_method(k, N), -A_weight_method(N - k, N)
    chk("A8.k%d" % k, "A(Λ^%d) = -A(Λ^%d)" % (k, N - k), lhs, rhs)

print("\n  === A(adjoint) = 0（權重法：根之立方和逐條相消）===")
adj_sum = sum(F(1) ** 3 + F(-1) ** 3 for _ in range(N * (N - 1)))
chk("A9", "A(adj) = 0", adj_sum, F(0))

print("\n  === A(Sym²) = N+4（權重法：對角 + 非對角兩軌道）===")
diag = F(N) * (F(2 * (N - 1), N) ** 3 + F(N - 1) * (F(-2, N) ** 3))
offd = F(math.comb(N, 2)) * sum_cube_per_weight(2, N)
sym2 = (diag + offd) / A_fund_denom(N)
chk("A10", "A(Sym²) = N+4 = 16", sym2, F(N + 4))

# 張量積和律（獨立重算）
print("\n  === 張量積異常和律 ===")
chk("A11", "A(12⊗12) = dim·A + dim·A = 24 = A(66)+A(78)",
    F(N) * 1 + F(N) * 1, F(REC_A["66"][0] + REC_A["78"][0]))
# A(R1⊗R2) = dim(R2)·A(R1) + dim(R1)·A(R2)；R1=12, R2=66
dim66 = math.comb(N, 2)
chk("A12", "A(12⊗66) = dim(66)·A(12) + dim(12)·A(66) = 66·1 + 12·8 = 162",
    F(dim66) * F(1) + F(N) * F(REC_A["66"][0]), F(162))
chk("A13", "A(12⊗12bar) = 0（1 ⊕ 143）",
    F(N) * 1 + F(N) * (-1), F(0))

# ============================================================
# 段 B — 異常自由組合（結論層：只用 A(12), A(12bar)）
# ============================================================
print()
print("=" * 74)
print("段 B — 異常自由組合")
print("=" * 74)
chk("B1", "3×(12⊕12bar) 異常自由：3(+1)+3(-1) = 0", F(3) * 1 + F(3) * (-1), F(0))
chk("B2", "dim 3×(12⊕12bar) = 72", F(3) * N + F(3) * N, F(72))
chk("B3", "dim 2×(12⊕12bar) = 48（最小異常自由）", F(2) * N + F(2) * N, F(48))
chk("B4", "72 - 48 = 24 個 vector-like 配對", F(72) - F(48), F(24))

# ============================================================
# 段 C — SU(4)×SU(3) 分解（維度守恒，獨立算）
# ============================================================
print()
print("=" * 74)
print("段 C — SU(4)×SU(3) 分支規則維度守恒")
print("=" * 74)
chk("C1", "12 = (4,3)：4×3 = 12", F(4) * F(3), F(N))
chk("C2", "66 = (6,6)⊕(10,3̄)：36+30 = 66", F(6) * F(6) + F(10) * F(3), F(66))
chk("C3", "78 = (10,6)⊕(6,3̄)：60+18 = 78", F(10) * F(6) + F(6) * F(3), F(78))
chk("C4", "143 = (15,1)⊕(1,8)⊕(15,8)：15+8+120 = 143",
    F(15) * F(1) + F(1) * F(8) + F(15) * F(8), F(143))
chk("C5", "143 = dim(SU(12)) = 12²−1", F(N * N - 1), F(143))
# 143 由 12⊗12bar ⊖ 1 獨立重算
chk("C6", "12⊗12bar = 144 = 1 ⊕ 143", F(N) * F(N), F(1) + F(143))

# ============================================================
# 段 D — SM 費米子內容量（逐態獨立點算）
# ============================================================
print()
print("=" * 74)
print("段 D — SM 費米子內容（逐態點算，非抄表）")
print("=" * 74)
# 逐態：Q_L(3色×2弱) + u^c(3) + d^c(3) + L_L(2) + e^c(1) + ν^c(1)
states = [
    ("Q_L  = (3,2)_{1/6}", 3 * 2),
    ("u^c  = (3bar,1)_{-2/3}", 3),
    ("d^c  = (3bar,1)_{1/3}", 3),
    ("L_L  = (1,2)_{-1/2}", 2),
    ("e^c  = (1,1)_{1}", 1),
    ("nu^c = (1,1)_{0}", 1),
]
tot = 0
for nm, m in states:
    tot += m
    print("    %-28s %d" % (nm, m))
chk("D1", "每代 SM Weyl 數 = 16", F(tot), F(16))
chk("D2", "3 代 SM Weyl 數 = 48", F(3 * tot), F(48))
chk("D3", "12 提供 9 夸克 + 3 輕子 = 12（左手徵）", F(9) + F(3), F(12))
chk("D4", "12bar 提供 9 夸克 + 3 輕子 = 12（右手徵）", F(9) + F(3), F(12))

# ============================================================
# 段 E — IDCM 身份（由 0,1 原始結構常數起算）
# ============================================================
print()
print("=" * 74)
print("段 E — IDCM 身份")
print("=" * 74)
# N_d = B × rank, rank = L_5 = 11 ⟹ N_d = 44
chk("E1", "N_d = B·L_5 = 4×11 = 44", F(B * L_5), F(N_d))
chk("E2", "N = B·N_gen = 4×3 = 12", F(B * N_gen), F(N))
chk("E3", "N = L_5 + 1 = 12", F(L_5 + 1), F(N))
chk("E4", "h11 = 3N = 36", F(3 * N), F(36))
chk("E5", "h11 = K_tree + N_gen = 33+3 = 36", F(K_tree + N_gen), F(36))
chk("E6", "dim 3×(12⊕12bar) = 2·h11 = 72", F(2 * 36), F(72))
chk("E7", "dim Λ²(12) = 66 = 2·K_tree", F(2 * K_tree), F(66))
chk("E8", "dim(SU(12)) = 143 = B·K_tree + L_5 = 4·33+11",
    F(B * K_tree + L_5), F(143))

# ============================================================
# 段 F — 空洞檢查偵測（PASS 計數 ≠ 驗證強度）
# ============================================================
print()
print("=" * 74)
print("段 F — 原 03_verifier.py 之空洞檢查偵測（AST 掃描）")
print("=" * 74)
import ast
vp = os.path.join(BASE, "scripts", "03_verifier.py")
src = open(vp, encoding="utf-8").read()
tree = ast.parse(src)
vacuous, real, looped = [], [], []
def _walk_checks(node, in_loop):
    for child in ast.iter_child_nodes(node):
        is_loop = in_loop or isinstance(child, (ast.For, ast.While))
        if isinstance(child, ast.Call) and getattr(child.func, "id", None) == "check":
            nm = child.args[0].value if child.args and isinstance(child.args[0], ast.Constant) else "<expr>"
            a1 = child.args[1] if len(child.args) > 1 else None
            if isinstance(a1, ast.Constant) and a1.value is True:
                (looped if is_loop else vacuous).append(nm)
            else:
                real.append(nm)
        _walk_checks(child, is_loop)
_walk_checks(tree, False)
n_vac = len(vacuous) + len(looped)
print("  check() 呼叫點（AST）: %d" % (len(vacuous) + len(looped) + len(real)))
print("  其中 check(..., True) 空洞斷言: %d（循環內 %d、循環外 %d）" % (n_vac, len(looped), len(vacuous)))
for nm in vacuous: print("     [VACUOUS  ] %s" % nm)
for nm in looped:  print("     [VACUOUS×L] %s" % nm)
print("  真斷言（有表達式）: %d" % len(real))
print("  ⟹ 空洞比例 = %d/%d = %.0f%%" % (n_vac, n_vac + len(real),
                                          100.0 * n_vac / (n_vac + len(real))))
results.append({"tag": "F1", "claim": "03_verifier 空洞斷言計數",
                "got": n_vac, "want": None, "pass": True, "vacuous": True,
                "note": "報告項（唔計入分母）"})
results.append({"tag": "F2", "claim": "03_verifier 真斷言計數",
                "got": len(real), "want": None, "pass": True, "vacuous": True,
                "note": "報告項（唔計入分母）"})

# ============================================================
# 段 G — 記錄值 vs 權重法 全表（新正典值）
# ============================================================
print()
print("=" * 74)
print("段 G — SU(12) 異常係數：新正典全表")
print("=" * 74)
canon = {}
print("  %-8s %-10s %10s %10s  %s" % ("rep", "type", "recorded", "correct", "flag"))
for k in range(1, 12):
    rep = math.comb(N, k)
    val = A_weight_method(k, N)
    canon["Lambda^%d" % k] = {"dim": rep, "A": int(val)}
# 只對「實際記錄過」嘅 k 做核對（避免 by-dim 折疊造成假 flag）
RECORDED = {1: 1, 2: 8, 3: 27, 4: 18, 5: -14, 6: 0}
for k in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]:
    dim = math.comb(N, k)
    val = int(A_weight_method(k, N))
    rec = RECORDED.get(k)
    if rec is None:
        flag = "  (未記錄)"
    elif rec == val:
        flag = "  ✓"
    else:
        flag = "  ← ★記錄值錯 (應為 %d)" % val
    print("  Λ^%-6d %-10s %10s %10d%s" % (k, "dim=%d" % dim,
          rec if rec is not None else "-", val, flag))

# ============================================================
# 總結
# ============================================================
scored = [r for r in results if not r["vacuous"]]
npass = sum(1 for r in scored if r["pass"])
nall = len(scored)
print()
print("=" * 74)
print("O88 獨立審計總結（唔 import 01–03；權重法）")
print("=" * 74)
print("  計分項: %d    PASS: %d    FAIL: %d" % (nall, npass, nall - npass))
print("  報告項（唔計分）: %d" % (len(results) - nall))
print()
if mismatch:
    print("  ★ 記錄值錯誤清單（audit findings）:")
    for nm, rec, cor in mismatch:
        print("      %-14s 記錄 %-6s → 正確 %-6s" % (nm, rec, cor))
else:
    print("  ★ 記錄值全部正確")

out = {
    "auditor": "scripts/04_audit_independent.py",
    "method": "weight method A(R)=sum_weights sum_i lambda_i^3 / (N-1)(N-2)/N",
    "imports_of_o88_scripts": 0,
    "scored": nall, "passed": npass, "failed": nall - npass,
    "report_only": len(results) - nall,
    "record_mismatches": [{"item": m[0], "recorded": m[1], "correct": m[2]}
                          for m in mismatch],
    "vacuous_in_03": {"count": n_vac, "real": len(real)},
    "canonical_anomaly_table": canon,
    "tests": results,
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("\n  結果已寫入 data/04_audit_independent.json")
print("  RESULT: %d/%d PASS" % (npass, nall))
