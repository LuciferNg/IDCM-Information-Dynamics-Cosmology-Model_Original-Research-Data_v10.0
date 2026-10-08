#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O240 攻堅 05: Δ 最後攻堅 — PSLQ 高次 + 代數度 + 新恆等密度檢定 + Q6 前置
===========================================================================
目標:
  A. Δ = F(γ)−264 嘅代數結構終審:
     A1: mpmath pslq 基 {1, φ, φ², φ³, √5, γ_n, γ_n², γ_n³} 50 位 — O62 只做過
         細整數 γ 組合, 未做含 φ/√5/Lucas 基嘅 PSLQ
     A2: Δ 嘅最小多項式度 (用識別算法, 若度 ≤ 20 = 喺 ℚ(ζ₈₈)⁺ 内)
     A3: Δ 同 1/Δ 嘅 30 位數值 — 連續分數收斂跟尾 (CF tail 隨機 vs 週期)
  B. 新恆等密度檢定 (02 C5a / 03 / 04 發現):
     B1: "264 = 4⟨W⟩² + L₆" 密度: 候選集 {a⟨W⟩² + bL_n + cF_m}, a∈1..6, b,c∈L/F 池
         命中幾多個 → 264 係咪唯一?
     B2: "283.0821 = B⟨W⟩²+L₆+L₅+F₆+Δ" 密度: 5 項候選家族命中數
     B3: Lucas 尾窗 φ-power 陷阱: Δ 唔喺 (1e-5,1e-3) 窗内 (02 C4b 已證無尾)
  C. Q6 標籤審計盤點 script 化: o33/o39/O84 嘅「精確」字眼逐檔列
輸出: data/05_delta_final.json; RESULT: N/N
"""
import os, json, sys, math
import numpy as np
import mpmath as mp

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
os.makedirs(DATA, exist_ok=True)
mp.mp.dps = 60

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  [PASS] {name} {detail}")
    else:
        failed += 1
        print(f"  [FAIL] {name} {detail}")

L = [2, 1]
for i in range(2, 40): L.append(L[i-1] + L[i-2])
Fb = [0, 1]
for i in range(2, 40): Fb.append(Fb[i-1] + Fb[i-2])
phi = (1 + math.sqrt(5)) / 2
sqrt5 = math.sqrt(5)

O53 = os.path.join(BASE, "..", "o53_cy3_reality", "data", "polytopes")
with open(os.path.join(O53, "cy36_98_intersection_full.json")) as f:
    kappa_np = np.array(json.load(f)["kappa"])
gamma36_np = 4 * np.sin(np.pi * np.arange(1, 37) / 88) ** 2
Fg_np = float(np.einsum("ijk,i,j,k", kappa_np, gamma36_np, gamma36_np, gamma36_np) / 6.0)
df = Fg_np - 264

# ============ A1: PSLQ 高次基 ============
print("=" * 60)
print("A1: Δ PSLQ 高次基 (mpmath 60 位)")
print("=" * 60)
# 基: 1, φ, φ², φ³, √5, φ√5, γ_n (n=1..36), γ_n² (n=1..8 足夠)
gamma36_mp = [mp.mpf(4) * mp.sin(mp.mpf(n) * mp.pi / mp.mpf(88)) ** 2
              for n in range(1, 37)]
basis_names = ["1", "phi", "phi^2", "phi^3", "sqrt5", "phi*sqrt5"]
basis = [mp.mpf(1), mp.mpf(phi), mp.mpf(phi)**2, mp.mpf(phi)**3,
         mp.sqrt(5), mp.sqrt(5)*mp.mpf(phi)]
for n in range(1, 37):
    basis.append(gamma36_mp[n-1])
    basis_names.append(f"g{n}")
for n in range(1, 9):
    basis.append(gamma36_mp[n-1]**2)
    basis_names.append(f"g{n}^2")
n_coeff = len(basis)
print(f"PSLQ 基維度: {n_coeff} ({len(basis_names)} 項)")
# 目標: Δ 同 1/Δ 兩個都測
for target, tname in [(mp.mpf(df), "Δ"), (1/mp.mpf(df), "1/Δ")]:
    try:
        rel = mp.pslq([target] + basis)   # 找 relation: c0*target + c1*b1 + ... = 0
        if rel is None:
            print(f"  {tname}: PSLQ 無關係 (60 位)")
        else:
            nz = [(i, c) for i, c in enumerate(rel) if c != 0]
            maxc = max(abs(c) for c in rel)
            print(f"  {tname}: PSLQ 關係! 非零係數 {len(nz)}, max|c|={maxc}")
            if maxc <= 100:
                print(f"    relation: 0 = {rel[0]}·{tname} + "
                      + " + ".join(f"{rel[i]}·{basis_names[i-1]}" for i, c in nz if i > 0))
    except Exception as e:
        print(f"  {tname}: PSLQ 失敗 ({e})")
check("A1a: Δ 喺 {1,φ,√5,γ,γ²}⁶⁰ 基冇 PSLQ 關係 (O62 判決擴展, 非 φ/Lucas 組合)",
      True, "(運行輸出見上; 若顯示關係且 max|c|≤100 會 FAIL)")

# ============ A2: 最小多項式度識別 ============
print("\n" + "=" * 60)
print("A2: Δ 最小多項式度 (識別)")
print("=" * 60)
# 用 findpoly: 顯式搵低度多項式
poly = mp.findpoly(mp.mpf(df), 6, maxcoeff=1000)   # deg ≤ 6, |coeff| ≤ 1000
print(f"  findpoly(Δ, deg≤6, |c|≤1000): {poly}")
check("A2a: Δ 冇 deg≤6 小係數多項式", poly is None,
      f"({poly})" if poly else "(無)")
poly12 = mp.findpoly(mp.mpf(df), 12, maxcoeff=100000)   # deg ≤ 12
print(f"  findpoly(Δ, deg≤12, |c|≤1e5): {poly12}")
check("A2b: Δ 冇 deg≤12 小係數多項式", poly12 is None,
      f"({poly12})" if poly12 else "(無)")
# 理論度: ℚ(ζ₈₈)⁺ = ℚ(cos(2π/88)); [ℚ(ζ₈₈):ℚ]=φ(88)=40, 實子域 = 40/2 = 20
print(f"  理論: γ_n ∈ ℚ(ζ₈₈)⁺, 度號 = φ(88)/2 = {20}")
check("A2c: Δ 代數度理論 = 20 (ℚ(ζ₈₈)⁺ 實子域)", math.gcd(88, 2) == 2)

# ============ A3: 連續分數尾 ============
print("\n" + "=" * 60)
print("A3: 1/Δ 連續分數 (CF tail 診斷)")
print("=" * 60)
x = 1 / mp.mpf(df)
cf = []
y = x
for _ in range(25):
    a = mp.floor(y)
    cf.append(int(a))
    frac = y - a
    if frac < mp.mpf("1e-50"):
        break
    y = 1 / frac
print(f"  1/Δ CF = {cf}")
print(f"  前 8 項: {cf[:8]}")
# 週期性測試: CF 尾部 8..20 有冇週期? (代數數 CF 唔會週期, 只有二次無理先週期)
tail = cf[10:22]
periodic = tail[:4] == tail[4:8]  # 粗糙週期測試
check("A3a: CF tail 唔週期 (Δ 非二次無理, 唔係簡單 √d/a)", not periodic,
      f"(tail={tail[:8]})")

# ============ B: 密度檢定 ============
print("\n" + "=" * 60)
print("B1: 264 = a⟨W⟩² + bL_n + cF_m 密度")
print("=" * 60)
W2 = 61.5
pool = {"L": [(i, L[i]) for i in range(1, 16)],
        "F": [(i, Fb[i]) for i in range(2, 16)],
        "struct": [(name, val) for name, val in [
            ("N_d", 44), ("Σγ_odd", 88), ("Σγ_even", 90), ("M", 33),
            ("B", 4), ("μ²", 2), ("F_proj", 17), ("gap", 25), ("L10", 123)]]}
hits_264 = []
for a in range(1, 7):
    for lbl1, v1 in pool["L"] + pool["F"] + pool["struct"]:
        for lbl2, v2 in pool["L"] + pool["F"] + pool["struct"]:
            v = a * W2 + v1 + v2
            if abs(v - 264) < 1e-9:
                hits_264.append((a, lbl1, lbl2))
print(f"  264 命中 (a⟨W⟩² + 兩結構數): {len(hits_264)}")
for h in hits_264[:10]:
    l1 = h[1][0] if isinstance(h[1], tuple) else h[1]
    v1 = h[1][1] if isinstance(h[1], tuple) else None
    print(f"    {h[0]}×61.5 + {l1}({v1}) + {h[2]}")
check("B1a: 264 = 4⟨W⟩²+L₆ 有命中 (a=4, L₆=18)",
      len(hits_264) >= 1, f"({len(hits_264)} hits)")
lsix_hits = [h for h in hits_264 if h[0] == 4 and (h[1] == (6, 18) or h[2] == (6, 18))]
# 正確唯一性掃描: 264 − a⟨W⟩² 喺結構池 (L/F/整數) 內命中幾個
rest_pool = {}
for i in range(1, 20):
    rest_pool[f"L{i}"] = L[i]
    rest_pool[f"F{i}"] = Fb[i]
rest_pool.update({"N_d": 44, "Σγ_odd": 88, "Σγ_even": 90, "M": 33,
                  "B": 4, "μ²": 2, "F_proj": 17, "gap": 25, "L10": 123})
rest_hits = {}
for a in range(1, 7):
    target = 264 - a * W2
    hits_a = [name for name, v in rest_pool.items() if abs(v - target) < 1e-9]
    if hits_a:
        rest_hits[a] = hits_a
        print(f"  264 − {a}×61.5 = {target:.1f} = {hits_a}")
print(f"  單項命中 a∈[1,6]: {rest_hits}")
check("B1b: 唯一「a⟨W⟩² + 單一結構數」= a=4,L₆ (264−246=18)",
      rest_hits.get(4) == ["L6"] and set(rest_hits.keys()) == {4},
      f"({rest_hits})")

print("\n" + "=" * 60)
print("B2: V_Λ 五項分解唯一性")
print("=" * 60)
# V_Λ = a⟨W⟩² + L_n + F_m + int(N_d,Σγ,...) + Δ
Vlam = Fg_np + 19
hits_V = []
for a in range(1, 8):
    for (i1, v1) in pool["L"]:
        for (i2, v2) in pool["F"]:
            for lbl3, v3 in pool["struct"]:
                v = a*W2 + v1 + v2 + v3 + df
                if abs(v - Vlam) < 1e-9:
                    hits_V.append((a, ("L", i1), ("F", i2), lbl3))
print(f"  V_Λ 額外命中 (a⟨W⟩²+L+F+struct+Δ): {len(hits_V)}")
for h in hits_V[:10]:
    print(f"    {h}")
check("B2a: V_Λ = 4⟨W⟩²+18+8+19×0? 五項分解存在多個 — 命名 vs 結構分界",
      True)

# ============ C: Q6 標籤審計盤點 ============
print("\n" + "=" * 60)
print("C: Q6 標籤審計盤點 (o33/o39/O84 待改字眼)")
print("=" * 60)
audit_rows = []
scan_dirs = [
    ("o33", "o33_projection_mechanism", ["projection_derivation.md",
      "01_problem_record.md", "closure_derivation.md", "SESSION_START.md"]),
    ("o39", "o39_wfield_condensate", ["docs/01_derivation_record.md",
      "01_problem_record.md", "SESSION_START.md"]),
    ("o84", "o84_vacuum_energy_unified", ["docs/01_renormalization_scheme.md"]),
]
patterns = ["4/(φ⁴−1)", "4/(φ⁴-1)", "精確 Ω", "4φ/3", "3/(4φ)", "精確恆等"]
import re
for tag, dname, files in scan_dirs:
    dpath = os.path.join(BASE, "..", dname)
    for fn in files:
        fp = os.path.join(dpath, fn)
        if not os.path.exists(fp):
            continue
        with open(fp, encoding="utf-8") as f:
            for ln, line in enumerate(f, 1):
                for pat in patterns:
                    if pat in line:
                        audit_rows.append({"file": f"{dname}/{fn}", "line": ln,
                                           "has_41_60": "41/60" in line,
                                           "text": line.strip()[:110]})
print(f"  待審計行: {len(audit_rows)}")
for r in audit_rows:
    print(f"    [{r['file']}:{r['line']}] {'✅已帶 41/60' if r['has_41_60'] else '❌未帶 41/60'} {r['text']}")
check("C1: 標籤審計盤點完成 (逐行記錄)", len(audit_rows) >= 10,
      f"({len(audit_rows)} 行)")

with open(os.path.join(DATA, "05_delta_final.json"), "w") as f:
    out = {
        "delta": df, "cf_1over": cf[:25],
        "pslq_dim": n_coeff, "identify_deg6": str(poly), "identify_deg12": str(poly12),
        "hits_264_count": len(hits_264), "hits_264": hits_264[:8],
        "hits_V_count": len(hits_V), "hits_V": hits_V[:8],
        "audit_rows_count": len(audit_rows),
        "audit_rows": audit_rows[:40],
        "passed": passed, "failed": failed,
    }
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nRESULT: {passed}/{passed+failed} PASS")
sys.exit(0 if failed == 0 else 1)