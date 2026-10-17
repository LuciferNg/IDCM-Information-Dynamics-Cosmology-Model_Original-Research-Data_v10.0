#!/usr/bin/env python3
"""
O252 — Script 01 v2: τ(v) 第一性原理候選族 (幾何 → 視線光深)
===========================================================
預註冊 (跑前凍結):
  I_obs(v) = I_int(v)·e^(−τ(v));  I_int 固有對稱 (γ_k=γ_{176−k} 代數必然);
  散射保對稱 ⟹ 唔對稱必來自遮蔽幾何 channel。
  ⚠️ 本 script 零觀測 reference — 只由世界環幾何+已閉合譜量構造 τ(v)。
  v1 修正: (a) 模態對 partner = k ↔ 176−k (θ→π−θ), 唔係 array mirror
           (b) 環帶厚度由 hop 結構定 (R_band/R = 1+2/15), 近分支光程非零
           (c) 加入 44-cascade 凝聚尺標 (ℓ_co=0..3) + FSR quantum 窗候選

候選族 (零新常數):
  T-a 近/遠分支光程差:   τ(θ) ∝ 視線穿越世界環帶光程 ℓ(θ)
       近分支 (θ<π/2): ℓ = √(R_b²−R²sin²θ) − R cosθ
       遠分支 (θ>π/2): ℓ = √(R_b²−R²sin²θ) + R|cosθ|
       R_b/R = 1+2/15 (hop 直徑 8/Σ60 結構錨)
  T-e 凝聚速度窗: τ(v) = τ₀·g(v−v_co), v_co = 凝聚層世界環速度
       v_co(ℓ) = √(a₀·R_ℓ), R_ℓ = R_world/44^ℓ (44-cascade 凝聚尺標)
  T-f a₀-locus 速度窗寬度: σ_co(ℓ) = c·π/N_ℓ = c·π/(88·4^ℓ) (FSR 階梯間距)
  T-g hop 層光深權重: τ_column = Σ_h n(h)·ℓ_h(θ,帶厚) (每 hop 層弦長)

判定準則:
  [G1] τ(±v) 唔對稱
  [G2] e^{−τ} 產生單側 dip
  [G3] dip 位置 (τ 峰) 由結構參數決定 (唔睇觀測)
  [G4] 零新常數
"""
import math, json, os
import numpy as np

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
os.makedirs(OUT, exist_ok=True)
LOG = []

def ck(name, cond, detail=''):
    LOG.append((name, bool(cond), detail))
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

# ---------- 已閉合譜量 ----------
c_km = 299792.458
R_world_Mpc = 4129.94
Mpc_km = 3.0856775814913673e19
R_world_km = R_world_Mpc * Mpc_km
a0 = c_km**2 / (2*math.pi*R_world_km)          # km/s², O180
B, L5, C = 4, 11, 4/11
hop_hist = [1,4,8,11,12,11,8,4,1]

print("="*74)
print("O252/01v2 — τ(v) first-principles candidates (zero-obs prereg)")
print("="*74)
print(f"a0 = {a0:.6e} km/s²  R_world = {R_world_Mpc} Mpc")

# 模態對: 全 θ ∈ [0,π] 用 k=1..176, pair (k, 176−k)。
# v_k = c·cos(kπ/176), γ_k = 4sin²(kπ/88) (record 27 正典: γ_k=4sin²(kπ/88), k=1..87)
Kmax = 176
v_full = [c_km*math.cos(k*math.pi/176) for k in range(1, Kmax)]
g_full = [4*math.sin(k*math.pi/88)**2 for k in range(1, Kmax)]   # 88-periodic
thetas = [k*math.pi/176 for k in range(1, 176)]
# G0: partner 對稱
sym_ok = all(abs(g_full[k-1] - g_full[176-k-1]) < 1e-12 for k in range(1,88))
vp_ok  = all(abs(v_full[k-1] + v_full[176-k-1]) < 1e-6 for k in range(1,88))
ck("G0.1 固有 γ 對稱 γ_k=γ_{176−k}", sym_ok)
ck("G0.2 速度反號 v_k=−v_{176−k}", vp_ok,
   f"max|Σv|={max(abs(v_full[k-1]+v_full[176-k-1]) for k in range(1,88)):.2e}")

# 44-cascade: ℓ=0..3 凝聚尺標
casc = []
for l in range(0,5):
    R_l = R_world_Mpc / (44**l)
    v_l = c_km/(math.sqrt(2*math.pi*44**l))     # v(R_ℓ) = c/√(2π)·44^{−ℓ/2}
    casc.append((l, R_l*1000.0, v_l))
    print(f"  cascade ℓ={l}: R = {R_l*1000:.3f} kpc, v = {v_l:.2f} km/s")

# ============================================================
# T-a 近/遠分支光程差 (世界環帶)
# ============================================================
R_band_ratio = 1 + 8/60     # 帶外半徑 = R + hop直徑/Σ = 1+2/15

def tau_a(theta, R=1.0, Rb_ratio=R_band_ratio):
    s = R*math.sin(theta); c_ = R*math.cos(theta)
    Rb = Rb_ratio*R
    inner = Rb*Rb - s*s
    if inner < 0: return 0.0
    return math.sqrt(inner) - c_

# 模態對: k ↔ 176−k, θ → π−θ
diffs = []
for k in range(1, 88):
    t1 = k*math.pi/176
    t2 = math.pi - t1
    d = abs(tau_a(t2) - tau_a(t1))
    diffs.append(d)
ck("T-a.1 模態對 τ 唔對稱 (帶厚>0)", max(diffs) > 1e-6, f"max Δℓ = {max(diffs):.6f} R")
# 遠分支 (θ>π/2, v<0) τ 大
ck("T-a.2 遠分支 (v<0) τ 大", tau_a(math.pi - math.pi/176) > tau_a(math.pi/176))

def tau_a_v(v):
    theta = math.acos(max(-1, min(1, v/c_km)))
    return tau_a(theta)

# 峰位置 (v>0 側都可能有? 近分支 ℓ 對 v 單調?)
vs = np.linspace(-c_km*0.9999, c_km*0.9999, 400001)
taus = np.array([tau_a_v(float(v)) for v in vs])
# local max (排除數值 noise ~1e-16)
peaks = []
for i in range(1, len(vs)-1):
    if taus[i] > taus[i-1] and taus[i] > taus[i+1] and taus[i] > 1e-9:
        peaks.append((float(vs[i]), float(taus[i])))
ck("T-a.3 τ 有局部峰 (dip 位置候選)", len(peaks) >= 2, f"n_peaks={len(peaks)}")
print("    τ_a 峰 (v,τ):", [(round(v,1), round(t,5)) for v,t in peaks[:10]])

# ============================================================
# T-e 凝聚速度窗: τ(v) = τ₀·g(v−v_co), v_co(ℓ)=√(a₀R_ℓ)
# ============================================================
def tau_window(v, v_co, sigma):
    return math.exp(-0.5*((v-v_co)/sigma)**2)

# 零常數候選: 每 ℓ 凝聚尺標一個 window center σ=FSR quantum
print("\nT-e 凝聚速度窗候選 (ℓ, v_co km/s, σ=FSR quantum km/s):")
for l in range(0,4):
    R_l_kpc = casc[l][1]
    R_l_km = R_l_kpc*3.0856775814913673e16   # kpc→km (1 kpc = 3.0857e16 km)
    v_co = math.sqrt(a0*R_l_km)
    N_l = 88*4**l
    sigma = c_km*math.pi/N_l
    print(f"  ℓ={l}: R={R_l_kpc:.3f} kpc, v_co={v_co:.2f} km/s, σ={sigma:.2f} km/s")

# ============================================================
# T-f a₀-locus 凝聚帶速度窗: 凝聚帶 r∈[r_in,r_out] 速度分佈投影
# ============================================================
# 凝聚帶 (hop 0..8 => 9 層) 包住 R_c (ℓ=3), 帶厚 δ = R_c·(hop直徑/Σ)=R_c·2/15
# v(r) = √(a₀r), 帶內速度 v ∈ [v_in, v_out]; 吸收窗 = 帶速度分佈
R3_kpc = casc[3][1]
R3_km = R3_kpc*3.0856775814913673e16
v3_in  = math.sqrt(a0*(R3_km*(1-8/60)))
v3_out = math.sqrt(a0*(R3_km*(1+8/60)))
print(f"\nT-f ℓ=3 凝聚帶: v∈[{v3_in:.2f}, {v3_out:.2f}] km/s, δv={v3_out-v3_in:.2f} km/s")
ck("T-f.1 凝聚帶速度窗非退化", v3_out > v3_in, f"δv={v3_out-v3_in:.2f} km/s")

# ============================================================
# T-g hop 層光深權重 (每 hop 層弦長, 沿視線)
# ============================================================
# 凝聚層 h: 半徑 r_h = R_c·(1 + (h−4)·Δ), Δ = 帶厚/8 每層; 層密度 n(h)
# 視線衝擊參數 b = R·|sinθ| (世界環帶模型) — 層 h 光程 = 2√(r_h²−b²) if b<r_h
def tau_g(theta, R=1.0, Rco=R3_km):
    # 層半徑 (相對 R): h=0..8 → 帶內 r_h = R·(1 + (h−4)·(2/15)/4)? 用帶內 9 層
    n_layers = len(hop_hist)
    b = R*abs(math.sin(theta))
    tot = 0.0
    for h, n_h in enumerate(hop_hist):
        r_h = R*(1 - 8/60) + R*(2*8/60)*(h/(n_layers-1))
        if b < r_h:
            tot += n_h * 2*math.sqrt(r_h*r_h - b*b)
    return tot

# 近/遠分支 (θ vs π−θ) 嘅 T-g 差:
d_g = abs(tau_g(math.pi - math.pi/176) - tau_g(math.pi/176))
ck("T-g.1 T-g 模態對唔對稱", d_g > 1e-9, f"Δτ_g = {d_g:.6f}")

# ============================================================
# T-h hop 完整梯 × 近/遠光程複合 (O252 核心候選)
# ============================================================
def tau_h(theta, R=1.0, Rco_ratio=R_band_ratio):
    """hop 完整梯光深: 帶幾何光程 × 凝聚層 hop 節點權重"""
    s = R*math.sin(theta); c_ = R*math.cos(theta)
    Rb = Rco_ratio*R
    inner = Rb*Rb - s*s
    if inner < 0: return 0.0
    ell = math.sqrt(inner) - c_
    w = 0.0
    for h, n_h in enumerate(hop_hist):
        r_h = Rco_ratio*R*(0.5 + 0.5*h/8.0)
        if r_h >= abs(s):
            w += n_h * (math.sqrt(max(r_h*r_h - s*s,0.0)) if r_h > abs(s) else 1.0)
    return ell*w

th1 = tau_h(thetas[1]); th2 = tau_h(math.pi - thetas[1])
ck("T-h.1 模態對唔對稱 (hop×光程複合)", abs(th1 - th2) > 1e-9,
   f"近={th1:.6f} 遠={th2:.6f} Δ={abs(th1-th2):.6f}")
vs_h = np.linspace(-c_km*0.9999, c_km*0.9999, 200001)
taus_h = np.array([tau_h(math.acos(max(-1,min(1,float(v)/c_km)))) for v in vs_h])
peaks_h = []
for i in range(1, len(vs_h)-1):
    if taus_h[i] > taus_h[i-1] and taus_h[i] > taus_h[i+1] and taus_h[i] > 1e-9:
        peaks_h.append((float(vs_h[i]), float(taus_h[i])))
ck("T-h.2 τ_h 有局部峰 (dip 位置候選)", len(peaks_h) >= 2, f"n_peaks={len(peaks_h)}")
print("    τ_h 峰 (v,τ):", [(round(v,1), round(t,4)) for v,t in peaks_h[:12]])

# ============================================================
# ★ 結構預言輸出 (零觀測 reference)
# ============================================================
sigma_candidates = {f"ell{l}": c_km*math.pi/(88*4**l) for l in range(0,5)}
vco_candidates   = {}
for l in range(0,4):
    R_l_km = casc[l][1]*3.0856775814913673e16/1000.
    vco_candidates[f"ell{l}"] = math.sqrt(a0*R_l_km)

data = {
  "constants": {"c_km": c_km, "R_world_Mpc": R_world_Mpc, "a0_km_s2": a0,
                "B": B, "L5": L5, "C": C, "hop_hist": hop_hist,
                "R_band_ratio": R_band_ratio},
  "cascade": [{"ell": l, "R_kpc": round(r,4), "v_kms": round(v,3)} for l,r,v in casc],
  "T_a": {"R_band_ratio": R_band_ratio,
          "max_pair_dl": round(max(diffs),6)},
  "T_e": {"v_co_kms": {k: round(v,3) for k,v in vco_candidates.items()},
          "sigma_fsr_kms": {k: round(v,3) for k,v in sigma_candidates.items()}},
  "T_f": {"R3_kpc": round(R3_kpc,3), "v_in_kms": round(v3_in,3),
          "v_out_kms": round(v3_out,3), "dv_kms": round(v3_out-v3_in,3)},
  "T_g": {"note": "hop 層弦長沿視線", "d_pair": round(d_g,8)},
  "checks": [{"name": n, "pass": p, "detail": d} for n,p,d in LOG],
}
with open(f"{OUT}/01_tau_candidates.json","w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

np_ok = sum(1 for _,p,_ in LOG if p)
print("\n" + "="*74)
print(f"結果: {np_ok}/{len(LOG)} PASS")
print("="*74)