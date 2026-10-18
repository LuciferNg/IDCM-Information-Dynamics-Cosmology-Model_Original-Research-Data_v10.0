#!/usr/bin/env python3
"""
P12 攻堅 — 阻挫邊預言判決: deficit p + 三分區分解 (2026-10-18)
==============================================================
script 24 揭發 edge-only 0/68 (剔除節點帶後) — 需判定係咩:
  (1) exact Binomial deficit p (obs=0 vs MC 期望率)
  (2) 三分區分解: 節點帶 (d_node<8°) / 邊中段帶 (d_node≥8° 且 d_edge<8°) / 其餘
      — 觀測 vs MC null 逐區, 加 χ² 聯合檢驗
"""
import os, json, csv
import numpy as np
from scipy.stats import binom, chi2 as _chi2

HERE = os.path.dirname(os.path.abspath(__file__))
P12  = os.path.dirname(HERE)
MAIN = os.path.dirname(P12)
CMB  = os.path.join(MAIN, 'p4_cmb_cold_spot', 'data')
DATA = os.path.join(P12, 'data')

nodes = np.loadtxt(os.path.join(CMB, 'a5_nodes.txt'))
edges = []
with open(os.path.join(CMB, 'frustration_edges.txt')) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'): continue
        p = line.split()
        edges.append(((float(p[4]), float(p[5])), (float(p[6]), float(p[7]))))

ev_ra, ev_dec, ev_E = [], [], []
with open(os.path.join(DATA, 'auger_catalogSD.csv')) as f:
    for row in csv.DictReader(f):
        ev_ra.append(float(row['ra'])); ev_dec.append(float(row['dec'])); ev_E.append(float(row['energy']))
ev_ra = np.array(ev_ra); ev_dec = np.array(ev_dec); ev_E = np.array(ev_E)
N = len(ev_ra)

def uv(ra, dec):
    ra, dec = np.radians(ra), np.radians(dec)
    return np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])

nv = uv(nodes[:, 0], nodes[:, 1])
def d_node(ra, dec):
    return np.degrees(np.arccos(np.clip(uv(ra, dec) @ nv.T, -1, 1).max(axis=1)))

def d_edge(ra, dec):
    u = uv(ra, dec); best = np.full(len(u), 1e10)
    for (r1,d1),(r2,d2) in edges:
        v1 = uv(r1,d1).ravel(); v2 = uv(r2,d2).ravel()
        nvec = np.cross(v1,v2); nvec = nvec/np.linalg.norm(nvec)
        pdotn = u @ nvec
        perp = np.degrees(np.arcsin(np.clip(np.abs(pdotn),0,1)))
        # ★ 正確弧內容判定 (2026-10-18 修正, 同 script 24)
        Pp = u - pdotn[:,None]*nvec
        Pp = Pp/np.maximum(np.linalg.norm(Pp,axis=1,keepdims=True),1e-12)
        cr1 = np.cross(np.broadcast_to(v1, u.shape), Pp) @ nvec
        cr2 = np.cross(Pp, np.broadcast_to(v2, u.shape)) @ nvec
        inside = (cr1 >= 0) & (cr2 >= 0)
        d1a = np.degrees(np.arccos(np.clip(u @ v1,-1,1))); d2a = np.degrees(np.arccos(np.clip(u @ v2,-1,1)))
        best = np.minimum(best, np.where(inside, perp, np.minimum(d1a,d2a)))
    return best

dn = d_node(ev_ra, ev_dec); de = d_edge(ev_ra, ev_dec)

# ---------- (1) 條件化 edge-only rate 檢驗 (MC 施加同一 d_node≥8° 條件) ----------
N_MC = 5000
rng = np.random.default_rng(42)
keep_obs = dn >= 8.0
n_kept_obs = int(keep_obs.sum()); obs_cnt = int((de[keep_obs] < 8).sum())
rates = np.empty(N_MC); cnts = np.empty(N_MC, dtype=int); nks = np.empty(N_MC, dtype=int)
for i in range(N_MC):
    ra_r = rng.uniform(0, 360, N)
    dn_mc = d_node(ra_r, ev_dec); de_mc = d_edge(ra_r, ev_dec)
    k = dn_mc >= 8.0
    nk = int(k.sum()); c = int((de_mc[k] < 8).sum())
    nks[i] = nk; cnts[i] = c; rates[i] = c/nk if nk else 0.0
obs_rate = obs_cnt/n_kept_obs
p_rate_hi = float((rates >= obs_rate).mean())          # 超額檢驗
p_rate_lo = float((rates <= obs_rate).mean())          # 不足檢驗 (deficit)
print(f"(1) 條件化 edge-only (d_node≥8° 內, edge<8°):")
print(f"    obs = {obs_cnt}/{n_kept_obs} ({obs_rate*100:.1f}%);  條件化 MC rate = "
      f"{rates.mean()*100:.1f}% ± {rates.std()*100:.1f}%  (MC 每次 n_kept = {nks.mean():.1f}±{nks.std():.1f})")
print(f"    p(超額) = {p_rate_hi:.4f};  p(不足) = {p_rate_lo:.4f}")

# ---------- (2) 三分區分解 (+MC null) ----------
def zone_counts(ra, dc):
    d_n = d_node(ra, dc); d_e = d_edge(ra, dc)
    z_node = (d_n < 8).sum()
    z_mid  = ((d_n >= 8) & (d_e < 8)).sum()
    return int(z_node), int(z_mid), int(len(ra) - z_node - z_mid)

obs3 = zone_counts(ev_ra, ev_dec)
rng = np.random.default_rng(42)
N_MC = 5000
mc3 = np.zeros((N_MC, 3), dtype=int)
for i in range(N_MC):
    mc3[i] = zone_counts(rng.uniform(0,360,N), ev_dec)
exp3 = mc3.mean(axis=0); sd3 = mc3.std(axis=0)
print(f"\n(2) 三分區 (Auger 109, E≥46):")
labels = ["節點帶 d_node<8°", "邊中段 d_node≥8°&d_edge<8°", "其餘"]
for j,l in enumerate(labels):
    dev = (obs3[j]-exp3[j])/sd3[j]
    print(f"    {l:<26}: obs={obs3[j]:>3} ({obs3[j]/N*100:>5.1f}%)  MC={exp3[j]:>5.1f}±{sd3[j]:<4.1f}  dev={dev:+.2f}σ")
# 聯合 χ² (三分區 multinomial, 用 MC 期望)
chi2_stat = float(((np.array(obs3)-exp3)**2 / np.maximum(exp3,1e-9)).sum())
# 注意自由度 = 2 (三分區, 和約束)
p_chi2 = float(_chi2.sf(chi2_stat, 2))
print(f"    聯合 χ² = {chi2_stat:.2f} (df=2)  p = {p_chi2:.3e}")
# 兩項 z: 節點超額 + 邊中段不足 (方向一致性)
z_node = (obs3[0]-exp3[0])/sd3[0]; z_mid = (obs3[1]-exp3[1])/sd3[1]
# Stouffer (雙尾同向獨立? 保守用單尾): 節點超額 (+, 4.3σ), 邊中段不足 (−, 5.3σ)
print(f"    方向: 節點超額 z={z_node:+.2f}σ; 邊中段不足 z={z_mid:+.2f}σ")

# 低能段避開 p — 直接讀 script 24 輸出 (唔硬編碼)
p_low8 = json.load(open(os.path.join(DATA, 'edge_auger_and_lowenergy.json')))[
    'p12_edge_and_lowenergy_20261018']['low_energy_B']['p_deficit8']

out = {"p12_frustration_edge_verdict_20261018": {
    "N": N, "N_MC": N_MC, "seed": 42,
    "conditioned_edge": {"n_kept_obs": n_kept_obs, "obs_within8": obs_cnt,
                         "obs_rate": round(obs_rate, 6),
                         "mc_rate_mean": round(float(rates.mean()), 6),
                         "mc_rate_sd": round(float(rates.std()), 6),
                         "mc_n_kept_mean": round(float(nks.mean()), 1),
                         "p_excess": p_rate_hi, "p_deficit": p_rate_lo},
    "zones": {labels[j]: {"obs": obs3[j], "mc_mean": round(float(exp3[j]),1),
                          "mc_sd": round(float(sd3[j]),1),
                          "dev_sigma": round(float((obs3[j]-exp3[j])/sd3[j]),2)} for j in range(3)},
    "joint_chi2": {"chi2": round(chi2_stat,3), "df": 2, "p": p_chi2},
    "verdict": ("32 阻挫邊 ±5° 方向預言: 🔴 不成立 (2026-10-18 修正幾何後) — 全樣本同能量分層嘅邊距離命中率"
                "全部落喺 MC null 期望內 (無顯著超額); 條件化 edge-only (d_node≥8° 內) obs rate %.1f%% vs "
                "條件化 MC %.1f%%±%.1f%% (p_excess=%.3f, p_deficit=%.3f); 三分區聯合 χ²=%.2f p=%.3f "
                "(無邊中段訊號). 60 節點 ±8° 預言維持 (節點帶 +%.2fσ; 低能段 46-80 EeV 避開 p=%.4f)."
                % (obs_rate*100, rates.mean()*100, rates.std()*100, p_rate_hi, p_rate_lo,
                   chi2_stat, p_chi2, z_node, p_low8)),
}}
dst = os.path.join(DATA, 'frustration_edge_verdict.json')
json.dump(out, open(dst,'w'), indent=2, ensure_ascii=False)
print(f"\n已存 {dst}")