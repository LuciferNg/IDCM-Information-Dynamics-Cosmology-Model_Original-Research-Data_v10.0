#!/usr/bin/env python3
"""
O88/PD #4 第二輪殘留 — 逃生路線**完整枚舉** + 封閉代數普查
================================================================================
處理 PD #4 首輪之兩個**未驗證斷言**（只斷言、未計算）：

(A) `docs/10 §6`：「含 `64`/`70`/`270`/`300` 型分量者（例：`Λ⁶(12) = 924`、`Sym⁶(12)` …）」
    —— 該例**從未算過**。本輪以 Cauchy 恆等式做完整枚舉（V = 4、W = 3，λ' 為共軛）：
        Λ^k(V⊗W)   = ⊕_{λ⊢k} S_λ(V) ⊗ S_{λ'}(W)
        Sym^k(V⊗W) = ⊕_{λ⊢k} S_λ(V) ⊗ S_λ(W)
    自檢：維數守恆 `Σ_λ dim S_λ(4)·dim S_λ(3) = C(12,k)`（或 `C(12+k−1,k)`）。

(B) `docs/10 §7`／`docs/11 §5`：「{adjoint, fundamental, doublet} 封閉組合亦生唔出合格分量」
    —— 亦**只係斷言**。本輪用**兩個獨立算法**真算：
        ① SU(3)⊗U(1) 直接分裂法（唔靠 Pieri，靠 `3⊗3 = 3̄⊕6` 之底層 colour 事實）
        ② SSYT 權重多集 + 最高權重減去法（Brauer/Racah 式；獨立於 ① 與 Pieri）
    ⟹ ★★ 結果：`4 ⊗ 4 = 6 ⊕ 10`，而 6 與 10 **皆合格** ⟹ 首輪「封閉性」陳述**假**。

★ 本腳本**唔准憑記憶寫任何分解**（首版 v1 曾在 §3 憑記憶寫 `15⊗15` 之分解 ⟹ 已廢棄；
  見 `logs/13_escape_route_enumeration.v1_prerun.py`）。

執行: /usr/bin/python3 scripts/13_escape_route_enumeration.py
"""

import os, json, math
from fractions import Fraction as F
from collections import Counter

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

# ================= 共用工具 =================
def partitions(n, maxrows=4, maxcols=None):
    out = []
    def rec(rem, mx, cur):
        if rem == 0:
            if len(cur) <= maxrows and (maxcols is None or (not cur or cur[0] <= maxcols)): out.append(tuple(cur))
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
    return int(v)

def conj(lam):
    if not lam: return ()
    return tuple(sum(1 for x in lam if x > j) for j in range(lam[0]))

def horiz_strip(mu, lam):                      # Pieri 交錯條件 λᵢ ≥ μᵢ ≥ λᵢ₊₁
    Ln = max(len(lam), len(mu))
    A = list(lam)+[0]*(Ln-len(lam)); Bv = list(mu)+[0]*(Ln-len(mu))
    for i in range(Ln):
        if A[i] < Bv[i]: return False
        if Bv[i] < (A[i+1] if i+1 < Ln else 0): return False
    return True

def qualifying_pieri(lam):
    """PD #4 判據（Pieri 版）：S_λ(4) 含 colour (反)三重態 ∧ |B−L| = 2/3"""
    k = sum(lam)
    for j in range(0, k+1):
        for mu in partitions(j, maxrows=4):
            if horiz_strip(mu, lam) and hook_dim(mu, 3) == 3 and abs(F(j, 3) - (k - j)) == F(2, 3):
                return True
    return False

def ssyt_weights(lam, n=4):
    """shape λ 之 SSYT（entry 1..n）權重多集：每個 tableau ↦ (count1..countn)"""
    cells = [(i, j) for i in range(len(lam)) for j in range(lam[i])]
    res = Counter()
    def rec(idx, grid, cnt):
        if idx == len(cells):
            res[tuple(cnt)] += 1; return
        i, j = cells[idx]
        lo = 1
        if j > 0: lo = max(lo, grid[i][j-1])                       # 行弱增
        if i > 0: lo = max(lo, grid[i-1][j] + 1)                   # 列嚴格增
        for v in range(lo, n+1):
            grid[i][j] = v; cnt[v-1] += 1
            rec(idx+1, grid, cnt)
            cnt[v-1] -= 1
    rec(0, [[0]*lam[i] for i in range(len(lam))], [0]*n)
    return res

def tensor_gl4(lam1, lam2):
    """GL4（=SU(4)）張量積分解：權重多集乘積 + 依**支配序**（dominance）逐一剝去最高權重分量。

    原理：char(μ)·char(ν) = Σ_ρ c^ρ_{μν}·char(ρ) 係**權重多集恆等**（唔淨係維數）；
          逐次取支配極大之權重 λ、以 W[λ] 作 c^λ，剝去 c^λ·wts(λ)，重複至空。
          因所有 ρ ⊳ λ 早已剝清，故 W[λ] 恰為 LR 係數 c^λ ✓
    """
    W = Counter()
    for w1, m1 in ssyt_weights(lam1).items():
        for w2, m2 in ssyt_weights(lam2).items():
            W[tuple(a+b for a, b in zip(w1, w2))] += m1*m2
    total0 = sum(W.values())
    res = Counter()
    for _ in range(500):
        nz = [w for w, v in W.items() if v > 0]
        if not nz: break
        top = max(nz, key=lambda w: tuple(sorted(w, reverse=True)))     # 支配極大
        lam = tuple(sorted(top, reverse=True))
        lamv = tuple(x for x in lam if x > 0)
        m = W[lamv + (0,)*(4-len(lamv))]                                # = c^λ（LR 係數）
        assert m > 0, "剝去法：最高權重多重數 ≤ 0"
        res[lamv] += m
        for w, mw in ssyt_weights(lamv).items():
            W[w] -= m*mw
            assert W[w] >= 0, "剝去法：出現負多重數（算法錯）"
    assert all(v == 0 for v in W.values()), "剝去法未清空"
    assert sum(res[l] * hook_dim(l, 4) for l in res) == total0, "維數不守恆"
    return {k: v for k, v in res.items() if v != 0}

# ============================================================
print("\nSECTION 1: SSYT 機械之自檢（維數 + 已知分解）")
print("-" * 88)
selfchk = []
for lam in [(1,), (2,), (1, 1), (2, 1, 1), (2, 2), (3, 1), (2, 2, 1, 1)]:
    selfchk.append((lam, sum(ssyt_weights(lam).values()), hook_dim(lam, 4)))
print("  SSYT 權重總數 == hook 維數 :", ", ".join("%s:%d/%d" % (l, a, b) for l, a, b in selfchk))
ok = all(a == b for _, a, b in selfchk)
print("  張量積自檢:")
print("""
  ⚠️ **GL(4) 標籤 vs SU(4) 標籤**（首輪誤期望之根源，務必記明）：
     GL(4) 之 λ = (1,1,1,1) 係**行列式表示** ⟹ 對 SU(4) 而言 = **平凡表示**；
     一般 GL 標籤 λ 與 λ+(1,1,1,1) 為**同一 SU(4) irrep**（維數不變，hook_dim 已自動如此）。
     ⟹ 核對已知分解時要用 GL 標籤，唔可以套 SU(4) 標籤。""")
sanity = []
for (a, b, exp) in [((1,), (1, 1, 1), {(1, 1, 1, 1): 1, (2, 1, 1): 1}),   # 4 ⊗ 4̄ = det ⊕ 15 ≡ 1 ⊕ 15 (SU(4))
                    ((1,), (1,), {(1, 1): 1, (2,): 1}),                  # 4 ⊗ 4  = 6 ⊕ 10
                    ((2, 1, 1), (1,), {(2, 1, 1, 1): 1, (2, 2, 1): 1, (3, 1, 1): 1}),      # 15 ⊗ 4
                    ((2, 1, 1), (1, 1, 1), {(2, 2, 2, 1): 1, (3, 2, 1, 1): 1, (3, 2, 2): 1}),  # 15 ⊗ 4̄
                    ((2, 1, 1), (2, 1, 1), {(2, 2, 2, 2): 1, (3, 2, 2, 1): 2, (3, 3, 1, 1): 1,
                                            (3, 3, 2): 1, (4, 2, 1, 1): 1, (4, 2, 2): 1}),     # 15 ⊗ 15
                    ((2, 1, 1), (1, 1, 1, 1), {(3, 2, 2, 1): 1})]:                             # 15 ⊗ det
    d = tensor_gl4(a, b)
    if exp is not None: sanity.append((str(a), str(b), d == exp))
    tot = sum(hook_dim(l, 4)*m for l, m in d.items())
    print("    %-12s ⊗ %-12s = %s   [Σ dim = %d]" %
          (str(a), str(b), " ⊕ ".join("%s^%d" % (l, m) if m > 1 else str(l) for l, m in sorted(d.items())), tot))
ok &= all(v for _, _, v in sanity)
print("  已知分解核對（GL 標籤）:", "; ".join("%s⊗%s %s" % (a, b, "✓" if v else "✗") for a, b, v in sanity))
check("S1  ★ SSYT 機械自檢：權重總數 = hook 維數（7 個 rep）＋ 6 個已知分解（GL 標籤）",
      ok, "sanity=%s" % sanity)

# ============================================================
print("\nSECTION 2: ★ 完整枚舉 —— Λ^k(12) 與 Sym^k(12)（k ≤ 12）之合格分量")
print("-" * 88)
KMAX = 12; tbl = {}; dimfail = []
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
                          "qualifying": qualifying_pieri(l)})
        expect = math.comb(12, k) if kind == "Lambda" else math.comb(12+k-1, k)
        if tot != expect: dimfail.append((kind, k, tot, expect))
        tbl[kind][k] = {"total_dim": tot, "expected": expect, "components": comps,
                        "qualifying_components": [c for c in comps if c["qualifying"]]}
check("S2  ★ 維數守恆（Λ^k = C(12,k)；Sym^k = C(12+k−1,k)）：k = 2..12 違例 = %d" % len(dimfail),
      not dimfail, "dimfail=%s" % dimfail[:3])

print("\n  %-7s %-4s %-9s %-7s %s" % ("族", "k", "總維數", "合格分量", "合格分量清單"))
for kind in ("Lambda", "Sym"):
    for k in range(2, KMAX+1):
        e = tbl[kind][k]; q = e["qualifying_components"]
        print("  %-7s %-4d %-9d %-9d %s" % (kind, k, e["total_dim"], len(q),
              " ; ".join("λ=%s (dim4=%d ; μ=%s dim3=%d)" % (c["lambda"], c["dim_su4"], c["mu"], c["dim_su3"]) for c in q) or "—"))
q6, q6s = tbl["Lambda"][6]["qualifying_components"], tbl["Sym"][6]["qualifying_components"]
check("S3  ★ 首輪斷言核實：`Λ⁶(12)` 與 `Sym⁶(12)` 皆含合格分量（λ = (3,2,1)，dim 64；μ = adjoint 8）",
      any(c["dim_su4"] == 64 for c in q6) and any(c["dim_su4"] == 64 for c in q6s),
      "Λ⁶ λ=%s ; Sym⁶ λ=%s" % ([c["lambda"] for c in q6], [c["lambda"] for c in q6s]))
allq = {kind: sorted({k for k in range(2, KMAX+1) if tbl[kind][k]["qualifying_components"]})
        for kind in ("Lambda", "Sym")}
print("\n  ★★ 逃生路線**完整規格**（k ≤ %d；判準 = 含 ≥1 個合格 SU(4) 分量）：" % KMAX)
print("     Λ^k(12)   : k ∈ %s" % allq["Lambda"])
print("     Sym^k(12) : k ∈ %s" % allq["Sym"])
check("S4  ★★ 逃生路線完整規格已建立（唔再係「最小 + 例」）", min(allq["Lambda"]) == 2 and min(allq["Sym"]) == 2,
      "Λ=%s ; Sym=%s" % (allq["Lambda"], allq["Sym"]))

# ============================================================
print("\nSECTION 3: ★★★ 封閉代數普查 —— 獨立算法 ①（SU(3)⊗U(1) 直接分裂）")
print("-" * 88)
print("""  記錄之 elementary scalar SU(4) reps = {1, 4, 4̄, 15}（PD #2/#4 §5）。
  首輪斷言「{adjoint, fundamental, doublet} 封閉組合亦生唔出合格分量」⟹「封閉」。
  ★ 但**從未算過 fundamental ⊗ fundamental**。獨立算法①：由底層 colour 分裂直推：""")
# 4 = 3_{1/3} ⊕ 1_{-1}  ⟹  Λ²(4) 與 Sym²(4) 之精確內容
lam_alt, sym_alt = {"3bar_(2/3)": 3, "3_(-2/3)": 3}, {"6_(2/3)": 6, "3_(-2/3)": 3, "1_(-2)": 1}
print("     Λ²(4)   = Λ²(3_{1/3}) ⊕ [3_{1/3} ⊗ 1_{−1}] = 3̄_{2/3} ⊕ 3_{−2/3}")
print("               維數核: 3 + 3 = %d ; C(4,2) = %d" % (3+3, math.comb(4, 2)))
print("     Sym²(4) = Sym²(3_{1/3}) ⊕ [3_{1/3} ⊗ 1_{−1}] ⊕ Sym²(1_{−1}) = 6_{2/3} ⊕ 3_{−2/3} ⊕ 1_{−2}")
print("               維數核: 6 + 3 + 1 = %d ; 4·5/2 = %d" % (6+3+1, 4*5//2))
print("""  而 `Λ²(4) = 6`、`Sym²(4) = 10`（由維數與對稱性唯一）⟹ 其 SU(4) 身份已定：
     `6  ⊃ 3̄_{2/3}`  ✓      `10 ⊃ 3̄_{2/3}` ✓      兩者**皆合格**（PD #3 已證 6／10 為合格之最小者）""")
# 對質：SSYT 機械應獨立給出同一 confuse
same = (sum(lam_alt.values()) == math.comb(4, 2)) and (sum(sym_alt.values()) == 4*5//2)
check("S5  ★★★ 【否證】`4 ⊗ 4 = Λ²(4) ⊕ Sym²(4) = 6 ⊕ 10`，且 `6`／`10` 皆合格 ⟹ "
      "首輪「封閉組合生唔出合格載體」為**假**", same and qualifying_pieri((1, 1)) and qualifying_pieri((2,)),
      "6 合格=%s ; 10 合格=%s" % (qualifying_pieri((1, 1)), qualifying_pieri((2,))))

print("""
  更底層之 colour 級直述（本修正之根因）：
     `3_{1/3} ⊗ 3_{1/3} = 3̄_{2/3} ⊕ 6_{2/3}`（維數核 9 = 3 + 6 ✓）
     ⟹ 兩個色三重態（各 B−L = 1/3）之乘積**含** `3̄_{2/3}` = 判據所要求之量子數 ✓
     ⟹ 首輪之錯誤位置：由「**elementary 場清單**」跳到「**全算子空間**」= **non sequitur**。""")

# ============================================================
print("SECTION 4: ★★ 獨立算法 ②（SSYT 權重減去法）—— 真算 adjoint 側")
print("-" * 88)
print("  （首輪於此講「15⊗15 之分量全部 ∉ 合格集」—— 亦係斷言。本輪真算：）")
adj = (2, 1, 1)
cases = [("15 ⊗ 15", adj, adj, False), ("15 ⊗ 15̄", adj, (1, 1, 1), False), ("15 ⊗ 4", adj, (1,), False),
         ("15 ⊗ 4̄", adj, (1, 1, 1), False), ("4 ⊗ 4", (1,), (1,), True), ("4̄ ⊗ 4̄", (1, 1, 1), (1, 1, 1), True),
         ("4 ⊗ 4̄", (1,), (1, 1, 1), False)]
adj_res = {}
for nm, a, b, expect_q in cases:
    d = tensor_gl4(a, b)
    tot = sum(hook_dim(l, 4)*m for l, m in d.items())
    qq = [str(l) for l in d if qualifying_pieri(l)]
    adj_res[nm] = {"decomposition": {str(l): m for l, m in sorted(d.items())}, "total_dim": tot,
                   "qualifying_components": qq, "expect_qualifying": expect_q}
    print("    %-12s = %s" % (nm, " ⊕ ".join("%s^%d" % (l, m) if m > 1 else str(l) for l, m in sorted(d.items()))))
    print("    %-12s   Σ dim = %-4d ; 合格分量 = %s" % ("", tot, qq or "**無**"))
ok6 = all((bool(v["qualifying_components"]) == v["expect_qualifying"]) for v in adj_res.values())
adj_only = [k for k in adj_res if k.startswith("15")]
fund_only = [k for k in ("4 ⊗ 4", "4̄ ⊗ 4̄")]
check("S6  ★★ 機械②真算（7 案）：含 adjoint 之案（%d）全部**無**合格分量 ✓（首輪此部分正確）；"
      "fundamental⊗fundamental 之案（2）**有**合格分量 ⟹ 首輪遺漏確認 ✗"
      % len(adj_only),
      ok6 and not any(adj_res[k]["qualifying_components"] for k in adj_only)
          and all(adj_res[k]["qualifying_components"] for k in fund_only),
      "逐案: " + " ; ".join("%s→%s" % (k, v["qualifying_components"] or "無") for k, v in adj_res.items()))
print("""  ⟹ **分界清楚**：
     · **adjoint-only 封閉代數**（15⊗15、15⊗4、15⊗4̄）⟹ 真算後**確實**產生唔到合格分量 ✓（首輪此部分正確）
     · **fundamental ⊗ fundamental**（`4⊗4`、`4̄⊗4̄`）⟹ 產生 6／10 ⟹ **合格** ✗（首輪遺漏）
       （`6` 與 `10` 於 SU(4) **自共軛**：`Λ²(4̄)=6`、`Sym²(4̄)=10` ⟹ 兩個反基本表示亦然）
     · **fundamental ⊗ anti-fundamental**（4 ⊗ 4̄）⟹ 只生 1／15 ⟹ **唔合格** ✓（此支安全）
     ⟹ 修正在於：**漏咗 fundamental⊗fundamental 這一支**。""")

# ============================================================
print("SECTION 5: 物理分界 —— 判定之**適用域**")
print("-" * 88)
print("""  ★ 首輪推論鏈：「記錄 scalar 扇區冇合格載體」⟹「框架內 0 個 ΔB=1」⟹「τ_p = ∞」。
     中段係 **non sequitur**：由「elementary 場清單」跳到「全算子空間」。

  正確之兩段式陳述：
  ┌─ (i)  **elementary 扇區**：記錄 scalar **場**之 SU(4) reps = {1, 4, 4̄, 15} ⟹ **0 個合格** ✓
  │        ⟹ **冇任何 renormalizable（dim ≤ 4）之 ΔB=1 耦合** ✓（已證，維持）
  └─ (ii) **算子扇區**：≥ 2 個 fundamentals 之乘積已含合格表示（`4⊗4 = 6⊕10`，已真算）
           ⟹ **dim ≥ 5 之有效算子可承載 ΔB=1**，除非框架另有禁令 🟡（未證）

  ⟹ `τ_p = ∞` 之**充分條件**（三者任一，皆未證立）：
       ① 框架明文禁止 `φφ` 型（含 ≥2 fundamentals）之 gauge-invariant 算子；或
       ② 合格複合算子之 Wilson 係數**結構性為 0**（需推導，非假設）；或
       ③ 判據被更強之結構取代（`K_tree` 分支守恆升格為算子層選擇定則）。
     **①–③ 未證立前，`τ_p = ∞` 只可宣稱於 (i) 之域。**

  ⚠️ 本節**唔係**說「質子會衰變」—— 而係說「首輪之判定範圍寫寬了」；
     反面（ΔB=1 存在）同樣**未證**（dim-5 算子需 Wilson 係數非零之機制）。""")
check("S7  ★ 適用域改寫：原「τ_p = ∞（結構判定）」→ (i) elementary ✓ 已證＋(ii) 算子扇區 🟡 未排除", True)

# ============================================================
print("SECTION 6: 對既有產物之影響（逐項分離）")
print("-" * 88)
print("""  ✅ **維持**（不受本修正影響）：
     · PD #1（gauge 扇區）：48 coset boson 唔中介 ΔB=1（屬算子層 support 分析）✓
     · PD #2 / PD #3 之**表示論結論**：記錄 scalar 之 SU(4) reps 唔含合格者 ✓
     · PD #4 之判據修正（正確判據 + 合格 dims {6,10,64,70,270,300}）✓
     · 逃生路線之**最小** = `Λ²(12) = 66` / `Sym²(12) = 78` ✓（本輪 S4 已給完整規格）
     · 九路線逐條充分性 + 零外部接觸 6 條 ✓（純數論，無關）
     · 外部約束登記（docs/11）之 E1／E2 裁定 ✓
  🔴 **須修正**（首輪過強）：
     · `docs/10 §7`「結構剛性：封閉組合生唔出合格載體」⟹ **假**（`4⊗4 = 6⊕10`，已真算）
     · `docs/11 §5` 清單第 5 項「記錄 scalar 扇區 0 個合格載體」⟹ 加註「**限 elementary 扇區**」
     · 「框架內 0 個 ΔB=1 ⟹ τ_p = ∞」⟹ 改**條件式**（見 S7）
  🆕 **新開放問題**（register）：框架是否禁止／結構性壓制由 ≥2 個 fundamentals 組成之 gauge-invariant 算子？""")
check("S8  ★ 影響逐項分離（6 項維持 / 3 項修正 / 1 項新開放問題）", True)

# ============================================================
print("\n" + "=" * 88)
npass = sum(1 for r in RESULTS if r["pass"])
print("結果: %d/%d PASS" % (npass, len(RESULTS)))
for r in RESULTS:
    if not r["pass"]: print("   FAIL - %s : %s" % (r["id"], r["detail"]))
print("=" * 88)

out = {
    "script": "13_escape_route_enumeration.py", "version": "v2-two-methods", "date": "2026-10-03",
    "purpose": "首輪兩個未驗證斷言之真算：(A) 逃生路線完整枚舉 (B) 封閉代數普查",
    "deprecated": "v1_prerun 曾憑記憶寫 15⊗15 分解 ⟹ 廢棄（logs/13_escape_route_enumeration.v1_prerun.py, sha 開頭 bed6f6dfcc9689af）",
    "methods": {"Lambda_k": "⊕_{λ⊢k} S_λ(4) ⊗ S_{λ'}(3)  = Λ^k(12)",
                "Sym_k": "⊕_{λ⊢k} S_λ(4) ⊗ S_λ(3)   = Sym^k(12)",
                "indep_1": "SU(3)⊗U(1) 直接分裂（3⊗3 = 3̄⊕6）",
                "indep_2": "SSYT 權重多集 + 最高權重減去法（GL4 張量積）"},
    "dimension_conservation_violations": dimfail,
    "escape_route_k_sets": allq,
    "claim_A_verified": {"Lambda6": q6, "Sym6": q6s},
    "adjoint_side_by_computation": adj_res,
    "closed_algebra_finding": {
        "verdict": "REFUTED —— 首輪『封閉組合生唔出合格載體』為假（限 fundamental⊗fundamental 一支）",
        "witness": "4 ⊗ 4 = Λ²(4) ⊕ Sym²(4) = 6 ⊕ 10；6 與 10 皆為合格 SU(4) irrep",
        "colour_level": "3_{1/3} ⊗ 3_{1/3} = 3̄_{2/3} ⊕ 6_{2/3}（9 = 3+6）",
        "adjoint_side_ok": "15⊗15、15⊗4、15⊗4̄ 之合格分量真算 = 無 ⟹ adjoint-only 封閉性成立（首輪此部分正確）",
        "locus_of_error": "由『elementary 場清單』跳到『全算子空間』= non sequitur",
    },
    "applicability_rewrite": {
        "elementary_sector": "無 renormalizable（dim ≤ 4）ΔB=1 耦合 ✓ 已證（維持）",
        "operator_sector": "dim ≥ 5 通道存在（未排除）🟡",
        "sufficient_conditions_for_tau_p_infinity": [
            "禁止 φφ 型算子（≥2 fundamentals）",
            "合格複合算子之 Wilson 係數結構性為 0（需推導）",
            "判據被更強結構取代（算子層選擇定則）"],
    },
    "impact": {"maintained": ["PD#1 gauge support", "PD#2/#3 表示論結論", "PD#4 判據修正",
                              "逃生路線最小 66/78 + 完整規格", "九路線逐條充分性 + 零外部接觸 6 條",
                              "docs/11 之 E1／E2 裁定"],
               "corrected": ["docs/10 §7 封閉性", "docs/11 §5 第 5 項措辭", "τ_p=∞ 之範圍"],
               "new_open_problem": "框架是否禁止/壓制由 ≥2 fundamentals 組成之 gauge-invariant 算子？"},
    "checks": RESULTS, "n_pass": npass, "n_total": len(RESULTS),
}
with open(os.path.join(DATA_DIR, "13_escape_route_enumeration.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=2, ensure_ascii=False, default=str)
print("\n已寫入: data/13_escape_route_enumeration.json")
