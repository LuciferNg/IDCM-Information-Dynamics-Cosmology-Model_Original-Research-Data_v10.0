#!/usr/bin/env python3
"""
COSMOS-Web 434 LRD 定量測試 (2026-09-09)
========================================
三大開放點一次過閉合檢驗:

Test A — N(z): 完整目錄 + 光度限制子樣本 vs IDCM 1/(1+z)
   - n(z) per z bin (0.54 deg², Planck18 共動體積)
   - ln n vs ln(1+z) 斜率 (預測 -1.00)
   - Lbol 限制子樣本 (45.5/46.0/46.5) 同一斜率 → 檢驗「z≈5峰值=光度選擇」
   - 峰值位置 + 同 z=6 ratio-3.1 記錄對比

Test B — 結構紅化定量: color (F277W-F444W) vs log₄(1+z)
   - 觀測斜率 b: color = a + b·log₄(1+z)
   - 零塵 Balmer break K-correction 模型 (α, R 網格) → 結構紅化可否零塵閉合
   - 對比 QSO fit Av (塵埃模型)

Test C — 質量標度絕對檢驗 (hop=4 波節!)
   - 全部 434 LRD 最近節點 = 8, hop=4 → 干涉相消波節
   - M_pred(8) = E_strain × η × S(8) × f(hop=4) vs 觀測 Lbol→M_BH 代理
   - 單節點場 → 預測質量分佈窄 (σ 只來自 Eddington ratio 散佈)
"""
import math, json
import numpy as np
from astropy.io import ascii
from astropy.cosmology import Planck18
from scipy import stats as scipy_stats

OUT = 'data/11_cosmosweb_tests.json'
PHI = (1 + 5**0.5)/2
ETA = PHI**(-21)
E_STRAIN = 1.565e12  # M☉ (32 條阻挫邊總應變能)
C_INT = 0.3636       # 干涉核對比度

# ============ 載入 ============
t = ascii.read('data/COSMOS-Web_LRDs.dat', format='ecsv')
N = len(t)
zq = np.array(t['z_qso_med'], dtype=float)
Lb = np.array(t['logLbol_med'], dtype=float)
m277 = np.array(t['m277'], dtype=float)
m444 = np.array(t['m444'], dtype=float)
Av = np.array(t['Av_qso_med'], dtype=float)
ra = np.array(t['ra'], dtype=float)
dec = np.array(t['dec'], dtype=float)

print("="*72)
print(f"COSMOS-Web 定量測試: {N} LRD")
print("="*72)

# ============ 位置: 最近節點 ============
# A₅ 節點 (cmb_cold_spot/data/a5_nodes.txt)
nodes = []
with open('../../open_problems_fresh/cmb_cold_spot/data/a5_nodes.txt') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'): continue
        p = line.split()
        nodes.append({'id': len(nodes), 'ra': float(p[0]), 'dec': float(p[1])})

def ang_dist(ra1, dec1, ra2, dec2):
    r1, d1 = math.radians(ra1), math.radians(dec1)
    r2, d2 = math.radians(ra2), math.radians(dec2)
    cosd = math.sin(d1)*math.sin(d2) + math.cos(d1)*math.cos(d2)*math.cos(r1-r2)
    return math.degrees(math.acos(max(-1, min(1, cosd))))

nearest = []
for i in range(N):
    ds = [ang_dist(ra[i], dec[i], nd['ra'], nd['dec']) for nd in nodes]
    j = int(np.argmin(ds))
    nearest.append({'lrd': int(t['id'][i]), 'node': j, 'dist_deg': float(ds[j])})
nn = np.array([x['node'] for x in nearest])
from collections import Counter
print("\n[Test C 前置] 最近節點分佈:", dict(Counter(nn.tolist())))

# ============ Test A: N(z) ============
print("\n" + "="*72)
print("Test A: N(z) vs 1/(1+z)")
print("="*72)
AREA = 0.54  # deg² (paper; 目錄extent 0.80 作敏感性)
area_sr = AREA * (math.pi/180)**2

cosmo = Planck18
# 共動體積每 bin
zbins = np.arange(4.25, 9.75, 0.5)
vols = []
for zlo, zhi in zip(zbins[:-1], zbins[1:]):
    V = cosmo.comoving_volume(zhi).value - cosmo.comoving_volume(zlo).value  # Mpc³ (全天空)
    vols.append(V * area_sr/(4*math.pi))  # 0.54 deg² 內
vols = np.array(vols)

zcen = (zbins[:-1] + zbins[1:])/2
counts, _ = np.histogram(zq, bins=zbins)
n_obs = counts / vols  # cMpc⁻³
n_err = np.sqrt(np.maximum(counts,1)) / vols
n_pred = 2.24e-5/(1+zcen)

print(f"{'z_bin':>10} {'N':>5} {'n_obs':>12} {'n_pred':>12} {'ratio':>8}")
for i in range(len(zcen)):
    print(f"{zcen[i]:>8.2f} {counts[i]:>5} {n_obs[i]:>12.3e} {n_pred[i]:>12.3e} {n_obs[i]/n_pred[i]:>8.2f}")

# 斜率: ln n vs ln(1+z), 加權 (z=4.5-7.5 完整性窗口)
def slope_fit(zsel, nobs, nerr, zlo, zhi):
    m = (zsel >= zlo) & (zsel <= zhi) & (nobs > 0)
    x = np.log(1 + zsel[m]); y = np.log(nobs[m]); w = 1/((nerr[m]/nobs[m])**2 + 1e-9)
    A = np.vstack([x, np.ones_like(x)]).T
    W = np.diag(w)
    beta, _, _, _ = np.linalg.lstsq(np.sqrt(W)@A, np.sqrt(W)@y, rcond=None)
    # 不確定性
    resid = y - A@beta
    chi2 = float(np.sum(resid**2 * w))
    dof = len(x) - 2
    cov = np.linalg.inv(A.T@W@A)
    return beta[0], math.sqrt(cov[0,0]), chi2, dof, int(np.sum(m))

b1, eb1, chi1, dof1, npt1 = slope_fit(zcen, n_obs, n_err, 4.5, 7.5)
print(f"\n斜率 (z=4.5-7.5): {b1:.3f} ± {eb1:.3f} (IDCM 預測 -1.00, n_pt={npt1}, chi2/dof={chi1/dof1:.1f})")

# 光度限制子樣本
print("\n光度限制子樣本 (log Lbol > cut):")
for Lcut in [45.5, 46.0, 46.5]:
    m_sel = Lb > Lcut
    c2, _ = np.histogram(zq[m_sel], bins=zbins)
    n2 = c2/vols; e2 = np.sqrt(np.maximum(c2,1))/vols
    b2, eb2, chi2v, dof2, npt2 = slope_fit(zcen, n2, e2, 4.5, 7.5)
    n_use = int(np.sum(m_sel))
    print(f"  Lbol>{Lcut}: n={n_use:4d}  斜率={b2:+.3f}±{eb2:.3f}  (chi2/dof={chi2v/dof2:.1f})")
    # 峰值 bin
    if np.sum(c2) > 0:
        pk = int(np.argmax(c2))
        print(f"         峰值 bin z={zcen[pk]:.2f} (N={c2[pk]})")

# z=6 ratio 記錄對比
i6 = int(np.argmin(np.abs(zcen-6.25)))
print(f"\nz≈6.2 對比: n_obs={n_obs[i6]:.2e} vs 預測 {n_pred[i6]:.2e} → ratio {n_obs[i6]/n_pred[i6]:.2f} (記錄: 3.1)")

# ============ Test B: 結構紅化 ============
print("\n" + "="*72)
print("Test B: 結構紅化 color(F277W-F444W) vs log₄(1+z)")
print("="*72)
good = np.isfinite(m277) & np.isfinite(m444) & (m444 > 0)
color = m277[good] - m444[good]
z_g = zq[good]
x4 = np.log(1 + z_g)/math.log(4)

# 線性 fit color = a + b·log₄(1+z)
A = np.vstack([x4, np.ones_like(x4)]).T
beta, _, _, _ = np.linalg.lstsq(A, color, rcond=None)
resid = color - A@beta
sxx = np.sum((x4 - x4.mean())**2)
se_b = np.sqrt(np.sum(resid**2)/(len(x4)-2)/sxx)
r = np.corrcoef(x4, color)[0,1]
tstat = beta[0]/se_b
pval = 2*(1 - scipy_stats.t.cdf(abs(tstat), len(x4)-2))
print(f"color = {beta[1]:.3f} + {beta[0]:.3f}·log₄(1+z)   [b={beta[0]:+.3f}±{se_b:.3f}, r={r:.3f}, p={pval:.2e}]")
print(f"樣本 n={len(color)}, 色範圍 {color.min():.2f}-{color.max():.2f}, median {np.median(color):.2f}")

# 零塵 Balmer break K-correction 模型
# 模板: f_ν = C·ν^α 喺 λ<365nm (斷裂藍側, 暗)  [3650 Å = Balmer break]
#        f_ν = C·R·ν^α 喺 λ>365nm (亮側)
# 合成光度: m1-m2 = -2.5log10[(∫f_ν dλ/λ)_F277W / (∫f_ν dλ/λ)_F444W]
def synth_color(z, alpha, R, lam_b=365.0):
    """頂帽濾波近似: F277W 2.4-3.1µm, F444W 3.8-5.0µm"""
    def flux_ratio(lam_lo, lam_hi):
        lam = np.linspace(lam_lo, lam_hi, 400)
        lam_rest = lam/(1+z)
        fv = (lam_rest/lam_b)**alpha * np.where(lam_rest < lam_b, 1.0, R)
        return np.trapezoid(fv/lam, lam)
    return -2.5*math.log10(flux_ratio(2.4e3, 3.1e3)/flux_ratio(3.8e3, 5.0e3))

def synth_cont_color(z, alpha_nu):
    """純連續譜 (冇 break): f_ν ∝ ν^alpha_nu"""
    def flux_ratio(lam_lo, lam_hi):
        lam = np.linspace(lam_lo, lam_hi, 400)
        lam_rest = lam/(1+z)
        fv = (lam_rest/365.0)**(-alpha_nu)  # f_ν ∝ λ^(-alpha_nu)
        return np.trapezoid(fv/lam, lam)
    return -2.5*math.log10(flux_ratio(2.4e3, 3.1e3)/flux_ratio(3.8e3, 5.0e3))

def synth_full_color(z, alpha_nu, R, lam_b=365.0):
    """紅連續譜 × Balmer break: f_ν = (λ/λ_b)^(-α_ν) × [R if λ_rest>λ_b else 1]"""
    def flux_ratio(lam_lo, lam_hi):
        lam = np.linspace(lam_lo, lam_hi, 400)
        lam_rest = lam/(1+z)
        fv = (lam_rest/lam_b)**(-alpha_nu) * np.where(lam_rest < lam_b, 1.0, R)
        return np.trapezoid(fv/lam, lam)
    return -2.5*math.log10(flux_ratio(2.4e3, 3.1e3)/flux_ratio(3.8e3, 5.0e3))

zgrid = np.linspace(4.0, 9.5, 12)
print("\n零塵 K-correction 模型 (color vs z):")
print(f"{'z':>5} {'obs_med':>8} {'break α=0,R=4':>13} {'break α=-1,R=4':>13} {'cont α_ν=-2':>12} {'cont α_ν=-3':>12} {'cont α_ν=-4':>12}")
zbins_c = np.arange(4.0, 9.5, 0.5)
med_c = []
for i in range(len(zbins_c)-1):
    m = (z_g >= zbins_c[i]) & (z_g < zbins_c[i+1])
    med_c.append(np.median(color[m]) if np.sum(m) else np.nan)
med_c = np.array(med_c)
zc = (zbins_c[:-1]+zbins_c[1:])/2
for i, z in enumerate(zc):
    if np.isfinite(med_c[i]):
        print(f"{z:>5.2f} {med_c[i]:>8.2f} " +
              f"{synth_color(z, 0, 4):>13.2f} {synth_color(z, -1, 4):>13.2f} " +
              f"{synth_cont_color(z, -2):>12.2f} {synth_cont_color(z, -3):>12.2f} {synth_cont_color(z, -4):>12.2f}")

# 最佳零塵模型 fit (break 網格 + 純連續譜 + 紅連續譜×break)
best_break = None; best_cont = None; best_full = None
for alpha in np.arange(-2.0, 1.01, 0.5):
    for R in np.arange(2.0, 15.01, 0.5):
        pred = np.array([synth_color(z, alpha, R) for z in zc])
        mok = np.isfinite(med_c)
        rms = np.sqrt(np.mean((med_c[mok]-pred[mok])**2))
        if best_break is None or rms < best_break[2]:
            best_break = (alpha, R, rms)
for anu in np.arange(-5.0, 1.01, 0.25):
    pred = np.array([synth_cont_color(z, anu) for z in zc])
    mok = np.isfinite(med_c)
    rms = np.sqrt(np.mean((med_c[mok]-pred[mok])**2))
    if best_cont is None or rms < best_cont[1]:
        best_cont = (anu, rms)
for anu in np.arange(-4.0, 0.01, 0.25):
    for R in np.arange(1.0, 9.01, 0.5):
        pred = np.array([synth_full_color(z, anu, R) for z in zc])
        mok = np.isfinite(med_c)
        rms = np.sqrt(np.mean((med_c[mok]-pred[mok])**2))
        if best_full is None or rms < best_full[2]:
            best_full = (anu, R, rms)
print(f"\n最佳零塵 break 模型: α={best_break[0]:.1f}, R={best_break[1]:.1f}, RMS={best_break[2]:.2f} mag")
print(f"最佳零塵純連續譜:   α_ν={best_cont[0]:.1f}, RMS={best_cont[1]:.2f} mag")
print(f"最佳零塵 full 模型: α_ν={best_full[0]:.1f}, R={best_full[1]:.1f}, RMS={best_full[2]:.2f} mag")
print(f"(觀測 bin 內散佈 ~{np.nanmedian([np.std(color[(z_g>=a)&(z_g<b)]) for a,b in zip(zbins_c[:-1],zbins_c[1:])]):.2f})")

# Av 對比
print(f"\nQSO-fit Av: median {np.median(Av):.2f}, 範圍 {Av.min():.2f}-{Av.max():.2f}")
print("注意: 高 Av + 內稟藍 SED ↔ 零 Av + 結構拉伸 係經典簡併; 零塵模型可否以物理 R(3-7) 重現決定結構紅化可行性")

# ============ Test C: 質量 ============
print("\n" + "="*72)
print("Test C: 質量標度 — 節點 8 (hop=4 波節!)")
print("="*72)
S8 = 0.047048509643483345
hop8 = 4
f4 = (1 - C_INT)/(1 + C_INT)  # 干涉核 hop=4 質量比 0.4667
# f(hop) = 1 + C·cos(π·hop/4), 相對 hop=0 歸一: M(4)/M(0) = (1-C)/(1+C)
print(f"節點 8: S(8)={S8:.4f}, hop={hop8}, f(4)=1-C={1-C_INT:.4f}")
print(f"M(4)/M(0) = (1-C)/(1+C) = {f4:.4f} (預測低 {(1-f4)*100:.1f}%)")

# Lbol → M_BH 代理
logM10 = Lb - 39.10   # λ_Edd=0.1
logM01 = Lb - 38.10   # λ_Edd=1.0
print(f"\n觀測 M_BH 代理 (434 LRD, 全同節點):")
print(f"  λ=0.1: median logM={np.median(logM10):.2f} → {10**np.median(logM10):.2e} M☉")
print(f"  λ=1.0: median logM={np.median(logM01):.2f} → {10**np.median(logM01):.2e} M☉")
print(f"  logM 散佈 (λ=0.1): σ={np.std(logM10):.2f} dex")

# IDCM 預測 (兩種歸一化)
M_pred_total = E_STRAIN * ETA * S8 * (1 - C_INT)      # 用總應變能
M_pred_quota = E_STRAIN/60 * ETA * S8 * (1 - C_INT)   # 用每節點配額
print(f"\nIDCM 預測 M(8) (hop=4 干涉相消):")
print(f"  總應變能歸一: M = E_strain × φ⁻²¹ × S(8) × f(4) = {M_pred_total:.2e} M☉")
print(f"  每節點配額歸一: M = (E_strain/60) × φ⁻²¹ × S(8) × f(4) = {M_pred_quota:.2e} M☉")
print(f"  對比: λ=0.1 median {10**np.median(logM10):.2e} → ratio {M_pred_total/10**np.median(logM10):.2f}")
print(f"         λ=1.0 median {10**np.median(logM01):.2e} → ratio {M_pred_total/10**np.median(logM01):.2f}")

# 單節點預測: 質量分佈窄
print(f"\n單節點場預測: 質量分佈寬度 ≈ Eddington ratio 散佈 (~0.3-0.5 dex)")
print(f"觀測 logLbol σ = {np.std(Lb):.2f} dex (含光度選擇邊界效應)")
# Lbol vs z 趨勢 (AGN 演化 vs 靜態節點)
b_z, _, _, _ = np.linalg.lstsq(np.vstack([z_g, np.ones_like(z_g)]).T, Lb[good], rcond=None)
print(f"logLbol vs z 斜率: {b_z[0]:+.3f} dex/z (ΛCDM AGN 演化強正; 靜態節點預測 ~0 或結構拉伸負斜率)")

# ============ 保存 ============
results = {
    "n_lrd": int(N),
    "test_A": {
        "area_deg2": AREA,
        "z_bins": zcen.tolist(),
        "n_obs": n_obs.tolist(),
        "n_pred": n_pred.tolist(),
        "counts": counts.tolist(),
        "slope_full_z45_75": {"b": float(b1), "err": float(eb1), "chi2_dof": float(chi1/dof1), "n_pt": int(npt1)},
        "slope_Lbol_455": None, "slope_Lbol_460": None, "slope_Lbol_465": None,
        "ratio_z6": float(n_obs[i6]/n_pred[i6]),
    },
    "test_B": {
        "color_slope_log4": float(beta[0]), "color_slope_err": float(se_b),
        "color_intercept": float(beta[1]), "corr_r": float(r), "p": float(pval),
        "best_zero_dust_break": {"alpha": float(best_break[0]), "R": float(best_break[1]), "rms": float(best_break[2])},
        "best_zero_dust_cont": {"alpha_nu": float(best_cont[0]), "rms": float(best_cont[1])},
        "best_zero_dust_full": {"alpha_nu": float(best_full[0]), "R": float(best_full[1]), "rms": float(best_full[2])},
        "Av_median": float(np.median(Av)),
    },
    "test_C": {
        "nearest_node_all": int(nn[0]),
        "node_hop": hop8, "node_S": float(S8),
        "mass_ratio_hop4": float(f4),
        "M_pred_total_Edd01": float(M_pred_total),
        "M_pred_quota_Edd01": float(M_pred_quota),
        "M_obs_Edd01_median": float(10**np.median(logM10)),
        "M_obs_Edd1_median": float(10**np.median(logM01)),
        "ratio_total_over_obs_Edd01": float(M_pred_total/10**np.median(logM10)),
        "ratio_total_over_obs_Edd1": float(M_pred_total/10**np.median(logM01)),
        "logLbol_sigma": float(np.std(Lb)),
        "logLbol_vs_z_slope": float(b_z[0]),
    },
}
json.dump(results, open(OUT, 'w'), indent=2)
print(f"\nSaved {OUT}")
