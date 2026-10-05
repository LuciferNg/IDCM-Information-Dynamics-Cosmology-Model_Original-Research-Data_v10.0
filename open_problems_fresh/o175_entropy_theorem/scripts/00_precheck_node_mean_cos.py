#!/usr/bin/env python3
"""
O175 pre-check — budget = node-write identity test
==================================================
Prediction: 60-node write cost = full observer budget 61.5
  60 x B(n) x gamma x <|cos theta|> = 61.5 x gamma
  => <|cos theta|> = 61.5 x 88 / (60 x 123) = 11/15 = 0.7333...
with cos theta_i = deltaT_i / A  (O7: h_i = deltaT_i = A cos theta_i, A = 134.2 uK)
i.e. the observed mean absolute node temperature deviation / A must equal 11/15.
"""
import numpy as np
from pathlib import Path

BASE = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p4_cmb_cold_spot/data")

A = 134.2          # uK — cold spot amplitude (O41: A = 88x61/40)
B = 4
Nd = 44
L10 = 123          # Lucas 10
Bn = L10 / (2*Nd)  # per-mode budget = 123/88

# read node temperatures: smica_smoothed.txt = "idx color T_smooth_uK l_deg b_deg"
temps = {}
with open(BASE / "smica_smoothed.txt") as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        p = line.split()
        idx = int(p[0]); T = float(p[2])
        temps[idx] = T

print(f"nodes read: {len(temps)}")

# node directions
nodes = np.loadtxt(BASE / "a5_nodes.txt")  # RA Dec, row index = node idx
print(f"node directions: {nodes.shape}")

Ts = np.array([temps[i] for i in range(60)])
dT = Ts - Ts.mean()   # mean-removed fluctuation at nodes

mean_abs_dT = np.mean(np.abs(dT))
ratio = mean_abs_dT / A
target = 11/15

print(f"<|dT|>  = {mean_abs_dT:.4f} uK")
print(f"<|dT|>/A = {ratio:.6f}")
print(f"11/15    = {target:.6f}")
print(f"dev      = {abs(ratio/target - 1)*100:.3f}%")
print(f"max|dT|  = {np.max(np.abs(dT)):.2f} uK (A = {A})")
print(f"max|dT|/A = {np.max(np.abs(dT))/A:.4f}")
print(f"<dT>     = {dT.mean():.4f} (should be ~0)")
print()
print("per-node write cost check:")
cost_per_node = Bn * mean_abs_dT   # B(n) x <|cos|> in uK-scale units (gamma cancels)
total_cost = 60 * Bn * (mean_abs_dT / A)   # in budget units (B(n) x <|cos|>)
print(f"  budget units consumed = 60 x B(n) x <|cos|> = {total_cost:.4f}  (61.5 = full budget)")
print(f"  fraction of budget    = {total_cost/61.5:.4f}  (1.0 = exact)")

# node with max |dT|
imax = int(np.argmax(np.abs(dT)))
print(f"\nnode {imax}: RA={nodes[imax,0]:.2f} Dec={nodes[imax,1]:.2f} T={Ts[imax]:+.1f} uK")

# cold spot at (209, -57)? find nearest node
cs_ra, cs_dec = 209.0, -57.0
ra = np.radians(nodes[:,0]); dec = np.radians(nodes[:,1])
cs_ra_r, cs_dec_r = np.radians(cs_ra), np.radians(cs_dec)
ang = np.arccos(np.clip(np.sin(dec)*np.sin(cs_dec_r) + np.cos(dec)*np.cos(cs_dec_r)*np.cos(ra-cs_ra_r), -1, 1))
inearest = int(np.argmin(ang))
print(f"cold spot (209,-57): nearest node {inearest} at {np.degrees(ang[inearest]):.2f} deg, T={Ts[inearest]:+.1f} uK")
