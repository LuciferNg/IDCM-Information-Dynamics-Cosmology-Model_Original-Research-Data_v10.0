#!/usr/bin/env python3
"""
O256 — Script 01: K_Chain 44 模態 propagator integration-by-sum (R1 路線核心)
=============================================================================
由 O83 basis 起點: C_ℓ = Σ_n w_n² · G_n(0) · δ_{ℓ,ℓ_n}
本 script 把 δ 攤開為有限峰形 (O48 Lorentzian) → 連續包絡, 並檢驗:

  Q1: 44 模態完整權重譜 w_n² G_n(0) 嘅形式 (零參數, 唔係 7 峰 filter)
  Q2: 峰形攤開 (γ=峰間隙/8=37.1, O48) 後, 峰間谷 + 高ℓ尾自然出現?
  Q3: 高ℓ尾 (ℓ>1409) 預言形式 vs P3 實測分段 λ (308/410/646) — 盲測比較
  Q4: FSR 精化層 (O140 N_j = 44·4^j) 加權疊加 → λ(ℓ) 上升有冇結構來源?

禁區核對: 唔 re-fit λ (零參數), 唔 φ-fit, 唔用 CAMB 前向, 唔重推 9055 層級2.
"""
import math, sys, json
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
phi = (1 + math.sqrt(5)) / 2

def C(n, k):
    from math import comb
    return comb(n, k) if n >= k >= 0 else 0

# ── 1. 44 模態 propagator 權重譜 (零參數) ─────────────────────────
print("="*76)
print("1. 44 模態 G_n(0) propagator 權重譜 (零參數)")
print("="*76)
G0 = np.array([1.0/(4*math.sin(math.pi*n/88)) for n in range(1, N_d+1)])
omega = np.array([2*math.sin(math.pi*n/88) for n in range(1, N_d+1)])
gamma = omega**2
print(f"  G_n(0): n=1 → {G0[0]:.6f}, n=7 → {G0[6]:.6f}, n=20 → {G0[19]:.6f}, n=44 → {G0[43]:.6f}")
check("G_n(0) 全部正有限", np.all(G0 > 0) and np.all(np.isfinite(G0)))
check("G_1 = 1/(4 sin(π/88)) 係最大", G0[0] == G0.max())

# ΣG_n(0) / Σγ 呢啲 44-模態總和類嘅 closed form
sum_G = float(np.sum(G0))
sum_gamma = float(np.sum(gamma))
print(f"  Σ_{N_d} G_n(0) = {sum_G:.6f}   Σγ = {sum_gamma:.6f} (=90?)")
check("Σγ_n = 90 (44-chain 標準)", abs(sum_gamma - 90.0) < 1e-9, f"({sum_gamma:.10f})")

# ── 2. 7 峰權重 (O83/O48 峰位 + 振幅母函數) ─────────────────────
print("\n" + "="*76)
print("2. 7 峰位 + 振幅 (O83 閉合) — 攤開 kernel 嘅 anchor")
print("="*76)
ell_m = {}
for m in range(1, 8):
    if m == 5:
        ell_m[m] = 44*(M - F6) + F8
    else:
        ell_m[m] = 44*(M - C(9-m, 2)) + ((m-1)*9) % 25
# 觀測峰位 (P3 用 220/537/810/1014/1121/1340/1409; O83 obs 220.1/537/810/1014/1121/1337/1400)
obs_ell = {1: 220, 2: 537, 3: 810, 4: 1014, 5: 1121, 6: 1340, 7: 1409}
# 振幅母函數: 偶峰 A_{2k}/A_1 = ((k+1)/(4k−1))², 奇峰 A_3=4/9, A_5=3/14, A_7=1/7
A_ratio = {1: 1.0, 2: (2/3)**2, 3: 4/9, 4: (3/7)**2, 5: 3/14, 6: (4/11)**2, 7: 1/7}
print(f"  {'m':>2} {'ℓ_struct':>7} {'ℓ_obs':>6} {'A/A1':>8}")
for m in range(1, 8):
    print(f"  {m:>2} {ell_m[m]:>7} {obs_ell[m]:>6} {A_ratio[m]:>8.4f}")

# ── 3. 峰形 Lorentzian 攤開 (γ = 峰間隙/8 = 306/8 = 38.25, O48) ──
print("\n" + "="*76)
print("3. Lorentzian 峰形攤開 → 連續包絡 (γ=峰間隙/8=38.25, O48)")
print("="*76)
GAMMA = 306.0/8.0   # 峰間隙/8 = 38.25 (O48 §2)
l_grid = np.arange(200, 2601, 1)
C_cont = np.zeros_like(l_grid, dtype=float)
for m in range(1, 8):
    A = A_ratio[m]
    # w_m² G_m(0) 已內建喺 A_ratio (O83: A_m = w_m² G_m(0))
    C_cont += A * (GAMMA/math.pi) / ((l_grid - obs_ell[m])**2 + GAMMA**2)

# 峰間谷檢查: ℓ=350 (221..527 之間) 有冇功率
i350 = int(np.argmin(abs(l_grid - 350)))
i400 = int(np.argmin(abs(l_grid - 400)))
i1000 = int(np.argmin(abs(l_grid - 1000)))
print(f"  谷位功率比: C(350)/C(220) = {C_cont[i350]/C_cont[i350] :.4f} (self)")
print(f"  C(400)/C(220) = {C_cont[i400]/C_cont[np.argmin(abs(l_grid-220))]:.4f}")
print(f"  C(1000)/C(220) = {C_cont[i1000]/C_cont[np.argmin(abs(l_grid-220))]:.4f}")
# 高ℓ尾: ℓ=1418 之後 Lorentz 尾
for lq in [1418, 1700, 2000, 2400]:
    iq = int(np.argmin(abs(l_grid - lq)))
    print(f"  C({lq})/C(220) = {C_cont[iq]/C_cont[np.argmin(abs(l_grid-220))]:.6e}")
    
# ── 4. 高ℓ尾 local e-folding λ_loc (P3 R7 方法) ──────────────────
print("\n" + "="*76)
print("4. 預言包絡嘅 local λ_loc(ℓ) (P3 R7 方法, 零 re-fit)")
print("="*76)
mask = (l_grid > 1409) & (l_grid <= 2500)
lg, cg = l_grid[mask], C_cont[mask]
segs = [(1418, 1700), (1700, 2000), (2000, 2400), (2400, 3000)]
print(f"  {'段':>14} {'λ_loc(預言)':>12} {'λ_obs(P3)':>12}")
pred_lams = {}
for (a, b) in segs:
    msk = (lg >= a) & (lg < b)
    if msk.sum() >= 3:
        slope = np.polyfit(lg[msk], np.log(cg[msk]), 1)[0]
        lam = -1.0/slope
        pred_lams[f"{a}-{b}"] = lam
        obs_map = {(1418,1700): 308, (1700,2000): 410, (2000,2400): 420, (2400,3000): 646}
        obs = obs_map.get((a,b), None)
        print(f"  {a}-{b:>4} {lam:>12.1f} {('' if obs is None else str(obs)):>12}")

# ── 5. FSR 精化層 (O140 N_j = 44·4^j) 加權疊加 — λ(ℓ) 上升來源 ──
print("\n" + "="*76)
print("5. FSR 層加權疊加 → λ(ℓ) 上升嘅結構候選 (O140)")
print("="*76)
# 層 j 模態: γ_k^(j) = 4 sin²(πk/(88·4^j)), k=1..44·4^j
# 每層提供嘅「模態密度」(arcsine 喺每層), 權重 ∝ G_k^(j)(0)
# 簡化: 每層取 head 模態, 統計 local e-folding
for j in [0, 1, 2, 3]:
    Nj = 44 * (4**j)
    kk = np.arange(1, Nj+1)
    # 高層嘅「峰位斷層」: rung law 飽和 1452 之後, FSR 模態填充高ℓ
    # 初步: 模態 k 嘅 γ → ℓ 用 O202 仿射橋 r=2πR(1−γ/4), ℓ ∝ γ_scale
    gamma_j = 4*np.sin(np.pi*kk/(2*Nj))**2   # 注意 denominator 88·4^j = 2Nj/4? (O140 用 88·4^j)
    # O140: γ_k(j) = 4sin²(πk/(88·4^j)) 用 88·4^j, Nj=44·4^j ⟹ denom = 2·44·4^j = 88·4^j ✓
    gamma_j = 4*np.sin(np.pi*kk/(88*4**j))**2
    print(f"  層 j={j}: N_j={Nj}, γ range [{gamma_j.min():.6f}, {gamma_j.max():.4f}]")

# 輸出摘要
print("\n" + "="*76)
print(f"RESULT: {PASS}/{TOTAL} PASS (FAIL={FAIL})")
print("="*76)
sys.exit(0 if FAIL == 0 else 1)