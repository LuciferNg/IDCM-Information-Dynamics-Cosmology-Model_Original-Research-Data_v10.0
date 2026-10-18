#!/usr/bin/env python3
"""
P12 攻堅 — 能量分層掃描嘅 look-elsewhere (LEE) 校正 (2026-10-18)
================================================================
docs/07 §六局限 (2) 標明: 4 能量層 × 2 窗 (8°/10°) 掃描未做 look-elsewhere 校正。
本 script 用 family-wise max-statistic null 校正:
  統計族 F = {節點帶命中數 (E 層 l, 窗 w)}  l ∈ 4 層, w ∈ {8,10}  → |F| = 8
  (節點側係唯一有偏離嘅方向; 邊側已判死, 另列)
做法: 每次 MC 迭代生成全部 109 事件嘅隨機 RA (keep dec) → 一次計晒 8 個統計 →
  逐迭代 z_lw = (obs_lw − mean_lw)/sd_lw → 取 max_lw z → null 分佈 → LEE 校正 p。
外加: 低能段 (46-80 EeV) 避開節點嘅 LEE 校正 p (單尾負方向, 取 max of −z)。
null: scramble RA keep dec; seed 42; N_MC=5000。
"""
import os, json, csv
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
P12  = os.path.dirname(HERE); MAIN = os.path.dirname(P12)
CMB  = os.path.join(MAIN, 'p4_cmb_cold_spot', 'data'); DATA = os.path.join(P12, 'data')

nodes = np.loadtxt(os.path.join(CMB, 'a5_nodes.txt'))
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

LAYERS = [("46-80", 46, 80), ("80-100", 80, 100), ("100-130", 100, 130), ("130+", 130, 1e9)]
WINDOWS = [8, 10]
lab = [(ln, w) for ln, _, _ in LAYERS for w in WINDOWS]

def family_counts(ra, dec):
    d = d_node(ra, dec); out = []
    for _, lo, hi in LAYERS:
        m = (ev_E >= lo) & (ev_E < hi)
        out += [int((d[m] < w).sum()) for w in WINDOWS]
    return out

obs = family_counts(ev_ra, ev_dec)
obs_arr = np.array(obs, dtype=float)

N_MC = 5000
rng = np.random.default_rng(42)
mc = np.zeros((N_MC, len(lab)), dtype=float)
for i in range(N_MC):
    mc[i] = family_counts(rng.uniform(0, 360, N), ev_dec)
mean = mc.mean(axis=0); sd = mc.std(axis=0)
z_obs = (obs_arr - mean) / np.maximum(sd, 1e-9)

# 逐迭代 z (用同一組 mean/sd) → family-wise max
z_mc = (mc - mean) / np.maximum(sd, 1e-9)
max_z_null = z_mc.max(axis=1)
max_z_obs = float(z_obs.max())
k = int(np.argmax(z_obs))
p_lee = float((max_z_null >= max_z_obs).mean())
p_naive = float((z_mc[:, k] >= max_z_obs).mean())

print("=== 族 F = 節點帶命中 (4 能量層 × 2 窗, |F|=8) ===")
for j, (ln, w) in enumerate(lab):
    print(f"  E {ln:>7} EeV  <{w:>2}°: obs={int(obs_arr[j]):>3}  MC={mean[j]:>5.1f}±{sd[j]:<4.1f}  z={z_obs[j]:+.2f}")
print(f"\n最強點: E {lab[k][0]} <{lab[k][1]}°  z_obs = {max_z_obs:+.3f}")
print(f"naive p (單一檢驗)      = {p_naive:.4f}")
print(f"LEE 校正 p (family-max) = {p_lee:.4f}   [max_z null mean {max_z_null.mean():.2f}, sd {max_z_null.std():.2f}]")

# 低能段避開 (單尾負): 46-80 EeV, 窗 8/10
low_idx = [j for j, (ln, w) in enumerate(lab) if ln == "46-80"]
neg = -z_obs[low_idx]
neg_mc = -z_mc[:, low_idx]
max_neg_obs = float(neg.max()); kk = int(np.argmax(neg))
p_low_naive = float((neg_mc[:, kk] >= max_neg_obs).mean())
p_low_lee = float((neg_mc.max(axis=1) >= max_neg_obs).mean())
print(f"\n=== 低能段 46-80 EeV 避開 (單尾負方向, |F|=2) ===")
for jj, j in enumerate(low_idx):
    print(f"  <{lab[j][1]}°: obs={int(obs_arr[j])}/{int(sum((ev_E>=46)&(ev_E<80)))}  MC={mean[j]:>4.1f}±{sd[j]:<4.1f}  z={z_obs[j]:+.2f}")
print(f"最強 (避開方向): <{lab[low_idx[kk]][1]}°  −z = {max_neg_obs:+.3f}")
print(f"naive p  = {p_low_naive:.4f}")
print(f"LEE 校正 p = {p_low_lee:.4f}")

out = {"p12_lee_correction_20261018": {
    "N": N, "N_MC": N_MC, "seed": 42, "null": "scramble RA keep dec",
    "family_node": [{"layer": lab[j][0], "window_deg": lab[j][1],
                     "obs": int(obs_arr[j]), "mc_mean": round(float(mean[j]),1),
                     "mc_sd": round(float(sd[j]),1), "z": round(float(z_obs[j]),3)} for j in range(len(lab))],
    "node_strongest": {"layer": lab[k][0], "window_deg": lab[k][1], "z_obs": round(max_z_obs,3),
                       "p_naive": p_naive, "p_lee_family_max": p_lee},
    "low_energy_avoid": {"window_deg": lab[low_idx[kk]][1], "neg_z_obs": round(max_neg_obs,3),
                         "p_naive": p_low_naive, "p_lee_family_max": p_low_lee},
    "note": "LEE p 係族內最強統計量嘅 family-wise 校正; 族 = 節點側 4 層×2 窗 (邊側已否證, 唔入族)",
}}
dst = os.path.join(DATA, 'lee_correction.json')
json.dump(out, open(dst, 'w'), indent=2, ensure_ascii=False)
print(f"\n已存 {dst}")