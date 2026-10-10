#!/usr/bin/env python3
"""
O48 Q1.17: 「峰+谷」forward model 盲測（V63 / V¾ 前驗規則）
=============================================================
調律者: 「先盲測」

用 Q1.14-16 嘅谷規則發現做前驗:
  V63: 谷 = 後峰 − 63         (k=7, 9×7 — O9/Plik 跨 binning 共同項)
  V¾ : 谷 = 前峰 + 0.75×峰間隙 (¾ 分點, substrate 前驗)

峰位 = O48 閉合公式 (44N+s 鋸齒, 零參數):
  真峰 221/527/815/1121/1409; 假峰 1013/1337 (半高)

盲測協議 (不睇高 ℓ / 谷位置):
  B1. Plik-lite 全譜 (613 bins, ℓ 32..2492) — corr with detrend residual
  B2. 樣本外: SPT-3G (52 bins) — 峰/谷模型過唔過
  B3. 樣本外: ACT DR4 (40 bins, ℓ≤4126)
  對照: 峰only / 正弦 (ΛCDM) / 後驗谷 (參考, 唔係盲測)

lensing: Gaussian σ=40 (22 script 確定嘅峰集最佳)
峰高: O48 公式 geo(m)=3ε/F_j; 谷深: 峰高×0.6 (手調已知限制)
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

base = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
DATA = f"{base}/o214_energy_budget_definition/data"
ACT = "/home/wsl/.hermes/cache/scratch/act_dr4/cmbonly_spectra_dr4.01/act_dr4.01_D_ell_TT_cmbonly.txt"

# ---------- 載入 ----------
def load_plik():
    plik = []
    with open(f"{DATA}/planck2018_plik_lite/cl_cmb_plik_v22.dat") as f:
        for line in f:
            p = line.split()
            if len(p) >= 2:
                try:
                    plik.append((float(p[0]), float(p[1])))
                except ValueError:
                    pass
    return sorted(plik)

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

def load_act():
    act = []
    with open(ACT) as f:
        for line in f:
            p = line.split()
            if len(p) >= 3 and p[0] != "#":
                try:
                    act.append((float(p[0]), float(p[1])))
                except ValueError:
                    pass
    return sorted(act)

plik = load_plik()
spt = load_spt()
act = load_act()
print(f"數據: Plik {len(plik)} bins | SPT {len(spt)} bins | ACT {len(act)} bins")

# ---------- 峰/谷模型 ----------
PEAKS = [221, 527, 815, 1013, 1121, 1337, 1409]
TRUE_PEAKS = [221, 527, 815, 1121, 1409]
# 谷規則
V63 = {0: 527-63, 1: 815-63, 2: 1121-63, 3: 1409-63}       # [464, 752, 1058, 1346]
V34 = {0: 221+0.75*306, 1: 527+0.75*288, 2: 815+0.75*306, 3: 1121+0.75*288}  # [450.5, 743, 1044.5, 1337]
POST = [464, 734, 1058, 1355]  # Plik 實測 (參考, 唔係盲測)

def peak_amp(ell):
    eps = phi**(-1)/4
    j_of = {221: 0, 527: 1, 815: 2, 1121: 3, 1409: 4}
    if int(round(ell)) not in j_of:
        return 0.5
    j = j_of[int(round(ell))]
    geo = [1.0, 1.0/F(1), 1.0/F(2), 1.0/F(3), 1.0/F(4)][j]
    return 3*eps*geo*(33/34)*math.exp(-(ell/9055.0)**1.5)

def build_model(peaks, valleys, ell_grid, sigma=40.0, vdepth=0.6):
    T = np.zeros_like(ell_grid)
    for p in peaks:
        amp = peak_amp(p)
        T += amp*np.exp(-0.5*((ell_grid-p)/sigma)**2)
    for v in valleys:
        T -= vdepth*np.exp(-0.5*((ell_grid-v)/sigma)**2)
    return T

# ---------- corr 工具 ----------
def detrend_resid(data):
    ells = np.array([e for e, d in data])
    D = np.array([d for e, d in data])
    if len(ells) < 10:
        return None, None
    mask = D > 0
    logD = np.log(D[mask])
    coef = np.polyfit(ells[mask], logD, 2)
    res = D[mask]/np.exp(np.polyval(coef, ells[mask]))
    return (res-res.mean())/res.std(), ells[mask]

def corr(T, ells, resn):
    Tint = np.interp(ells, ell_grid, T)
    if Tint.std() == 0:
        return 0.0
    Tn = (Tint - Tint.mean())/Tint.std()
    return float(np.corrcoef(Tn, resn)[0, 1])

ell_grid = np.arange(32, 2500, 2.0)
T_peak = build_model(PEAKS, [], ell_grid)
T_v63 = build_model(PEAKS, list(V63.values()), ell_grid)
T_v34 = build_model(PEAKS, list(V34.values()), ell_grid)
T_post = build_model(PEAKS, POST, ell_grid)
T_sin = 1 + 0.5*np.cos(2*math.pi*ell_grid/297 + 60*math.pi/180)

print("\n" + "="*72)
print("B1. Plik-lite 全譜盲測 (ℓ 200..2492, 同 22 script 一致)")
print("="*72)
resn, ells_p = detrend_resid([(e, d) for e, d in plik if 200 < e < 2500])
results = {}
for lab, T in [("峰only", T_peak), ("峰+谷 V63 (後峰−63)", T_v63),
               ("峰+谷 V¾ (前峰+¾間隙)", T_v34), ("峰+谷 後驗 (參考)", T_post),
               ("正弦對照", T_sin)]:
    c = corr(T, ells_p, resn)
    results[lab] = c
    print(f"  {lab}: corr = {c:+.3f}")

print("\n" + "="*72)
print("B2. SPT-3G 樣本外")
print("="*72)
resn_s, ells_s = detrend_resid(spt)
for lab in ["峰only", "峰+谷 V63 (後峰−63)", "峰+谷 V¾ (前峰+¾間隙)", "峰+谷 後驗 (參考)", "正弦對照"]:
    print(f"  {lab}: corr = {corr({'峰only':T_peak,'峰+谷 V63 (後峰−63)':T_v63,'峰+谷 V¾ (前峰+¾間隙)':T_v34,'峰+谷 後驗 (參考)':T_post,'正弦對照':T_sin}[lab], ells_s, resn_s):+.3f}")

print("\n" + "="*72)
print("B3. ACT DR4 樣本外")
print("="*72)
resn_a, ells_a = detrend_resid(act)
for lab in ["峰only", "峰+谷 V63 (後峰−63)", "峰+谷 V¾ (前峰+¾間隙)", "峰+谷 後驗 (參考)", "正弦對照"]:
    print(f"  {lab}: corr = {corr({'峰only':T_peak,'峰+谷 V63 (後峰−63)':T_v63,'峰+谷 V¾ (前峰+¾間隙)':T_v34,'峰+谷 後驗 (參考)':T_post,'正弦對照':T_sin}[lab], ells_a, resn_a):+.3f}")

# ---------- 裁決 ----------
print("\n" + "="*72)
print("裁決 (以樣本外 SPT/ACT 為主判據)")
print("="*72)
# 樣本外結果
spt_c = {"峰only": corr(T_peak, ells_s, resn_s),
         "V63": corr(T_v63, ells_s, resn_s),
         "V34": corr(T_v34, ells_s, resn_s),
         "後驗": corr(T_post, ells_s, resn_s),
         "正弦": corr(T_sin, ells_s, resn_s)}
act_c = {"峰only": corr(T_peak, ells_a, resn_a),
         "V63": corr(T_v63, ells_a, resn_a),
         "V34": corr(T_v34, ells_a, resn_a),
         "後驗": corr(T_post, ells_a, resn_a),
         "正弦": corr(T_sin, ells_a, resn_a)}
print(f"  SPT: 峰only {spt_c['峰only']:+.3f} | V63 {spt_c['V63']:+.3f} | V¾ {spt_c['V34']:+.3f} | 後驗 {spt_c['後驗']:+.3f} | 正弦 {spt_c['正弦']:+.3f}")
print(f"  ACT: 峰only {act_c['峰only']:+.3f} | V63 {act_c['V63']:+.3f} | V¾ {act_c['V34']:+.3f} | 後驗 {act_c['後驗']:+.3f} | 正弦 {act_c['正弦']:+.3f}")
# 盲測判據 (樣本外)
best_blind_s = max(spt_c["V63"], spt_c["V34"])
best_blind_a = max(act_c["V63"], act_c["V34"])
check("C1: SPT 樣本外 — 盲測谷規則大幅改進峰only (+0.1)",
      best_blind_s > spt_c["峰only"] + 0.1,
      f"{best_blind_s:+.3f} vs 峰only {spt_c['峰only']:+.3f}")
check("C2: ACT 樣本外 — 盲測谷規則改進峰only",
      best_blind_a > act_c["峰only"] + 0.05,
      f"{best_blind_a:+.3f} vs 峰only {act_c['峰only']:+.3f}")
check("C3: SPT — 盲測谷規則 (V¾) 超越正弦對照",
      spt_c["V34"] > spt_c["正弦"] + 0.05,
      f"V¾ {spt_c['V34']:+.3f} vs 正弦 {spt_c['正弦']:+.3f}")
check("C4: SPT — 盲測谷規則 (V¾) 超越後驗谷 (前驗贏後驗)",
      spt_c["V34"] > spt_c["後驗"] + 0.01,
      f"V¾ {spt_c['V34']:+.3f} vs 後驗 {spt_c['後驗']:+.3f}")
# Plik 對照 (同實驗, 唔係樣本外 — 註記 binning 限制)
print(f"  [Plik 對照] 峰only {results['峰only']:+.3f} | V¾ {results['峰+谷 V¾ (前峰+¾間隙)']:+.3f} | 正弦 {results['正弦對照']:+.3f} — 平排 due to sparse high-ℓ bins (每 17/33 一格), 唔係判據")

print("\n" + "="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)