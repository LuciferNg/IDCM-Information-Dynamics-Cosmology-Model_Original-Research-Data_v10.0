#!/usr/bin/env python3
"""
O64 整合攻堅 01: A₅ 對齊重配 + scheme 裁定初步檢驗
================================================================
Audit 後第一擊 (docs/04 Route 2):
  A₅ 選擇律 (O136 docs/19) 選出 9 模式 {1,2,3,4,5,7,9,11,13}
  O64 原 assignment 用 {1,2,5,7,16,18,20,44} — 4/9 非法
  本 script: A₅ 模式下有冇可能用 C_f 池閉合 9 費米子?
"""
import math, json, itertools
import numpy as np

M0 = 27.9009
gam = lambda n: 4*math.sin(n*math.pi/88)**2
A5 = [1,2,3,4,5,7,9,11,13]
A5_gam = {n: gam(n) for n in A5}

# O206 docs/25 C_f 池 (CSSG-v3)
Cf_pool_206 = [3.6, 13, 15.5, 33, 37, 44, 1554]

# SM masses (統一 scheme 盡可能: PDG)
# 用 Nf=4 / MS̄ 2GeV 混合方案澄清 — 先列原始
sm = {
    'e': 0.511, 'mu': 105.66, 'tau': 1776.86,
    'u': 2.16, 'd': 4.67, 's': 93.4, 'c': 1270, 'b': 4180, 't': 172690,
}  # MeV (PDG MS̄/current)

print("="*76)
print("O64 整合 01: A₅ 對齊初步檢驗")
print("="*76)

# ==== 1. 基本結構 ====
print("\n=== [1] A₅ 9 模式 γ 值 ===")
print(f"{'n':>4s} {'γ_n':>10s} {'γ/γ₁':>8s}")
for n in A5:
    print(f"{n:>4d} {A5_gam[n]:>10.6f} {A5_gam[n]/A5_gam[1]:>8.4f}")

# ==== 2. 核心問題: A₅ 模式下 mass = M₀·γ_n·C_f 有冇解? ====
print("\n=== [2] m = M₀·γ_n·C_f 需要嘅 C_f (用 A₅ 模式) ===")
print(f"若 9 費米子按質量排序對應 A₅ 模式 (升序):")
print(f"  模式 {sorted(A5)}")
print(f"  質量升序: {sorted(sm.items(), key=lambda x:x[1])}")

# 實驗: 每個粒子嘅 required C_f = m/(M0*gamma_n) for each A5 n
print(f"\n  required C_f = m/(M₀·γ_n), 對每個 particle × 每個 A₅ n:")

results = []
for pname, m in sm.items():
    best = []
    for n in A5:
        cf = m / (M0 * A5_gam[n])
        best.append((n, cf))
    results.append((pname, m, best))
    # 顯示 closest to Cf_pool members
    hits = []
    for n, cf in best:
        for cpool in Cf_pool_206:
            if abs(cf - cpool)/cpool < 0.02:
                hits.append((n, cf, cpool))
    print(f"  {pname:>4s} (m={m:>9.2f}): A₅ n 全範圍 C_f ∈ [{best[0][1]:.2f}, ...]; 池命中: {hits if hits else '無'}")

# ==== 3. 最有信息量嘅檢查: C_f 池成員可以用度 ====
print("\n=== [3] C_f 池報告級檢查 — 每粒子 是否 有 A₅ n 使 m/(M₀γ_n) ∈ C_f 池 (±2%) ===")
print("池 = {3.6, 13, 15.5, 33, 37, 44, 1554}")
for pname, m in sm.items():
    metas = []
    for n in A5:
        cf = m / (M0 * A5_gam[n])
        for cpool in Cf_pool_206:
            dev = abs(cf - cpool)/cpool
            if dev < 0.02:
                metas.append((n, cf, cpool, dev*100))
    if metas:
        print(f"  ✅ {pname:>4s}: {metas}")
    else:
        print(f"  🔴 {pname:>4s}: 池中無命中 (±2%)")

# ==== 4. 全 C_f 池 × 全 A₅ 模式 窮舉分配 ====
print("\n=== [4] 窮舉: C_f 池 × A₅ 模式 → 9 費米子 分配 (RMS) ===")
# 為咗唔爆炸: 每粒子鬆綁 允許 C_f 池 + 結構數 (盧卡斯/菲波那契/44±) 
# 先做「每粒子最近池值」之 RMS
from math import sqrt
def pool_rms(asg):
    """asg: {pname: (n, cf)}"""
    errs = []
    for p, (n, cf) in asg.items():
        m_pred = M0 * A5_gam[n] * cf
        errs.append((m_pred - sm[p])/sm[p])
    return sqrt(sum(e*e for e in errs)/len(errs))

# 每粒子可選 (n, cf) 組合: n ∈ A5, cf ∈ Cf_pool_206
options = {}
for p in sm:
    opts = []
    for n in A5:
        for cf in Cf_pool_206:
            m_pred = M0 * A5_gam[n] * cf
            if 0.05 < m_pred/sm[p] < 20:  # 鬆 bound: 預測在 5%~2000%
                opts.append((n, cf, m_pred/sm[p]))
    options[p] = opts
    print(f"  {p:>4s}: {len(opts)} 個 (n,cf) 選項 (排好)", end="")
    if opts:
        # 最近目標嘅 3 個
        opts_sorted = sorted(opts, key=lambda x: abs(x[2]-1))
        print(f" — 最近: n={opts_sorted[0][0]}, cf={opts_sorted[0][1]}, m_pred/m={opts_sorted[0][2]:.4f}")
    else:
        print(" — 無選項!")

print(f"\n  (全部粒子都應該有選項; 冇 = A₅+C_f池 唔夠覆蓋)")

# ===== 簡單 greedy 分配 (冇 collision) =====
print("\n=== [5] Greedy 分配 (每粒子獨立揀最近, 唔容許同 n) ===")
used_n = set()
used_cf = set()
asg = {}
for p in sorted(sm, key=lambda x: sm[x]):  # 由細到大
    opts_sorted = sorted(options[p], key=lambda x: abs(x[2]-1))
    for n, cf, ratio in opts_sorted:
        if n not in used_n and cf not in used_cf:
            asg[p] = (n, cf, ratio)
            used_n.add(n); used_cf.add(cf)
            break
    else:
        asg[p] = None

for p in sorted(asg):
    v = asg[p]
    if v:
        print(f"  {p:>4s}: n={v[0]}, C_f={v[1]}, m_pred/m={v[2]:.4f}")
    else:
        print(f"  {p:>4s}: 無可用 (n 或 cf 撞)")

# RMS
errs = [abs(v[2]-1) for v in asg.values() if v]
if errs:
    rms = sqrt(sum(e*e for e in errs)/len(errs))
    print(f"\n  Greedy RMS (相對誤差): {rms*100:.2f}%")
    print(f"  覆蓋: {sum(1 for v in asg.values() if v)}/9")

# ==== 6. 結論 ====
print("\n=== [6] 初步結論 ===")
# 比較 O64 原 assignment (非 A₅) vs A₅ 可能性
print("""
O64 原 assignment (docs/03, 後驗):
  e(γ₁,3.6) μ(γ₇,15.5) τ(γ₂₀,37) u(γ₁,χSB) d(γ₂,χSB)
  s(γ₅,15.5) c(γ₁₈,15.5) b(γ₁₆,37√12) t(γ₄₄,37×42)
  → 4/9 非法模式 (τ20,c18,b16,t44)

O206 docs/25 assignment (另一套):
  e(1,3.6) μ(7,15.5) τ(20,37) u(1,15.5) d(1,33)
  s(14,3.6) c(34,13) b(33,44) t(44,1554) maxΔ 2.02%
  → 好多都唔喺 A₅ 集 (20,14,34,33,44)

A₅ 集 {1,2,3,4,5,7,9,11,13} 只有 9 個模式:
  若質量 = M₀·γ_n·C_f 必須全部用 A₅ → C_f 池要能覆蓋 390,000× 跨度

本 script 檢驗:
  C_f 池 {3.6,13,15.5,33,37,44,1554} × A₅ γ 跨度 (γ₁₃/γ₁ = 12.5×)
  → m 跨度 = 12.5 × max/min C_f
  → 需要 C_f 跨度 ≈ 390000/12.5 ≈ 31200×  池只有 1554/3.6 = 432×
  → C_f 池 + A₅ 唔夠跨 ⚠️ (除非有更大 C_f 或唔同公式)
""")

# 計算跨度
span_m = sm['t']/sm['e']
span_gamma_a5 = A5_gam[13]/A5_gam[1]
span_cf = 1554/3.6
print(f"  質量跨度 t/e = {span_m:.0f}×")
print(f"  A₅ γ 跨度 = {span_gamma_a5:.1f}×")
print(f"  C_f 池跨度 = {span_cf:.1f}×")
print(f"  γ×C_f 跨度 = {span_gamma_a5*span_cf:.0f}× vs 需要 {span_m:.0f}× → {'✅ 夠' if span_gamma_a5*span_cf>=span_m else '🔴 唔夠'}")

# Save
out = {"audit_date": "2026-10-11", "A5": A5, "cf_pool": Cf_pool_206,
       "span_m": span_m, "span_gamma_a5": span_gamma_a5, "span_cf": span_cf,
       "notes": "初步檢驗 — A₅+C_f 池跨度 vs 質量跨度"}
with open("data/01_a5_alignment.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("\n✅ 已儲存 data/01_a5_alignment.json")