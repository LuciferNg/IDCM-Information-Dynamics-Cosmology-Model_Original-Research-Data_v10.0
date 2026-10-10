#!/usr/bin/env python3
"""
O48 Q1.21: 全部推 — 谷深/σ 結構身份 + k 值 binning 統一
=============================================================
調律者:「全部推」

三問:
  A. 谷深 0.5 結構身份: 喺 IDCM 數族度搵 — 候選 {φ⁻²=0.382, ½, φ⁻¹=0.618,
     3ε=0.464, 44/88=½, F₂/F₃=½, 22/44=½...}
  B. σ≈50 機制: 候選 {44=N_d, 297/6=49.5, 50, 55, 33/34×50=48.5?}
  C. k 值 binning 統一: Plik k=[7,9,7,6] vs O9 k=[10,11,9,7] — 真谷=? 
     用重疊概念: 兩 binning 都覆蓋同一物理谷, 谷→後峰距離嘅真值
     = 兩測量嘅 common structure?

方法: SPT 樣本外 corr 掃描谷深/σ 候選值 + k 統一分析
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

phi = (1+5**0.5)/2
F = lambda n: int(round((phi**n - (-phi)**(-n))/math.sqrt(5)))
L = lambda n: int(round(phi**n + (-phi)**(-n)))
N_d = 44

base = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
DATA = f"{base}/o214_energy_budget_definition/data"
ACT = "/home/wsl/.hermes/cache/scratch/act_dr4/cmbonly_spectra_dr4.01/act_dr4.01_D_ell_TT_cmbonly.txt"

def load_spt():
    bdp = np.loadtxt(f"{DATA}/spt3g_d1/SPT3G_D1_TnE_bdp.txt")
    spectra = [("TT_90x90",52),("TE_90x90",72),("EE_90x90",72),("TT_90x150",52),
               ("TE_90x150",72),("TE_150x90",72),("EE_90x150",72),("TT_90x220",52),
               ("TE_90x220",72),("TE_220x90",72),("EE_90x220",72),("TT_150x150",52),
               ("TE_150x150",72),("EE_150x150",72),("TT_150x220",52),("TE_150x220",72),
               ("TE_220x150",72),("EE_150x220",72),("TT_220x220",52),("TE_220x220",72),
               ("EE_220x220",72)]
    off = 0
    for name, n in spectra:
        if name == "TT_150x150":
            break
        off += n
    tt150 = bdp[off:off+52]
    win = np.loadtxt(f"{DATA}/spt3g_d1/TT_150x150_window.txt")
    lgr = win[:, 0]
    return sorted([(lgr[np.argmax(win[:, b])], tt150[b-1]) for b in range(1, 53)])

spt = load_spt()
ells = np.array([e for e, d in spt])
D = np.array([d for e, d in spt])
mask = D > 0
ells2, D2 = ells[mask], D[mask]
logD = np.log(D2)
coef = np.polyfit(ells2, logD, 2)
res = D2/np.exp(np.polyval(coef, ells2))
resn = (res - res.mean())/res.std()

PEAKS = [221, 527, 815, 1013, 1121, 1337, 1409]
V34 = [221+0.75*306, 527+0.75*288, 815+0.75*306, 1121+0.75*288]

def peak_amp(ell):
    eps = phi**(-1)/4
    j_of = {221: 0, 527: 1, 815: 2, 1121: 3, 1409: 4}
    if int(round(ell)) not in j_of:
        return 0.5
    j = j_of[int(round(ell))]
    geo = [1.0, 1.0/F(1), 1.0/F(2), 1.0/F(3), 1.0/F(4)][j]
    return 3*eps*geo*(33/34)*math.exp(-(ell/9055.0)**1.5)

def build_corr(vdepth, sig):
    T = np.zeros_like(ell_grid)
    for p in PEAKS:
        T += peak_amp(p)*np.exp(-0.5*((ell_grid-p)/sig)**2)
    for v in V34:
        T -= vdepth*np.exp(-0.5*((ell_grid-v)/sig)**2)
    Tint = np.interp(ells2, ell_grid, T)
    if Tint.std() == 0:
        return 0.0
    Tn = (Tint - Tint.mean())/Tint.std()
    return float(np.corrcoef(Tn, resn)[0, 1])

ell_grid = np.arange(32, 2500, 2.0)

print("="*72)
print("A. 谷深結構身份 — IDCM 數族候選 (SPT 樣本外, σ=50)")
print("="*72)
cand_v = {
    "1/2  (F₂/F₃, N_d/88, 22/44)": 0.5,
    "φ⁻¹  (0.618)": phi**(-1),
    "φ⁻²  (0.382)": phi**(-2),
    "3ε   (0.464)": 3*phi**(-1)/4,
    "33/34×3ε": (33/34)*3*phi**(-1)/4,
    "1/φ  (0.618)": 1/phi,
    "F₃/F₅ (2/5)": 2/5,
    "F₄/F₅ (3/5)": 3/5,
    "L₃²/44 (4/44)": L(3)**2/44,
}
best_v = (0, None)
for lab, v in cand_v.items():
    c = build_corr(v, 50)
    print(f"  vdepth={v:.4f} ({lab}): corr={c:+.3f}")
    if c > best_v[0]:
        best_v = (c, lab)
print(f"  最佳谷深候選: {best_v[1]} corr={best_v[0]:+.3f}")
# 0.5 具體身份候選比較
c_05 = build_corr(0.5, 50)
c_046 = build_corr(3*phi**(-1)/4, 50)
check("A1: 1/2 表現 ≥ 3ε (谷深係 ½ 唔係 3ε)", c_05 >= c_046 - 1e-9,
      f"½={c_05:+.3f} vs 3ε={c_046:+.3f}")

print("\n" + "="*72)
print("B. σ 機制 — 候選寬度 (SPT 樣本外, vdepth=0.5)")
print("="*72)
cand_s = {
    "44 (N_d)": 44,
    "49.5 (297/6=峰週期/6)": 297/6,
    "50 (5×10=F₅×N_d/4.4?)": 50,
    "55 (L₅? 唔係 L₅=11... F₁₀=55)": 55,
    "48.5 (33/34×50?)": 33/34*50,
    "40 (22 script 峰集)": 40,
    "60 (Q1.18 SPT 最佳)": 60,
}
best_s = (0, None)
for lab, s in cand_s.items():
    c = build_corr(0.5, s)
    print(f"  σ={s:6.1f} ({lab}): corr={c:+.3f}")
    if c > best_s[0]:
        best_s = (c, lab)
print(f"  最佳 σ 候選: {best_s[1]} corr={best_s[0]:+.3f}")
c_50 = build_corr(0.5, 50)
c_60 = build_corr(0.5, 60)
# σ=50 vs 60: 差幾多?
print(f"  σ=50 corr={c_50:+.3f}, σ=60 corr={c_60:+.3f}, 差={abs(c_50-c_60):.3f}")
check("B1: σ∈{50,60} 平台 (差距<0.05)", abs(c_50-c_60) < 0.05, f"|{c_50:+.3f}−{c_60:+.3f}|={abs(c_50-c_60):.3f}")

print("\n" + "="*72)
print("C. k 值 binning 統一 — 真谷位置推斷")
print("="*72)
# Plik k=[7,9,7,6] 谷→後峰距 [63,81,63,54]
# O9   k=[10,11,9,7] 谷→後峰距 [90,99,81,63]
# 共同項: 谷距 63 (m2 Plik + m5? O9 m7), 81 (m3), 7/9 兩個值兩處出現
# 概念: 真谷位置 ∈ [谷1, 谷2] 兩 binning 之間
plik_v = [464, 734, 1058, 1355]
o9_v = [437, 716, 1040, 1346]
peaks_m = [527, 815, 1121, 1409]  # 對應谷 (後峰)
print("  兩 binning 谷位:")
print(f"    Plik: {plik_v}   O9: {o9_v}")
print(f"    差:   {[b-a for a, b in zip(o9_v, plik_v)]}")
print("  谷→後峰 b 值:")
for i, (pv, ov) in enumerate(zip(plik_v, o9_v)):
    bp = (peaks_m[i]-pv)/9
    bo = (peaks_m[i]-ov)/9
    print(f"    m峰{i+2}: Plik k={bp:.1f}  O9 k={bo:.1f}  中點={ (bp+bo)/2:.2f}")
print("  觀察: b 值唔係整數喺兩 binning 一致, 但谷→後峰距離全 ≤ 99 = 11×9")
print("  峰間隙 288/306 對 k 化: 谷距 = 峰間隙 - 峰→谷距")
# 統一候選: 谷 = 峰 − b×9, b 由 (峰間隙 - ¾×峰間隙)/9 = (¼×峰間隙)/9
# V¾: 峰→谷 = ¾×間隙 → 谷→後峰 = ¼×間隙 = 76.5 或 72 = 8.5×9 或 8×9
print()
print("  V¾ 預言: 谷→後峰 = ¼×峰間隙 = (¼×306, ¼×288) = (76.5, 72)")
print("  Plik 實測: [63, 81, 63, 54]  O9: [90, 99, 81, 63]")
v34_pred = [0.25*306, 0.25*288, 0.25*306, 0.25*288]
resid_plik = [int(p - v) for p, v in zip(v34_pred, [63, 81, 63, 54])]
print(f"  V¾(76.5/72) − Plik實測: {resid_plik}")
# ¾ 用近似 (峰→谷=¾): 谷距 = ¼間隙 → 但個位 27:7 分點即 27/34=0.794 
print()
print("  更準: Q1.16 谷係峰間隙 27:7 → 谷→後峰 = 7/(27+7)×間隙 = 7/34×306 = 63")
print("  同 7/32×288 = 63 — 一致!! 谷→後峰距離 = 63 固定 = 7×9 = L₄·F₄²")
print("  Plik m2/m5: 63 ✓✓  O9 m7: 63 ✓  Plik m3: 81, O9 m3: 81")
print("  兩 binning 4+4=8 點中, 谷→後峰 ∈ {63, 81} 每點對應:")
# 完整表
for i, (pv, ov) in enumerate(zip(plik_v, o9_v)):
    bp = peaks_m[i]-pv
    bo = peaks_m[i]-ov
    print(f"    m={peaks_m[i]}: Plik 谷距 {bp}, O9 谷距 {bo} → 共有候選 {sorted(set([bp,bo]))}")

print("\n" + "="*72)
print("C 結論候選規則: 谷→後峰 = 7×9=63 (L₄·F₄²) 或 9×9=81 (F₄²²? 9²)")
print("  4 峰對 × 2 binning = 8 樣本: 63 出現 3 次, 81 出現 2 次")
print("  m2: 90(63) m3: 99(81) m5: 81(63) m7: 63(54) — 每對谷距兩 binning 唔同")
print("  ⟹ k 值 binning 依賴成立, 但 63/81 係跨 binning 共存值")
print("="*72)

print("\n" + "="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)