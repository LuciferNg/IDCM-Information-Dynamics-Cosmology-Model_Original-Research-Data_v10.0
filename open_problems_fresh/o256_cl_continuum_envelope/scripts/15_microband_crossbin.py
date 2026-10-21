#!/usr/bin/env python3
"""
O256 — Script 15: ★ 微帶跨-bin 檢驗 (ACT/SPT/Planck 三實驗合併)
=====================================================================
微帶 [1452,1476] (script 06 結構預言: 37 模態塌入 25ℓ)

新檢驗策略: ACT bin 1448.5 / SPT bin 1437+1487 / Planck 3 bins
全部「跨住」微帶 — 微帶 bump 會令覆蓋微帶嘅 bin 相對平滑背景增強.

方法 (零 fit):
  1. 用段首尾 (1398.5, 1548.5 / 1387, 1587 / 1418, 1700) 做線性插值
     估計「無微帶 baseline」
  2. 實測 / baseline − 1 = 局部增強
  3. 三實驗合併: 全部指向 +?% 增強 = 微帶支持; 全部 ≈ 0 = refute

⚠️ 峰 7 (1409) tail 喺 1418-1476 係下降 — baseline 用「繼續下降」插值,
   任何正增強都喺 tail 之上 = 獨立結構.
"""
import math, sys
import numpy as np
import astropy.io.fits as fits

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

def load_spt():
    DATA = f"{BASE}/open_problems_fresh/o214_energy_budget_definition/data/spt3g_d1"
    bdp = np.loadtxt(f"{DATA}/SPT3G_D1_TnE_bdp.txt")
    cov = np.loadtxt(f"{DATA}/SPT3G_D1_TnE_cov.dat")
    win = np.loadtxt(f"{DATA}/TT_150x150_window.txt")
    centers = np.array([win[np.argmax(win[:, b]), 0] for b in range(1, 53)])
    spectra = [("TT_90x90",52),("TE_90x90",72),("EE_90x90",72),("TT_90x150",52),
               ("TE_90x150",72),("TE_150x90",72),("EE_90x150",72),("TT_90x220",52),
               ("TE_90x220",72),("TE_220x90",72),("EE_90x220",72),("TT_150x150",52),
               ("TE_150x150",72),("EE_150x150",72),("TT_150x220",52),("TE_150x220",72),
               ("TE_220x150",72),("EE_150x220",72),("TT_220x220",52),("TE_220x220",72),
               ("EE_220x220",72)]
    off = 0
    for name, n in spectra:
        if name == "TT_150x150": break
        off += n
    tt150 = bdp[off:off+52]
    Cmat = cov[off:off+52, off:off+52]
    sm = tt150 > 0
    return centers[sm], tt150[sm], Cmat[sm][:, sm], centers, Cmat

def load_act():
    h = fits.open(f"{BASE}/open_problems_fresh/o9_high_ell_peaks/data/act_dr6_cmb_sacc.fits")
    d = h['data:cl_00'].data
    cmat = h['covariance'].data
    ell_a = np.array([r['ell'] for r in d])
    val_a = np.array([r['value'] for r in d])
    cov_tt = cmat[:45, :45]
    return ell_a, val_a, cov_tt

def load_planck():
    planck = []
    with open(f"{BASE}/open_problems_fresh/o9_high_ell_peaks/data/planck_tt.txt") as f:
        for line in f:
            p = line.split()
            if len(p) >= 2:
                try: planck.append((float(p[0]), float(p[1])))
                except ValueError: pass
    planck = np.array(sorted(planck))
    l, C = planck[:, 0], planck[:, 1]
    return l, C * l*(l+1)/(2*math.pi)

spt_l, spt_d, spt_cov, _, _ = load_spt()
act_l, act_d, act_cov = load_act()
pl_l, pl_d = load_planck()

print("="*76)
print("1. 跨微帶 bin 檢驗: 逐實驗 baseline 插值")
print("="*76)
def linear_enhance(l, d, sig, lo_idx, hi_idx, tgt_idx, name, band_l, band_r):
    """用 lo/hi bin 做線性 baseline, 計 tgt bin 增強 (多 sigma)."""
    ll, dd = l[lo_idx], d[lo_idx]
    lu, du = l[hi_idx], d[hi_idx]
    lt = l[tgt_idx]
    slope = (du-dd)/(lu-ll)
    base = dd + slope*(lt-ll)
    enh = d[tgt_idx]/base - 1.0
    # 誤差傳播: var = var_t + (∂/∂dd)²var_dd + (∂/∂du)²var_du
    t_in = (lu-lt)/(lu-ll); t_out = (lt-ll)/(lu-ll)
    v = sig[tgt_idx]**2 + (t_in*sig[lo_idx])**2 + (t_out*sig[hi_idx])**2
    s = math.sqrt(v)/base
    in_band = band_l <= lt <= band_r
    print(f"  {name:>7} ℓ={lt:7.1f}  D={d[tgt_idx]:7.1f}  base={base:7.1f}  "
          f"enh={enh*100:+5.1f}±{s*100:.1f}%  {'★微帶內' if in_band else '(微帶外)'}")
    return enh, s, in_band

print("\n— ACT (bin 1448.5 覆蓋 1423..1473, 含微帶 21/25) —")
# 用 1398.5 (idx) 同 1548.5 插值, 取沿近樣本:
def idx(l, v):
    return int(np.argmin(np.abs(np.array(l)-v)))
sig_a = np.sqrt(np.maximum(np.diag(act_cov), 0))
enh_a, sa, ina = linear_enhance(act_l, act_d, sig_a, idx(act_l,1398.5), idx(act_l,1548.5), idx(act_l,1448.5), "ACT", 1452, 1476)
check("ACT 1448 bin 增強 > 2σ", abs(enh_a) > 2*sa, f"({enh_a*100:+.1f}±{sa*100:.1f}%)")

print("\n— SPT (bin 1437 覆蓋 1412..1462, 含微帶 10/25) —")
sig_s = np.sqrt(np.maximum(np.diag(spt_cov), 0))
spt_l2, spt_d2, spt_cov2 = spt_l, spt_d, spt_cov
ens1, ss1, in1 = linear_enhance(spt_l2, spt_d2, sig_s, idx(spt_l2,1387.0), idx(spt_l2,1587.0), idx(spt_l2,1437.0), "SPT", 1452, 1476)
print("\n— SPT (bin 1487 覆蓋 1462..1512, 含微帶 15/25) —")
ens2, ss2, in2 = linear_enhance(spt_l2, spt_d2, sig_s, idx(spt_l2,1387.0), idx(spt_l2,1587.0), idx(spt_l2,1487.0), "SPT", 1452, 1476)

print("\n— Planck (bins 1454/1463/1472 全部微帶內) —")
# Planck 冇 error: 用 5% 近似 (P3 慣例)
sig_p = pl_d*0.05
enhs, ss_ = [], []
for tgt in [1454, 1463, 1472]:
    if tgt not in pl_l:
        # 最近 bin
        ii = idx(pl_l, tgt)
        tgt = pl_l[ii]
    ii = int(np.where(pl_l == tgt)[0][0])
    lo = int(np.where(pl_l == 1418)[0][0]) if 1418 in pl_l else 0
    hi = int(np.where(pl_l == 1700)[0][0]) if 1700 in pl_l else len(pl_l)-1
    e, s, _ = linear_enhance(pl_l, pl_d, sig_p, lo, hi, ii, "Planck", 1452, 1476)
    enhs.append(e); ss_.append(s)
    if e == enhs[0]: pass

print("="*76)
print("2. 合併判決")
print("="*76)
# 合併: ACT + SPT(2) + Planck(3) = 6 個 bin 位, 全部微帶覆蓋
print("  微帶內 bin 增強 (實測/線性baseline − 1):")
print(f"    ACT 1448:      {enh_a*100:+.1f}±{sa*100:.1f}%")
print(f"    SPT 1437:      {ens1*100:+.1f}±{ss1*100:.1f}%")
print(f"    SPT 1487:      {ens2*100:+.1f}±{ss2*100:.1f}%")
print(f"    Planck x3:     {[f'{x*100:+.1f}%' for x in enhs]}")
# 若 Planck 三 bin 平均
if len(enhs) >= 2:
    m = np.mean(enhs); se = np.std(enhs)/math.sqrt(len(enhs))
    print(f"    Planck mean:   {m*100:+.1f}±{se*100:.1f}%")

print("""
  判讀:
  ✅ 全部增強 > 0 且 SPT/ACT 顯著 → 微帶 bump 三實驗交叉支持
  ⚠️ 增強 ≈ 0 (±1σ)      → 無微帶訊號, S5 結構預言 refute
  ⚠️ 混合正負             → 信噪不足, 待高分辨
""")
print(f"RESULT: {PASS}/{TOTAL} PASS (FAIL={FAIL})")
sys.exit(0 if FAIL == 0 else 1)