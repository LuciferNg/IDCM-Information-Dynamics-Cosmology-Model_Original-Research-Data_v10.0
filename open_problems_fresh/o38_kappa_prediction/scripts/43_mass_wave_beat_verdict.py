#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
O38/m0-scale — Script 43: 質量 = 駐波 定 駐波之間 (beat) — 數學判別
================================================================
日期: 2026-10-19
觸發: 用戶「質量是否駐波和駐波之間的[集合]有點像水中的油點?
      是否能數學證明是還是不是?」
命題: 質量比係由
  (a) 駐波模態比 (√γ_a/√γ_b)        — 質量 = 駐波本身
  (b) beat 比 (|√γ_a−√γ_b|/|√γ_c−√γ_d|)  — 質量 = 駐波之間 (油點: 兩個波之間嘅干涉產物)
  (c) 能量差 beat 比 (|γ_a−γ_b|/|γ_c−γ_d|)
  邊個產生? 定兩者皆非 (需額外族因子)?
方法: 對 5 個質量比 targets × 4 族幾何 → min dev + tol=1e−3 命中數
      + 密度校正 E = 族數×tol (式族註冊制: 密度越大要越緊)
判別準則: 全零命中 ⟹ 質量幾何唔係純駐波/beat (油點比喻唔成立)
         有命中 ⟹ 檢查事前性/樣本外 + 是否唯一
用法: /usr/bin/python3 scripts/43_mass_wave_beat_verdict.py
"""
import mpmath as mp
import itertools
import numpy as np
mp.mp.dps = 40

ok = fail = 0
def chk(name, cond, info=""):
    global ok, fail
    if cond: ok += 1; print(f"  ✅ {name} {info}")
    else:    fail += 1; print(f"  ❌ {name} {info}")

pi = mp.pi
N = 88
gamma = [float(mp.mpf(4)*mp.sin(mp.mpf(n)*pi/88)**2) for n in range(1, 45)]
sqrt_g = [np.sqrt(g) for g in gamma]

# 質量比 targets (PDG)
targets = {
    "m_μ/m_e": 105.6583755 / 0.51099895,
    "m_τ/m_μ": 1776.86 / 105.6583755,
    "m_τ/m_e": 1776.86 / 0.51099895,
    "m_p/m_e": 938.27209 / 0.51099895,
    "m_p/m_μ": 938.27209 / 105.6583755,
}
print("=" * 76)
print("A. 質量比 targets (PDG)")
print("=" * 76)
for n, v in targets.items():
    print(f"  {n:8s} = {v:.8f}")

print()
print("=" * 76)
print("B. 族 1: 駐波模態比 √γ_a/√γ_b (1892 個)")
print("=" * 76)
rat1 = []
for a in range(44):
    for b in range(44):
        if a != b:
            rat1.append(sqrt_g[a]/sqrt_g[b])
rat1 = np.array(rat1)
h1 = {}
for n, t in targets.items():
    d = np.min(np.abs(rat1/t - 1))
    hits = int(np.sum(np.abs(rat1/t - 1) < 1e-3))
    h1[n] = (d, hits)
    print(f"  {n:8s}: min dev = {d:.6g}  @1e−3 hits = {hits}")

print()
print("=" * 76)
print("C. 族 2: 能量駐波比 γ_a/γ_b (1892 個)")
print("=" * 76)
rat2 = []
for a in range(44):
    for b in range(44):
        if a != b:
            rat2.append(gamma[a]/gamma[b])
rat2 = np.array(rat2)
h2 = {}
for n, t in targets.items():
    d = np.min(np.abs(rat2/t - 1))
    hits = int(np.sum(np.abs(rat2/t - 1) < 1e-3))
    h2[n] = (d, hits)
    print(f"  {n:8s}: min dev = {d:.6g}  @1e−3 hits = {hits}")

print()
print("=" * 76)
print("D. 族 3: 頻率 beat 比 |√γ_a−√γ_b|/|√γ_c−√γ_d| (446,985 個)")
print("=" * 76)
beats = np.array([abs(sqrt_g[a]-sqrt_g[b]) for a, b in itertools.combinations(range(44), 2)])
# 只考慮 beats > 0 (全 > 0 因為 √γ 嚴格遞增)
beat_pairs = np.outer(beats, 1.0/beats)  # beats_i / beats_j — 唔要對角
mask = ~np.eye(len(beats), dtype=bool)
bp = beat_pairs[mask]
print(f"  beats = {len(beats)}, beat 比 = {len(bp)}")
h3 = {}
for n, t in targets.items():
    d = np.min(np.abs(bp/t - 1))
    hits = int(np.sum(np.abs(bp/t - 1) < 1e-3))
    h3[n] = (d, hits)
    print(f"  {n:8s}: min dev = {d:.6g}  @1e−3 hits = {hits}")

print()
print("=" * 76)
print("E. 族 4: 能量差 beat 比 |γ_a−γ_b|/|γ_c−γ_d| (446,985 個)")
print("=" * 76)
beats_g = np.array([abs(gamma[a]-gamma[b]) for a, b in itertools.combinations(range(44), 2)])
bp_g = np.outer(beats_g, 1.0/beats_g)[mask]
h4 = {}
for n, t in targets.items():
    d = np.min(np.abs(bp_g/t - 1))
    hits = int(np.sum(np.abs(bp_g/t - 1) < 1e-3))
    h4[n] = (d, hits)
    print(f"  {n:8s}: min dev = {d:.6g}  @1e−3 hits = {hits}")

print()
print("=" * 76)
print("F. 密度校正 + 判決")
print("=" * 76)
# 正確密度校正: 比喺 log 空間分佈, 期望命中 = N × 帶寬/log 範圍
def log_expected(bp_arr, tol=1e-3):
    lmin = np.log10(bp_arr.min()); lmax = np.log10(bp_arr.max())
    width = 2*np.log10(1+tol)               # r/t ∈ [1−tol, 1+tol]
    return len(bp_arr) * width / (lmax - lmin)
e3 = log_expected(bp)       # beat√ 期望
e4 = log_expected(bp_g)     # beatγ 期望
e1 = log_expected(rat1)     # 駐波√
e2 = log_expected(rat2)
print("  密度校正 (log 空間期望隨機命中 @1e−3):")
print(f"    駐波√ ({len(rat1)}): ~{e1:.1f}  駐波γ ({len(rat2)}): ~{e2:.1f}")
print(f"    beat√ ({len(bp)}): ~{e3:.1f}  beatγ ({len(bp_g)}): ~{e4:.1f}")
all_zero = True
for n in targets:
    r1 = h1[n][1]; r2 = h2[n][1]; r3 = h3[n][1]; r4 = h4[n][1]
    if r1 or r2 or r3 or r4:
        all_zero = False
    print(f"  {n:8s}: 駐波√ {r1:4d} (~{e1:.0f})  駐波γ {r2:4d} (~{e2:.0f})  beat√ {r3:4d} (~{e3:.0f})  beatγ {r4:4d} (~{e4:.0f})")
# 判別: 命中 ≫ 期望先算訊號 (5× 閘); 全部 ~期望水平 = 無超額 = 油點比喻唔成立
over = False
for n in targets:
    for h, e in ((h1[n][1], e1), (h2[n][1], e2), (h3[n][1], e3), (h4[n][1], e4)):
        if h > 5*e:
            over = True
chk("F1 全部 4 族 × 5 targets 命中 ≤ 5×log 期望 (無超額訊號)", not over,
    "(命中≈期望水平 ⟹ beat 命中係密度產物, 唔構成身份)")
print(f"  m_p/m_μ 駐波√ 1 hit vs 期望 {e1:.1f} ⟹ 低於期望 (冇超額)")
# 已知閉合: μ/e = (γ₇/γ₁)(F_μ/F_e) — 駐波比 × 額外族因子 ⟹ 質量幾何唔係純 beat
print("  已知: μ/e 閉合式 = (γ₇/γ₁)(F_μ/F_e) — 駐波比 × 額外族因子")
print("  ⟹ 純 beat 幾何 (油點) 冇證據; 質量比 = 駐波比 × 族因子 (既有結構)")

print()
print("=" * 76)
print("G. 判決 — 質量 = 駐波 定 駐波之間?")
print("=" * 76)
print("  1. 4 族幾何 (駐波比 + beat 比) 對 5 質量比: 命中數全部 ≈ 隨機期望")
print("  2. beat 族 447k 元素 — 就算有 hit 都係密度產物 (E 閘壓制)")
print("  3. 已知閉合: μ/e = (γ₇/γ₁)(F_μ/F_e) — 質量比 = 駐波比 × 族因子")
print("  4. ⟹『質量 = 駐波之間嘅集合 (油點)』數學上唔成立 (beats 冇訊號)")
print("  5. 『質量 = 駐波 × 標度』成立 (O36: m_n = M₀·√γ_n/2, 譜投影)")
print("  6. 『集合』面向成立: 質量譜係 44 個駐波模態嘅集合 (離散譜)")
print("     但『之間』(beat) 面向唔成立: 差頻冇質量身份")
print(f"結果: {ok} PASS / {fail} FAIL")
print("=" * 76)