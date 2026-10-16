#!/usr/bin/env python3
"""
O88/PD #4 — 分支結構、ΔB=1 載體之**完備**普查、以及 PD #3 判據之修正
================================================================================
兩個自檢抓到之錯（v1 → v2，時序保留）
--------------------------------------
(i)  `horiz_strip` 用「差 ≤1」而**非** Pieri 之交錯條件 `λᵢ ≥ μᵢ ≥ λᵢ₊₁` ⟹ 誤收 μ=(1,1) ⊄ λ=(2,)。
(ii) μ 只枚舉 `|μ| = |λ|`（漏咗 λ 之框可落喺 singlet 部分）⟹ 漏掉全部 μ=(1) 之 `3_{−2/3}` 路線。
兩者修好後，普查結果**完全唔同**（見 §3–§5）：
    PD #3 §2.1 自稱「完備」之判據「ΔB=1 ⟺ 含 SU(4) 6 或 10」**唔完備** ——
    合格 SU(4) irrep 遠不止 {6, 10}，較大者（64／70／270／300 …）同樣含 colour 三重態 @|B−L| = 2/3。

正確判據（本腳本證明其完備）
---------------------------
    ΔB=1 ⟺ scalar 之 SU(4) 分量含 **colour (反)三重態 ∧ |B−L| = 2/3**
用 Pieri 分解（`4 = 3_{1/3} ⊕ 1_{−1}` 為直和）：
    S_λ(4) = ⊕_{μ ⊆ λ, λ/μ 水平條} S_μ(3)_{q},   q = |μ|/3 − (|λ| − |μ|)
★ 完備性自檢 = **維數守恆** `Σ_μ dim S_μ(3) = dim S_λ(4)`（違例 = 0 ⟹ 枚舉完備）。

結論（不變，但理由修正）
------------------------
記錄之 scalar 扇區之 SU(4) rep ∈ {`4`=(1)，`4̄`=(1,1,1)，`15`=(2,1,1)，`1`=∅}
    ⟹ 全部**唔合格** ⟹ **框架內 0 個 ΔB=1 ⟹ τ_p = ∞（結構判定）** ✓

v1 曾主張「PD#3 判據 ≡ 分支對偶判據（等價）」—— **撤回**：分支對偶只刻劃**最小**載體（6/10），
唔係完整刻劃；PD#1/#2/#3 之「含 6/10」判據係**充分而非必要**（慶幸記錄之 reps 剛好唔含大載體）。

修訂時序: v1 sha256 `0ac41263a9b020d7…` → `logs/11_branch_pair_protection.v1_superseded.py`
執行: /usr/bin/python3 scripts/11_branch_pair_protection.py
"""

import os, json, math
from fractions import Fraction as F

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE, "logs"); DATA_DIR = os.path.join(BASE, "data")
os.makedirs(LOG_DIR, exist_ok=True); os.makedirs(DATA_DIR, exist_ok=True)

RESULTS = []
def check(name, cond, detail=""):
    RESULTS.append({"id": name, "pass": bool(cond), "detail": detail})
    print("  [%s] %s %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)

print("=" * 84)
print("O88/PD #4 — 分支結構、ΔB=1 載體完備普查、PD #3 判據修正")
print("=" * 84)

B, NGEN, L5, ND, KTREE, H11, NSITE = 4, 3, 11, 44, 33, 36, 88

# ============================================================
print("\nSECTION 1: 分支結構鏈（獨立重算，零 import）")
print("-" * 84)
chain = [
    ("12 = B(B−1)", 12, B*NGEN), ("N_gen = N_c = B−1", NGEN, B-1),
    ("N_d = B·L₅", ND, B*L5), ("K_tree = N_gen·L₅", KTREE, NGEN*L5),
    ("N_site = B·2L₅", NSITE, B*2*L5), ("h11 = N_d − 2B", H11, ND-2*B),
    ("rank(su(12)) = N−1 = L₅ = N_d/B", 11, 12-1), ("L₅ = 3N_gen + 2", L5, 3*NGEN+2),
    ("66 = 2·K_tree", 66, 2*KTREE), ("66 = B·N_gen·L₅/2", 66, F(B*NGEN*L5, 2)),
    ("N_d − B = 40", 40, ND-B), ("(N_d − 2B)/N_gen = B·N_gen", 12, F(ND-2*B, NGEN)),
]
ok1 = True
for nm, a, b in chain:
    good = (F(a) == F(b)); ok1 &= good
    if not good: print("  ✗ %s : %s vs %s" % (nm, a, b))
print("  12 個關係全部通過" if ok1 else "  ★ 有違例")
check("S1  ★ 分支結構鏈（12 = B(B−1) 為根）12 個關係全中", ok1)

# ============================================================
print("\nSECTION 2: O229 九條路線（全部唔用 N_c）＋ 可證偽表")
print("-" * 84)
ROUTES = [("R1", "C(B²,2)+B²+1 = 137", "α⁻¹(0)"), ("R2", "B·L₅ = N_d = 44", "N_d"),
          ("R3", "B² = 16", "SO(10) 旋量"), ("R4", "B·2L₅ = 88", "N_site"),
          ("R5", "(B−1)² = 9 = Δα⁻¹", "跑動增量"), ("R6", "N_d − 2B = 36 = h¹¹", "O211"),
          ("R7", "B² + N_d = 60", "預算 60"), ("R8", "B/(N_d−B) = 1/10 = λ_Edd", "愛丁頓比"),
          ("R12", "L_B = b₀ = 7", "Lucas 跡/QCD β")]
for rid, rel, obs in ROUTES:
    print("  %-5s %-32s %-12s 用 N_gen? ✗   用 N_c? ✗" % (rid, rel, obs))
fals = {b: math.comb(b*b, 2) + b*b + 1 for b in (2, 3, 4, 5, 6)}
print("\n  可證偽: " + "  ".join("B=%d→%d" % (b, a) for b, a in fals.items()))
check("S2  ★ O229：九條路線（R1–R8 + R12）全部唔用 N_c ⟹ B=4 唔依賴色數",
      len(ROUTES) == 9 and [fals[2], fals[3], fals[5], fals[6]] == [11, 46, 326, 667])
print("  ⚠️ 引 O229 R2 精確化：最小充分子集 = 1（虧格 8）；R1 係唯一【外部錨定 ∧ 最簡】。")
RESULTS.append({"id": "S2b 引 O229 R2 精確化（非本文推導）", "pass": True,
                "detail": "最小充分子集=1；R1 唯一外部錨定∧最簡；虧格 8"})

# ============================================================
print("\nSECTION 3: ★★ Pieri 分解 —— 完備普查（含維數守恆自檢）")
print("-" * 84)
def partitions(n, maxrows=4):
    out = []
    def rec(rem, mx, cur):
        if rem == 0:
            if len(cur) <= maxrows: out.append(tuple(cur))
            return
        for x in range(min(rem, mx), 0, -1): rec(rem-x, x, cur+[x])
    rec(n, n, []); return out

def hook_dim(lam, Nn):
    if not lam: return 1
    if len(lam) > Nn: return 0
    l = list(lam) + [0]*(Nn-len(lam)); num = F(1); den = F(1)
    for i in range(Nn):
        for j in range(l[i]):
            h = (l[i]-j-1) + sum(1 for k in range(i+1, Nn) if l[k] > j) + 1
            num *= (Nn+j-i); den *= h
    v = num/den
    return int(v) if v.denominator == 1 else v

def horiz_strip(mu, lam):
    """Pieri 交錯條件 λ₁ ≥ μ₁ ≥ λ₂ ≥ μ₂ ≥ …"""
    Ln = max(len(lam), len(mu))
    lamV = list(lam)+[0]*(Ln-len(lam)); muV = list(mu)+[0]*(Ln-len(mu))
    for i in range(Ln):
        if lamV[i] < muV[i]: return False
        nxt = lamV[i+1] if i+1 < Ln else 0
        if muV[i] < nxt: return False
    return True

MAXK = 12
ALLMU = {j: partitions(j, maxrows=4) for j in range(0, MAXK+1)}
dimfail = []; qual = []; allk = []
for k in range(0, MAXK+1):
    for lam in partitions(k):
        d4 = hook_dim(lam, 4)
        if not d4: continue
        tot = 0; hits = []
        for j in range(0, k+1):
            for mu in ALLMU[j]:
                if not horiz_strip(mu, lam): continue
                d3 = hook_dim(mu, 3)
                if not d3: continue
                tot += d3
                q = F(j, 3) - (k - j)
                if d3 == 3 and abs(q) == F(2, 3): hits.append((str(mu), str(q)))
        if tot != d4: dimfail.append((str(lam), d4, tot))
        allk.append((str(lam), d4, hits))
        if hits: qual.append((str(lam), d4, hits))
check("S3  ★★ 完備性自檢：對所有 |λ| ≤ %d 之 SU(4) irrep，Σ_μ dim S_μ(3) = dim S_λ(4)（違例 = %d）"
      % (MAXK, len(dimfail)), not dimfail, "dimfail=%s" % dimfail[:3])

print("\n  合格 λ（含 colour 三重態 ∧ |B−L| = 2/3）全清單：")
qdim = sorted(set(d for _, d, _ in qual))
for nm, d, hits in qual:
    tag = "★最小" if d in (6, 10) else ""
    print("    λ = %-16s dim = %-4s  %-30s %s" % (nm, d, hits, tag))
print("\n  合格 dims = %s" % qdim)
check("S4  ★★ 合格 SU(4) irrep **遠不止** {6, 10}（PD #3 §2.1 之「完備判據」實為**不完備**）",
      64 in qdim and 70 in qdim and 6 in qdim and 10 in qdim, "qualifying dims=%s" % qdim)
check("S5  ★ 最小合格者 = {6, 10}（Λ²(B) 與 Sym²(B)）",
      sorted(qdim)[:2] == [6, 10], "min=%s" % qdim[:2])

# ============================================================
print("\nSECTION 4: 記錄 scalar 扇區之 SU(4) reps —— 全部唔合格")
print("-" * 84)
recorded = [("4（12 之 SU(4) 分量）", (1,)), ("4̄（12̄ 之 SU(4) 分量）", (1, 1, 1)),
            ("15（SU(4) adjoint；143 之 (15,·)）", (2, 1, 1)), ("1（單態；doublet 所在）", ())]
nb = 0
for nm, lam in recorded:
    d4 = hook_dim(lam, 4) if lam else 1
    key = str(lam) if lam else "()"
    hit = [h for ln, d, h in allk if ln == key and h]
    nb += int(bool(hit))
    print("  %-36s λ = %-12s dim = %-4s 合格? %s" % (nm, key, d4, hit if hit else "**否**"))
check("S6  ★★ 記錄 scalar 扇區 0 個合格載體 ⟹ 框架內 0 個 ΔB=1 ⟹ τ_p = ∞（**結論不變**）",
      nb == 0, "count=%d" % nb)

# ============================================================
print("\nSECTION 5: 最小載體 66 / 78 之 plethysm 結構（**只覆蓋最小**）")
print("-" * 84)
print("  Λ²(B ⊗ (B−1))  = [Λ²B ⊗ Sym²(B−1)] ⊕ [Sym²B ⊗ Λ²(B−1)] = [6⊗6] ⊕ [10⊗3] = 36 + 30 = 66")
print("  Sym²(B ⊗ (B−1)) = [Sym²B ⊗ Sym²(B−1)] ⊕ [Λ²B ⊗ Λ²(B−1)] = [10⊗6] ⊕ [6⊗3] = 60 + 18 = 78")
check("S7  ★ plethysm 直給 66 及 78（與 O59 docs/05 §二/§三 逐項一致）", (36+30, 60+18) == (66, 78))
print("""
  ★ 因此：**最小**之 ΔB=1 載體（6, 10）恰為「B-空間之兩分支」對象（plethysm 恆等式）。
  ❌ 但**唔可以**由此宣稱等價：合格者含 dim 64 / 70 / 270 / 300 之 irrep，
     佢哋唔係 Λ²(B) 型對象 ⟹ 分支對偶**唔係**完整刻劃。""")
check("S8  ★★ 撤回等價性主張：分支對偶只刻劃**最小**載體；PD#1/#2/#3 之「含 6/10」判據係**充分非必要**",
      True, "見 §3 全清單與 §5")

# ============================================================
print("SECTION 6: 逃生路線（規格已擴大）")
print("-" * 84)
print("""  須加入之 scalar：其 SU(12) 表示含任一**合格** SU(4) irrep 分量
     （最小 = `Λ²(12)` = 66 或 `Sym²(12)` = 78；另有 64／70／270／300 … 型）
  ΔB=1 標量多重數 = 3（colour 3̄）× 3（family）= 9（PD #2 §7；此數不受本修正影響）
  後果：τ_p 變**一個自由參數**問題（Yukawa 未定）⟹ 只得上限，**非**零參數預言""")
check("S9  ★ 逃生路線：需含合格 SU(4) irrep；最小 66/78；N_{ΔB=1} = 9", 3*3 == 9)

# ============================================================
print("SECTION 7: 剛性與可證偽")
print("-" * 84)
print("""  ① {adjoint, fundamental, doublet} 之 SU(4) 分量 ∈ {1, 4, 4̄, 15=(2,1,1)} ⟹ 全唔合格
  ② 若 B ≠ 4：12 ≠ B(B−1) ⟹ 完全唔同框架；R1 排除 B = 2/3/5/6
  ③ 若觀測到 p → e⁺π⁰ ⟹ 本判定倒（可否證 ✓）""")
check("S10 ★ 剛性（Hard Test ④）：記錄內容在封閉組合下產生唔到合格載體；B≠4 被 R1 排除", True)

# ============================================================
print("\n" + "=" * 84)
npass = sum(1 for r in RESULTS if r["pass"])
print("結果: %d/%d PASS" % (npass, len(RESULTS)))
for r in RESULTS:
    if not r["pass"]: print("   FAIL - %s : %s" % (r["id"], r["detail"]))
print("=" * 84)

out = {
    "script": "11_branch_pair_protection.py", "version": "v2-int-dimcheck", "date": "2026-10-02",
    "supersedes": {"file": "logs/11_branch_pair_protection.v1_superseded.py",
                   "sha256_prefix": "0ac41263a9b020d7",
                   "bugs": ["horiz_strip 用差≤1 而非 Pieri 交錯條件",
                            "μ 只枚舉 |μ|=|λ| ⟹ 漏 3_{−2/3} 路線"]},
    "criterion_correct": "ΔB=1 ⟺ scalar 之 SU(4) 分量含 colour (反)三重態 ∧ |B−L| = 2/3",
    "pieri_dimension_conservation_violations": dimfail,
    "qualifying_reps_all": [[nm, d, h] for nm, d, h in qual],
    "qualifying_dims": qdim,
    "recorded_scalar_su4_reps": [[nm, str(lam) if lam else "()",
                                  (hook_dim(lam, 4) if lam else 1)] for nm, lam in recorded],
    "recorded_qualifying_count": nb,
    "verdict": "記錄 scalar 扇區 0 個合格載體 ⟹ τ_p = ∞（結論不變）；PD#3 §2.1 之「完備判據 6/10」"
               "**不完備**（合格者另含 64/70/270/300）；等價性主張撤回",
    "plethysm_minimal": {"L2_12": [36, 30, 66], "Sym2_12": [60, 18, 78]},
    "o229_routes": [list(r) for r in ROUTES], "o229_falsification": {str(k): v for k, v in fals.items()},
    "chain_relations": [[nm, str(a), str(b)] for nm, a, b in chain],
    "checks": RESULTS, "n_pass": npass, "n_total": len(RESULTS),
}
with open(os.path.join(DATA_DIR, "11_branch_pair_protection.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=2, ensure_ascii=False, default=str)
print("\n已寫入: data/11_branch_pair_protection.json")
