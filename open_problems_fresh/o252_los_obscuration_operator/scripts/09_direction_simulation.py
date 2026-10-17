#!/usr/bin/env python3
"""
O252 — Script 09 v2: 方向閉合模擬 (修正: Δχ² dip fit 檢出)
============================================================
v1 bug: resid.min() 受 10001 點 noise 極值污染 → 全部「兩側檢出」。
v2: 窗內 Gaussian dip fit (amplitude only, center/σ 固定結構值),
    Δχ² > 25 (≈5σ, 對應 ΔAIC>4 保守) 先算檢出。
模擬: 1000 源, sign 隨機 ±, noise 由 ΔAIC 觀測分佈 (9..372) 校準,
      τ(v) = τ₀·ℓ_band + τ_w·g(v∓v_abs, σ₃)  (script 04-06 結構值)
預言: q_blue(檢出側向) vs 觀測 10/13。
"""
import json, math, os
import numpy as np

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
LOG = []
def ck(name, cond, detail=''):
    LOG.append((name, bool(cond), detail))
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

C_KM = 299792.458
R_world_Mpc = 4129.94
Mpc_km = 3.0856775814913673e19
a0 = C_KM**2/(2*math.pi*R_world_Mpc*Mpc_km)
R_c_kpc = R_world_Mpc/44**3*1000.0
R_c_km = R_c_kpc*3.0856775814913673e16
V_max = math.sqrt(a0*R_c_km)
v_abs = V_max/math.sqrt(2.0)
sig3 = C_KM*math.pi/(88*4**3)
R_band_ratio = 1 + 8/60
tau_w = 4.0

def tau_band_ell(v):
    co = max(-1.0, min(1.0, v/C_KM))
    th = math.acos(co)
    s = math.sin(th); c = math.cos(th)
    Rb = R_band_ratio
    inner = Rb*Rb - s*s
    if inner < 0: return 0.0
    ell = math.sqrt(inner) - c if th < math.pi/2 else math.sqrt(inner) + abs(c)
    return ell/(2*R_band_ratio)

def I0(vg):
    return (np.exp(-0.5*((vg-V_max)/sig3)**2) + np.exp(-0.5*((vg+V_max)/sig3)**2)
            + 0.5*np.exp(-0.5*(vg/sig3)**2))

print("="*84)
print("O252/09v2 — 方向閉合模擬 (Δχ² dip fit)")
print("="*84)

# 校準 noise: 觀測 fit ΔAIC 9..372. ΔAIC ≈ Δχ² − 6 (M4 7 參數 vs M0 4).
# Δχ²_obs ∈ [15, 378]. 用 Δχ² = (dip_amp/σ_noise)²·(有效點數).
# 簡單: noise = amp/sqrt(Δχ²_eff), 用 dip amp = τ_w·I0(v_abs) 尺度.
rng = np.random.default_rng(20261017)
N_SIM = 500
blue, red, both, none = 0,0,0,0
vg = np.linspace(-1200, 1200, 601)
I = I0(vg)
tb = np.array([tau_band_ell(x) for x in vg])
# blue/red windows
w_b = (vg < 0) & (vg > -v_abs-2.5*sig3) & (vg < -v_abs+2.5*sig3)
w_r = (vg > 0) & (vg > v_abs-2.5*sig3) & (vg < v_abs+2.5*sig3)
wg = np.exp(-0.5*((vg-v_abs)/sig3)**2)      # window shape (red side)

def dchi(spec, w):
    """窗內 dip fit Δχ²: 對 window 內點 fit amp"""
    x = vg[w]; y = spec[w]; g = wg[w]
    n = len(x)
    if n < 10: return 0.0
    amp_num = np.sum(g*(y-I[w]))
    amp_den = np.sum(g*g)
    amp = amp_num/amp_den
    resid0 = y - I[w]
    resid1 = y - (I[w] + amp*g)
    chi0 = np.sum(resid0**2)/np.var(resid0) if np.var(resid0)>0 else 0
    chi1 = np.sum(resid1**2)/np.var(resid1) if np.var(resid1)>0 else 0
    return chi1 - chi0   # negative = better with dip

# noise 掃描: sigma_noise 由 ΔAIC 9..372 對應 — 用幾檔 noise 值
for noise in [0.05, 0.10, 0.18, 0.30, 0.55, 1.0]:
    b=r=bt=nn=0
    for _ in range(N_SIM):
        sign = +1 if rng.random()<0.5 else -1
        tw = tau_w*np.exp(-0.5*((vg-sign*v_abs)/sig3)**2)
        spec = I*np.exp(-(tb+tw)) + noise*rng.standard_normal(len(vg))
        db = dchi(spec, w_b); dr = dchi(spec, w_r)
        # sign 校正: dip 應該喺 sign 側更深 — 偵測兩側都很深 → both
        sb = db < -25; sr = dr < -25
        # 但 noise 令兩側 random dip — 用 sign side 深 2× 先算真
        if sb and sr:
            if db < dr*1.5: b+=1
            elif dr < db*1.5: r+=1
            else: bt+=1
        elif sb: b+=1
        elif sr: r+=1
        else: nn+=1
    tot = b+r+bt
    q = (b+bt)/tot if tot else float('nan')
    print(f"  noise={noise:5.2f}: 藍={b}, 紅={r}, 兩側={bt}, 冇={nn} → q_blue={q:.3f}")

# 用噪最似觀測嘅檔 (dip 檢出率 ~15/16=0.94): 揀 noise=0.30 做最終
for noise in [0.30]:
    b=r=bt=nn=0
    for _ in range(N_SIM*4):
        sign = +1 if rng.random()<0.5 else -1
        tw = tau_w*np.exp(-0.5*((vg-sign*v_abs)/sig3)**2)
        spec = I*np.exp(-(tb+tw)) + noise*rng.standard_normal(len(vg))
        db = dchi(spec, w_b); dr = dchi(spec, w_r)
        sb = (db < -25) and (db < dr*1.5)
        sr = (dr < -25) and (dr < db*1.5)
        if sb and sr: bt+=1
        elif sb: b+=1
        elif sr: r+=1
        else: nn+=1
    tot = b+r+bt
    q_blue = (b+bt)/tot if tot else float('nan')
    print(f"\n最終 noise={noise}: 藍={b}, 紅={r}, 兩側={bt}, 冇={nn} → q_blue={q_blue:.3f}")
    n_obs = 13; k_obs = 10
    p_ge = sum(math.comb(n_obs,k)*q_blue**k*(1-q_blue)**(n_obs-k) for k in range(k_obs, n_obs+1))
    ck("V5-obs 10/13 合模擬 q_blue 分佈", 0.1 < p_ge < 1.0,
       f"obs 10/13, q_blue={q_blue:.3f}, P(≥10/13)={p_ge:.4f}")
    ck("V5-bias q_blue>0.5", q_blue > 0.5, f"q_blue={q_blue:.3f}")

data = {"note": "Δχ² dip fit; noise 掃描; 最終 noise=0.30",
        "v_abs": v_abs, "sig3": sig3, "tau_w": tau_w,
        "checks": [{"name": n, "pass": p, "detail": d} for n,p,d in LOG]}
with open(f"{DATA}/09_direction_simulation.json","w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
np_ok = sum(1 for _,p,_ in LOG if p)
print(f"\n結果: {np_ok}/{len(LOG)} PASS → data/09_direction_simulation.json")