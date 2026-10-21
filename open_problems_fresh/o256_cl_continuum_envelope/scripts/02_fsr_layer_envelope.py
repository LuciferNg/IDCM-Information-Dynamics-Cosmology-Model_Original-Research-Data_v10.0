#!/usr/bin/env python3
"""
O256 — Script 02: FSR 精化層 (O140 N_j = 44·4^j) 完整包絡疊加
================================================================
R1 深化: 7 峰 Lorentz 尾只係「層 0」。O140 FSR 世界層提供更高層模態,
每層 j 有 N_j = 44·4^j 模態, 峰位公式每層 re-scale:

  層 j 峰位: ℓ_m^(j) = N_j·(M − C(9−m,2)) + frac^(j)   (rung law 每層重演)

高層 (j≥1) 嘅峰位落喺 ℓ>1409 → 高ℓ尾連續化 + lensing floor 結構來源!

檢驗:
  Q1: 層 j=1 峰位落喺邊? (5808 定其他) — 是否覆蓋 ACT window ℓ<6124
  Q2: 高層模態尾疊加 → λ(ℓ) 上升 94→743 是否收斂到實測 308/410/420/646?
  Q3: 分層權重 (K_Tree B=4 每層 ×? ) — 零參數
  Q4: lensing floor (B≈const @2400+) 對應邊層?

禁區: 唔 re-fit λ, 唔 fitting amplitude (層權重由 K_Tree 結構).
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
N_d = 44
M   = 33
F6, F8 = 8, 21

def C(n, k):
    from math import comb
    return comb(n, k) if n >= k >= 0 else 0

def peak_pos(m, Nj):
    """層 j rung law: ℓ_m = Nj·(M−C(9−m,2)) + frac; m=5 特殊"""
    if m == 5:
        return Nj*(M - F6) + F8
    return Nj*(M - C(9-m, 2)) + ((m-1)*9) % 25

print("="*76)
print("1. FSR 層峰位 (rung law 每層 re-scale)")
print("="*76)
for j in range(0, 4):
    Nj = 44*(4**j)
    row = [peak_pos(m, Nj) for m in range(1, 8)]
    print(f"  層 j={j}: N_j={Nj:>6}  峰位 = {row}")

# 層 j=1: N=176 → 峰7 = 176×32+4 = 5636? 計算:
print()
for j in [1, 2]:
    Nj = 44*(4**j)
    print(f"  層 j={j} 峰 6,7: ℓ6 = {peak_pos(6,Nj)}, ℓ7 = {peak_pos(7,Nj)}")
check("層1 峰7 > 1409 (覆蓋高ℓ尾)", peak_pos(7, 44*4) > 1409)
check("層1 峰7 < ACT ℓ_max 6124 (ACT window 內)", peak_pos(7, 44*4) < 6124)

print("\n" + "="*76)
print("2. FSR 層疊加包絡 (零參數權重: 每層 1/B^j = 4^-j?)")
print("="*76)
# O140: K_Tree B=4 精化; 層 j 模態數 4^j 倍, 每模態「能量」攤薄
# 權重候選 (全部結構, 零手調):
#   (a) w_j^2 = 4^{-j} (模態數增加, 每模態權重攤薄 — 總權重守恆)
#   (b) w_j^2 = N_0/N_j (同)
# 用 (a): Σ_j 4^{-j} = 4/3 歸一化
LAYER_W = {0: 1.0, 1: 0.25, 2: 0.0625, 3: 0.015625}   # 4^-j
GAMMA = 306.0/8.0   # 峰形 γ (O48 峰間隙/8)

# 峰形右重 (O48: γR/γL = 1.18..1.46, v3c γR=41.5 γL=28.5 → ratio 1.46)
GAMMA_L, GAMMA_R = 28.5, 41.5   # O48 v3c
A_ratio = {1: 1.0, 2: (2/3)**2, 3: 4/9, 4: (3/7)**2, 5: 3/14, 6: (4/11)**2, 7: 1/7}

def asym_lorentz(l, lc, A, gL, gR):
    """右重 Lorentzian: Δ<0 用 gL, Δ>0 用 gR"""
    out = np.zeros_like(l, dtype=float)
    for i, x in enumerate(l):
        d = x - lc
        g = gL if d < 0 else gR
        out[i] = A * (g/math.pi) / (d*d + g*g)
    return out

l_grid = np.arange(200, 6200, 4)   # 覆蓋 ACT window
C_full = np.zeros_like(l_grid, dtype=float)
for j in [0, 1, 2]:
    Nj = 44*(4**j)
    wj = LAYER_W[j]
    for m in range(1, 8):
        lc = peak_pos(m, Nj)
        C_full += wj * asym_lorentz(l_grid, lc, A_ratio[m], GAMMA_L, GAMMA_R)

# ── 3. λ_loc(ℓ) 分段預言 ─────────────────────────────────────────
print("\n" + "="*76)
print("3. FSR 疊加包絡 local λ_loc(ℓ) vs P3 實測")
print("="*76)
segs = [(1418, 1700), (1700, 2000), (2000, 2400), (2400, 3000)]
obs =  {(1418, 1700): 308, (1700, 2000): 410, (2000, 2400): 420, (2400, 3000): 646}
print("  段            λ_pred        λ_obs    dev%")
for (a, b) in segs:
    msk = (l_grid >= a) & (l_grid < b)
    if msk.sum() >= 3:
        slope = np.polyfit(l_grid[msk], np.log(C_full[msk]), 1)[0]
        lam = -1.0/slope
        o = obs[(a,b)]
        dev = (lam - o)/o*100
        print(f"  {a}-{b:>4} {lam:>12.1f} {o:>12} {dev:>7.1f}%")

# ── 4. Planck 高ℓ尾直接對比 (盲測, 零 re-fit) ────────────────────
print("\n" + "="*76)
print("4. Planck 高ℓ尾盲測對比 (ℓ>1409, 零 re-fit)")
print("="*76)
planck = []
with open(f"{BASE}/open_problems_fresh/o9_high_ell_peaks/data/planck_tt.txt") as f:
    for line in f:
        p = line.split()
        if len(p) >= 2:
            try: planck.append((float(p[0]), float(p[1])))
            except ValueError: pass
planck = np.array(sorted(planck))
l_p, C_p = planck[:,0], planck[:,1]
D_p = C_p * l_p*(l_p+1)/(2*math.pi)
mask_tail = (l_p > 1409) & (l_p <= 3000)
l_t, D_t = l_p[mask_tail], D_p[mask_tail]
print(f"  Planck 高ℓ尾 {len(l_t)} bins, ℓ {l_t[0]:.0f}..{l_t[-1]:.0f}")

# 用 C_full 預言 D: C_pred(ℓ) → D_pred = ℓ(ℓ+1)C_pred/2π, 幅度自由 (IDCM 冇絕對振幅)
# 盲測: 用第一個 bin 歸一化幅度 (零 re-fit shape)
C_pred = np.interp(l_t, l_grid, C_full)
D_pred = C_pred * l_t*(l_t+1)/(2*math.pi)
norm = D_t[0]/D_pred[0]
Dp = D_pred * norm
rms = np.sqrt(np.mean(((D_t-Dp)/D_t)**2))
med = np.median(np.abs((D_t-Dp)/D_t))
print(f"  RMS frac dev = {rms*100:.1f}%  median = {med*100:.1f}%")
check("RMS < 15% (P3 閘)", rms < 0.15, f"({rms*100:.1f}%)")
check("median < 10%", med < 0.10, f"({med*100:.1f}%)")

# 高段 lensing floor 檢查: 2400-3000 有冇平緩?
m2400 = (l_grid >= 2400) & (l_grid <= 3000)
lam_high = -1.0/np.polyfit(l_grid[m2400], np.log(C_full[m2400]), 1)[0]
print(f"  2400-3000 λ_pred = {lam_high:.1f} (lensing floor 出現?)")

print("\n" + "="*76)
print(f"RESULT: {PASS}/{TOTAL} PASS (FAIL={FAIL})")
print("="*76)
sys.exit(0 if FAIL == 0 else 1)