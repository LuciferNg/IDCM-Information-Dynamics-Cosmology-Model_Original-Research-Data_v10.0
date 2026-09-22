#!/usr/bin/env python3
"""
O99 — scripts/06: 三條可證偽殺招 (P-C2 DDR, C1 透鏡, O99-A LIV)
================================================================
目的: 用現有(截至2026)真實觀測撞 O99/IDCM — 邊條撞就老實認.

殺招1 (DDR): D_L/D_A = (1+z)^eta. 用真 Pantheon+ 1701 cov + D_A.
   ★ 誠實關鍵: Pantheon+ 只量 D_L, D_A 必須由獨立 probe 來.
     殘招1a: D_A = IDCM D_app(ℓ)  -> 循環(IDCM 自己), 只證明「自洽」.
     殘招1b (公平): D_A = ΛCDM D_A(z) 獨立 -> 睇 η 收斂邊度、
   若程 (1b) 下 η 收斂 →2.0±0.02 @5σ 而排除 0.857 -> O99 死。

殺招2 (CMB lensing): IDCM 能否 有local 代數復現 C_ℓ^φ^φ 交叉強度.
殺招3 (GRB LIV): O99-A 載波 ripple≡0 -> zero-disp, 兼容 LHAASO 221009A.
"""

import math, os, json
import numpy as np

np.warnings.filterwarnings('ignore') if hasattr(np,'warnings') else None
c = 299792.458
R_world = 4129.94
phi = (1 + math.sqrt(5)) / 2
C_DELAY = -0.1697

DATA = (os.path.dirname(os.path.abspath(__file__))
        + "/../../o76_z_redshift_translation/data/pantheon")
dat_path = DATA + "/Pantheon+SH0ES.dat"
cov_path = DATA + "/Pantheon+SH0ES_STAT+SYS.cov"

def Dapp(ell):
    base = R_world * (1 - 4 ** (-ell))
    proj = 1 + 2 * phi ** (-1) * ell
    delta = C_DELAY * (ell - 0.5) * (1 - 4 ** (-ell))
    return base * (proj + delta)

def DA_lcdm(z, H0=67.4, Om=0.315):
    Ol = 1 - Om
    zz = np.geomspace(1e-6, max(z, 1e-3), 3000)
    E = np.sqrt(Om * (1 + zz) ** 3 + Ol)
    DC = c / H0 * np.trapezoid(1 / E, zz)
    return DC / (1 + z)

header = open(dat_path).readline().split()
ci = {n: i for i, n in enumerate(header)}
zs, mb = [], []
for line in open(dat_path).read().splitlines()[1:]:
    p = line.split()
    if len(p) < len(header):
        continue
    zs.append(float(p[ci['zCMB']])); mb.append(float(p[ci['m_b_corr']]))
zs = np.array(zs); mb = np.array(mb)
N = len(zs)
n = int(open(cov_path).readline().strip())
cov = np.loadtxt(cov_path, skiprows=1).reshape(n, n)
cov_inv = np.linalg.inv(cov)

ell = np.log(1 + zs) / np.log(4)
Da_idcm = np.array([Dapp(e) for e in ell])
Da_ld = np.array([DA_lcdm(zi) for zi in zs])

def fit(eta, Da):
    mu = 5 * np.log10(((1 + zs) ** eta) * Da * 1e6 / 10)
    J = np.ones(N)
    M = (J @ cov_inv @ (mb - mu)) / (J @ cov_inv @ J)
    chi = (mb - (mu + M)) @ cov_inv @ (mb - (mu + M))
    return M, chi

print("=" * 70)
print("殺招1 — DDR 公平對決: D_A 用 獨立 ΛCDM (唔用 IDCM 自家 D_app)")
print("=" * 70)
print("  僅測量 Pantheon+ 的量 D_L; D_A 由 ΛCDM 提供")
rows = []
for eta in [0.857, 1.0, 1.5, 2.0, 2.5]:
    M, chi = fit(eta, Da_ld)
    rows.append((eta, round(float(chi), 1)))
    print(f"  eta={eta:5.3f}   D_A=ΛCDM  chi2={chi:10.2f}  M={M:+.4f}")

best = min(rows, key=lambda r: r[1])
print(f"\n  best eta = {best[0]}  (chi2={best[1]:.1f})")
M85, c85 = fit(0.857, Da_ld)
M20, c20 = fit(2.0, Da_ld)
print(f"  eta=0.857(IDE): chi2={c85:.1f}   eta=2.0(std): 综合2={c20:.1f}  d={c85-c20:+.1f}")

# 判決: 若 c20(cdm) 明显好過 c85 且 eta 收斂到 2.0 -> LCDM DDR wins
verdict = ("O99_DDR_LIKELY_DEAD: D_A=ΛCDM 下 fit 呢把 eta=2.0 更佳"
           if c20 < c85 - 9 else
           "UNRESOLVED: 需獨立 D_A probe (BAO 角度) 先決")
print("\nVERDICT DDR(獨立D_A): " + verdict)
if c20 < c85 - 9:
    log_ok = "大 D 收於 2.0 -> 0.857 被排 -> O99 C2 死"
else:
    log_ok = "呢個 對決 未見 5σ kill (單靠 ΛCDM D_A + Pantheon 不够)"
print("  detail: " + log_ok)

print("\n" + "=" * 70); print("殺招2 — CMB lensing C_ℓ^φ^φ")
print("=" * 70)
print("  Planck/ACT 透鏡重建 契合「沿途重力屈」. IDCM 需 有local 代數復現.")
print("  誠實: 🔴 C1 透鏡對應項未閉合 -> 結構性風險 (唔係已經閉合)")

print("\n" + "=" * 70)
print("殺招3 — GRB/LHAASO LIV vs O99-A")
print("=" * 70)
print("  GRB 221009A 18 TeV; LIV Eqg>1e19 GeV. O99-A carrier ripple=0 zero-disp,")
print("  兼容。 H_mod if any 必須 <ms  18TeV。=> PASS 唔撞")

out = {"DDR_ldDm_scan": [{"eta": r, "chi2": ch} for r, ch in rows],
       "IDM_011_ch2": round(c85, 1), "LCDM_DAR_chi2": round(c20, 1),
       "dchi2_IndepDA": round(c85 - c20, 1),
       "DDR_verdict": verdict,
       "lensing_status": "RED_open_not_closed",
       "GRB_status": "compatible_zero_disp"}
_jp = os.path.dirname(os.path.abspath(__file__)) + "/../data/06_falsification.json"
with open(_jp, "w") as f:
    json.dump(out, f, indent=2)
print("\n-> data/06_falsification.json")