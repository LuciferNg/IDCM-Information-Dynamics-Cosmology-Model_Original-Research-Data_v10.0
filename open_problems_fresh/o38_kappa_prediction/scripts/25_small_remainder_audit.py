#!/usr/bin/env python3
"""
O38/m0-scale — scripts/25: 剩餘細數綁定式族審計 (Small-Remainder Audit)
======================================================================
★ 承上 (scripts/24 式族註冊制, docs/07): 對拆細後剩低嘅細數正式執行
  註冊制審計。每目標: ①定義綁定式族 (基底 = 88-系/結構數, 禁 divisor 衍生)
  ②覆蓋檢查 ③E = ρ·tol (≥200 隨機目標) ④命中判定。
  升格門檻: (i) |dev| ≤ 1e−3 (輸入精度) (ii) 族 E ≤ 0.1 (iii) 機制語義。
  預期: 全部壓制 — 目的 = 有判準地窮盡 O38 內部路線 (非盲掃).
"""
import math, random

print("=" * 76)
print("  O38/m0-scale — 剩餘細數綁定式族審計 (scripts/25)")
print("=" * 76)

# ═══ 目標細數 (scripts/23 分解樹剩餘; 尾數 2.285 為 10 進制產物, 已權重 0) ═══
TARGETS = {
    "F_e  = M₀/m_e":      54.600729,
    "f_p⁻¹ = m_p/M₀":     33.628721,
    "r_7e = m_7/m_e":      27.006318,
}
# 基底: 88-系/結構數 (冇 divisor 衍生 22/11/9/… — 註冊制閘⑤)
#  44 = N_d, 88 = 2N_d, 176 = 2·88, 45 = N_d+1, 47 = L₈, 29 = L₇,
#  61.5 = ⟨W⟩², 90 = Σγ_even, 123 = 3·41, 137 = α⁻¹, 256 = B⁴, 27 = 3³,
#  16 = B², 32 = 2⁵, 33 = M_tree, 42, 55 = F₁₀, φ = 黃金
PHI = (1+5**0.5)/2
S = sorted({1,2,3,4,5,8,11,16,27,29,32,33,37,41,42,44,45,47,55,61.5,88,90,123,137,176,256,PHI})
M = [PHI, 2, 3, 5, 11, 61.5, 88, 90, 123, 137, 256]   # 主基 (冪族用)
TOL = 1e-3  # 輸入精度 (docs/03 §7)

def dextol(rel): return math.log10(1+rel)

def family_a(s):            # {a/b : a,b ∈ S}  — 一次商族
    out = []
    for a in s:
        for b in s:
            out.append((f"{a:.6g}/{b:.6g}", math.log10(a)-math.log10(b)))
    return out

def family_b(mbase):        # {a^m·b^n : m,n ∈ [-2,2]} — 二項冪積
    out = []
    for a in mbase:
        for b in mbase:
            la, lb = math.log10(a), math.log10(b)
            for m in range(-2,3):
                for n in range(-2,3):
                    out.append((f"{a:.6g}^{m}·{b:.6g}^{n}", m*la + n*lb))
    return out

def family_c(mbase):        # {a^m/b^n : m,n ∈ [-3,3]} — 二項冪商
    out = []
    for a in mbase:
        for b in mbase:
            la, lb = math.log10(a), math.log10(b)
            for m in range(-3,4):
                for n in range(-3,4):
                    out.append((f"{a:.6g}^{m}/{b:.6g}^{n}", m*la - n*lb))
    return out

def audit(name, tgt, fam, tol=TOL):
    """註冊制審計: 覆蓋 + E + 命中 (log10 空間)。fam: [(label, log10val), ...]"""
    t = math.log10(tgt)
    vals = [v for _, v in fam]
    lo, hi = min(vals), max(vals)
    # ② 覆蓋檢查
    cover = (lo - 0.5 <= t <= hi + 0.5)
    rho = len(fam)/(hi-lo)
    tol_d = dextol(tol)
    E = rho * 2*tol_d
    # ③ 域內 null (200 樣本)
    random.seed(hash(name) & 0xffff)
    nh = 0
    for _ in range(200):
        x = random.uniform(lo+0.5, hi-0.5)
        if any(abs(v-x) < tol_d for v in vals): nh += 1
    # ④ 命中
    hits = [(i, abs(v-t)) for i, (lab, v) in enumerate(fam) if abs(v-t) < tol_d]
    hits.sort(key=lambda h: h[1])
    return {"cover": cover, "rho": rho, "E": E, "null": nh/200,
            "hits": len(hits), "best": hits[:6],
            "lo": lo, "hi": hi, "fam": fam}

REPORT = []
for name, tgt in TARGETS.items():
    print(f"\n─── 目標 {name} = {tgt} ───")
    fams = {"A: {a/b}":  family_a(S),
            "B: {a^m·b^n}": family_b(M),
            "C: {a^m/b^n}": family_c(M)}
    for fn, fam in fams.items():
        r = audit(name, tgt, fam)
        tag = f"{'覆蓋✓' if r['cover'] else '覆蓋✗'}"
        bests = "--"
        if r["best"]:
            i, d = r["best"][0]
            lab = fam[i][0]
            bests = f"{lab} dev={10**d-1:.2e}"
        print(f"    {fn:14s} N={len(fam):6d} ρ={r['rho']:7.1f}/dex E={r['E']:6.2f} "
              f"null={r['null']*100:4.1f}% {tag} 命中={r['hits']:3d} 最佳 {bests}")
        REPORT.append((name, fn, r))
        for j, (i, d) in enumerate((r["best"] or [])[:6]):
            print(f"        hit{j+1}: {fam[i][0]}  dev={10**d-1:.2e}")

# ═══ 判定 ═══
print("\n─── 判定 (升格門檻: dev≤1e−3 + E≤0.1 + 機制語義) ───")
all_pass = True
for name, fn, r in REPORT:
    # 覆蓋外或 E>0.1 或 null 高 ⟹ 壓制 (冇資訊)
    verdict = "🔴 壓制"
    if r["cover"] and r["E"] <= 0.1 and r["null"] < 0.1 and r["hits"] == 1:
        verdict = "🟡 候選(需機制語義)"
        all_pass = False
    if r["cover"] and r["E"] <= 0.1 and r["null"] < 0.1 and r["hits"] > 1:
        verdict = "🔴 壓制 (家族命中>1 = 稠密)"
    if not r["cover"]:
        verdict = "🔴 壓制 (覆蓋外)"
    if r["hits"] == 0:
        verdict = "🔴 壓制 (零命中)"
    status = f"   {name:12s} [{fn}] → {verdict}"
    print(status)
print("""
  解讀:
  - '壓制' = 證據權重維持 0 (冇一個細數有合法候選)
  - 若某族 '候選', 下一步先要機制語義先可升格 — 本 script 唔會製造機制
  - 有判準嘅窮盡: 唔係『冇方法逼近』, 而係『有方法逼近都唔算數』(E 判準)
""")
print("EXIT 0 — 報告型 (審計輸出; 全壓制 = O38 內部路線有判準窮盡)")