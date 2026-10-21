#!/usr/bin/env python3
"""
O256 — Script 05: 44 模態完整 integration-by-sum + 背景權重解剖
================================================================
R1 核心: O83 嘅 C_ℓ = Σ w_n² G_n(0) δ_{ℓ,ℓ_n} 只兌現 7 個峰。
本 script 兌現全部 44 個模態權重 — 其餘 37 個模態 (n=8..44)
權重和 = ΣG0[n=8..44] = 42% total! 呢 42% 就係「連續背景」:

  Σ_{n=1}^{44} G_n(0) = 32.3586
  Σ_{n=1}^{7}  G_n(0) = 18.63  (峰, 58%)
  Σ_{n=8}^{44} G_n(0) = 13.73  (背景, 42%)

Q1: 背景點分配? 結構候選:
  B1: 37 模態同權重均勻落喺 ℓ∈[1418, 3000] (連續譜冇峰)
  B2: 37 模態按 γ_n 光譜密度 (arcsine) 落到 ℓ∈[44×32, L_TOP+...]
  B3: 峰後背景 ∝ Σ_{n>m} G_n(0)·Lorentz(ℓ−ℓ_m, γ) — 唔係, 峰已經有
  B4: 最後峰後 tail 全部由「37 模態」嘅 G0 權重構成

禁區: 唔 fit — 只檢驗結構候選預言 λ(ℓ).
"""
import math, sys
import numpy as np

PASS, FAIL, TOTAL = 0, 0, 0
def check(name, cond, detail=""):
    global PASS, FAIL, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {detail}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {detail}")

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat"
N_d, M, F6, F8 = 44, 33, 8, 21

def C(n, k):
    from math import comb
    return comb(n, k) if n >= k >= 0 else 0

def peak_pos(m):
    if m == 5:
        return 44*(M-F6)+F8
    return 44*(M-C(9-m,2)) + ((m-1)*9) % 25

A_O83 = {1: 1.0, 2: (2/3)**2, 3: 4/9, 4: (3/7)**2, 5: 3/14, 6: (4/11)**2, 7: 1/7}
OBS_ELL = {1: 221, 2: 537, 3: 810, 4: 1014, 5: 1121, 6: 1340, 7: 1409}

print("="*76)
print("1. 44 模態權重解剖 (O83 basis)")
print("="*76)
G0 = np.array([1/(4*math.sin(math.pi*n/88)) for n in range(1,45)])
S_total = G0.sum()
S_7 = G0[:7].sum()
S_rest = G0[7:].sum()
print(f"  ΣG0[1..44] = {S_total:.4f}")
print(f"  ΣG0[1..7]  = {S_7:.4f}  ({S_7/S_total*100:.1f}%)  ← 峰")
print(f"  ΣG0[8..44] = {S_rest:.4f}  ({S_rest/S_total*100:.1f}%)  ← 背景 (未兌現)")
check("背景權重 > 40%", S_rest/S_total > 0.40, f"({S_rest/S_total*100:.1f}%)")

# ── 2. 背景候選 B1: 37 模態均勻落喺 ℓ=1452..3000 ────────────────
print("\n" + "="*76)
print("2. B1: 37 模態均勻背景 ℓ∈[1452,3000] + 7 峰 Lorentz tail")
print("="*76)
l_grid = np.arange(200, 3001, 2)
GAMMA = 306.0/8.0
# 峰 (Lorentzian)
C_peak = np.zeros_like(l_grid, dtype=float)
for m in range(1,8):
    lm = OBS_ELL[m]
    C_peak += A_O83[m]*(GAMMA/math.pi)/((l_grid-lm)**2+GAMMA**2)
# 均勻背景: C = const (37 模態同權重)
BG = np.zeros_like(l_grid, dtype=float)
mask_bg = l_grid >= 1452
BG[mask_bg] = S_rest/ (37.0*(3000-1452) / (l_grid[1]-l_grid[0]))   # per-bin 權重
# 相對標度: 峰嘅絕對權重 vs 背景權重 — 用「權重和」比例
# 峰 m 權重 = A_O83[m] (A₁ 標度), 背景 = S_rest/37 per 模態 → 要歸一化
# 簡化: 峰 C_peak 已歸一化到 A₁(=1), 背景 per 模態權重 = G0[n]/G0[1]?
# ⟹ 用「峰嘅總權重」對比背景權重 — 但 A 同 G0 唔同單位
# 呢度純形態檢驗: λ(ℓ) 由 C 形狀決定, 唔受整體標度影響
C_B1 = C_peak + BG*0.01   # 背景幅度探索: 1% 峰高
print(f"  形態檢驗 (λ 由形狀定):")

segs = [(1418,1700),(1700,2000),(2000,2400),(2400,3000)]
obs  = {(1418,1700):308,(1700,2000):410,(2000,2400):420,(2400,3000):646}
print(f"  {'段':>14} {'λ峰only':>9} {'λB1(1%)':>9} {'λ_obs':>7}")
for bg_amp in [0.0, 0.005, 0.01, 0.02, 0.05]:
    Cb = C_peak + BG*bg_amp
    row = [f"{bg_amp*100:g}%"]
    for (a,b) in segs:
        msk = (l_grid>=a)&(l_grid<b)
        sl = np.polyfit(l_grid[msk], np.log(Cb[msk]), 1)[0]
        row.append(f"{-1/sl:7.1f}")
    print("  " + "  ".join(row))
print("  對照 obs: 1418-1700=308, 1700-2000=410, 2000-2400=420, 2400-3000=646")

# ── 3. 背景候選 B2: arcsine γ光譜密度 → ℓ (O202 已整族證偽, 只作對照) ─
print("\n" + "="*76)
print("3. B2 對照: arcsine 背景 (O202 E1 已證偽 — 唔會好)")
print("="*76)
# O202 docs/07: E1 arcsine KS=0.4796, 標度選擇性無 — 唔重複

# ── 4. 關鍵: 峰形 γ 探討 — Lorentz γ 影響尾長度 ─────────────────
print("\n" + "="*76)
print("4. 峰尾結構: Lorentz γ 值掃描 (結構候選唔係 fit)")
print("="*76)
# 結構候選 γ: 峰間隙/8=38.25, /6=51, /4=76.5, /3=102, /2=153, =306
for gname, gamma in [("峰間隙/8=38.25", 38.25), ("峰間隙/6=51", 51.0),
                     ("峰間隙/4=76.5", 76.5), ("峰間隙/3=102", 102.0),
                     ("峰間隙/2=153", 153.0), ("峰間隙=306", 306.0)]:
    Cp = np.zeros_like(l_grid, dtype=float)
    for m in range(1,8):
        lm = OBS_ELL[m]
        Cp += A_O83[m]*(gamma/math.pi)/((l_grid-lm)**2+gamma**2)
    row = [f"{gname:>16}"]
    for (a,b) in segs:
        msk = (l_grid>=a)&(l_grid<b)
        sl = np.polyfit(l_grid[msk], np.log(Cp[msk]), 1)[0]
        row.append(f"{-1/sl:7.1f}")
    print("  " + "  ".join(row))

print("\n" + "="*76)
print(f"RESULT: {PASS}/{TOTAL} PASS (FAIL={FAIL})")
print("="*76)
sys.exit(0 if FAIL==0 else 1)