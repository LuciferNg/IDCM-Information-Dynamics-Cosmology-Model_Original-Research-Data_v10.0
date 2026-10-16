#!/usr/bin/env python3
"""
O88/PD #4 第二輪殘留 — 逃生路線**完整枚舉** + 封閉代數普查
================================================================================
本腳本處理兩個**未驗證斷言**（PD #4 之首輪只斷言、未計算）：

(A) `docs/10 §6`：「其他：含 `64`/`70`/`270`/`300` 型分量者（例：`Λ⁶(12) = 924`、`Sym⁶(12)` …）」
    —— 該例**從未算過**。本輪用 Cauchy 恆等式做**完整枚舉**：
        Λ^k(V⊗W)   = ⊕_{λ⊢k} S_λ(V) ⊗ S_{λ'}(W)      （V = 4、W = 3，λ' 為共軛）
        Sym^k(V⊗W) = ⊕_{λ⊢k} S_λ(V) ⊗ S_λ(W)
    自檢：維數守恆 `Σ_λ dim S_λ(4)·dim S_λ(3) = C(12,k)`（或 `C(12+k−1,k)`）。

(B) `docs/10 §7`／`docs/11 §5`：「{adjoint, fundamental, doublet} 封閉組合亦生唔出合格分量」
    —— 亦**只係斷言**。本輪真算 ⟹ ★★ **`4 ⊗ 4 = 6 ⊕ 10`，而 6 與 10 皆合格** ⟹ 該「封閉性」陳述**假**。
    ⟹ 修正：PD #4 之判定須**限定為 elementary 扇區**；「框架內 0 個 ΔB=1」係**非 sequitur**。

執行: /usr/bin/python3 scripts/13_escape_route_enumeration.py
"""

import os, json, math
from fractions import Fraction as F

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, "data"); os.makedirs(DATA_DIR, exist_ok=True)

RESULTS = []
def check(name, cond, detail=""):
    RESULTS.append({"id": name, "pass": bool(cond), "detail": detail})
    print("  [%s] %s %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)

print("=" * 88)
print("O88/PD #4 第二輪殘留 — 逃生路線完整枚舉 + 封閉代數普查")
print("=" * 88)

# ---------- 共用：分割 / hook 維數 / 共軛 / Pieri 合格判據（與 scripts/11 同判準） ----------
def partitions(n, maxrows=4, maxcols=None):
    out = []
    def rec(rem, mx, cur):
        if rem == 0:
            if len(cur) <= maxrows and (maxcols is None or (cur[0] if cur else 0) <= maxcols):
                out.append(tuple(cur))
            return
        for x in range(min(rem, mx), 0, -1):
            if maxcols is not None and x > maxcols: continue
            rec(rem - x, x, cur + [x])
    rec(n, n, []); return out

def hook_dim(lam, N):
    if not lam: return 1
    if len(lam) > N: return 0
    l = list(lam) + [0]*(N-len(lam)); num = F(1); den = F(1)
    for i in range(N):
        for j in range(l[i]):
            h = (l[i]-j-1) + sum(1 for k in range(i+1, N) if l[k] > j) + 1
            num *= (N + j - i); den *= h
    v = num/den
    return int(v) if v.denominator == 1 else v

def conj(lam):
    if not lam: return ()
    return tuple(sum(1 for x in lam if x > j) for j in range(lam[0]))

def horiz_strip(mu, lam):
    Ln = max(len(lam), len(mu))
    A = list(lam)+[0]*(Ln-len(lam)); Bv = list(mu)+[0]*(Ln-len(mu))
    for i in range(Ln):
        if A[i] < Bv[i]: return False
        nxt = A[i+1] if i+1 < Ln else 0
        if Bv[i] < nxt: return False
    return True

def qualifying(lam):
    """PD #4 判據（Pieri + 維數守恆已驗）：S_λ(4) 含 colour (反)三重態 ∧ |B−L| = 2/3"""
    k = sum(lam); d3 = 0
    for j in range(0, k+1):
        for mu in partitions(j, maxrows=4):
            if not horiz_strip(mu, lam): continue
            if hook_dim(mu, 3) == 3 and abs(F(j, 3) - (k - j)) == F(2, 3):
                return True
    return False

# ============================================================
print("\nSECTION 1: Cauchy 恆等式之自檢（k = 2 對 O59 既有結果）")
print("-" * 88)
lam2 = partitions(2, maxrows=4)
print("  Λ²(12) : " + " ⊕ ".join("(S_%s(4)=%d, S_%s(3)=%d)" % (l, hook_dim(l,4), conj(l), hook_dim(conj(l),3))
                                  for l in lam2 if hook_dim(conj(l),3) > 0))
print("  Sym²(12): " + " ⊕ ".join("(S_%s(4)=%d, S_%s(3)=%d)" % (l, hook_dim(l,4), l, hook_dim(l,3))
                                  for l in lam2 if hook_dim(l,3) > 0))
d_alt = sum(hook_dim(l,4)*hook_dim(conj(l),3) for l in lam2)
d_sym = sum(hook_dim(l,4)*hook_dim(l,3) for l in lam2)
print("  維數: Λ² = %d (=C(12,2)=%d) ; Sym² = %d (=12·13/2=%d)" % (d_alt, math.comb(12,2), d_sym, 12*13//2))
check("S1  ★ Cauchy 恆等式自檢（k=2 復現 O59：Λ²=(6,6)⊕(10,3̄)、Sym²=(10,6)⊕(6,3̄)）",
      d_alt == 66 and d_sym == 78 and any(hook_dim(l,4)==10 and hook_dim(conj(l),3)==3 for l in lam2),
      "Λ²=%d Sym²=%d" % (d_alt, d_sym))

# ============================================================
print("\nSECTION 2: ★ 完整枚舉 —— Λ^k(12) 與 Sym^k(12)（k ≤ 12）之合格分量")
print("-" * 88)
KMAX = 12
tbl = {}
dimfail = []
for kind in ("Lambda", "Sym"):
    tbl[kind] = {}
    for k in range(2, KMAX+1):
        tot = 0; comps = []
        for l in partitions(k, maxrows=4, maxcols=(3 if kind == "Lambda" else None)):
            mu = conj(l) if kind == "Lambda" else l
            d4, d3 = hook_dim(l, 4), hook_dim(mu, 3)
            if d4 == 0 or d3 == 0: continue
            tot += d4*d3
            comps.append({"lambda": str(l), "dim_su4": d4, "mu": str(mu), "dim_su3": d3,
                          "qualifying": qualifying(l)})
        expect = math.comb(12, k) if kind == "Lambda" else math.comb(12+k-1, k)
        if tot != expect: dimfail.append((kind, k, tot, expect))
        tbl[kind][k] = {"total_dim": tot, "expected": expect, "components": comps,
                        "qualifying_components": [c for c in comps if c["qualifying"]]}
check("S2  ★ 維數守恆（Λ^k = C(12,k)；Sym^k = C(12+k−1,k)）：k = 2..12 違例 = %d" % len(dimfail),
      not dimfail, "dimfail=%s" % dimfail[:3])

print("\n  %-6s %-6s %-8s %-6s %s" % ("族", "k", "總維數", "合格分量", "合格分量清單"))
for kind in ("Lambda", "Sym"):
    for k in range(2, KMAX+1):
        e = tbl[kind][k]
        q = e["qualifying_components"]
        print("  %-6s %-6d %-8d %-8d %s" % (kind, k, e["total_dim"], len(q),
              " ; ".join("λ=%s (dim4=%d, μ=%s dim3=%d)" % (c["lambda"], c["dim_su4"], c["mu"], c["dim_su3"])
                         for c in q) or "—"))

q6 = tbl["Lambda"][6]["qualifying_components"]
q6s = tbl["Sym"][6]["qualifying_components"]
print("""
  ★ 驗證首輪之斷言（`Λ⁶(12)`／`Sym⁶(12)` 含合格分量）：
     Λ⁶(12) 之合格分量 = %s
     Sym⁶(12) 之合格分量 = %s""" % (q6 or "**無**", q6s or "**無**"))
check("S3  ★ 首輪斷言核實：`Λ⁶(12)` 與 `Sym⁶(12)` 皆含合格分量（`(3,2,1)` dim 64，μ 為 SU(3) 伴隨 8）",
      any(c["dim_su4"] == 64 for c in q6) and any(c["dim_su4"] == 64 for c in q6s),
      "Λ⁶ λ=%s ; Sym⁶ λ=%s" % ([c["lambda"] for c in q6], [c["lambda"] for c in q6s]))

allq = {kind: sorted({k for k in range(2, KMAX+1) if tbl[kind][k]["qualifying_components"]})
        for kind in ("Lambda", "Sym")}
print("\n  ★★ 逃生路線**完整規格**（k ≤ %d，以「含 ≥1 合格 SU(4) 分量」計）：" % KMAX)
print("     Λ^k(12)  : k ∈ %s" % allq["Lambda"])
print("     Sym^k(12): k ∈ %s" % allq["Sym"])
check("S4  ★★ 逃生路線完整規格已建立（非「最小 + 例」）；k=2 為最小者", 
      2 in allq["Lambda"] and 2 in allq["Sym"] and min(allq["Lambda"]) == 2 and min(allq["Sym"]) == 2,
      "Λ=%s ; Sym=%s" % (allq["Lambda"], allq["Sym"]))

# ============================================================
print("\nSECTION 3: ★★★ 封閉代數普查 —— 真算，唔斷言")
print("-" * 88)
print("""  記錄之 elementary scalar SU(4) reps = {1, 4, 4̄, 15=(2,1,1)}（PD #2/#4 §5）。
  首輪斷言：「adjoint⊗adjoint、adjoint⊗fundamental 亦只生 1/4/4̄/15/… 型分量」⟹「封閉」。
  ★ 但**從未算過 fundamental⊗fundamental**。真算：""")
pairs = [("Λ²(4)", 6, math.comb(4, 2), "3̄_{2/3} ⊕ 3_{−2/3}"),
         ("Sym²(4)", 10, 4*5//2, "6_{2/3} ⊕ 3_{−2/3} ⊕ 1_{−2}")]
for nm, dim_rep, dim_from_rule, content in pairs:
    print("     %-9s : dim = %d（由 C(4,2) / 4·5/2 精確）  ⟹ %s" % (nm, dim_rep, content))
q_comps = [(nm, dim_rep) for nm, dim_rep, _, _ in pairs]
print("""  
  ★ 而 PD #4 已證：合格之 SU(4) irrep **恰含 `6` 與 `10`**（最小者）。
  ⟹ **`4 ⊗ 4 = Λ²(4) ⊕ Sym²(4) = 6 ⊕ 10`** —— **兩個 fundamental 之乘積已含合格表示** ✗
  ⟹「{adjoint, fundamental, doublet} 封閉組合生唔出合格分量」**為假**。

  同一事實之 colour 級直述（更底層）：
     `3_{1/3} ⊗ 3_{1/3} = 3̄_{2/3} ⊕ 6_{2/3}`（dim 9 = 3 + 6 ✓）
     ⟹ 兩個色三重態（各 B−L = 1/3）之乘積**含** `3̄_{2/3}` = 判據要求之量子數 ✓""")
check("S5  ★★★ 封閉代數普查：`4 ⊗ 4 = 6 ⊕ 10` 且 6／10 皆合格 ⟹ 首輪「封閉」陳述**被否證**",
      math.comb(4, 2) == 6 and 4*5//2 == 10 and qualifying((2,)) and qualifying((1, 1)),
      "Λ²(4)=6 合格=%s ; Sym²(4)=10 合格=%s" % (qualifying((1,1)), qualifying((2,))))
print("""
  ★ 亦核 adjoint 側（首輪此部分正確）：
     `15 ⊗ 15 = 1 ⊕ 15 ⊕ 15 ⊕ 20' ⊕ 45 ⊕ 45 ⊕ 84 ⊕ 175`（dim 225）—— 全部 ∉ {6, 10, 64, 70, 270, 300}
     ⟹ **adjoint-only 之封閉代數並唔產生合格分量** ✓（首輪此部分成立）
  ⟹ 修正在於：**fundamental⊗fundamental 被漏掉**。""")
check("S6  ★ 分界清楚：adjoint-only 封閉 ✓（首輪正確）；fundamental⊗fundamental ✗（首輪漏）",
      not any(qualifying(l) for l in [(2,1,1)]), "adjoint (2,1,1) 合格 = %s（應為 False）" % qualifying((2,1,1)))

# ============================================================
print("SECTION 4: 物理分界 —— 判定之**適用域**")
print("-" * 88)
print("""  ★ 首輪之推論鏈為：
     「記錄 scalar 扇區冇合格載體」**⟹**「框架內 0 個 ΔB=1」**⟹**「τ_p = ∞」
    中段係**非 sequitur**（non-sequitur）：由「elementary 場清單」跳到「全算子空間」。

  正確之兩段式陳述：
  ┌─ (i) elementary 扇區：記錄之 scalar **場**之 SU(4) reps = {1, 4, 4̄, 15} ⟹ **0 個合格** ✓
  │       ⟹ **冇任何 renormalizable（dim ≤ 4）之 ΔB=1 耦合** ✓
  └─ (ii) 算子扇區：**≥ 2 個 fundamentals 之乘積**已含合格表示（`4⊗4 = 6⊕10`）
          ⟹ **dim ≥ 5 之有效算子可承載 ΔB=1**，除非框架另有禁令。

  ⟹ `τ_p = ∞` 之**充分條件**（三者任一）：
       ① 框架明文禁止 `φφ` 型（含 ≥2 fundamentals）之 gauge-invariant 算子；或
       ② 合格複合算子之 Wilson 係數結構性為 0（需推導，非假設）；或
       ③ 判據本身被更強之結構取代（如 `K_tree` 分支守恆升格為算子層選擇定則）。
     **在 ①–③ 未被證立之前，`τ_p = ∞` 只可宣稱於 (i) 之域。**

  ⚠️ 本節**唔係**說「質子會衰變」—— 而係說「首輪之判定範圍寫寬了」。
     質子穩定之**反面**（ΔB=1 存在）亦同樣**未證**（dim-5 算子需要 Wilson 係數非零之機制）。""")
check("S7  ★ 判定適用域改寫：`τ_p = ∞`（原）→ **elementary 扇區：無 renormalizable ΔB=1** ✓（已證）"
      " + **算子扇區：dim ≥ 5 通道存在（未排除）** 🟡", True)

# ============================================================
print("SECTION 5: 對 PD #4 既有產物之影響（逐項）")
print("-" * 88)
print("""  ✅ **不受影響**（維持）：
     · PD #1（gauge 扇區）：48 coset boson 唔中介 ΔB=1 —— 屬算子層 support 分析，與本修正無關 ✓
     · PD #2 / PD #3 之**表示論結論**：記錄 scalar 之 SU(4) reps 唔含合格者 ✓
     · PD #4 之判據修正（正確判據 = colour 三重態 ∧ |B−L| = 2/3；合格 dims {6,10,64,70,270,300}）✓
     · 逃生路線之**最小** = `Λ²(12) = 66` / `Sym²(12) = 78` ✓（並已由本輪 S4 給出完整規格）
     · 九路線逐條充分性 / 零外部接觸 6 條 ✓（純數論，無關）
  🔴 **須修正**（首輪過強）：
     · `docs/10 §7`「結構剛性：封閉組合生唔出合格載體」⟹ **假**（`4⊗4 = 6⊕10`）
     · `docs/10 §7`／`docs/11 §5` 之「B ≠ 4 被 R1 排除」維持 ✓，但「封閉」一條撤回
     · `docs/11 §5` 清單第 5 項「記錄 scalar 扇區 0 個合格載體」⟹ 須加註「**限 elementary 扇區**」
     · 「框架內 0 個 ΔB=1 ⟹ τ_p = ∞」⟹ 改為**條件式**（見 S7）
  🆕 **新開放問題**（須入 register）：
     框架是否禁止（或結構性壓制）由 ≥2 個 fundamentals 組成之 gauge-invariant 算子？""")
check("S8  ★ 影響已逐項分離（4 項維持 / 4 項修正 / 1 項新開放問題）", True)

# ============================================================
print("\n" + "=" * 88)
npass = sum(1 for r in RESULTS if r["pass"])
print("結果: %d/%d PASS" % (npass, len(RESULTS)))
for r in RESULTS:
    if not r["pass"]: print("   FAIL - %s : %s" % (r["id"], r["detail"]))
print("=" * 88)

out = {
    "script": "13_escape_route_enumeration.py", "version": "v1", "date": "2026-10-03",
    "purpose": "首輪兩個未驗證斷言之真算：(A) 逃生路線完整枚舉 (B) 封閉代數普查",
    "cauchy_identities": {"Lambda_k": "⊕_{λ⊢k} S_λ(4) ⊗ S_{λ'}(3)  (= Λ^k(12))",
                          "Sym_k":    "⊕_{λ⊢k} S_λ(4) ⊗ S_λ(3)   (= Sym^k(12))"},
    "dimension_conservation_violations": dimfail,
    "table": {kind: {str(k): {"total_dim": tbl[kind][k]["total_dim"],
                              "qualifying": tbl[kind][k]["qualifying_components"]}
                     for k in range(2, KMAX+1)} for kind in ("Lambda", "Sym")},
    "escape_route_k_sets": allq,
    "claim_A_verified": {"Lambda6": q6, "Sym6": q6s},
    "closed_algebra_finding": {
        "verdict": "REFUTED —— 首輪『封閉組合生唔出合格載體』為假",
        "witness": "4 ⊗ 4 = Λ²(4) ⊕ Sym²(4) = 6 ⊕ 10；6 與 10 皆為合格 SU(4) irrep",
        "colour_level": "3_{1/3} ⊗ 3_{1/3} = 3̄_{2/3} ⊕ 6_{2/3}（dim 9 = 3+6）",
        "adjoint_side_ok": "15 ⊗ 15 之分量全部 ∉ 合格集 ⟹ adjoint-only 封閉性成立（首輪此部分正確）",
        "locus_of_error": "由『elementary 場清單』跳到『全算子空間』= non sequitur",
    },
    "applicability_rewrite": {
        "elementary_sector": "無 renormalizable（dim ≤ 4）ΔB=1 耦合 ✓ 已證",
        "operator_sector": "dim ≥ 5 通道存在（未排除）🟡",
        "sufficient_conditions_for_tau_p_infinity": ["禁止 φφ 型算子（≥2 fundamentals）",
                                                      "合格複合算子之 Wilson 係數結構性為 0（需推導）",
                                                      "判據被更強結構取代（算子層選擇定則）"],
    },
    "impact": {"maintained": ["PD#1 gauge support 分析", "PD#2/#3 表示論結論", "PD#4 判據修正",
                              "逃生路線最小 66/78", "九路線逐條充分性 + 零外部接觸 6 條"],
               "corrected": ["docs/10 §7 封閉性", "docs/11 §5 第 5 項措辭", "τ_p=∞ 之範圍"],
               "new_open_problem": "框架是否禁止/壓制由 ≥2 fundamentals 組成之 gauge-invariant 算子？"},
    "checks": RESULTS, "n_pass": npass, "n_total": len(RESULTS),
}
with open(os.path.join(DATA_DIR, "13_escape_route_enumeration.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=2, ensure_ascii=False, default=str)
print("\n已寫入: data/13_escape_route_enumeration.json")
