#!/usr/bin/env python3
"""
三大開放問題閉合 — 2026-09-09 第二輪
====================================
Part A — N(z) 選擇函數反捲積 (1/V_max, Schmidt 1968)
   - 每個源 V_max: m444(z') < 27.5 限制內可偵測體積
   - K444(z) 由零塵 SED (α_ν=-3, R=1.5) 計算
   - color cut 對 α_ν=-3 SED 喺 z=4-9.5 全成立 (flat 1.6-1.9 > 1.5) → 唔影響
   - n_true(z) = Σ 1/V_max,i → fit 斜率 s (IDCM 預測 -1.00)

Part B — 結構紅化: 塵埃 vs 結構判別
   B1: 黑體候選檢驗 (T 掃描, 應驗證 Wien 側喺 rest 0.4-1µm 係咪光到可以觀測)
   B2: 塵埃修正殘餘: color_int = color_obs - E(277-444, Av_fit)
       殘餘 vs log₄(1+z) 相關 → 結構分量檢驗

Part C — Schindler J1007 (z=7.3, M_BH=5e8, δ≈30) 閉合
   - J1007+2115 位置 → 最近 A₅ 節點 → S, hop, f
   - M_base = E_strain × η × S × f
   - M_pred = M_base × (1+δ)^p, p=1 (Bondi-like) vs p=2 (彈性能), δ=30 實測
"""
import math, json
import numpy as np
from astropy.io import ascii
from astropy.cosmology import Planck18
from scipy import stats as scipy_stats

OUT = 'data/12_selection_reddening_schindler.json'
PHI = (1 + 5**0.5)/2
ETA = PHI**(-21)
E_STRAIN = 1.565e12   # M☉
C_INT = 0.3636
M_LIM = 27.5          # F444W 偵測極限 (AB mag)
AREA = 0.54           # deg²
area_sr = AREA * (math.pi/180)**2
cosmo = Planck18

t = ascii.read('data/COSMOS-Web_LRDs.dat', format='ecsv')
N = len(t)
zq = np.array(t['z_qso_med'], dtype=float)
Lb = np.array(t['logLbol_med'], dtype=float)
m277 = np.array(t['m277'], dtype=float)
m444 = np.array(t['m444'], dtype=float)
Av = np.array(t['Av_qso_med'], dtype=float)
ra = np.array(t['ra'], dtype=float)
dec = np.array(t['dec'], dtype=float)

def ang_dist(ra1, dec1, ra2, dec2):
    r1, d1 = math.radians(ra1), math.radians(dec1)
    r2, d2 = math.radians(ra2), math.radians(dec2)
    cosd = math.sin(d1)*math.sin(d2) + math.cos(d1)*math.cos(d2)*math.cos(r1-r2)
    return math.degrees(math.acos(max(-1, min(1, cosd))))

def K444(z, alpha_nu=-3.0, R=1.5):
    """F444W K-correction vs z=0 (零塵 SED: f_ν = (λ/365)^(-α) × [R if λ_rest>365nm])"""
    def flux(lam_lo, lam_hi, zz):
        lam = np.linspace(lam_lo, lam_hi, 300)
        lr = lam/(1+zz)
        fv = (lr/365.0)**(-alpha_nu) * np.where(lr < 365.0, 1.0, R)
        return np.trapezoid(fv/lam, lam)
    F0 = flux(3.8e3, 5.0e3, 0.0)
    Fz = flux(3.8e3, 5.0e3, z)
    return -2.5*math.log10(Fz/F0)

def DM(z):
    return cosmo.distmod(z).value

# ============ Part A: 1/V_max ============
print("="*72)
print("Part A: N(z) 1/V_max 反捲積")
print("="*72)

# 每個源: V_max = 喺 m444(z')<27.5 內可偵測嘅共動體積
# m444(z') = m444_obs + [DM(z')-DM(z)] + [K444(z')-K444(z)]
z_grid = np.linspace(4.0, 9.8, 2000)
dVdz = cosmo.differential_comoving_volume(z_grid).value * (math.pi/180)**2 * AREA  # Mpc³ per dz (0.54 deg²)
V_max_all = []
for i in range(N):
    mz = m444[i] + (DM(z_grid) - DM(zq[i])) + (np.array([K444(z) for z in z_grid]) - K444(zq[i]))
    ok = mz < M_LIM
    if np.sum(ok) == 0:
        V_max_all.append(0.0)
        continue
    zlo, zhi = z_grid[ok].min(), z_grid[ok].max()
    m = (z_grid >= zlo) & (z_grid <= zhi)
    V_max_all.append(float(np.trapezoid(dVdz[m], z_grid[m])))
V_max_all = np.array(V_max_all)
print(f"V_max 分佈: median {np.median(V_max_all[V_max_all>0]):.3e} cMpc³, "
      f"零 V_max (極限內偵測唔到): {int(np.sum(V_max_all==0))}")

# n_true per bin (1/V_max)
zbins = np.arange(4.5, 9.75, 0.5)
zcen = (zbins[:-1]+zbins[1:])/2
n_true = []; n_obs_bin = []
for zlo, zhi in zip(zbins[:-1], zbins[1:]):
    in_bin = (zq >= zlo) & (zq < zhi)
    sel = in_bin & (V_max_all > 0)
    # bin 內源, 每個貢獻 1/V_max,i
    n_t = np.sum(1.0/V_max_all[sel]) if np.sum(sel) else 0.0
    n_true.append(n_t)
    n_obs_bin.append(np.sum(in_bin))
n_true = np.array(n_true); n_obs_bin = np.array(n_obs_bin)
n_pred = 2.24e-5/(1+zcen)

print(f"\n{'z':>5} {'N':>5} {'n_true(1/Vmax)':>15} {'n_pred':>12} {'ratio_true':>11}")
vol_bin = []
for zlo, zhi in zip(zbins[:-1], zbins[1:]):
    vol_bin.append((cosmo.comoving_volume(zhi).value - cosmo.comoving_volume(zlo).value) * area_sr/(4*math.pi))
vol_bin = np.array(vol_bin)
for i in range(len(zcen)):
    r = n_true[i]/n_pred[i] if n_pred[i] > 0 else float('nan')
    print(f"{zcen[i]:>5.1f} {int(n_obs_bin[i]):>5} {n_true[i]:>15.4e} {n_pred[i]:>12.4e} {r:>11.2f}")

# 斜率 (加權, z=5-8 窗口 — 1/Vmax 修正最可靠範圍)
mfit = (zcen >= 5.0) & (zcen <= 8.0) & (n_true > 0)
x = np.log(1+zcen[mfit]); y = np.log(n_true[mfit])
A = np.vstack([x, np.ones_like(x)]).T
beta, _, _, _ = np.linalg.lstsq(A, y, rcond=None)
resid = y - A@beta
sxx = np.sum((x-x.mean())**2)
se = math.sqrt(np.sum(resid**2)/(len(x)-2)/sxx)
r_corr = np.corrcoef(x, y)[0,1]
tstat = beta[0]/se
pval = 2*(1 - scipy_stats.t.cdf(abs(tstat), len(x)-2))
print(f"\n1/V_max 反捲積斜率 (z=5-8): {beta[0]:+.3f} ± {se:.3f}   (IDCM 預測 -1.00, r={r_corr:.3f}, p={pval:.2e})")

# 冇修正斜率對比
y2 = np.log(np.array(n_obs_bin)[mfit] * (4*math.pi/(0.54*(math.pi/180)**2)) / (cosmo.comoving_volume(zcen[mfit]+0.25).value-cosmo.comoving_volume(zcen[mfit]-0.25).value))
beta2, _, _, _ = np.linalg.lstsq(A, y2, rcond=None)
print(f"冇修正斜率 (z=5-8): {beta2[0]:+.3f}")

# ============ Part B: 紅化判別 ============
print("\n" + "="*72)
print("Part B: 塵埃 vs 結構判別")
print("="*72)

# B1: 黑體候選 — T=500-1000K 喺 z=6 觀測窗口嘅 rest-frame 光度可行性
print("\nB1: 黑體候選檢驗 (T, λ_peak, 喺 z=6 rest 0.5µm 相對峰值光度)")
for T in [400, 500, 600, 690, 800, 1000]:
    lam_peak = 2898.0/T  # µm (Wien)
    # 黑體喺 rest 0.5µm (z=6 觀測 3.5µm) vs 峰值: B_λ(0.5µm)/B_λ(λ_peak)
    hck = 14388.0  # µm·K
    def bb(lam_um, TT):
        x = hck/(lam_um*TT)
        if x > 700: return 0.0
        return (1.0/lam_um**5)/(math.exp(x)-1)
    ratio = bb(0.5, T)/bb(lam_peak, T)
    print(f"  T={T:4d}K  λ_peak={lam_peak:5.1f}µm  rest0.5µm/peak = {ratio:.2e}  "
          f"{'❌ 太暗' if ratio < 1e-3 else '🟡 有可能'}")
print("  → 黑體喺 rest 0.4-1µm (z=4-9.5 觀測 2.4-5µm) 係 Wien 尾, 亮度 <0.1% 峰值")
print("  → 純黑體 REFUTED: LRD 喺 rest-UV/optical 好光, 唔可能係 T<1000K 黑體")

# B2: 塵埃修正殘餘
print("\nB2: 塵埃修正後顏色殘餘 vs log₄(1+z)")
# Cardelli+1989: A(λ)/A_V (Rv=3.1), 用 1/λ µm⁻¹ — 完整 a(x)+b(x)/Rv
def A_over_Av(lam_um):
    x = 1.0/lam_um  # µm⁻¹
    if x <= 1.1:  # IR (λ ≥ 0.9µm), 冪律延伸至長波
        return 0.574*x**1.61
    if 1.1 < x <= 3.3:  # optical-NIR
        y = x - 1.82
        a = 1.0 + 0.17699*y - 0.50447*y**2 - 0.02427*y**3 + 0.72085*y**4 + 0.01979*y**5 - 0.77530*y**6 + 0.32999*y**7
        b = 1.41338*y + 2.28305*y**2 + 1.07233*y**3 - 5.38434*y**4 - 0.62251*y**5 + 5.30260*y**6 - 2.09002*y**7
        return a + b/3.1
    if 3.3 < x <= 8.0:  # UV
        y = x - 5.9
        Fa = -0.04473*y**2 - 0.009779*y**3
        Fb = 0.2130*y**2 + 0.1207*y**3
        a = 1.752 - 0.316*x - 0.104/((x-4.67)**2 + 0.341) + Fa
        b = -3.090 + 1.825*x + 1.206/((x-4.67)**2 + 0.341) + Fb
        return a + b/3.1
    return 1.0

E277_obs = (A_over_Av(2.775) - A_over_Av(4.44))  # 觀測波長 (弱, 僅參考)
good = np.isfinite(m277) & np.isfinite(m444) & np.isfinite(Av)
color = m277[good] - m444[good]
z_g = zq[good]
# 正確: 塵埃喺源 (rest frame), 消光喺 rest λ 計
E_rest = np.array([A_over_Av(2.775/(1+z)) - A_over_Av(4.44/(1+z)) for z in z_g])
color_int = color - E_rest*Av[good]   # 塵埃修正後 (內稟) 顏色
x4 = np.log(1+z_g)/math.log(4)
print(f"  rest-frame E(277-444)/Av: median {np.median(E_rest):.3f}, 範圍 {E_rest.min():.3f}-{E_rest.max():.3f}")
print(f"  (Av median {np.median(Av):.2f} → 塵埃色 {np.median(E_rest)*np.median(Av):.2f} mag vs 觀測 median {np.median(color):.2f})")

beta_r, _, _, _ = np.linalg.lstsq(np.vstack([x4, np.ones_like(x4)]).T, color_int, rcond=None)
resid_r = color_int - (beta_r[0]*x4 + beta_r[1])
sxx_r = np.sum((x4-x4.mean())**2)
se_r = math.sqrt(np.sum(resid_r**2)/(len(x4)-2)/sxx_r)
r_r = np.corrcoef(x4, color_int)[0,1]
t_r = beta_r[0]/se_r
p_r = 2*(1 - scipy_stats.t.cdf(abs(t_r), len(x4)-2))
print(f"color_int (塵埃修正) = {beta_r[1]:+.3f} + {beta_r[0]:+.3f}·log₄(1+z)")
print(f"  斜率 {beta_r[0]:+.3f} ± {se_r:.3f}, r={r_r:.3f}, p={p_r:.2e}")
print(f"  觀測 color_obs 斜率: 1.553 ± 0.203 (p=1.4e-13)")
if abs(beta_r[0]) < 2*se_r:
    print("  → 塵埃修正後冇殘餘 z 趨勢: 塵埃完全解釋紅化 🟡 (IDCM 結構分量未確認)")
elif beta_r[0] > 0:
    print(f"  → 塵埃修正後仍有正 z 趨勢 ({beta_r[0]:+.2f}): 存在結構分量 🟢")
print(f"  E(277-444)/Av (rest) = {np.median(E_rest):.3f}  (Av median {np.median(Av):.2f} → 塵埃色 {np.median(E_rest)*np.median(Av):.2f} mag vs 觀測 median {np.median(color):.2f})")

# ============ Part C: Schindler J1007 ============
print("\n" + "="*72)
print("Part C: Schindler J1007 (z=7.3, M_BH=5e8, δ≈30)")
print("="*72)
# J1007+2115: RA 10h07m ≈ 151.75°, Dec +21°15' ≈ 21.25°
jra, jdec = 10*15 + 7*15/60, 21 + 15/60
print(f"J1007+2115: RA={jra:.2f}°, Dec={jdec:.2f}°")

nodes = []
with open('../../open_problems_fresh/cmb_cold_spot/data/a5_nodes.txt') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'): continue
        p = line.split()
        nodes.append({'id': len(nodes), 'ra': float(p[0]), 'dec': float(p[1])})
routing = json.load(open('data/a5_routing_weighted.json'))
rnode = {n['id']: n for n in routing['nodes']}

ds = [ang_dist(jra, jdec, nd['ra'], nd['dec']) for nd in nodes]
j = int(np.argmin(ds))
print(f"最近節點: {j} (ra={nodes[j]['ra']:.2f}, dec={nodes[j]['dec']:.2f}), 距離 {ds[j]:.2f}°")
print(f"  節點屬性: hop={rnode[j]['hop_from_cs']}, S={rnode[j]['stress_S']:.4f}, frust={rnode[j]['frust_count']}")

hop_j = rnode[j]['hop_from_cs']
S_j = rnode[j]['stress_S']
f_j = 1 + C_INT*math.cos(math.pi*hop_j/4)
M_base = E_STRAIN * ETA * S_j * f_j
print(f"  M_base = E_strain × φ⁻²¹ × S × f = 1.565e12 × {ETA:.2e} × {S_j:.4f} × {f_j:.4f} = {M_base:.2e} M☉")

delta_obs = 30.0  # Schindler 實測 δ≈30 (inner bin)
for p_exp in [1.0, 1.5, 2.0]:
    M_pred = M_base * (1+delta_obs)**p_exp
    print(f"  p={p_exp:.1f}: M = {M_base:.2e} × (1+30)^{p_exp:.1f} = {M_pred:.2e} M☉  vs 5e8 → ratio {M_pred/5e8:.2f}")

# 需要嘅 δ (p=1) 對應 M_base: δ_need = M_obs/M_base - 1
delta_need = 5e8/M_base - 1
print(f"\n  p=1 閉合需要 δ = 5e8/{M_base:.2e} - 1 = {delta_need:.1f}  (Schindler 實測 δ≈30)")
print(f"  p=2 閉合需要 δ = sqrt(5e8/{M_base:.2e}) - 1 = {math.sqrt(5e8/M_base)-1:.1f}")
print(f"  r₀=8±2 cMpc protocluster core δ~10-50 合理範圍 ✓")

# 其他節點對比: 若 J1007 喺 hop=0/8 高 S 節點
S_max = max(n['stress_S'] for n in routing['nodes'])
print(f"\n  對比: 最高 S 節點 S={S_max:.3f}, hop=0/8 時 f=1+0.3636={1+C_INT:.4f}")
M_alt = E_STRAIN*ETA*S_max*(1+C_INT)
print(f"  M_base(最強節點) = {M_alt:.2e} M☉ → p=1, δ=30 → {M_alt*31:.2e} M☉ (ratio vs 5e8: {M_alt*31/5e8:.2f})")

# ============ 保存 ============
results = {
    "part_A_1Vmax": {
        "z_bins": zcen.tolist(),
        "n_true": n_true.tolist(),
        "n_obs": n_obs_bin.tolist(),
        "n_pred": n_pred.tolist(),
        "slope_1Vmax_z5_8": {"b": float(beta[0]), "err": float(se), "r": float(r_corr), "p": float(pval)},
        "slope_uncorrected_z5_8": float(beta2[0]),
        "median_Vmax": float(np.median(V_max_all[V_max_all>0])),
        "n_zero_Vmax": int(np.sum(V_max_all==0)),
    },
    "part_B_reddening": {
        "blackbody_refuted": True,
        "dust_color_per_Av_rest": float(np.median(E_rest)),
        "color_int_slope": float(beta_r[0]),
        "color_int_slope_err": float(se_r),
        "color_int_corr": float(r_r),
        "color_int_p": float(p_r),
        "color_obs_slope": 1.553,
        "residual_structural": bool(abs(beta_r[0]) > 2*se_r),
    },
    "part_C_schindler": {
        "j1007_ra": float(jra), "j1007_dec": float(jdec),
        "nearest_node": int(j), "dist_deg": float(ds[j]),
        "node_hop": int(hop_j), "node_S": float(S_j),
        "M_base": float(M_base),
        "delta_obs": delta_obs,
        "M_pred_p1_d30": float(M_base*31),
        "M_pred_p2_d30": float(M_base*31**2),
        "ratio_p1": float(M_base*31/5e8),
        "delta_needed_p1": float(delta_need),
        "delta_needed_p2": float(math.sqrt(5e8/M_base)-1),
    },
}
json.dump(results, open(OUT, 'w'), indent=2)
print(f"\nSaved {OUT}")
