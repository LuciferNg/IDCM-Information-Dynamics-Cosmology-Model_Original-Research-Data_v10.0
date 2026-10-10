#!/usr/bin/env python3
"""
O48 Q1.11: 「峰+谷」一體 C_ℓ 模型盲測
=============================================================
背景 (Q1.8/Q1.9-1.10):
  - 峰位鋸齒已閉合 (306/288 交替, ΔN=7=L₄, Δs=−2/−20)
  - 峰集 only forward model corr = +0.408 vs 正弦 +0.554 (22 script)
  - 谷位冇 44 週期結構 (C1 FAIL, 26 script) — 谷係聲學 trough 平滑層

本模型: C_ℓ(ℓ) = 峰梳(正幅度) − 谷梳(負幅度)  ⊗ lensing Gaussian (σ=40)

峰位 (零參數, O48 公式): 221, 527, 815, 1013(假), 1121, 1337(假), 1409
谷位:
  G1 (後驗): 真實 Planck 峰間谷 {437, 716, 1040, 1346} — 結構參考
  G2 (前驗): 谷 = 峰 + 半聲學週期 (~150) — 真盲測

幅度 (零參數):
  峰: O48 峰高公式 A_m ∝ (33/34)·Π(F_k/F_{k+1})·exp[−(ℓ/9055)^{1.5}]
  谷: 負, 深度 = 相鄰兩峰平均嘅 0.6 (聲學 trough 典型形狀)

盲測:
  B1. 全譜 corr: 峰+谷(後驗) vs 峰+谷(前驗) vs 峰only vs 正弦
  B2. 樣本外 ℓ>1409: 用頭 5 峰 + 3 谷定前驗谷, 預言高ℓ corr
"""
import math, sys
import numpy as np

phi = (1+5**0.5)/2
F = lambda n: int(round((phi**n - (-phi)**(-n))/math.sqrt(5)))
L = lambda n: int(round(phi**n + (-phi)**(-n)))

base = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
planck_tt = []
with open(f"{base}/o9_high_ell_peaks/data/planck_tt.txt") as f:
    for line in f:
        parts = line.split()
        if len(parts) >= 2:
            try:
                planck_tt.append((float(parts[0]), float(parts[1])))
            except ValueError:
                pass
planck_tt = sorted(planck_tt)

# ---------- 數據 (test 段) ----------
ells_p = np.array([e for e, d in planck_tt if 200 < e < 2500])
Ds_p = np.array([d for e, d in planck_tt if 200 < e < 2500])
logD = np.log(Ds_p)
coef = np.polyfit(ells_p, logD, 2)
res = Ds_p / np.exp(np.polyval(coef, ells_p))
res_n = (res - res.mean()) / res.std()

# ---------- 峰位/谷位 ----------
PEAKS = {221: 1.0, 527: 1.0, 815: 1.0, 1013: 0.42, 1121: 1.0, 1337: 0.42, 1409: 1.0}
VALLEYS_POST = {437: -1.0, 716: -1.0, 1040: -1.0, 1346: -1.0}

def peak_height(ell):
    """O48 峰高公式 (零參數, scripts/14 正確 telescoping):
    geo(m) = 3ε/F_j, j = 峰序 (m=1→j0, 2→j1, 3→j2, 5→j3, 7→j4)
    A(m) = geo(m)·(33/34)·exp[-(ℓ/ℓ_D)^{3/2}], ℓ_D=9055"""
    eps = phi**(-1)/4
    # Π_{k=1}^{j-1} F_k/F_{k+1} = F_1/F_j = 1/F_j; m=1 j=0 → 空積 = 1
    geo_j = {0: 1.0, 1: 1.0/F(1), 2: 1.0/F(2), 3: 1.0/F(3), 4: 1.0/F(4)}  # 1,1,1,1/2,1/3
    j_of = {221: 0, 527: 1, 815: 2, 1121: 3, 1409: 4}
    if int(round(ell)) not in j_of:
        return 0.5  # 假峰 (1013, 1337) 半高
    j = j_of[int(round(ell))]
    val = 3*eps*geo_j[j]*(33/34)*math.exp(-(ell/9055.0)**1.5)
    return val

# ---------- 模型 ----------
def build_model(ells, use_post_valleys=True, sigma=40.0, valley_depth=0.6):
    """峰+谷 模型: 峰梳(正) − 谷梳(負), lensing 卷積"""
    T = np.zeros_like(ells, dtype=float)
    # 峰 (O48 峰位 + 峰高公式)
    for pl, base_amp in PEAKS.items():
        amp = base_amp * peak_height(pl)
        T += amp * np.exp(-0.5*((ells - pl)/sigma)**2)
    # 谷
    valleys = VALLEYS_POST if use_post_valleys else {815+150: -1, 1121+150: -1, 527+150: -1}
    for vl, amp in valleys.items():
        T += valley_depth * amp * np.exp(-0.5*((ells - vl)/sigma)**2)
    return T

ell_grid = np.arange(200, 2500, 4.0)

print("="*72)
print("A. 峰高公式抽樣 (零參數)")
print("="*72)
for pl in [221, 527, 815, 1121, 1409]:
    print(f"    峰 {pl}: A = {peak_height(pl):.5f}")

# ---------- B1. 全譜 corr ----------
print("\n" + "="*72)
print("B1. 全譜 correlation 對比")
print("="*72)
models = {
    "峰only (22 script 重現)": build_model(ell_grid, use_post_valleys=False) - build_model(ell_grid, use_post_valleys=False),  # placeholder
}
# 峰only (冇谷)
T_peak = np.zeros_like(ell_grid, dtype=float)
for pl, base_amp in PEAKS.items():
    amp = base_amp * peak_height(pl)
    T_peak += amp * np.exp(-0.5*((ell_grid - pl)/40.0)**2)

# 峰+谷(後驗)
T_pv = build_model(ell_grid, use_post_valleys=True)
# 峰+谷(前驗: 谷=峰+150)
T_pv2 = np.zeros_like(ell_grid, dtype=float)
for pl, base_amp in PEAKS.items():
    amp = base_amp * peak_height(pl)
    T_pv2 += amp * np.exp(-0.5*((ell_grid - pl)/40.0)**2)
for pl in [527, 815, 1121, 1409]:
    if pl + 150 < 2500:
        T_pv2 -= 0.6 * np.exp(-0.5*((ell_grid - (pl+150))/40.0)**2)

# 正弦 (ΛCDM 對照)
T_sin = 1 + 0.5*np.cos(2*math.pi*ell_grid/300 + 60*math.pi/180)

def corr_with(T, label):
    Tint = np.interp(ells_p, ell_grid, T)
    if Tint.std() == 0:
        print(f"  {label}: std=0 (冇信號)")
        return 0
    Tn = (Tint - Tint.mean())/Tint.std()
    c = float(np.corrcoef(Tn, res_n)[0, 1])
    print(f"  {label}: corr = {c:+.3f}")
    return c

best = 0
best_lab = ""
for lab, T in [("峰 only", T_peak), ("峰+谷(後驗)", T_pv), ("峰+谷(前驗+150)", T_pv2), ("正弦 對照", T_sin)]:
    c = corr_with(T, lab)
    if abs(c) > abs(best):
        best, best_lab = c, lab

# ---------- B2. 樣本外 ℓ>1409 ----------
print("\n" + "="*72)
print("B2. 樣本外 (ℓ>1409): 前驗模型預言")
print("="*72)
ells_out = np.array([e for e, d in planck_tt if 1409 < e < 2500])
Ds_out = np.array([d for e, d in planck_tt if 1409 < e < 2500])
if len(ells_out) > 10:
    logDo = np.log(Ds_out)
    coefo = np.polyfit(ells_out, logDo, 2)
    reso = Ds_out / np.exp(np.polyval(coefo, ells_out))
    reson = (reso - reso.mean())/reso.std()
    # 前驗模型 (只峰 7 之後 apply exp 包絡, 谷 = 峰+150)
    Tout = np.zeros(len(ell_grid), dtype=float)
    # 峰 7 後: 高ℓ 峰由 44N+s 生成: N=33+7k, 相位迴路續
    # 峰 8 候選: 1409+306 = 1715; 峰 9: 1715+288 = 2003; 
    for fp in [1715, 2003, 2291]:
        if fp < 2600:
            Tout += 0.5 * np.exp(-0.5*((ell_grid - fp)/40.0)**2)
    for fp in [1715+150, 2003-150]:
        if 1400 < fp < 2600:
            Tout -= 0.4 * np.exp(-0.5*((ell_grid - fp)/40.0)**2)
    Tint2 = np.interp(ells_out, ell_grid, Tout)
    if Tint2.std() > 0:
        Tn2 = (Tint2 - Tint2.mean())/Tint2.std()
        c_out = float(np.corrcoef(Tn2, reson)[0, 1])
        print(f"  樣本外 {len(ells_out)} bins (1409..{int(ells_out[-1])}): corr = {c_out:+.3f}")
        print(f"  (峰8候選 1715 = 1409+306, 峰9 = 1715+288=2003 — 鋸齒 pattern 延續)")
    else:
        c_out = 0
        print("  樣本外信號 std=0")
else:
    print("  樣本外 bins 太少")

print("\n" + "="*72)
print("裁決: 峰+谷 模型 vs 22 script 基準")
print("="*72)
print(f"  22 script: 峰only +0.408, 正弦 +0.554")
print(f"  best now : {best_lab} = {best:+.3f}")
print("="*72)