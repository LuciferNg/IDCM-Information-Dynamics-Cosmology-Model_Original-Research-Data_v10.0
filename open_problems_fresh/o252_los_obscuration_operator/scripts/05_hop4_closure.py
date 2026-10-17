#!/usr/bin/env python3
"""
O252 — Script 05: hop=4 凝聚窗精準閉合 (含後驗標記 + MC null)
============================================================
結構預言 (script 04, 零參數):
  v_abs = V_max/√2 = √(a₀·R_c/2) = 289.76 km/s
  推導鏈: ⟨hop⟩ = 4.000000 = B (O179 434/434 錨定)
          hop=4 → O180 cos² 映射 → r₄ ∝ cos²(kπ/176)|重層 = R_c/2
          凝聚層轉速 v(r) = √(a₀·r) (O180 EXACT) → v₄ = V_max/√2
  窗寬 σ = FSR ℓ=3 quantum = cπ/5632 = 167.23 km/s (record 14)
後驗標記 (honest):
  script 04 嘅「凝聚層半徑映射 (A/B/C)」喺見到 A dip 之後收窄去 hop=4 —
  故 v₄ 數值係零參數 (由已閉合譜量出), 但「用 hop=4 而唔係其他層」係後驗。
  閉合判定以 MC null + 樣本外 (E) 為準, 唔可以單靠 A 單點。
判定:
  [F1] |v_obs(A Hα) − v_abs| / σ_dip(obs) < 1   (命中緊度, σ=183)
  [F2] FSR quantum 167.23 vs σ_dip(A)=183: 同量級 (窗寬 identity)
  [F3] MC null: 隨機 dip 喺 ±1500 內撞 v_abs±σ 窗嘅機率
  [F4] E Hα +47 / E Hβ −79: 唔喺 hop=4 窗 → 分類為 outflow/窄線 (Rusakov mild
        outflow, record 21 §6③) — 樣本外反例, 誠實記錄
"""
import math, json, os, random
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'data')
LOG = []
def ck(name, cond, detail=''):
    LOG.append((name, bool(cond), detail))
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

c_km = 299792.458
R_world_Mpc = 4129.94
Mpc_km = 3.0856775814913673e19
R_world_km = R_world_Mpc*Mpc_km
a0 = c_km**2/(2*math.pi*R_world_km)
R_c_kpc = R_world_Mpc/44**3*1000.0
R_c_km = R_c_kpc*3.0856775814913673e16
V_max = math.sqrt(a0*R_c_km)
v_abs = V_max/math.sqrt(2.0)                  # 289.76 km/s
sig3 = c_km*math.pi/(88*4**3)                 # 167.23
print("="*84)
print("O252/05 — hop=4 凝聚窗精準閉合 (honest, posterior-labelled)")
print("="*84)
print(f"v_abs = V_max/√2 = {v_abs:.3f} km/s   σ_window = {sig3:.2f} km/s")

# ---------- 觀測 (retention: 最後 reference) ----------
obs = [
  ("A", "Hα", -283.01, 183.0, "depth 0.979, M4_abs_dv (record 24)"),
  ("E", "Hα", +47.0,   175.0, "paper +47 FWHM 350 (Rusakov outflow?)"),
  ("E", "Hβ", -79.0,   260.0, "paper −79 FWHM 520"),
]

# F1: A 命中緊度
A_dip = abs(obs[0][2]); A_sig = obs[0][3]
tight = abs(A_dip - v_abs)/A_sig
ck("F1 A dip 緊度 <1σ", tight < 1.0, f"|283.01−289.76|/183 = {tight:.4f}σ")
dev_pct = abs(A_dip - v_abs)/v_abs*100
print(f"    A dev: {dev_pct:.2f}% (2.4% 內)")

# F2: 窗寬 identity — FSR ℓ=3 quantum vs σ_dip(A)
ratio = A_sig/sig3
ck("F2 σ 同量級 (1±0.2)", 0.8 < ratio < 1.2, f"183/167.23 = {ratio:.3f}")

# F3: MC null — 隨機檢驗
rng = random.Random(20261017_05)
N_MC = 100000
# 池: 均匀 ±1500 km/s (LRD 寬線窗, record 14: FWHM 1000-1500)
win_half = 167.23
hits = 0
for _ in range(N_MC):
    v = rng.uniform(-1500.0, 1500.0)
    if abs(abs(v) - v_abs) <= win_half:
        hits += 1
p_null = hits/N_MC
samples = 3   # A Hα, A Hβ(無), E Hα...
# A Hβ 冇 dip (record 24: ΔAIC +4.3 冇), 有望機 ~1/2
# Ber(p) pooled: P(≥1 命中緍 3 樣本) — conservative
p_ge1 = 1 - (1-p_null)**3
ck("F3 MC null p ≪ 0.05", p_ge1 < 0.05, f"p(≥1 hit in 3) = {p_ge1:.4f} (隨機)")
print(f"    MC null: single-draw hit prob {p_null:.4f} (窗 {win_half} km/s 於 ±1500)")
print(f"    p(≥1 命中喺 3 樣本) = {p_ge1:.4f}")

# F4: E 反例 (樣本外)
E_hits = [s for s,l,v,_,n in obs if s=="E" and abs(abs(v)-v_abs) <= win_half]
ck("F4 E 唔喺窗內 (樣本外反例, 誠實)", len(E_hits)==0,
   "E +47/−79 細速度 = outflow/窄線 成份 (Rusakov mild outflow 支持)")

# ---------- τ(v) 模型重建 (documented) ----------
print("\n── τ(v) 模型 (documented, 零參數) ──")
print("τ(v) = τ₀·ℓ_band(θ(v)) + τ_w·exp(−(v−v_abs)²/2σ²)")
print("  ℓ_band: 近/遠分支光程差 (smooth 帶, 藍弱方向)")
print("  v_abs = √(a₀·R_c/2) = V_max/√2 = 289.76 km/s  ← 凝聚重心窗")
print("  σ     = c·π/(88·4³) = 167.23 km/s           ← FSR ℓ=3 quantum")

data = {"v_abs_kms": v_abs, "sigma_window_kms": sig3,
        "obs": [{"source": s, "line": l, "v_kms": v, "sigma_obs_kms": sig, "note": n} for s,l,v,sig,n in obs],
        "F1_tight_sigma": tight, "F2_ratio": ratio,
        "MC": {"N": N_MC, "p_single": p_null, "p_ge1_3samples": p_ge1},
        "posterior_note": "「用 hop=4 層」係後驗收窄; v_abs 數值本身零參數。E 反例最要命: 唔可 all-in 窗模型",
        "checks": [{"name": n, "pass": p, "detail": d} for n,p,d in LOG]}
with open(f"{DATA}/05_hop4_closure.json","w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

np_ok = sum(1 for _,p,_ in LOG if p)
print(f"\n結果: {np_ok}/{len(LOG)} PASS → data/05_hop4_closure.json")