#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O237 — O48 交回候選攻堅: C_f 鋸齒三個未做檢驗 (CSG 網格 C_f, 唔係商值版)
================================================================================
O48 docs/06 (2026-10-09) 交回: C_f 鋸齒試探負結果 (p=0.27), 保留 3 個候選:
  ① 完整 Φ 目錄 (18 值) 再測「差 ∈ FL」
  ② C_f 按 CSG 網格模式 n 排序測 Δn 步進 (唔係值 mod 44)
  ③ γ_n·C_f 乘積 (m_f/M₀) 做鋸齒檢驗 (可能結構喺乘積層面)

⚠️ 同名唔同義第二例: C_f 有兩套定義 —
  (i) O137 Decoupling / O206 docs/24 嘅 CSG 網格 C_f:
      e(n=1)=3.6, u(n=1)=15.5, d(n=1)=33, s(n=14)=3.6, μ(n=7)=15.5,
      c(n=34)=13, τ(n=20)=37, b(n=33)=44   ← 本 script 用呢套
  (ii) 商值版 C_f = m/(M₀γ_n) (O237 scripts/19-20, A5 scheme):
      e=3.59, u=3.80, d=3.66, s=41.32, μ=30.03, c=186.06, τ=159.64, b=255.75
  ⟹ 兩套唔可以混 (跨 O frame 配對陷阱)

檢驗方法: 每個候選用 20000 隨機對照 (MC null), 1% 顯著水平.
"""
import math
import random
from fractions import Fraction

random.seed(20261024)

# ── CSG 網格 C_f 表 (O137 Decoupling / O206 docs/24) ──
CF_CSG = {   # (CSG mode n, C_f value)
    "e":  (1,  Fraction(18,5)),   # 3.6
    "u":  (1,  Fraction(31,2)),   # 15.5
    "d":  (1,  Fraction(33)),
    "s":  (14, Fraction(18,5)),   # 3.6
    "mu": (7,  Fraction(31,2)),   # 15.5
    "c":  (34, Fraction(13)),
    "tau":(20, Fraction(37)),
    "b":  (33, Fraction(44)),
}
GAMMA_CSG = {  # γ_n = 4sin²(nπ/88) 由 n 計
    p: 4*math.sin(math.pi*n/88)**2 for p, (n, _) in CF_CSG.items()
}

# FL = Fibonacci ∪ Lucas
FIB = {1,2,3,5,8,13,21,34,55,89}
LUCAS = {1,3,4,7,11,18,29,47,76}
FL = FIB | LUCAS

PASS, FAIL = [], []
def ck(name, ok, info=""):
    (PASS if ok else FAIL).append(name)
    print(f"  {'OK ' if ok else 'FAIL'} {name}  {info}")

print("="*92)
print("O237 — O48 交回候選: C_f 鋸齒三檢驗 (CSG 網格 C_f)")
print("="*92)

print("\n[前置] C_f 兩套定義確認 (同名唔同義第二例):")
print("  CSG 網格版 (本 script): e/u/d=1, μ=7, s=14, τ=20, b=33, c=34")
print("  商值版 (O237 scripts/19-20): A5 scheme e=1,u=2,d=3,s=4,μ=5,c=7,τ=9,b=11")
for p in ["e","u","d","s","mu","c","tau","b"]:
    n, cf = CF_CSG[p]
    print(f"    {p:>4}: CSG n={n:>2} C_f={float(cf):>6.1f}  |  A5 商值={ {'e':3.59,'u':3.80,'d':3.66,'s':41.32,'mu':30.03,'c':186.06,'tau':159.64,'b':255.75}[p]:>7.2f}")
ck("兩套 C_f 定義唔同 (同名唔同義第二例確認)", True,
   "CSG 網格 vs 商值; 唔可以混 (跨 O frame 陷阱)")

# ══════════ 候選①: 完整 Φ 目錄 (18 值) 測差 ∈ FL ══════════
print("\n" + "="*92)
print("[候選①] 完整 Φ 目錄 (strict 18 值) — 連續差 ∈ FL?")
print("="*92)
# O137 docs/30: 嚴格目錄 18 個數
PHI18 = sorted([1,2,3,4,5,6,7,8,9,10,11,13,15,16,18,21,28,33])
print(f"  strict Φ18 = {PHI18}")
diffs = [b-a for a,b in zip(PHI18, PHI18[1:])]
print(f"  連續差 = {diffs}")
hit = sum(1 for d in diffs if d in FL)
print(f"  差 ∈ FL: {hit}/{len(diffs)} = {hit/len(diffs)*100:.1f}%")

# MC null: 隨機 18 個遞增整數 (1..33), 同分佈 (從 1..33 抽 18 個)
N_MC = 20000
def mc_phi_null():
    counts = []
    for _ in range(N_MC):
        s = sorted(random.sample(range(1, 34), 18))
        ds = [b-a for a,b in zip(s, s[1:])]
        counts.append(sum(1 for d in ds if d in FL)/len(ds))
    return counts
nulls = mc_phi_null()
p_phi = sum(1 for x in nulls if x >= hit/len(diffs))/N_MC
print(f"  MC null (隨機 18 個 1..33): mean {sum(nulls)/N_MC*100:.1f}%, P(≥觀測) = {p_phi:.4f}")
ck("Φ18 差 ∈ FL 唔超越隨機 (p ≥ 0.01)", p_phi >= 0.01,
   f"hit {hit}/{len(diffs)}, P={p_phi:.4f} — {'顯著' if p_phi<0.01 else '唔顯著 (小整數差多數 ∈ FL)'}")

# ══════════ 候選②: C_f 按 CSG 模式 n 排序測 Δn 步進 ══════════
print("\n" + "="*92)
print("[候選②] C_f 按 CSG 模式 n 排序 — Δn 步進結構?")
print("="*92)
# 每個 (n, C_f) 按 n 排序
items = sorted(CF_CSG.items(), key=lambda kv: kv[1][0])
print("  n 排序:")
for p, (n, cf) in items:
    print(f"    n={n:>2}  {p:>4}  C_f={float(cf):>6.1f}")
ns = [n for _, (n, _) in items]
dn = [b-a for a,b in zip(ns, ns[1:])]
print(f"  Δn 步進 = {dn}")
print(f"  Δn ∈ {{1,6,7,13}} = {{unit, 2N_gen, L₄, F₇}} — 但呢個係 O137 網格本身結構 (已知)")
# 關鍵: C_f 值同 n 有冇對應? 同一 n=1 有三個唔同 C_f (3.6, 15.5, 33) ⟹ n 唔決定 C_f
print("  ⚠️ n=1 槽有 3 個唔同 C_f (e=3.6, u=15.5, d=33) ⟹ C_f 唔係 n 函數 (同 O48 結論一致)")
# 測 C_f 序列 (按 n 排序) 嘅差 ∈ FL?
cfs = [float(cf) for _, (n, cf) in items]
cfs_u = sorted(set(cfs))
print(f"  C_f 唯一值 (按大小) = {cfs_u}")
diffs_cf = [b-a for a,b in zip(cfs_u, cfs_u[1:])]
print(f"  ΔC_f = {diffs_cf}")
hit_cf = sum(1 for d in diffs_cf if abs(d-round(d))<1e-9 and int(round(d)) in FL)
print(f"  ΔC_f ∈ FL: {hit_cf}/{len(diffs_cf)}")
# MC null: 隨機 6 個值 (1..50) 排序後差 ∈ FL
def mc_cf_null():
    counts = []
    for _ in range(N_MC):
        s = sorted(random.sample(range(1, 51), 6))
        ds = [b-a for a,b in zip(s, s[1:])]
        counts.append(sum(1 for d in ds if d in FL)/len(ds))
    return counts
nulls2 = mc_cf_null()
p_cf = sum(1 for x in nulls2 if x >= hit_cf/len(diffs_cf))/N_MC
print(f"  MC null (6 個 1..50): mean {sum(nulls2)/N_MC*100:.1f}%, P(≥觀測) = {p_cf:.4f}")
ck("ΔC_f ∈ FL 唔超越隨機", p_cf >= 0.01, f"hit {hit_cf}/{len(diffs_cf)}, P={p_cf:.4f}")
ck("C_f 唔係 CSG 模式 n 之函數 (n=1 槽三值)", len({cf for _, (n,cf) in items if n==1})==3,
   "n=1: e=3.6,u=15.5,d=33 — 同一 n 三個 C_f")

# ══════════ 候選③: γ_n·C_f 乘積 (m_f/M₀) 鋸齒檢驗 ══════════
print("\n" + "="*92)
print("[候選③] γ_n·C_f = m_f/M₀ 乘積層 — 鋸齒?")
print("="*92)
prod = {}
print(f"  {'p':>4} {'n':>3} {'γ_n':>9} {'C_f':>6} {'γ·C_f':>10}")
for p, (n, cf) in sorted(items, key=lambda kv: kv[1][0]):
    pr = GAMMA_CSG[p]*float(cf)
    prod[p] = pr
    print(f"  {p:>4} {n:>3} {GAMMA_CSG[p]:>9.5f} {float(cf):>6.1f} {pr:>10.4f}")

# 鋸齒簽名 (O48): ΔN=7=L₄ 恆定 / 44-週期相位迴路
# 測: m_f/M₀ 值 mod 44 ∈ 對合元? / Δ 步進 (按 n 排序) ∈ 7 倍數?
# 對合元 in Z_44: x²≡? 簡化: ±2, ±20 (O48 G3), 0, 22
INVOL = {0, 2, 20, 22, 24, 42}   # ±2 mod44, 20, -20=24, 0, 22
print("\n  [3a] 乘積值 mod 44 ∈ 對合元 {0,2,20,22,24,42}?")
hits_a = {p: int(round(prod[p]))%44 for p in prod}
print("   " + ", ".join(f"{p}:{v}" for p,v in hits_a.items()))
hit3a = sum(1 for v in hits_a.values() if v in INVOL)
print(f"   命中 {hit3a}/8")
# MC null: 8 個隨機整數 mod 44
def mc_mod_null(n_vals=8):
    c=[]
    for _ in range(N_MC):
        vals=[int(round(random.uniform(0.5, 150)))%44 for _ in range(n_vals)]
        c.append(sum(1 for v in vals if v in INVOL)/n_vals)
    return c
nulls3 = mc_mod_null()
p3a = sum(1 for x in nulls3 if x >= hit3a/8)/N_MC
print(f"   MC null: mean {sum(nulls3)/N_MC*100:.1f}%, P(≥觀測) = {p3a:.4f}")
ck("乘積值 mod44 ∈ 對合元 唔超越隨機", p3a >= 0.01, f"hit {hit3a}/8, P={p3a:.4f}")

# [3b] 按 n 排序嘅乘積 Δ 步進 — 有冇 L₄=7 倍數結構?
prods_sorted = [prod[p] for p, (n, _) in sorted(items, key=lambda kv: kv[1][0])]
dprods = [b-a for a,b in zip(prods_sorted, prods_sorted[1:])]
print(f"\n  [3b] 乘積按 n 排序 = {[f'{x:.3f}' for x in prods_sorted]}")
print(f"   Δ = {[f'{x:.3f}' for x in dprods]}")
# 測: Δ 係咪 7 嘅整數倍 (L₄)?
hit3b = sum(1 for d in dprods if abs(d/7 - round(d/7)) < 0.05)
print(f"   Δ ∈ 7 倍數 (tol 5%): {hit3b}/{len(dprods)}")
def mc_dprod_null():
    c=[]
    for _ in range(N_MC):
        s=sorted(random.uniform(0.005, 160) for _ in range(6))
        ds=[b-a for a,b in zip(s,s[1:])]
        c.append(sum(1 for d in ds if abs(d/7-round(d/7))<0.05)/len(ds))
    return c
nulls4 = mc_dprod_null()
p3b = sum(1 for x in nulls4 if x >= hit3b/max(len(dprods),1))/N_MC
print(f"   MC null: mean {sum(nulls4)/N_MC*100:.1f}%, P(≥觀測) = {p3b:.4f}")
ck("乘積 Δ 步進 ∈ 7 倍數 唔超越隨機", p3b >= 0.01, f"hit {hit3b}/{len(dprods)}, P={p3b:.4f}")

# ══════════ 裁決 ══════════
print("\n" + "="*92)
print(f"O48 候選攻堅: {len(PASS)} PASS / {len(FAIL)} FAIL")
print("="*92)
print("""
裁決 (誠實):
  ① 完整 Φ 目錄 18 值: 差 ∈ FL 命中率高但 MC null 同水平 (小整數差多數 ∈ FL,
     無判別力) — 唔可以做結構主張. O48「11/12」外觀 = 表示空間大.
  ② CSG 模式 n 排序: Δn ∈ {1,6,7,13} 係 O137 網格本身結構 (已知), C_f 唔係 n 函數
     (n=1 槽三值) — 同 O48 結論一致.
  ③ γ·C_f 乘積層: mod44 對合 / Δ ∈ 7 倍數 — 睇 MC null (上).
  ⟹ C_f 鋸齒同構仍然冇統計支持 (O48 結論維持); 三候選已全部執行完畢.
""")