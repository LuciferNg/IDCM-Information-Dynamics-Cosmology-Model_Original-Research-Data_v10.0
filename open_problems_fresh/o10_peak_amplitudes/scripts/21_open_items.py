#!/usr/bin/env python3
"""
O10 21: 誠實開放項 🟡 全面推進
================================
A. P₁ 偏差: CAMB ISW 成分分離 (spectra=['isw'])
B. P₂ 跨實驗散射: 用 O9 修正峰位 (221/527/815/1013/1121/1337/1400) 重讀
C. Silk 解耦: unlensed @ 修正峰位, 擬合 ℓ_D
D. 階梯截斷: C(9−m,2) 三角形數階梯 → m=8,9 退化
"""
import numpy as np, math, os, json
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

phi = (1 + 5**0.5) / 2
eps = phi**-1/4
F = [1, 1, 2, 3, 5, 8, 13, 21, 34]
def P_th(m):
    return 3*eps*F[m-1]*phi**(-2*(m-1))

# O9 修正峰位 (閉合 RMS 0.83%)
IDCM_POS = {1: 221, 2: 527, 3: 815, 4: 1013, 5: 1121, 6: 1337, 7: 1400}

print("=" * 72)
print("A. P₁ ISW 成分分離 (CAMB)")
print("=" * 72)
try:
    import camb
    pars = camb.CAMBparams()
    pars.set_cosmology(H0=67.36, ombh2=0.02237, omch2=0.1200, tau=0.0544)
    pars.InitPower.set_params(ns=0.9649, As=2.1e-9)
    pars.set_for_lmax(3000)
    res = camb.get_results(pars)
    # 試 isw spectrum
    try:
        spec = res.get_cmb_power_spectra(spectra=['total', 'unlensed_scalar', 'isw'], CMB_unit='muK')
        print("CAMB spectra keys:", list(spec.keys()))
        if 'isw' in spec:
            isw = spec['isw'][:, 0]
            tot = spec['total'][:, 0]
            for lp in [100, 150, 220, 300, 527]:
                if lp < len(isw):
                    frac = isw[lp]/tot[lp]*100
                    print(f"  ℓ={lp}: ISW={isw[lp]:.0f} μK², total={tot[lp]:.0f}, 佔比={frac:.1f}%")
    except Exception as e:
        print(f"  isw spectrum 不可用: {e}")
        # fallback: source cls dict
        try:
            src = res.get_source_cls_dict()
            print("  source cls keys:", list(src.keys())[:10])
        except Exception as e2:
            print(f"  source cls 不可用: {e2}")
except ImportError:
    print("  CAMB 不可用")

print()
print("=" * 72)
print("B. P_m 用 O9 修正峰位重讀 (三實驗)")
print("=" * 72)

# Planck
DATA = os.path.join(os.path.dirname(__file__), "..", "..", "o9_high_ell_peaks", "data", "planck_tt.txt")
data = np.loadtxt(DATA)
l, val, err = data[:,0], data[:,1], data[:,2]
Dl = val * l*(l+1)/(2*np.pi)
Dl_err = err * l*(l+1)/(2*np.pi)
D1 = Dl[np.argmin(np.abs(l-221))]

def read_pl(lp):
    idx = np.argmin(np.abs(l-lp))
    return Dl[idx]/D1, Dl_err[idx]/D1, l[idx]

print("\nPlanck @ O9 峰位:")
A_pl = {}
for m in range(1, 8):
    r, e, lb = read_pl(IDCM_POS[m])
    A_pl[m] = r
    print(f"  m={m}: ℓ_idcm={IDCM_POS[m]} → bin {lb:.0f}, A={r:.4f}±{e:.4f}")

# ACT DR6
from astropy.io import fits
path = os.path.join(os.path.dirname(__file__), "..", "..", "o9_high_ell_peaks", "data", "act_dr6_cmb_sacc.fits")
hdul = fits.open(path)
tt = hdul['data:cl_00'].data
act_ell, act_D = tt['ell'], tt['value']
# cross-cal via 峰3 (ACT 798 vs Planck 815)
cal = Dl[np.argmin(np.abs(l-815))]/(act_D[np.argmin(np.abs(act_ell-815))])
print(f"\nACT DR6 (cross-cal factor {cal:.4f}):")
A_act = {}
for m in range(1, 8):
    lp = IDCM_POS[m]
    if lp < act_ell[0]:
        print(f"  m={m}: ℓ={lp} 範圍外")
        A_act[m] = None
        continue
    idx = np.argmin(np.abs(act_ell-lp))
    A_act[m] = act_D[idx]*cal/D1
    print(f"  m={m}: ℓ={lp} → bin {act_ell[idx]:.0f}, A={A_act[m]:.4f}")

# SPT
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
# SPT cross-cal via 峰3 (825 vs Planck 815)
spt_cal = Dl[np.argmin(np.abs(l-815))]/spt_150[np.argmin(np.abs(spt_centers-815))]
print(f"\nSPT-3G (cross-cal factor {spt_cal:.4f}):")
A_spt = {}
for m in range(1, 8):
    lp = IDCM_POS[m]
    if lp < 400 or lp > 3000:
        A_spt[m] = None
        continue
    idx = np.argmin(np.abs(spt_centers-lp))
    A_spt[m] = spt_150[idx]*spt_cal/D1
    print(f"  m={m}: ℓ={lp} → bin {spt_centers[idx]:.0f}, A={A_spt[m]:.4f}")

# P_m 三實驗表
print("\n" + "=" * 72)
print("P_m 三實驗 (O9 峰位)")
print("=" * 72)
pairs = {1: (2, 3), 2: (4, 5), 3: (6, 7)}
for m, (a, b) in pairs.items():
    th = P_th(m)
    print(f"  P_{m} (m{a},{m}{b}? no, ({a},{b})): 理論 {th:.4f}")
    if A_pl[a] and A_pl[b]:
        p = (A_pl[a]+A_pl[b])/2
        print(f"    Planck: {p:.4f} (偏差 {(p-th)/th*100:+.2f}%)")
    if A_act[a] and A_act[b]:
        p = (A_act[a]+A_act[b])/2
        print(f"    ACT:    {p:.4f} (偏差 {(p-th)/th*100:+.2f}%)")
    if A_spt[a] and A_spt[b]:
        p = (A_spt[a]+A_spt[b])/2
        print(f"    SPT:    {p:.4f} (偏差 {(p-th)/th*100:+.2f}%)")
    print()

# 峰內不對稱性
print("=" * 72)
print("簡併對內部不對稱性 (A_{2m}/A_{2m+1})")
print("=" * 72)
for m, (a, b) in pairs.items():
    if A_pl[a] and A_pl[b]:
        print(f"  P_{m} Planck: A{a}/A{b} = {A_pl[a]/A_pl[b]:.4f} (1=完美簡併)")
    if A_act[a] and A_act[b]:
        print(f"  P_{m} ACT:    A{a}/A{b} = {A_act[a]/A_act[b]:.4f}")
    if A_spt[a] and A_spt[b]:
        print(f"  P_{m} SPT:    A{a}/A{b} = {A_spt[a]/A_spt[b]:.4f}")

# 儲存
results = {"idcm_pos": IDCM_POS,
           "planck": A_pl, "act": A_act, "spt": A_spt,
           "P_th": {str(m): P_th(m) for m in [1,2,3]}}
with open(os.path.join(os.path.dirname(__file__), "..", "data", "o9_positions_crosscheck.json"), "w") as f:
    json.dump(results, f, indent=1)
print("\n已儲存 -> data/o9_positions_crosscheck.json")
