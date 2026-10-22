#!/usr/bin/env python3
"""O176 D1 attack — A5 node write = budget/N_gen (null->positive candidate).

O175 null: <|cos theta|> = 11/15 = 0.7333 predicted, observed 0.2443 (dev 66.7%)
Attack finding (docs/08): observed budget 60*B(n)*0.2443 = 20.49 = 61.5/3 (dev 0.06%)
  -> corrected candidate <|cos theta|> = 11/45 = 0.24444 (dev 0.06%)
Here: statistical robustness + structural subset tests + honest post-hoc flag.
"""
import numpy as np, math, statistics

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p4_cmb_cold_spot/data"
A = 134.2
B = 4; Nd = 44; L10 = 123
Bn = L10/(2*Nd)   # 123/88 = 1.3977

temps = {}
with open(f"{BASE}/smica_smoothed.txt") as f:
    for line in f:
        if line.startswith("#") or not line.strip(): continue
        p = line.split()
        temps[int(p[0])] = (float(p[2]), float(p[3]), float(p[4]), int(p[1]))  # T, l, b, color

# frustration edges: which node indices are involved?
frust = set()
try:
    with open(f"{BASE}/frustration_edges.txt") as f:
        for line in f:
            if line.startswith("#") or not line.strip(): continue
            for tok in line.replace("->", " ").replace(",", " ").split():
                if tok.isdigit(): frust.add(int(tok))
except FileNotFoundError:
    pass

idxs = list(range(60))
Ts = np.array([temps[i][0] for i in idxs])
dT = Ts - Ts.mean()
r = np.mean(np.abs(dT))/A

print("="*72)
print("D1: A5 60-node mean |cos theta| — reproduction & candidate test")
print("="*72)
print(f"  <|dT|>/A (obs)  = {r:.6f}")
print(f"  11/45 candidate = {11/45:.6f}  dev = {abs(r-11/45)/(11/45)*100:.4f}%")
print(f"  11/15 (O175)    = {11/15:.6f}  factor = {11/15/r:.4f} (~N_gen = 3)")

# bootstrap uncertainty on the mean
rng = np.random.default_rng(7)
bs = [np.mean(np.abs(rng.choice(dT, 60, replace=True)))/A for _ in range(2000)]
print(f"  bootstrap: mean={np.mean(bs):.4f} std={np.std(bs):.4f}  "
      f"(11/45 within {abs(np.mean(bs)-11/45)/np.std(bs):.2f} sigma)")

# budget interpretation
cost = 60*Bn*r
print(f"\n  budget cost 60*B(n)*obs = {cost:.4f} vs 61.5/3 = 20.5: dev {abs(cost-20.5)/20.5*100:.4f}%")
print(f"  obs/11/15 = {r/(11/15):.4f} (exactly N_gen? {abs(r/(11/15)-3)/3*100:.3f}% off)")

print("\n" + "="*72)
print("Structural subset tests (same data, split hypotheses)")
print("="*72)
def med_abs(arr): return np.mean(np.abs(arr - arr.mean()))/A

# (a) color split (smica_smoothed color 0/1)
c0 = np.array([temps[i][0] for i in idxs if temps[i][3]==0])
c1 = np.array([temps[i][0] for i in idxs if temps[i][3]==1])
print(f"  (a) color0 (N={len(c0)}): {med_abs(c0):.4f} | color1 (N={len(c1)}): {med_abs(c1):.4f}")

# (b) galactic hemisphere |b|>30 vs |b|<30
gal = np.array([temps[i][0] for i in idxs if abs(temps[i][2])>30])
loc = np.array([temps[i][0] for i in idxs if abs(temps[i][2])<=30])
print(f"  (b) |b|>30 (N={len(gal)}): {med_abs(gal):.4f} | |b|<=30 (N={len(loc)}): {med_abs(loc):.4f}")

# (c) frustration-edge nodes vs rest (if edges found)
if frust:
    fr = np.array([temps[i][0] for i in idxs if i in frust])
    nf = np.array([temps[i][0] for i in idxs if i not in frust])
    print(f"  (c) frust nodes (N={len(fr)}): {med_abs(fr):.4f} | non-frust (N={len(nf)}): {med_abs(nf):.4f}")
else:
    print("  (c) no frustration edge index map available")

# (d) every single-node leave-one-out: stability of the 11/45 match
loo = []
for i in idxs:
    rest = [j for j in idxs if j != i]
    T2 = np.array([temps[j][0] for j in rest])
    loo.append(np.mean(np.abs(T2 - T2.mean()))/A)
print(f"  (d) leave-one-out: mean={np.mean(loo):.4f} std={np.std(loo):.4f} min={min(loo):.4f} max={max(loo):.4f}")

# (e) node-level |cos| distribution vs uniform
absdT = np.abs(dT)/A
print(f"  (e) node |cos|: mean={absdT.mean():.4f} median={np.median(absdT):.4f} "
      f"std={absdT.std():.4f} max={absdT.max():.4f}")

# (f) sign structure: cold/hot balance
print(f"  (f) cold (dT<0): {np.sum(dT<0)} nodes, mean|dT|={np.mean(np.abs(dT[dT<0])):.2f} uK | "
      f"hot: {np.sum(dT>0)} nodes, mean|dT|={np.mean(np.abs(dT[dT>0])):.2f} uK")

print("\n" + "="*72)
print("VERDICT (honest)")
print("="*72)
print(f"  11/45 match: dev {abs(r-11/45)/(11/45)*100:.3f}% — within bootstrap std {np.std(bs):.4f}")
print(f"  BUT: single node set, single map, single smoothing — post-hoc risk REMAINS")
print(f"  Independent confirmation needs: other CMB maps (Commander/SEVEM/NILC),")
print(f"  other smoothing scales, other node sets (B5/C5, full 88-lattice)")
