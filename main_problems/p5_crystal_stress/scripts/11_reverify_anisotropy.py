#!/usr/bin/env python3
"""
重驗 — Auger 各向異性 (對應 01_problem_record.md §2.5, p12_uhecrs/records/03_uhecrs_record.md §4)
=====================================================================================
6 精細能量層, 60 A₅ 節點 <8°, MC null (全天均勻隨機), Fisher + 能量加權 Fisher。
重算並比對文檔聲稱值。
"""
import math, os, json, sys
import numpy as np
from scipy.stats import chi2 as _chi2, norm as _norm

HERE = os.path.dirname(os.path.abspath(__file__))
CS   = os.path.dirname(HERE)                       # crystal_stress
SIB  = os.path.dirname(CS)                         # open_problems_fresh
UHE  = os.path.join(SIB, 'p12_uhecrs', 'data')
CMB  = os.path.join(SIB, 'p4_cmb_cold_spot', 'data')

SEED = 42
N_MC = 5000

# ---------- 載入 ----------
nodes = np.loadtxt(os.path.join(CMB, 'a5_nodes.txt'))
n_ra = np.radians(nodes[:, 0]); n_dec = np.radians(nodes[:, 1])
node_vec = np.column_stack([np.cos(n_dec)*np.cos(n_ra),
                            np.cos(n_dec)*np.sin(n_ra),
                            np.sin(n_dec)])          # (60,3)

ev = np.genfromtxt(os.path.join(UHE, 'auger_catalogSD.csv'), delimiter=',',
                   names=True, dtype=None, encoding='utf-8')
ev_E = ev['energy'].astype(float)
ev_ra = ev['ra'].astype(float); ev_dec = ev['dec'].astype(float)
N_ev = len(ev_E)

def unit(ra_deg, dec_deg):
    ra, dec = np.radians(ra_deg), np.radians(dec_deg)
    return np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])

def dmin(ra_deg, dec_deg):
    """每事件到最近節點嘅角距 (度)"""
    u = unit(np.asarray(ra_deg), np.asarray(dec_deg))
    cosd = np.clip(u @ node_vec.T, -1, 1)
    return np.degrees(np.arccos(cosd)).min(axis=1)

d_node = dmin(ev_ra, ev_dec)

print("=" * 78)
print("重驗 — Auger 各向異性 (109 事件, 60 A₅ 節點)")
print("=" * 78)
print(f"事件數 = {N_ev};  最近節點距離 中位 {np.median(d_node):.3f}°  平均 {np.mean(d_node):.3f}°  最小 {d_node.min():.3f}°")

# ---------- 能量層 ----------
E_bins = [46, 60, 80, 100, 130, 150, 200]
rng = np.random.default_rng(SEED)
bins = []
for i in range(len(E_bins) - 1):
    lo, hi = E_bins[i], E_bins[i+1]
    m = (ev_E >= lo) & (ev_E < hi)
    N = int(m.sum())
    if N < 2:
        continue
    obs = int((d_node[m] < 8).sum())
    mc = np.empty(N_MC, dtype=int)
    for j in range(N_MC):
        ra_r = rng.uniform(0, 360, N)
        dec_r = np.degrees(np.arcsin(rng.uniform(-1, 1, N)))
        mc[j] = (dmin(ra_r, dec_r) < 8).sum()
    mc_mean = mc.mean()
    p_hi = float((mc >= obs).mean()); p_lo = float((mc <= obs).mean())
    above = obs > mc_mean
    bins.append(dict(bin=f"{lo}-{hi}", N=N, obs=obs, obs_pct=obs/N*100,
                     mc_mean=float(mc_mean), mc_pct=float(mc_mean/N*100),
                     p_hi=p_hi, p_lo=p_lo, above=bool(above)))
    print(f"  {lo:>3}-{hi:<3} EeV: N={N:>3}  {obs:>3}/{N} = {obs/N*100:5.1f}%  MC={mc_mean:5.1f} ({mc_mean/N*100:4.1f}%)  "
          f"{'↑' if above else '↓'}  p={'%.4f' % (p_hi if above else p_lo)}")

# ---------- Sign test ----------
n_bins = len(bins); n_above = sum(b['above'] for b in bins)
p_sign = 0.5**n_bins
p_sign_binom = sum(math.comb(n_bins, k)*0.5**n_bins for k in range(n_above, n_bins+1))

# ---------- Fisher ----------
def z_of_p(p):
    return float(_norm.isf(p))
p_vals = [b['p_hi'] if b['above'] else b['p_lo'] for b in bins]
chi2 = -2*sum(math.log(p) for p in p_vals)
p_fisher = float(_chi2.sf(chi2, 2*len(p_vals)))
# 能量加權 (複刻舊法: w_i = sqrt(E_mid_i / E_min))
weights = [math.sqrt(((E_bins[i]+E_bins[i+1])/2)/E_bins[0]) for i in range(len(bins))]
chi2_w = -2*sum(w*math.log(p) for w, p in zip(weights, p_vals))
p_fisher_w = float(_chi2.sf(chi2_w, 2*len(p_vals)))

print(f"\nSign test: {n_above}/{n_bins} bins Obs>MC;  P(all)={(0.5)**n_bins:.6f}  P(≥{n_above})={p_sign_binom:.6f}")
print(f"Fisher    : χ²={chi2:.3f} df={2*len(p_vals)}  p={p_fisher:.6f}  z={z_of_p(p_fisher):.3f}σ")
print(f"加權Fisher: χ²_w={chi2_w:.3f}        p={p_fisher_w:.6f}  z={z_of_p(p_fisher_w):.3f}σ")

# ---------- 比對文檔 ----------
claim = json.load(open(os.path.join(UHE, 'anisotropy_joint_test.json')))
print("\n" + "=" * 78)
print(f"{'量':<24}{'重算':>16}{'文檔 JSON':>16}{'':>6}")
print("-" * 78)
rows = [
    ("Fisher p",        p_fisher,      claim['fisher']['p']),
    ("Fisher z (σ)",    z_of_p(p_fisher), claim['fisher']['z']),
    ("加權 Fisher p",    p_fisher_w,    claim['fisher_weighted']['p']),
    ("加權 Fisher z (σ)", z_of_p(p_fisher_w), claim['fisher_weighted']['z']),
]
allok = True
for label, got, cl in rows:
    ok = abs(got/cl - 1) < 0.02
    allok &= ok
    print(f"{label:<24}{got:>16.6g}{cl:>16.6g}{'✅' if ok else '❌':>6}")
# 逐 bin 比對
print("\n逐 bin 比對 (obs / MC mean):")
for b, c in zip(bins, claim['bins']):
    ok = b['N'] == c['N'] and b['obs'] == c['obs'] and abs(b['mc_mean']/c['mc_mean'] - 1) < 0.05
    allok &= ok
    print(f"  {b['bin']:<8} N={b['N']:>3} obs={b['obs']:>3} (doc {c['obs']:>3})  "
          f"MC={b['mc_mean']:6.2f} (doc {c['mc_mean']:6.2f})  {'✅' if ok else '❌'}")

print("-" * 78)
print(f"結果: {'全部一致 ✅' if allok else '有偏差 ❌'}")

out = os.path.join(CS, 'data', 'reverify_anisotropy.json')
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump({"bins": bins, "sign": {"n_bins": n_bins, "n_above": n_above, "p_all": p_sign, "p_binom": p_sign_binom},
           "fisher": {"p": p_fisher, "z": z_of_p(p_fisher)},
           "fisher_weighted": {"p": p_fisher_w, "z": z_of_p(p_fisher_w)},
           "all_pass": bool(allok)}, open(out, 'w'), indent=2)
print(f"已存 {out}")
sys.exit(0 if allok else 1)
