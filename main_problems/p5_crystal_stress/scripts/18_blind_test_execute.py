#!/usr/bin/env python3
"""
執行 — 路線 3: 盲測 (AugerPrime 預註冊協議) + 功效表修正 (2026-10-17)
========================================================================
預註冊協議: augerprime_blind_prediction.json (2026-08-16)
  P0: median d_node < 9.6° (E>150 EeV)
  P1: >50% within 8°  (MC null 31.4%)
  P2: >50% within 10° (MC null 47.6%)
  null: MC scramble RA, keep dec field (conservative); seed 42
  否證: median > 12° OR <30% within 8° (N>=20)

功效表修正: 舊文檔「20→3.1σ, 50→5.2σ」不自洽 (z(50)/z(20)=1.677≠√2.5)
  → 重算: 雙比例 3.07σ/4.86σ; 單比例 4.20σ/6.64σ; N_for_5σ(雙)≈53, N_for_5σ(單)≈29
"""
import os, json, math
import numpy as np
from scipy.stats import binom

HERE = os.path.dirname(os.path.abspath(__file__))
CS   = os.path.dirname(HERE)
SIB  = os.path.dirname(CS)
UHE  = os.path.join(SIB, 'p12_uhecrs', 'data')
DATA = os.path.join(CS, 'data')
NODES = os.path.join(SIB, 'p4_cmb_cold_spot', 'data', 'a5_nodes.txt')

def unit(ra_deg, dec_deg):
    ra, dec = np.radians(ra_deg), np.radians(dec_deg)
    return np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])

# ---------- 節點 + 事件 ----------
nodes = np.loadtxt(NODES)                      # 60 x [RA, Dec]
node_vec = unit(nodes[:,0], nodes[:,1])

rows = [l.strip().split(',') for l in open(os.path.join(UHE,'auger_catalogSD.csv'))][1:]
ev = [(r[0], float(r[2]), float(r[6]), float(r[7])) for r in rows if float(r[2]) > 150]  # E>150 EeV
print(f"E>150 EeV 事件: N={len(ev)}")
for eid,e,ra,dec in ev:
    print(f"  {eid}  E={e:.0f} EeV  ra={ra:.1f} dec={dec:.1f}")

def d_node(ra, dec):
    c = np.clip(unit([ra],[dec]) @ node_vec.T, -1, 1)
    return float(np.degrees(np.arccos(c.max())))

ds = [d_node(ra,dec) for _,_,ra,dec in ev]
med = float(np.median(ds))
k8  = sum(1 for d in ds if d < 8)
k10 = sum(1 for d in ds if d < 10)
print(f"\n最細節點角距: {[f'{d:.2f}°' for d in ds]}")
print(f"中位數 d_node = {med:.2f}°   (P0 預報: < 9.6° ⇒ {'✅ 命中' if med<9.6 else '❌ 未中'})")
print(f"8° 內命中 {k8}/{len(ev)}  (需 >50% 先過 P1; 滿充 MC null 31.4%)")
print(f"10° 內命中 {k10}/{len(ev)}  (需 >50% 先過 P2; MC null 47.6%)")

# ---------- 精確二項檢定 ----------
p1 = float(binom.sf(k8-1, len(ev), 0.314))   # P(>=k8 | 4, 0.314)
p2 = float(binom.sf(k10-1, len(ev), 0.476))
from scipy.stats import norm as _norm
print(f"\n二項檢定: P1(8°, p0=0.314) P(≥{k8}) = {p1:.5f} ({(p1<0.05) and '✅' or '❌'})")
print(f"          P2(10°, p0=0.476) P(≥{k10}) = {p2:.5f} ({(p2<0.05) and '✅' or '❌'})")

# ---------- MC null (scramble RA keep dec; seed 42) ----------
rng = np.random.default_rng(42)
N_MC = 100_000
m_med = np.empty(N_MC); m_k8 = np.empty(N_MC); m_k10 = np.empty(N_MC)
decs = np.array([d for _,_,_,d in ev])
for i in range(N_MC):
    ras = rng.uniform(0, 360, len(ev))
    c = np.clip(unit(ras, decs) @ node_vec.T, -1, 1).max(axis=1)
    m_med[i] = np.median(np.degrees(np.arccos(c)))
    m_k8[i]  = (np.degrees(np.arccos(c)) < 8).sum()
    m_k10[i] = (np.degrees(np.arccos(c)) < 10).sum()
p_med = float((m_med <= med).mean())
p_mc8 = float((m_k8 >= k8).mean())
p_mc10= float((m_k10 >= k10).mean())
print(f"\nMC null (scramble RA, keep dec, N_MC={N_MC}): ")
print(f"  P(median ≤ {med:.2f}°) = {p_med:.5f}")
print(f"  P(k8 ≥ {k8}) = {p_mc8:.5f}")
print(f"  P(k10 ≥ {k10}) = {p_mc10:.5f}")

# ---------- 功效表修正 ----------
p0 = 0.314; rate = 0.75
def z_two(N):  return (rate-p0)/math.sqrt(rate*(1-rate)/N + p0*(1-p0)/N)
def z_single(N): return (rate-p0)/math.sqrt(p0*(1-p0)/N)
z20t, z50t = z_two(20), z_two(50)
z20s, z50s = z_single(20), z_single(50)
def N_for(z_target, f):
    lo, hi = 1, 10_000
    while lo < hi:
        mid = (lo+hi)//2
        if f(mid) >= z_target: hi = mid
        else: lo = mid+1
    return lo
n5t = N_for(5, z_two); n5s = N_for(5, z_single)
print(f"\n功效表修正 (p0=0.314, rate=0.75):")
print(f"  舊文檔: N=20→3.1σ, N=50→5.2σ  [z 比 1.677 ≠ √2.5=1.5811 ⇒ 不自洽]")
print(f"  雙比例: N=20→{z20t:.2f}σ, N=50→{z50t:.2f}σ;  N_for_5σ = {n5t}")
print(f"  單比例: N=20→{z20s:.2f}σ, N=50→{z50s:.2f}σ;  N_for_5σ = {n5s}")
print(f"  AugerPrime ~10 事件/年 >150 EeV: 雙比例 5σ ≈ {n5t/10:.1f} 年; 單比例 5σ ≈ {n5s/10:.1f} 年")

# ---------- 判決 ----------
verdicts = {
    "P0_median_lt_9p6": bool(med < 9.6),
    "P1_gt50pct_8deg": bool(k8/len(ev) > 0.5),
    "P2_gt50pct_10deg": bool(k10/len(ev) > 0.5),
}
gate_N = len(ev) >= 20
falsified = gate_N and (med > 12 or k8/len(ev) < 0.3)
print(f"\n預註冊協議判決: N={len(ev)} (<20 ⇒ 否證條件唔適用, 維持預註冊, 等 AugerPrime)")
print(f"  P0={verdicts['P0_median_lt_9p6']} P1={verdicts['P1_gt50pct_8deg']} P2={verdicts['P2_gt50pct_10deg']}")
print(f"  否證門檻 (N≥20): {'已觸發 ❌' if falsified else '未觸發 (等數據 N≥20)'}")

out = {
    "route3_blind_test_20261017": {
        "sample": [{"id":i,"E_EeV":e,"ra":ra,"dec":dec,"d_node_deg":d} for (i,e,ra,dec),d in zip(ev,ds)],
        "N": len(ev), "median_d_node": med, "k8": k8, "k10": k10,
        "binom_p1": p1, "binom_p2": p2,
        "mc_null_median_p": p_med, "mc_null_k8_p": p_mc8, "mc_null_k10_p": p_mc10,
        "verdicts": verdicts, "falsification_gate": gate_N and not falsified, "note": "N<20, 否證條件未適用, 等 AugerPrime"
    },
    "power_table_corrected": {
        "old": {"N20": "3.1σ", "N50": "5.2σ", "ratio": 5.2/3.1, "self_consistent_ratio": math.sqrt(50/20)},
        "two_proportion": {"z20": round(z20t,2), "z50": round(z50t,2), "N_for_5sigma": n5t},
        "single_proportion": {"z20": round(z20s,2), "z50": round(z50s,2), "N_for_5sigma": n5s},
        "augerprime_10per_yr_years_5sigma_two": n5t/10
    },
}
with open(os.path.join(DATA,'reverify_blind_test.json'),'w') as f:
    json.dump(out, f, indent=2)
print(f"\n已存 {os.path.join(DATA,'reverify_blind_test.json')}")