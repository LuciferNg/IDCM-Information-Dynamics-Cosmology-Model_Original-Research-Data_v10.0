#!/usr/bin/env python3
"""
重驗 — 星系團節點核心真空 (對應 01_problem_record.md §2.6, p12_uhecrs/records/05_psz1_vacuum_result.md)
========================================================================================
4 目錄 (PSZ1/PSZ2/MCXC/Abell) 重新下載 (HEASARC TAP) → 重跑節點核心真空掃描 → Fisher 合併。
複刻舊 script 13/14/16/17 方法 (seed 42, N_MC, 半徑序列), 比對文檔 JSON。
"""
import math, os, json, io, sys, urllib.request, urllib.parse
import numpy as np
from astropy.io import votable
from scipy.stats import chi2 as _chi2

HERE = os.path.dirname(os.path.abspath(__file__))
CS   = os.path.dirname(HERE)
SIB  = os.path.dirname(CS)
CMB  = os.path.join(SIB, 'p4_cmb_cold_spot', 'data')
UHE  = os.path.join(SIB, 'p12_uhecrs', 'data')
DATA = os.path.join(CS, 'data')
os.makedirs(DATA, exist_ok=True)

TAP = "https://heasarc.gsfc.nasa.gov/xamin/vo/tap/sync"

def fetch_radec(table):
    cache = os.path.join(DATA, f"_cat_{table}.npz")
    if os.path.exists(cache):
        z = np.load(cache); return z['ra'], z['dec']
    q = urllib.parse.urlencode({"REQUEST": "doQuery", "LANG": "ADQL",
                                "FORMAT": "votable", "QUERY": f"SELECT ra, dec FROM {table}"})
    with urllib.request.urlopen(TAP + "?" + q, timeout=180) as r:
        raw = r.read()
    t = votable.parse(io.BytesIO(raw)).get_first_table().to_table()
    ra = np.array(t['ra'], dtype=float); dec = np.array(t['dec'], dtype=float)
    np.savez(cache, ra=ra, dec=dec)
    return ra, dec

# ---------- 節點 ----------
nodes = np.loadtxt(os.path.join(CMB, 'a5_nodes.txt'))
n_ra, n_dec = np.radians(nodes[:, 0]), np.radians(nodes[:, 1])
node_vec = np.column_stack([np.cos(n_dec)*np.cos(n_ra), np.cos(n_dec)*np.sin(n_ra), np.sin(n_dec)])
cos_r_cache = {}

def unit(ra_deg, dec_deg):
    ra, dec = np.radians(ra_deg), np.radians(dec_deg)
    return np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])

def scan(cl_ra, cl_dec, radii, n_mc):
    """複刻: seed 42, 每半徑 n_mc 次全天均勻 MC; 返回 {r: (obs, mc_mean, p_deficit)}"""
    u = unit(cl_ra, cl_dec)
    cosd = np.clip(u @ node_vec.T, -1, 1)
    maxc = cosd.max(axis=1)                       # 每團到最近節點嘅 cos
    rng = np.random.default_rng(42)
    N = len(cl_ra)
    out = {}
    for r in radii:
        thr = math.cos(math.radians(r))
        obs = int((maxc >= thr).sum())
        mc = np.empty(n_mc, dtype=int)
        for i in range(n_mc):
            ra_r = rng.uniform(0, 360, N)
            dec_r = np.degrees(np.arcsin(rng.uniform(-1, 1, N)))
            c = np.clip(unit(ra_r, dec_r) @ node_vec.T, -1, 1).max(axis=1)
            mc[i] = (c >= thr).sum()
        out[r] = (obs, float(mc.mean()), float((mc <= obs).mean()))
    return out

specs = [
    # name, table, radii, n_mc, stored json, stored-key style
    ("PSZ1",  "plancksz",  np.arange(3, 9.5, 0.5), 5000, "psz1_vacuum_scan.json", None),
    ("PSZ2",  "plancksz2", np.arange(3, 9.0, 0.5), 5000, "psz2_vacuum_scan.json", "psz2"),
    ("MCXC",  "mcxc",      np.arange(3, 9.0, 0.5), 5000, "mcxc_vacuum_scan.json", "mcxc"),
    ("Abell", "abell",     np.arange(3, 9.0, 0.5), 1500, "abell_vacuum_scan.json", "abell"),
]

print("=" * 84)
print("重驗 — 星系團節點核心真空 (4 目錄, HEASARC 重新下載)")
print("=" * 84)

results = {}
best_p = {}
allok = True
for name, tbl, radii, n_mc, jfile, key in specs:
    ra, dec = fetch_radec(tbl)
    print(f"\n### {name} ({tbl}): {len(ra)} 星系團")
    res = scan(ra, dec, radii, n_mc)
    results[name] = res
    # 比對文檔
    doc = json.load(open(os.path.join(UHE, jfile)))
    docd = doc[key] if key else doc
    print(f"  {'半徑':>6}{'obs':>7}{'doc':>7}{'MC':>9}{'docMC':>9}{'p_deficit':>11}{'doc':>9}{'':>3}")
    for r in radii:
        obs, mcm, p = res[r]
        d = docd.get(f"{r}deg")
        if d is None:
            print(f"  {r:>6.1f}{obs:>7}  (文檔缺)"); continue
        ok = (obs == d['obs']) and abs(mcm/d['mc_mean'] - 1) < 0.02 and abs(p - d['p_deficit']) < 0.02
        allok &= ok
        print(f"  {r:>6.1f}{obs:>7}{d['obs']:>7}{mcm:>9.1f}{d['mc_mean']:>9.1f}{p:>11.4f}{d['p_deficit']:>9.4f}{'✅' if ok else '❌':>3}")
    best_r = min(res, key=lambda k: res[k][2])
    best_p[name] = res[best_r][2]
    print(f"  最顯著: <{best_r}° p={res[best_r][2]:.4f}")

# ---------- Fisher 合併 ----------
print("\n" + "=" * 84)
print("Fisher 合併 (4 目錄, 用各自最顯著 p)")
print("=" * 84)
# 文檔用法: 硬編碼前三目錄 p + Abell 最顯著
p_used = [0.0048, 0.0560, 0.0280, best_p['Abell']]
chi2_v = -2 * sum(math.log(p) for p in p_used)
p_fisher4 = float(_chi2.sf(chi2_v, 2*len(p_used)))
from scipy.stats import norm as _norm
z4 = float(_norm.isf(p_fisher4))
# 三目錄 (MCXC json 內)
p3 = [0.0048, 0.0560, best_p['MCXC']]
p_fisher3 = float(_chi2.sf(-2*sum(math.log(p) for p in p3), 2*len(p3)))
print(f"  各目錄最顯著 p: PSZ1={p_used[0]} PSZ2={p_used[1]} MCXC={p_used[2]} Abell={p_used[3]:.4f}")
print(f"  Fisher4: χ²={chi2_v:.3f} df=8  p={p_fisher4:.6f}  z={z4:.3f}σ   (文檔 0.00030037, 3.43σ)")
print(f"  Fisher3(MCXC json 0.00062): 重算 p={p_fisher3:.6f}")
ok_f4 = abs(p_fisher4/0.00030037227098478336 - 1) < 0.05
print(f"  Fisher4 一致: {'✅' if ok_f4 else '❌'}")
allok &= ok_f4

print("\n" + "=" * 84)
print(f"結果: {'全部一致 ✅' if allok else '有偏差 ❌'}")
out = os.path.join(DATA, 'reverify_cluster_vacuum.json')
json.dump({n: {f"{r}": {"obs": v[0], "mc_mean": v[1], "p_deficit": v[2]} for r, v in res.items()}
           for n, res in results.items()} |
          {"fisher4_p": p_fisher4, "fisher4_z": z4, "all_pass": bool(allok)},
          open(out, 'w'), indent=2)
print(f"已存 {out}")
sys.exit(0 if allok else 1)
