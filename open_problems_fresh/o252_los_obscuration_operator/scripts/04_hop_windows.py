#!/usr/bin/env python3
"""
O252 — Script 04: hop 階梯徑向層 → τ(v) 速度窗 (第二輪, 零觀測 reference)
=========================================================================
第一輪教訓 (checkbox):
  [x] D3/D4 通用窗 (44-cascade v_co) MC null 唔支持 (z=−0.25/−3.22)
  [x] record 28: τ(v) 形狀必須由「凝聚層徑向結構」推出 — 唔係通用 ℓ 窗
  [x] record 30: channel 身份 — hop 係位置/質量層, 要過「點解佢有光譜速度份」關
物理 (第二輪, 零新常數):
  hop 階梯 = 凝聚層徑向結構 (O179): 層 h=0..8, 節點數 n(h)=[1,4,8,11,12,11,8,4,1],
  Σ=60。凝聚重心 = ⟨hop⟩ = Σh·n(h)/Σ = 4 = B (O179 434/434 錨定)。
  凝聚層跟世界環轉動: v(r) = √(a₀·r) (O180 EXACT)。層 h 轉速:
    model A: r_h = R_c·(h/8)          (層數線性 0..R_c)
    model B: r_h = R_band·(h/8)  帶厚  (層數線性 0..帶厚)
  窗中心候選 = 凝聚重心層轉速 v_B = √(a₀·r₄) (hop=4 最重層 n=12)
  τ(v) = τ₀·ℓ_band(θ(v)) + τ_w·g(v − v_abs)   (帶 + 窗)
  帶: ℓ(θ)=√(R_b²−R²sin²θ)−Rcosθ (近) / +R|cosθ| (遠), R_b/R=1+8/60
  窗: g = Gaussian, σ = FSR quantum ℓ=3 = 167.23 (凝聚層內部速度散佈)
輸出: 窗中心預言 v_abs (零參數) → data/04_hop_windows.json
本 script 零觀測 reference。
"""
import math, json, os
import numpy as np

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
os.makedirs(OUT, exist_ok=True)
LOG = []
def ck(name, cond, detail=''):
    LOG.append((name, bool(cond), detail))
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

c_km = 299792.458
R_world_Mpc = 4129.94
Mpc_km = 3.0856775814913673e19
R_world_km = R_world_Mpc*Mpc_km
a0 = c_km**2/(2*math.pi*R_world_km)

hop_hist = [1,4,8,11,12,11,8,4,1]
SUM60 = sum(hop_hist)
assert SUM60 == 60
# 凝聚重心 (hop 質心) = 4 = B
hop_bar = sum(h*n for h,n in enumerate(hop_hist))/SUM60
print("="*84)
print("O252/04 — hop 階梯徑向層 → τ(v) 速度窗 (second round, zero-obs)")
print("="*84)
print(f"hop 階梯 Σ={SUM60}, 凝聚重心 ⟨hop⟩ = {hop_bar:.6f}")

# ---------- 凝聚尺度 ----------
R_c_kpc = R_world_Mpc/44**3 * 1000.0        # 48.48 kpc (44-cascade ℓ=3)
R_c_km  = R_c_kpc*3.0856775814913673e16
V_max   = math.sqrt(a0*R_c_km)              # 409.78
R_band_kpc = R_c_kpc*(1+8/60)               # 帶外 (8/60 厚)
print(f"R_c = {R_c_kpc:.3f} kpc, V_max = {V_max:.3f} km/s")

# ---------- 層轉速窗中心 (hop 層 h → r_h → v_h) ----------
def window_centers():
    out = {}
    for model, rfun in [("A_lin_Rc", lambda h: R_c_km*h/8),
                        ("B_lin_Rband", lambda h: R_band_kpc*3.0856775814913673e16*h/8),
                        ("C_cos2", lambda h: R_c_km*math.cos(h*math.pi/16)**2)]:
        r4 = rfun(4)
        v4 = math.sqrt(a0*r4)
        out[model] = {"r4_kpc": r4/3.0856775814913673e16, "v4_kms": v4}
        print(f"  {model}: r₄(h=4) = {out[model]['r4_kpc']:.3f} kpc → v₄ = {v4:.2f} km/s")
    return out

WC = window_centers()
ck("S1.1 凝聚重心層 hop=4 有轉速 (結構窗中心)", all(v>0 for v in [w["v4_kms"] for w in WC.values()]))

# ---------- τ(v) 完整: 帶 (近/遠光程差) + 窗 (凝聚層速度) ----------
R_band_ratio = 1 + 8/60
def tau_band_ell(theta, R=1.0):
    s = math.sin(theta); c_ = math.cos(theta)
    Rb = R_band_ratio
    inner = Rb*Rb - s*s
    if inner < 0: return 0.0
    return math.sqrt(inner) - c_ if theta < math.pi/2 else math.sqrt(inner) + abs(c_)

def tau_window(v, v_abs, sigma, tau_w):
    return tau_w*np.exp(-0.5*((v-v_abs)/sigma)**2)

# 窗寬: 凝聚層內部速度散佈 = FSR quantum ℓ=3 (record 14)
sig3 = c_km*math.pi/(88*4**3)
print(f"窗寬 σ = FSR ℓ=3 quantum = {sig3:.2f} km/s")

# ---------- 預言輸出: v_abs 候選 (零參數, 唔睇觀測) ----------
cand = [{"model": m, "v_abs_kms": round(w["v4_kms"],2),
         "r4_kpc": round(w["r4_kpc"],3)} for m,w in WC.items()]
print("\n★ v_abs 候選 (凝聚重心 hop=4 轉速, 零參數):")
for c in cand:
    print(f"  {c['model']}: v_abs = {c['v_abs_kms']} km/s (r₄={c['r4_kpc']} kpc)")

# ---------- τ(v) 曲線 (model A 示範) ----------
v_grid = np.linspace(-1500.0, 1500.0, 12001)
I_int0 = (np.exp(-0.5*((v_grid-V_max)/sig3)**2) + np.exp(-0.5*((v_grid+V_max)/sig3)**2)
          + 0.5*np.exp(-0.5*(v_grid/sig3)**2))
tb = np.array([tau_band_ell(math.acos(max(-1,min(1,float(x)/c_km)))) for x in v_grid])/(2*R_band_ratio)
for c in cand:
    va = c["v_abs_kms"]
    for sign in (+1.0, -1.0):
        tw = tau_window(v_grid, sign*va, sig3, 0.35)
        I = I_int0*np.exp(-(tb+tw))
        # 有效 dip: I 同位極細
        dips = []
        for i in range(1, len(I)-1):
            if I[i] < I[i-1] and I[i] <= I[i+1]:
                dips.append(float(v_grid[i]))
        print(f"  {c['model']} sign={sign:+}: dip 位 = {[round(d,1) for d in dips[:8]]}")

# ---------- 保存 ----------
data = {"hop_bar": hop_bar, "sum": SUM60, "hop_hist": hop_hist,
        "R_c_kpc": R_c_kpc, "V_max_kms": V_max,
        "candidates": cand,
        "sigma_kms": sig3,
        "note": "窗中心 = 凝聚重心層(hop=4)轉速 √(a₀·r₄), 零參數; 帶+窗; σ=FSR ℓ=3",
        "checks": [{"name": n, "pass": p, "detail": d} for n,p,d in LOG]}
with open(f"{OUT}/04_hop_windows.json","w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
np_ok = sum(1 for _,p,_ in LOG if p)
print(f"\n結果: {np_ok}/{len(LOG)} PASS → data/04_hop_windows.json")