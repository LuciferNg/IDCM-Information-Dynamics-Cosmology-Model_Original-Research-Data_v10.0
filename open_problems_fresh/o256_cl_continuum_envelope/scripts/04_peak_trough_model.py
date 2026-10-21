#!/usr/bin/env python3
"""
O256 — Script 04: 峰梳−谷梳 forward model (O48 Q1.11 結構) 連續包絡
=====================================================================
O48 Q1.11 已閉合: C_ℓ = (峰梳 − 谷梳) ⊗ Gaussian(σ=40) lensing,
峰 higher 零參數 + 谷 with 後驗位置 ({437,716,1040,1346}, 谷深 0.6).

本 script 測試完整 IDCM forward 連續包絡是否預言 P3 高ℓ尾 λ(ℓ):
  308/410/420/646 (Planck/SPT/ACT 實測分段)

關鍵問題 Q1: IDCM 連續包絡 form factor 係咪 = (峰梳−谷梳)⊗Gauss ?
           Q2: λ(ℓ) 上升 (308→646) 有冇 IDCM 結構來源?

禁區: 谷位係 O48 後驗 (非零參數) — 本 script 只用佢測結構,
      閉合判決睇「峰梳 alone ⊗ Gauss」同「+谷梳」嘅差別.
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
phi = (1+math.sqrt(5))/2
eps = phi**-1/4.0
F = lambda n: int(round((phi**n - (-phi)**-n)/math.sqrt(5)))

def C(n, k):
    from math import comb
    return comb(n, k) if n >= k >= 0 else 0

def peak_pos(m):
    if m == 5:
        return 44*(M-F6)+F8
    return 44*(M-C(9-m,2)) + ((m-1)*9) % 25

A_O83 = {1: 1.0, 2: (2/3)**2, 3: 4/9, 4: (3/7)**2, 5: 3/14, 6: (4/11)**2, 7: 1/7}

print("="*76)
print("1. O48 峰+谷模型重現 (Q1.11: 峰梳−谷梳 ⊗ Gaussian σ=40)")
print("="*76)
# 峰位 (O48 用 221/527/815/1013/1121/1337/1409)
PEAKS = {1: 221.1, 2: 527, 3: 815, 4: 1013.9, 5: 1121, 6: 1337, 7: 1409}
TROUGHS = [437, 716, 1040, 1346]   # O48 Q1.11 後驗谷位
T_DEPTH = 0.6
SIGMA_LEN = 40.0   # Gaussian lensing σ (O48 Q1.11)

l_grid = np.arange(200, 3001, 1)
def gauss_kernel(l, lc, A, sigma):
    return A*np.exp(-0.5*((l-lc)/(sigma))**2)

# 峰梳 (零參數振幅 A_O83, 峰位 O48)
comb_p = np.zeros_like(l_grid, dtype=float)
for m in [1,2,3,5,7]:
    comb_p += A_O83[m]*gauss_kernel(l_grid, PEAKS[m], 1.0, SIGMA_LEN)
# 谷梳 (O48 後驗: 谷深 0.6)
comb_t = np.zeros_like(l_grid, dtype=float)
for t in TROUGHS:
    comb_t += T_DEPTH*gauss_kernel(l_grid, t, 1.0, SIGMA_LEN)

C_lensed = comb_p - comb_t   # 峰 − 谷
C_peakonly = comb_p.copy()

# ── 2. λ_loc(ℓ) 分段 (1418..3000) ────────────────────────────────
print("\n" + "="*76)
print("2. λ_loc(ℓ) 分段預言: 峰 only vs 峰+谷")
print("="*76)
segs = [(1418,1700),(1700,2000),(2000,2400),(2400,3000)]
obs  = {(1418,1700):308,(1700,2000):410,(2000,2400):420,(2400,3000):646}
print(f"  {'段':>14} {'λ峰only':>9} {'λ峰+谷':>9} {'λ_obs':>7}")
for (a,b) in segs:
    msk = (l_grid>=a)&(l_grid<b)
    if msk.sum() < 3: continue
    s1 = np.polyfit(l_grid[msk], np.log(C_peakonly[msk]), 1)[0]
    s2 = np.polyfit(l_grid[msk], np.log(np.maximum(C_lensed[msk],1e-12)), 1)[0]
    print(f"  {a}-{b:>4} {-1/s1:>9.1f} {-1/s2:>9.1f} {obs[(a,b)]:>7}")

# ── 3. Planck 高ℓ尾盲測 (零 re-fit) ─────────────────────────────
print("\n" + "="*76)
print("3. Planck 高ℓ尾盲測 vs 峰only / 峰+谷 (零 re-fit shape)")
print("="*76)
planck = []
with open(f"{BASE}/open_problems_fresh/o9_high_ell_peaks/data/planck_tt.txt") as f:
    for line in f:
        p = line.split()
        if len(p)>=2:
            try: planck.append((float(p[0]), float(p[1])))
            except ValueError: pass
planck = np.array(sorted(planck))
l_p, C_p = planck[:,0], planck[:,1]
D_p = C_p*l_p*(l_p+1)/(2*math.pi)
mask_tail = (l_p>1409)&(l_p<=2492)
l_t, D_t = l_p[mask_tail], D_p[mask_tail]

for name, Cmod in [("峰only", C_peakonly), ("峰+谷", np.maximum(C_lensed,1e-12))]:
    C_pd = np.interp(l_t, l_grid, Cmod)
    D_pd = C_pd*l_t*(l_t+1)/(2*math.pi)
    # 用第一 bin 歸一化
    norm = D_t[0]/D_pd[0]
    Dn = D_pd*norm
    rms = np.sqrt(np.mean(((D_t-Dn)/D_t)**2))
    md = np.median(np.abs((D_t-Dn)/D_t))
    print(f"  {name:>8}: RMS={rms*100:.1f}%  median={md*100:.1f}%  norm={norm:.2e}")

# ── 4. 關鍵結構問題: 高ℓ尾 λ≈308 係咪「最後峰 tail」定「谷梳洞」──
print("\n" + "="*76)
print("4. 高ℓ尾結構解剖: 邊個組件造出 1418-1700 段?")
print("="*76)
# 最後峰 1409 嘅 Gaussian tail (σ=40) 喺 1418-1700:
# Gaussian exp(-Δ²/2σ²) → ln C = const − Δ²/2σ² → λ_loc = σ²/Δ
lc7 = PEAKS[7]
for lq in [1450, 1500, 1550, 1600, 1650]:
    d = lq - lc7
    lam_g = SIGMA_LEN**2/d
    print(f"  ℓ={lq}: Δ={d:>3}, Gaussian-tail λ_loc = σ²/Δ = {lam_g:6.1f}  (實測段均 308)")
print("  ⟹ Gaussian tail 喺 Δ≈5 時 λ≈320, Δ≈10 時 λ≈160 — 只有近期好窄區 match 308")
print("  ⟹ 309@1418-1700 需要更長 tail (Lorentz 或指數), 唔係 Gaussian σ=40")

print("\n" + "="*76)
print(f"RESULT: {PASS}/{TOTAL} PASS (FAIL={FAIL})")
print("="*76)
sys.exit(0 if FAIL==0 else 1)