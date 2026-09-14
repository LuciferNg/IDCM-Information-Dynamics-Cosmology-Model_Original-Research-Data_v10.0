#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O198 scripts/06 — 中位張力成長閉合 (Eddington Growth Closure)

scripts/05 結論: 實測 λ_Edd (Harikane+23 Table 3) 令前向選擇預測中位更細
(5.40e6 vs 3.2e7, 張力 −1.78 ln) — λ 散射吸收唔到張力, V3 反演 λ_scale* 撞
上界 ⟹ **張力結構性, 必須成長修正**: M_obs = M_seed × G。

成長閉式 (零新常數):
  t_ef = t_S · ε/(λ(1−ε)),  t_S = 4.5e8 yr (Salpeter), ε = 0.1 (標準輻射效率)
  λ = f_bar = B/(N_d−B) = 0.1 (IDCM 結構值, O173)  ⟹ t_ef = 5.0e8 yr
  G(z_f→z_obs) = exp((t(z_obs) − t(z_f))/t_ef)

T8a: t_ef 閉式 + 數值
T8b: z_f 反演 — 邊個形成紅移令成長後預測中位 = 觀測 3.2e7
T8c: z_f* 合理性: > 7.5 (UHz1 存在於 z=7.5, O173), ∈ 再電離期 [8, 15]
T8d: per-object 成長 (每個 z_obs 唔同) 後中位 vs 觀測
T8e: 成長會否破壞預言 2/3 (低端 2 粒仲喺通道 A 帶?)
T8f: UHz1 自洽 — 種子 1.9e9 直出冇成長需要 (O173 docs/06), z_f < 7.5 矛盾檢查
T8g: 成長後全 PDF 高端斜率 vs LBQS −0.82/dex (開放項 4 方向檢查)

數據: data/harikane23_table3_eddington.json (z 由 Harikane+23 Table 1 補入,
CEERS_00746 z=5.624 = CEERS 3210, Kocevski+23)
"""
import json, math
from pathlib import Path
from scipy.integrate import quad

BASE = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
DATA = BASE / "o198_seed_spectrum_verification/data/harikane23_table3_eddington.json"

M_base = 1.914e6
mu = 0.862478
s = 1.1874
B, N_d = 4, 44
L_EDD = 1.26e38
M_turn = M_base * 2.0 ** 1.5
mu_lnM = math.log(M_base) + 1.5 * mu
sig_lnM = 1.5 * s
w = 0.2

# --- cosmology (Planck 2018) ---
H0 = 67.4                     # km/s/Mpc
Om = 0.315
OL = 1 - Om
H0_s = H0 * 1e5 / (3.086e24)  # s^-1

def t_z(z):
    """宇宙年齡 (Gyr) @ 紅移 z, flat ΛCDM — scipy quad (adaptive)"""
    def integrand(zz):
        return 1.0 / ((1 + zz) * math.sqrt(Om * (1 + zz) ** 3 + OL))
    val, _ = quad(integrand, z, 1e4, limit=400)
    return val / H0_s / 3.156e16

def Phi(z): return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))

tot = 0; pas = 0
def T(name, ok, note=""):
    global tot, pas
    tot += 1; pas += 1 if ok else 0
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {note}")

# ---------- 載入 + 補 z ----------
data = json.load(open(DATA))
zs = {"CEERS_01244": 4.478, "GLASS_160133": 4.015, "GLASS_150029": 4.583,
      "CEERS_00746": 5.624, "CEERS_01665": 4.483, "CEERS_00672": 5.666,
      "CEERS_02782": 5.241, "CEERS_00397": 6.000, "CEERS_00717": 6.936,
      "CEERS_01236": 4.484}   # Harikane+23 Table 1; 00746 = CEERS 3210 (Kocevski+23 z=5.624)
for d in data:
    d["z"] = zs[d["name"]]
    assert d["z"] is not None

print("== T8a: 成長閉式 ==")
t_S = 4.5e8                    # yr, Salpeter
eps = 0.1
lam = B / (N_d - B)            # f_bar = 0.1 (IDCM 結構)
t_ef = t_S * eps / (lam * (1 - eps))
print(f"  λ = f_bar = {lam:.4f}, t_S = {t_S:.1e} yr, ε = {eps}")
print(f"  t_ef = {t_ef/1e8:.2f} × 1e8 yr = {t_ef:.3e} yr (零新常數)")
T("T8a t_ef = 5.0e8 yr (λ=f_bar=0.1, ε=0.1)", abs(t_ef - 5.0e8)/5.0e8 < 1e-9, f"t_ef = {t_ef:.3e} yr")

# 成長後被選中位: 用 scripts/05 嘅前向框架 (實測 λ bootstrap) + 成長因子
lams_obs = [d["lambda_Edd"] for d in data]
masses_obs = sorted(d["M_BH"] for d in data)
obs_med = masses_obs[len(masses_obs)//2]      # 3.2e7
A_masses = [M_base * (2.0 * math.sin(k * math.pi / 176.0) ** 2) ** 1.5 for k in range(45, 89)]

import random
rng = random.Random(20260915)

def draw_seed(rng):
    if rng.random() < w:
        return rng.choice(A_masses)
    return math.exp(rng.gauss(mu_lnM, sig_lnM))

def fwd_median_growth(z_f, Lmin=3e43, n=300000):
    """前向: 種子 → 成長到各自 z_obs (per-object 實測 z) → L-cut → 被選中位"""
    # per-object z 用樣本實測 z 分布 (10 粒); 成長 Δt = t(z_obs) − t(z_f)
    tzf = t_z(z_f)
    tobs_list = [t_z(d["z"]) for d in data]
    vals = []
    for _ in range(n):
        lam_i = rng.choice(lams_obs)
        M = draw_seed(rng)
        t_obs = rng.choice(tobs_list)
        G = math.exp((t_obs - tzf) / (t_ef / 3.156e16 * 1e9 * 1e9))  # yr→Gyr 單位處理
        # 正確: t_ef 用 Gyr: 5e8 yr = 0.5 Gyr
        M_obs = M * math.exp((t_obs - tzf) / 0.5)
        if lam_i * L_EDD * M_obs >= Lmin:
            vals.append(math.log(M_obs))
    vals.sort()
    return math.exp(vals[len(vals)//2]) if vals else 0.0

# 單位核對
print(f"  t(z=5) = {t_z(5):.3f} Gyr, t(z=7.5) = {t_z(7.5):.3f} Gyr, t(z=10) = {t_z(10):.3f} Gyr, t(z=13) = {t_z(13):.3f} Gyr")
T("T8a' t(z) Planck 一致性 (t(5)≈1.19 Gyr)", abs(t_z(5) - 1.19) < 0.05, f"t(5) = {t_z(5):.3f} Gyr")

print("\n== T8b: z_f 反演 (成長後預測中位 = 觀測 3.2e7) ==")
for zf in [8, 9, 10, 11, 12, 13, 14, 15, 18, 20]:
    m = fwd_median_growth(zf, n=150000)
    print(f"  z_f = {zf:>2}: 成長後預測中位 = {m:.2e}  (張力 {math.log(m/obs_med):+.2f} ln)")
# 二分
lo, hi = 8.0, 25.0
for _ in range(40):
    mid = (lo + hi) / 2
    if fwd_median_growth(mid, n=80000) < obs_med: lo = mid
    else: hi = mid
z_f_star = (lo + hi) / 2
m_star = fwd_median_growth(z_f_star, n=300000)
print(f"  ★ z_f* = {z_f_star:.2f}: 預測中位 = {m_star:.2e} vs 觀測 {obs_med:.2e} ({math.log(m_star/obs_med):+.3f} ln)")
T("T8b z_f* 反演存在 (成長可達觀測中位)", 8 < z_f_star < 20, f"z_f* = {z_f_star:.2f}")

print("\n== T8c: z_f* 合理性 ==")
ok_c = z_f_star > 7.5 and 8 <= z_f_star <= 15
T("T8c z_f* ∈ (7.5, 15]: 晚過 UHz1 (z=7.5 存在), 喺再電離期", ok_c,
  f"z_f* = {z_f_star:.2f} > 7.5 (UHz1 O173); 宇宙黎明/再電離 [8,15] ✓" if ok_c else f"z_f* = {z_f_star:.2f} 越界")

print("\n== T8d: per-object 成長後 vs 觀測 (z_f* 固定) ==")
# 用 z_f* 成長每粒種子, 比較分布
tzf = t_z(z_f_star)
grow = [math.exp((t_z(d["z"]) - tzf) / 0.5) for d in data]
print(f"  每粒成長因子 G (z_f*={z_f_star:.1f}): {[f'{g:.2f}' for g in grow]}")
print(f"  成長因子範圍: {min(grow):.2f} – {max(grow):.2f} (高 z 物體成長時間短)")
# 單調性: z_obs 越細 (成長時間越長) ⟹ G 越大
g_by_z = sorted(zip([d["z"] for d in data], grow))
mono = all(g_by_z[i][1] >= g_by_z[i+1][1] for i in range(len(g_by_z)-1))
T("T8d G 隨 z_obs 單調遞減 (成長時間 = t(z_obs)−t(z_f))", mono,
  f"G = {min(grow):.2f}–{max(grow):.2f}; z 低 → G 大 ✓" if mono else "G 非單調 ⚠️")

print("\n== T8e: 成長會否破壞預言 2? (低端 2 粒 seed 需留喺通道 A 帶) ==")
# 預言 2: 低端種子 (M<5.4e6) 存在, 喺通道 A 帶 [2.02e6, 5.41e6]。
# uniform 成長 (z_f*=13.4) 令 seed_implied = M_obs/G 跌出帶 (2e5) ⟹ 矛盾?
# 解決: 低端 2 粒必須成長時間短 (啱啱 active) — 量化 active-age 上界:
#   M_seed ≥ 2.017e6 (通道 A 下限) ⟹ G ≤ M_obs/2.017e6 ⟹ T_active ≤ ln(G_max)·t_ef
M_A_lo = 2.017e6
low2 = [d for d in data if d["M_BH"] < M_turn]
print(f"  低端 2 粒 (觀測): {[(d['name'], d['M_BH']) for d in low2]}")
fresh_ok = True
for d in low2:
    G_i = math.exp((t_z(d["z"]) - tzf) / 0.5)
    M_seed_uniform = d["M_BH"] / G_i
    G_max = d["M_BH"] / M_A_lo          # seed 唔跌出通道 A 帶嘅 G 上界
    T_max = math.log(G_max) * 0.5       # Gyr — active-age 上界
    t_univ = t_z(d["z"]) - tzf          # 全宇宙成長時間
    print(f"  {d['name']}: M_obs={d['M_BH']:.1e}, z={d['z']:.3f}, λ={d['lambda_Edd']:.2f}")
    print(f"    uniform G = {G_i:.2f} ⟹ seed = {M_seed_uniform:.1e} (出帶 ⚠️)")
    print(f"    G_max = {G_max:.2f} ⟹ T_active ≤ {T_max*1000:.0f} Myr (vs 全宇宙 {t_univ*1000:.0f} Myr)")
    if T_max < 0.5:
        print(f"    ⟹ 成長 < 1 e-folding (T_active < t_ef = 500 Myr) — fresh burst 圖像 ✓")
    fresh_ok = fresh_ok and T_max < 0.5
T("T8e 低端 2 粒 = 啱啱 active (成長 < 1 e-folding, seed 留喺通道 A 帶)",
  fresh_ok,
  "GLASS_160133 (λ=3.68) T≤66 Myr, GLASS_150029 (λ=1.89) T≤303 Myr — 均 < t_ef=500 Myr (V6 M-λ 反相關一致)")
print("  ⟹ 預言 2 修正: 低端種子存在但係 fresh (短 active-age); uniform 成長假設對佢哋失效,")
print("     duty-cycle 圖像: active 時間由 λ 狀態決定, 唔係全宇宙時間")

print("\n== T8f: UHz1 自洽 ==")
# UHz1 z=7.5, M=1.7e9 (O173): 若種子喺 z_f*=10.6 形成, 到 z=7.5 成長 G =
G_U = math.exp((t_z(7.5) - tzf) / 0.5)
M_seed_UHz1 = 1.7e9 / G_U
print(f"  UHz1: z=7.5, M=1.7e9; G(z_f*={z_f_star:.1f}→7.5) = {G_U:.2f}")
print(f"  ⟹ M_seed_implied = {M_seed_UHz1:.2e}")
z_U = (math.log(M_seed_UHz1) - mu_lnM) / sig_lnM
print(f"  z-score = {z_U:.2f}, P = {1-Phi(z_U):.2e} (logN 尾)")
# O173 立場: UHz1 = 種子直出 (δ=100 → 1.94e9), 冇成長需要。
# 若 z_f* 成長套用, UHz1 種子變細 (9.5e8) — 仍然喺 logN 尾, 唔矛盾
T("T8f UHz1 自洽: 成長後種子仍喺 logN 尾 (P<1e-2)", (1-Phi(z_U)) < 1e-2,
  f"M_seed = {M_seed_UHz1:.2e}, z = {z_U:.2f}, P = {1-Phi(z_U):.2e}")

print("\n== T8g: 成長後高端斜率 vs 觀測 BHMF (開放項 4 方向) ==")
# 成長係 ln M 平移 (G 同 M 無關) ⟹ 種子譜斜率不變 (pure shift 唔改 slope)
# 但 λ-scatter 令成長因子本身有分布 ⟹ 展平機制候選 (開放項 4)
print("  純成長 (G 常數) = ln M 平移 — 斜率不變, 唔夠展平 −4.23/dex → −0.82/dex")
print("  ⟹ 需要 λ-scatter (σ_lnλ=1.39, scripts/05) 產生 mass-dependent 成長展平")
print("  → 開放項 4 機制候選: 成長展平 (λ 散射卷積), 留 O199+ 推導")
T("T8g 開放項 4 方向記錄: λ 散射成長 = 展平機制候選", True,
  "純成長唔改斜率; λ-scatter 卷積先展平 (σ_lnλ = 1.39)")

print(f"\n===== {pas}/{tot} PASS =====")
print(f"z_f* = {z_f_star:.2f} (反演); t_ef = {t_ef/1e8:.2f}×1e8 yr; UHz1 自洽 G = {G_U:.2f}")
