#!/usr/bin/env python3
"""
O256 — Script 07: 微帶攤開 γ 掃描 + 高ℓ尾形狀結構
=====================================================================
Script 06 發現: 峰位公式 m≥8 飽和分支 → ℓ∈[1452,1476] 微帶 (密度 1/ℓ)
但 λ_pred 第一段 48 vs 308 唔夠 — Lorentz tail 太抖.

問題: 1418-1700 段 λ=308 好平 — 唔似單峰 tail (Δ=9 Lorentz 急墜).
候選: 微帶 (1452-1476, 37 模態) 喺段內製造「高原」→ λ 變大.
      γ_bg 決定微帶攤開程度 (γ=38.25 峰形同機制? γ=12.5 半微帶寬? γ=25?)

本 script: 掃描 γ_bg ∈ 結構候選, 睇 λ₁ 有冇 308 帶內, 同時唔好爆第二段.
另: 用「微帶 1452..1476 每個 ℓ 一個模態」嘅密度直接檢驗 λ 結構.
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

def C(n, k):
    from math import comb
    return comb(n, k) if n >= k >= 0 else 0

def peak_pos(m):
    if m == 5:
        return 44*(M-F6)+F8
    return 44*(M-C(9-m,2)) + ((m-1)*9) % 25

A_O83 = {1: 1.0, 2: (2/3)**2, 3: 4/9, 4: (3/7)**2, 5: 3/14, 6: (4/11)**2, 7: 1/7}
OBS_ELL = {1: 221, 2: 537, 3: 810, 4: 1014, 5: 1121, 6: 1340, 7: 1409}
G0 = np.array([1/(4*math.sin(math.pi*n/88)) for n in range(1,45)])

def lorentz(l, lc, A, gamma):
    return A*(gamma/math.pi)/((l-lc)**2+gamma**2)

l_grid = np.arange(200, 3001, 2)
GAMMA = 306.0/8.0

# 微帶結構
bkg_ells = np.array([peak_pos(m) for m in range(8, 45)])
bkg_w = G0[7:]/G0[0]          # 相對權重 Σ = 2.02
print("="*76)
print("1. 微帶結構: ℓ∈[1452,1476], 密度 1.00/ℓ, 37 模態, Σw=2.02")
print("="*76)
print("  模態權重 (G_n(0)/G_1(0)):")
for n in range(8, 45):
    print(f"    n={n:>2} ℓ={peak_pos(n)} w={G0[n-1]/G0[0]:.4f}")

# ── 2. γ_bg 掃描 ────────────────────────────────────────────────
print("\n" + "="*76)
print("2. γ_bg 掃描: λ(ℓ) 分段 vs P3 實測 308/410/420/646")
print("="*76)
segs = [(1418,1700),(1700,2000),(2000,2400),(2400,3000)]
obs  = {(1418,1700):308,(1700,2000):410,(2000,2400):420,(2400,3000):646}

def lam_segs(Cv):
    out = {}
    for (a,b) in segs:
        msk = (l_grid>=a)&(l_grid<b)
        if msk.sum() < 3:
            out[f"{a}-{b}"] = float('nan')
            continue
        sl = np.polyfit(l_grid[msk], np.log(Cv[msk]), 1)[0]
        out[f"{a}-{b}"] = -1/sl
    return out

cands = [
    ("γ=峰形 38.25", 38.25),
    ("γ=半微帶 12.5", 12.5),
    ("γ=微帶寬 25", 25.0),
    ("γ=峰間隙/16 19.1", 19.1),
    ("γ=5 (F₅)", 5.0),
    ("γ=1 (微帶密度單位)", 1.0),
]
print(f"  {'γ_candidate':>18} {'λ1':>8} {'λ2':>8} {'λ3':>8} {'λ4':>8}")
for gname, gb in cands:
    Cv = np.zeros_like(l_grid, dtype=float)
    for m in range(1,8):
        Cv += lorentz(l_grid, OBS_ELL[m], A_O83[m], GAMMA)
    for i, lc in enumerate(bkg_ells):
        Cv += lorentz(l_grid, lc, bkg_w[i], gb)
    L = lam_segs(Cv)
    print(f"  {gname:>18} {L['1418-1700']:>8.1f} {L['1700-2000']:>8.1f} {L['2000-2400']:>8.1f} {L['2400-3000']:>8.1f}")
print(f"  {'obs':>18} {308:>8} {410:>8} {420:>8} {646:>8}")

# ── 3. 純指數 vs 微帶結構 ────────────────────────────────────────
print("\n" + "="*76)
print("3. 結構比對: 微帶密度 (1/ℓ) 本身 give 咩 λ?")
print("="*76)
# 如果 C(ℓ) ∝ density(ℓ) = 1/ℓ in 微帶 → ln C = -ln ℓ → λ = ℓ/@1418 = 1418?? 
# 唔係: 實測 308 < 1418. 所以微帶唔係主角? 或者 density ~ const?
# 試: 微帶均勻密度 (每 ℓ 一個) + 兩邊 zero → box 函數 → 
l_box = np.zeros_like(l_grid, dtype=float)
box_mask = (l_grid >= 1452) & (l_grid <= 1476)
l_box[box_mask] = 1.0
msk1 = (l_grid>=1418)&(l_grid<1700)
sl = np.polyfit(l_grid[msk1][l_box[msk1]>0], np.log(l_box[msk1][l_box[msk1]>0]), 1)[0] if (l_box[msk1]>0).sum()>2 else None
print(f"  box 微帶 pure: λ(1418-1700) = {'n/a (全零)' if sl is None else -1/sl:.1f}")
# 加峰 tail
for gb in [38.25, 25.0, 12.5]:
    Cv = np.zeros_like(l_grid, dtype=float)
    for m in range(1,8):
        Cv += lorentz(l_grid, OBS_ELL[m], A_O83[m], GAMMA)
    for i, lc in enumerate(bkg_ells):
        Cv += lorentz(l_grid, lc, bkg_w[i], gb)
    L = lam_segs(Cv)
    print(f"  full model γ_bg={gb}: λ1={L['1418-1700']:.1f} (obs 308)")

# ── 4. 峰權重試驗: 峰 7 (1409) 係「最後峰」, 佢嘅 tail 主導 1418-1700 ──
print("\n" + "="*76)
print("4. 解剖 1418-1700: 邊個組件主導?")
print("="*76)
for gb in [38.25, 25.0]:
    Cv = np.zeros_like(l_grid, dtype=float)
    for m in range(1,8):
        Cv += lorentz(l_grid, OBS_ELL[m], A_O83[m], GAMMA)
    for i, lc in enumerate(bkg_ells):
        Cv += lorentz(l_grid, lc, bkg_w[i], gb)
    # 各組件喺 1418,1550 嘅值
    for lq in [1418, 1500, 1550, 1600, 1700]:
        iq = np.argmin(abs(l_grid-lq))
        peak7 = lorentz(l_grid, OBS_ELL[7], A_O83[7], GAMMA)[iq]
        bkg = sum(lorentz(l_grid, lc, bkg_w[i], gb)[iq] for i, lc in enumerate(bkg_ells))
        peakall = sum(lorentz(l_grid, OBS_ELL[m], A_O83[m], GAMMA)[iq] for m in range(1,7))
        tot = Cv[iq]
        print(f"  {gname} ℓ={lq}: peak7={peak7/tot*100:.1f}% all6={peakall/tot*100:.1f}% bkg={bkg/tot*100:.1f}%")

print("\n" + "="*76)
print(f"RESULT: {PASS}/{TOTAL} PASS (FAIL={FAIL})")
print("="*76)
sys.exit(0 if FAIL==0 else 1)