#!/usr/bin/env python3
"""
O252 — Script 02 v2: 完整前向模型 I_obs(v) = I_int·e^(−τ) (零觀測 reference)
============================================================================
預註冊 (跑前凍結):
  v1 修正: I_int 用 FSR ℓ=3 細化模態對 (record 14: Δv = n·cπ/N_ℓ, N_3=5632,
           V_max = 409.78, 2V_max = 819.56) — 唔係裸 88-chain (±c)。

  模型: I_obs(v) = I_int(v)·e^(−τ(v))
        I_int(v) = 對稱雙峰 (±v_pair, 本徵寬 σ_int) + 中心模態 (v=0)
        τ(v)     = τ_band(v) + τ_window(v)
  結構身份:
    τ_band: 視線穿越世界環帶光程 (近/遠分支)
        ℓ(θ) = √(R_b²−R²sin²θ) − R cosθ  (θ<π/2, 近: 短)
        ℓ(θ) = √(R_b²−R²sin²θ) + R|cosθ| (θ>π/2, 遠: 長)
        R_b/R = 1+2/15 (hop 直徑 8/Σ60)
        ⟹ v<0 (藍側) τ 大 → 藍弱 (record 21 一致)
    τ_window: 凝聚層速度窗 (dip)
        窗中心 v_co(ℓ) = ±√(a₀·R_ℓ),  R_ℓ = R_world/44^ℓ   (44-cascade)
        窗寬 σ_ℓ = c·π/(88·4^ℓ)     (FSR quantum, record 14)
        sign: 近分支凝聚 → +; 遠分支凝聚 → − (由源幾何定, 容許 Hα/Hβ 反 sign)
  盲測預言:
    dip 位置 |v_dip| ∈ {v_co(ℓ)} ∪ {n·σ_3}  (ℓ=0..4, n=1..6)
    dip 深度 = 1−e^{−τ_w} (τ_w 深度尺度待 W 權重閉合 → 輸出相對值)
  本 script 零觀測 reference。 輸出 data/02_forward_model.json
"""
import math, json, os
import numpy as np

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
os.makedirs(OUT, exist_ok=True)
LOG = []
def ck(name, cond, detail=''):
    LOG.append((name, bool(cond), detail))
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

# ---------- 已閉合譜量 (record 14 / O180 / O140) ----------
c_km = 299792.458
R_world_Mpc = 4129.94
Mpc_km = 3.0856775814913673e19
R_world_km = R_world_Mpc * Mpc_km
a0 = c_km**2 / (2*math.pi*R_world_km)          # km/s²
B, L5, C = 4, 11, 4/11
hop_hist = [1,4,8,11,12,11,8,4,1]
R_band_ratio = 1 + 8/60
N3 = 88*4**3
sig3 = c_km*math.pi/N3                          # FSR ℓ=3 quantum 167.23
Vmax = math.sqrt(a0*R_world_km/44**3)           # 409.78
print("="*78)
print("O252/02v2 — forward model I_int(FSR ℓ=3) × e^(−τ)  (zero-obs prereg)")
print("="*78)
print(f"σ_3 (FSR ℓ=3) = {sig3:.3f} km/s   V_max = {Vmax:.3f} km/s   2V_max = {2*Vmax:.3f} km/s")

# ---------- 固有譜 I_int: FSR ℓ=3 對稱雙峰 + 中心模態 ----------
# 晶格模態對: ±V_max (凝聚區邊界) 或 ±V_max/2 (R_d 尺標) 或多 rung n·σ_3
def I_int(v, v_pair, s_int):
    """對稱: 峰 @ ±v_pair + 中心峰 @ 0 (中心模態 γ=2)"""
    out = np.exp(-0.5*((v-v_pair)/s_int)**2)/np.sqrt(2*math.pi)
    out += np.exp(-0.5*((v+v_pair)/s_int)**2)/np.sqrt(2*math.pi)
    out += 0.5*np.exp(-0.5*(v/s_int)**2)/np.sqrt(2*math.pi)   # 中心模態權重 ½
    return out

# ---------- τ_band: 帶光程 (近/遠分支) ----------
def tau_band(v, R=1.0, Rb_ratio=R_band_ratio, scale=1.0):
    out = np.zeros_like(v)
    for i, vv in enumerate(v):
        co = max(-1.0, min(1.0, float(vv)/c_km))
        th = math.acos(co)
        s = math.sin(th); c_ = math.cos(th)
        Rb = Rb_ratio*R
        inner = Rb*Rb - s*s
        ell = math.sqrt(inner) if inner > 0 else 0.0
        ell = ell - c_ if th < math.pi/2 else ell + abs(c_)
        out[i] = scale*ell
    return out

# ---------- τ_window: 凝聚層速度窗 (dip) ----------
WIN_ELL = {}
for l in range(0,5):
    R_l_km = R_world_km/44**l
    v_co = math.sqrt(a0*R_l_km)
    sig_l = c_km*math.pi/(88*4**l)
    WIN_ELL[l] = (v_co, sig_l)

def tau_window(v, l=3, sign=+1.0, tau_w=0.3, center_ratio=1.0):
    v_co, sig = WIN_ELL[l]
    vc = sign*v_co*center_ratio
    return tau_w*np.exp(-0.5*((v-vc)/sig)**2)

# ---------- 組合: I_obs = I_int·e^{−τ} ----------
v_grid = np.linspace(-1500.0, 1500.0, 30001)
# 基線: v_pair = V_max (凝聚區 σ3 量子 rung n=2.45?) — 用純結構: v_pair = 2V_max/2 = V_max
# 雙峰間距 Δv = 2V_max = 819.56 (邊緣) 或 Δv = 409.78 (R_d) — 掃兩者
RESULTS = []
for tag, v_pair in [("edge", Vmax), ("Rd", Vmax/2)]:
    I0 = I_int(v_grid, v_pair, s_int=sig3)
    tb = tau_band(v_grid)/ (2*R_band_ratio)      # 歸一: 最大帶程 2R_b
    # 窗掃: sign ±, 中心 ℓ=3
    for sign in [+1.0, -1.0]:
        tw = tau_window(v_grid, l=3, sign=sign, tau_w=0.35)
        tau = tb + tw
        I_obs = I0*np.exp(-tau)
        # 揾 dip (局部極細) 喺 ±1500 內
        dips = []
        for i in range(1, len(I_obs)-1):
            if I_obs[i] < I_obs[i-1] and I_obs[i] <= I_obs[i+1]:
                dips.append((float(v_grid[i]), float(I_obs[i])))
        # 峰 (局部極大)
        peaks = []
        for i in range(1, len(I_obs)-1):
            if I_obs[i] > I_obs[i-1] and I_obs[i] >= I_obs[i+1]:
                peaks.append((float(v_grid[i]), float(I_obs[i])))
        RESULTS.append({"tag": tag, "sign": sign, "dips": dips[:6], "peaks": peaks[:6]})
        print(f"\n[{tag} sign={sign}] I_obs dip 位置: {[(round(v,1),round(i,4)) for v,i in dips[:6]]}")
        print(f"                  峰值:   {[(round(v,1),round(i,4)) for v,i in peaks[:6]]}")

# ---------- 盲測預言 ----------
D3 = [WIN_ELL[l][0] for l in range(4)]          # 窗中心 |v| (ℓ=0..3)
D4 = [n*sig3 for n in range(1,7)]               # FSR ℓ=3 rung 量子
# ℓ=3 窗 ±V_max 側 dip 位置 (由 I_obs 實算, 上面 OUTPUT)
pred = {
  "window_centers_pos_kms": [round(v,1) for v in D3],
  "fsr_l3_rungs_kms": [round(v,1) for v in D4],
  "band_direction": "v<0 藍側 τ 大 → 藍弱 (record 21 一致)",
  "dip_rule": "|v_dip| ∈ {v_co(ℓ)} ∪ {n·σ_3}; sign 由源近/遠分支定 (±)",
  "note": "盲測: scripts/03 之前禁 reference 觀測 dip"
}
print("\n★ 盲測預言:")
print("  窗中心 |v|:", [round(v,1) for v in D3])
print("  FSR ℓ=3 n·167.23:", [round(v,1) for v in D4])

# ---------- 保存 ----------
data = {"pred": pred, "sim": RESULTS,
        "checks": [{"name": n, "pass": p, "detail": d} for n,p,d in LOG]}
with open(f"{OUT}/02_forward_model.json","w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print(f"\n保存 → {OUT}/02_forward_model.json")