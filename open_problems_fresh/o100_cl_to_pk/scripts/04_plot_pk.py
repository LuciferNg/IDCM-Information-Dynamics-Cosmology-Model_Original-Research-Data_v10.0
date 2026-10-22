#!/usr/bin/env python3
"""
O100 — 視覺化: IDCM P_3D(k) 線譜 vs BOSS DR12 P(k)
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
d2 = json.load(open(os.path.join(OUT, "02_inverse_abel.json")))
k_h = np.array(d2["k_h"]); P_m = np.array(d2["P_Mpc3"]); h = 0.6727
P_m_h = P_m/h**3

WIG = "/home/wsl/IDCM/sync_bump_analysis/boss_dr12_bao_wiggles.txt"
kb, Pb, Psb = [], [], []
for line in open(WIG):
    if line.startswith('#') or not line.strip(): continue
    p = line.split()
    if len(p) < 4: continue
    kb.append(float(p[0])); Pb.append(float(p[1])); Psb.append(float(p[2]))
kb = np.array(kb); Pb = np.array(Pb); Psb = np.array(Psb)

fig, ax = plt.subplots(figsize=(9, 6))
ax.loglog(kb, Pb, '-', color='#888888', lw=1.2, label='BOSS DR12 P(k)')
ax.loglog(kb, Psb, '--', color='#aaaaaa', lw=1.0, label='P_smooth (BAO 分解)')
# IDCM 線譜 (豎線)
for kk, pp in zip(k_h, P_m_h):
    ax.plot([kk, kk], [pp*0.3, pp], color='#c0392b', lw=2.0)
    ax.plot(kk, pp, 'v', color='#c0392b', ms=7)
# σ8 窗 (R=8 h⁻¹Mpc)
kwin = np.linspace(0.02, 1.0, 200)
W = 3*(np.sin(kwin*8)-kwin*8*np.cos(kwin*8))/(kwin*8)**3
ax.axvspan(0.1, 0.45, color='#2e86c1', alpha=0.08)
ax.text(0.11, 3e3, 'σ$_8$ 窗 (k ~ 0.1-0.45)', fontsize=9, color='#2e86c1')
ax.set_xlabel('k (h/Mpc)'); ax.set_ylabel('P(k)  (Mpc/h)$^3$')
ax.set_title('O100: IDCM C$_\\ell$ → P$_{3D}$(k) 逆投影線譜 (σ$_8^{ID}$=0.748) vs BOSS DR12')
ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUT, "P3D_vs_BOSS.png"), dpi=150)
print("saved:", os.path.join(OUT, "P3D_vs_BOSS.png"))