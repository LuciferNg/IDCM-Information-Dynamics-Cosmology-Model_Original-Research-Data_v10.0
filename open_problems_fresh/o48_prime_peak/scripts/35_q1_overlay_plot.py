#!/usr/bin/env python3
"""
O48 Q1.19: 疊圖 — 「峰+谷」模型 vs 三實驗數據
=============================================================
可視確認峰谷對齊: 模型 (峰 44N+s + 谷 V¾, vdepth=0.5, σ=50)
vs Planck Plik-lite (613 bins) + SPT-3G (52) + ACT DR4 (40)
輸出: png 存 o48 docs/
"""
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

phi = (1+5**0.5)/2
F = lambda n: int(round((phi**n - (-phi)**(-n))/math.sqrt(5)))

base = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
DATA = f"{base}/o214_energy_budget_definition/data"
ACT = "/home/wsl/.hermes/cache/scratch/act_dr4/cmbonly_spectra_dr4.01/act_dr4.01_D_ell_TT_cmbonly.txt"
OUT = f"{base}/o48_prime_peak/docs/fig_q1_peak_valley_overlay.png"

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

plik = load_plik(); spt = load_spt(); act = load_act()

# ---------- 模型 ----------
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

ell = np.arange(200, 2500, 2.0)
T = np.zeros_like(ell)
for p in PEAKS:
    T += peak_amp(p)*np.exp(-0.5*((ell-p)/50.0)**2)
for v in V34:
    T -= 0.5*np.exp(-0.5*((ell-v)/50.0)**2)

# ---------- 繪圖 ----------
fig, ax = plt.subplots(2, 1, figsize=(11, 8), sharex=True)

# 上: 相對殘差 (detrend)
def resid_n(data, refT):
    ells = np.array([e for e, d in data])
    D = np.array([d for e, d in data])
    mask = D > 0
    logD = np.log(D[mask])
    coef = np.polyfit(ells[mask], logD, 2)
    res = D[mask]/np.exp(np.polyval(coef, ells[mask]))
    rn = (res - res.mean())/res.std()
    tint = np.interp(ells[mask], ell, refT)
    tn = (tint - tint.mean())/tint.std()
    return ells[mask], rn, tn

ax0 = ax[0]
for data, lab, col in [(plik, "Planck Plik-lite", "k"), (spt, "SPT-3G", "c"), (act, "ACT DR4", "m")]:
    e, r, _ = resid_n(data, T)
    ax0.plot(e, r, ".", ms=2, color=col, label=lab)
ax0.plot(ell, (T - T.mean())/T.std(), "-", color="r", lw=1.2, label="IDCM 峰+谷 V¾ model")
for p in PEAKS:
    ax0.axvline(p, color="r", ls=":", lw=0.5, alpha=0.4)
for v in V34:
    ax0.axvline(v, color="b", ls=":", lw=0.5, alpha=0.4)
ax0.set_ylabel("detrended residual (std)")
ax0.set_title("O48 Q1.19: 峰+谷 V¾ model vs Planck/SPT/ACT")
ax0.legend(fontsize=8, ncol=4)
ax0.grid(alpha=0.3)

# 下: 峰/谷標記 + D_ell 線
ax1 = ax[1]
e_p, d_p = [], []
with open(f"{DATA}/planck2018_plik_lite/cl_cmb_plik_v22.dat") as f:
    for line in f:
        p = line.split()
        if len(p) >= 2:
            try:
                e_p.append(float(p[0])); d_p.append(float(p[1]))
            except ValueError:
                pass
ax1.plot(e_p, d_p, "k.", ms=2, label="Planck Plik-lite D_ell")
e_s, d_s = zip(*spt); ax1.plot(e_s, d_s, "c.", ms=4, label="SPT-3G")
e_a, d_a = zip(*act); ax1.plot(e_a, d_a, "m.", ms=5, label="ACT DR4")
ax1.set_yscale("log")
# 峰/谷 annotate
for p in PEAKS:
    ax1.axvline(p, color="r", ls=":", lw=0.5, alpha=0.4)
for v in V34:
    ax1.axvline(v, color="b", ls=":", lw=0.5, alpha=0.4)
for i, p in enumerate([221, 527, 815, 1121, 1409]):
    ax1.annotate(f"P{i+1}", (p, 800), fontsize=8, color="r")
ax1.set_xlabel("ℓ"); ax1.set_ylabel("D_ell (μK²)")
ax1.legend(fontsize=8, ncol=4)
ax1.grid(alpha=0.3); ax1.set_xlim(200, 2500)

plt.tight_layout()
plt.savefig(OUT, dpi=150, bbox_inches="tight")
print(f"PNG saved: {OUT}")
print("Peaks:", PEAKS)
print("Valleys V¾:", [round(v,1) for v in V34])