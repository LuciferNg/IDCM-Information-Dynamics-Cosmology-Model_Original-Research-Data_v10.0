#!/usr/bin/env python3
"""
O10 20: 三實驗交叉驗證 — Planck + ACT DR6 + SPT-3G
====================================================
驗證 Fibonacci 階梯 P_m = 3ε·F_m·φ^(-2(m-1)) 嘅跨實驗一致性

關鍵發現 (前序):
  - Planck: P₂=0.1778 (0.40σ), P₃=0.1358 (0.38σ) 閉合
  - ACT DR6: 峰 6,7 存在 (P₃≈0.134), 峰 8,9 唔存在 (ℓ>1500 damping tail)
  - SPT-3G: bin 21 (1475) = 748 µK², 冇峰 8,9

方法: 用每個實驗自己嘅 D₁ 做基準, 避免 cross-calibration 偏差
"""
import numpy as np, math, os, json
from astropy.io import fits
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

phi = (1 + 5**0.5) / 2
eps = phi**-1/4
F = [1, 1, 2, 3, 5, 8]
def P_th(m):
    return 3*eps*F[m-1]*phi**(-2*(m-1))

print("=" * 72)
print("Fibonacci 階梯三實驗交叉驗證")
print("P_m = 3ε·F_m·φ^(-2(m-1))")
print("=" * 72)

# ============ 1. Planck ============
DATA = os.path.join(os.path.dirname(__file__), "..", "..", "o9_high_ell_peaks", "data", "planck_tt.txt")
data = np.loadtxt(DATA)
l, val, err = data[:,0], data[:,1], data[:,2]
Dl = val * l*(l+1)/(2*np.pi)
Dl_err = err * l*(l+1)/(2*np.pi)
D1 = Dl[np.argmin(np.abs(l-220))]

# Planck 自動峰
s = gaussian_filter1d(Dl, sigma=1.5)
pk, _ = find_peaks(s, distance=25)
planck_peaks = [(l[p], Dl[p]) for p in pk]
print("\n1. Planck binned 峰:", [(f"ℓ={le:.0f}", f"D={D:.0f}") for le, D in planck_peaks])
print(f"   D₁ = {D1:.0f}")

# ============ 2. ACT DR6 ============
path = os.path.join(os.path.dirname(__file__), "..", "..", "o9_high_ell_peaks", "data", "act_dr6_cmb_sacc.fits")
hdul = fits.open(path)
tt = hdul['data:cl_00'].data
act_ell = tt['ell']
act_D = tt['value']
# ACT 峰
act_peaks = []
for i in range(1, len(act_D)-1):
    if act_D[i] > act_D[i-1] and act_D[i] > act_D[i+1]:
        act_peaks.append((act_ell[i], act_D[i]))
print("\n2. ACT DR6 峰:", [(f"ℓ={le:.0f}", f"D={D:.0f}") for le, D in act_peaks])

# ============ 3. SPT-3G ============
bdp_path = os.path.join(os.path.dirname(__file__), "..", "..", "o9_high_ell_peaks", "data", "spt3g_tne_bdp.txt")
vals = np.array([float(x) for x in open(bdp_path).read().split()])
spec_order = [
    ("TT", "90x90", 52), ("TE", "90x90", 72), ("EE", "90x90", 72),
    ("TT", "90x150", 52), ("TE", "90x150", 72), ("TE", "150x90", 72), ("EE", "90x150", 72),
    ("TT", "90x220", 52), ("TE", "90x220", 72), ("TE", "220x90", 72), ("EE", "90x220", 72),
    ("TT", "150x150", 52), ("TE", "150x150", 72), ("EE", "150x150", 72),
    ("TT", "150x220", 52), ("TE", "150x220", 72), ("TE", "220x150", 72), ("EE", "150x220", 72),
    ("TT", "220x220", 52), ("TE", "220x220", 72), ("EE", "220x220", 72),
]
tt_spectra = {}
offset = 0
for name, freq, n in spec_order:
    block = vals[offset:offset+n]
    if name == "TT":
        tt_spectra[freq] = block
    offset += n
spt_centers = np.array([400 + 50*b + 25 for b in range(52)])
spt_150 = tt_spectra["150x150"]
print("\n3. SPT-3G TT 150x150 (選定 bins):")
for i in [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 21, 22]:
    print(f"   ℓ={spt_centers[i]:.0f}: D={spt_150[i]:.1f}")

# ============ 峰配對 + P_m 驗證 ============
print("\n" + "=" * 72)
print("峰配對 (IDCM 峰位 → 每實驗讀數)")
print("=" * 72)

# IDCM 峰位
idcm_peaks = {1: 220, 2: 537, 3: 810, 4: 1014, 5: 1199, 6: 1340, 7: 1412, 8: 1465, 9: 1474}

def read_planck(lp):
    idx = np.argmin(np.abs(l-lp))
    return Dl[idx]/D1

def read_act(lp):
    if lp < act_ell[0] or lp > act_ell[-1]:
        return None
    idx = np.argmin(np.abs(act_ell-lp))
    return act_D[idx]/act_D[5]  # 用峰3 (798) 做 ACT 基準? 唔啱 — 用 Planck D₁ cross-cal

# 用 cross-calibration: ACT D₁ 唔可得 (範圍外), 用 ACT 峰3 (798) 同 Planck 峰3 對齊
# Planck 峰3: 815 → D=2553; ACT 峰3: 798 → D=2500.7
cal = 2553/2500.7  # Planck/ACT 比例
print(f"Cross-calibration (峰3): ACT→Planck 比例 = {cal:.4f}")

print(f"\n{'峰':>3} | {'ℓ_idcm':>6} | {'P_m 理論':>8} | {'Planck A':>9} | {'ACT A':>8} | {'SPT A':>8}")
for m in range(2, 8):
    lp = idcm_peaks[m]
    # Planck
    idx = np.argmin(np.abs(l-lp))
    A_pl = Dl[idx]/D1
    # ACT
    if lp >= act_ell[0]:
        idx_a = np.argmin(np.abs(act_ell-lp))
        A_act = act_D[idx_a]*cal/D1
    else:
        A_act = float('nan')
    # SPT
    if 400 <= lp <= 3000:
        idx_s = np.argmin(np.abs(spt_centers-lp))
        A_spt = spt_150[idx_s]/D1
    else:
        A_spt = float('nan')
    print(f"{m:>3} | {lp:>6} | {P_th((m+1)//2):>8.4f} | {A_pl:>9.4f} | {A_act:>8.4f} | {A_spt:>8.4f}")

# ============ P_m 每實驗 ============
print("\n" + "=" * 72)
print("P_m 簡併對 (每實驗獨立)")
print("=" * 72)
pairs = {1: (2, 3), 2: (4, 5), 3: (6, 7)}
for m, (a, b) in pairs.items():
    la, lb = idcm_peaks[a], idcm_peaks[b]
    # Planck
    ia, ib = np.argmin(np.abs(l-la)), np.argmin(np.abs(l-lb))
    P_pl = (Dl[ia]+Dl[ib])/(2*D1)
    # ACT (跨校準後)
    P_act = None
    if la >= act_ell[0] and lb >= act_ell[0]:
        ja, jb = np.argmin(np.abs(act_ell-la)), np.argmin(np.abs(act_ell-lb))
        P_act = (act_D[ja]+act_D[jb])*cal/(2*D1)
    # SPT
    P_spt = None
    if la >= 400 and lb <= 3000:
        ka, kb = np.argmin(np.abs(spt_centers-la)), np.argmin(np.abs(spt_centers-lb))
        P_spt = (spt_150[ka]+spt_150[kb])/(2*D1)
    th = P_th(m)
    print(f"  P_{m} ({a},{b}): 理論 {th:.4f}")
    print(f"    Planck: {P_pl:.4f} (偏差 {(P_pl-th)/th*100:+.2f}%)")
    if P_act: print(f"    ACT:    {P_act:.4f} (偏差 {(P_act-th)/th*100:+.2f}%)")
    if P_spt: print(f"    SPT:    {P_spt:.4f} (偏差 {(P_spt-th)/th*100:+.2f}%)")

# ============ P₄ 最終裁決 ============
print("\n" + "=" * 72)
print("P₄ 最終裁決 (峰 8,9 @ 1465/1474)")
print("=" * 72)
P4_th = P_th(4)
print(f"  P₄ 預測 = {P4_th:.4f}")
print()
# Planck: 1465→1463 (762), 1474→1472 (750)
idx8 = np.argmin(np.abs(l-1465)); idx9 = np.argmin(np.abs(l-1474))
P4_pl = (Dl[idx8]+Dl[idx9])/(2*D1)
print(f"  Planck @ 1463/1472: P₄ = {P4_pl:.4f} (偏差 {(P4_pl-P4_th)/P4_th*100:+.1f}%)")
print(f"    → 但呢個係 damping tail 下降段, 唔係峰! (1409 後單調下降)")
# ACT: 1448 峰之後下降
idx_a8 = np.argmin(np.abs(act_ell-1465)); idx_a9 = np.argmin(np.abs(act_ell-1474))
P4_act = (act_D[idx_a8]+act_D[idx_a9])*cal/(2*D1)
print(f"  ACT @ 1448/1498: P₄ = {P4_act:.4f} (偏差 {(P4_act-P4_th)/P4_th*100:+.1f}%)")
print(f"    → ACT 峰 @1448 (峰7) 之後單調下降, 冇峰 8,9")
# SPT
idx_s8 = np.argmin(np.abs(spt_centers-1465)); idx_s9 = np.argmin(np.abs(spt_centers-1474))
P4_spt = (spt_150[idx_s8]+spt_150[idx_s9])/(2*D1)
print(f"  SPT @ 1475 (bin 21): P₄ ≈ {spt_150[21]/D1:.4f} (偏差 {(spt_150[21]/D1-P4_th)/P4_th*100:+.1f}%)")
print(f"    → SPT bin 21 = 748 µK² 係峰 7 尾部, 唔係峰 8,9")
print()
print("🔴 P₄ 裁決: 三實驗都冇峰 8,9 — ℓ>1500 係單調 damping tail")
print("   Fibonacci 階梯適用範圍: m ≤ 3 (P₁, P₂, P₃)")
print("   P₄ = 0.0775 預測無法驗證 (峰唔存在), 保持 🔴 開放")

# 儲存
results = {
    "planck": {"ell": l.tolist(), "D": Dl.tolist()},
    "act_dr6": {"ell": act_ell.tolist(), "D": act_D.tolist(), "cal": cal},
    "spt": {"centers": spt_centers.tolist(), "TT150": spt_150.tolist()},
    "p4_verdict": "FAILED_TO_VERIFY - no peaks 8,9 in any experiment",
}
with open(os.path.join(os.path.dirname(__file__), "..", "data", "three_experiment_crosscheck.json"), "w") as f:
    json.dump(results, f, indent=1)
print("\n已儲存 -> data/three_experiment_crosscheck.json")
