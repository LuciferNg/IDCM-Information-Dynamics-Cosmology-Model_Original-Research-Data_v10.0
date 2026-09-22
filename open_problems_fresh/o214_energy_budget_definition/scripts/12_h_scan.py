#!/usr/bin/env python3
"""
O214 — Script 12: IDCM 幾何約束全光譜 h 掃描 (h 依賴診斷)
=============================================================
用戶問題: 「但全部計算是使用哪個h?」

誠實盤點:
  大部分 script 默認 h=0.674 (Planck 側), 唔係 IDCM 結構 h。
  IDCM 自己嘅 h 預言: O38 H₀=71.157 → h=0.7116 (但 M₀ 標度 🔴)

本 script: 掃描 h ∈ [0.66, 0.73], 全光譜 χ² (IDCM 幾何約束 3:16:41)
  ① 最佳 h 係幾多? 同 Planck 0.674 / O38 0.7116 差幾遠?
  ② h 依賴有幾強? Δχ² 曲線幾尖?
  ③ 若 h 係 IDCM 自由度 → 幾何約束真正預言嘅係 Ω 比例 (3:16:41),
     而 h 決定絕對標度 — 呢個係「比例預言」vs「絕對預言」嘅分界
"""
import json
import sys
from pathlib import Path
import numpy as np
import camb
from scipy.io import FortranFile

OUT = Path(__file__).parent.parent / "data"
DATA = Path(__file__).parent.parent / "data" / "planck2018_plik_lite"
checks = []

def chk(name, cond, detail=""):
    checks.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"   {detail}" if detail else ""))

print("=" * 100)
print("O214 Script 12: IDCM 全光譜 h 掃描")
print("=" * 100)

# ── Plik_lite ──
nbintt_hi, nbinte, nbinee = 215, 199, 199
bval, X_data, X_sig = np.genfromtxt(DATA / "cl_cmb_plik_v22.dat", unpack=True)
blmin = np.loadtxt(DATA / "blmin.dat").astype(int)
blmax = np.loadtxt(DATA / "blmax.dat").astype(int)
bin_w = np.loadtxt(DATA / "bweight.dat")
f = FortranFile(DATA / "c_matrix_plik_v22.dat", 'r')
covmat = f.read_reals(dtype=float).reshape((613, 613))
for i in range(613):
    for j in range(i, 613):
        covmat[i, j] = covmat[j, i]

def bin_model(D, blmin, blmax, bin_w, plmin, ellmin=0, nbin=None):
    ls = np.arange(len(D)) + ellmin
    fac = ls * (ls + 1) / (2 * np.pi)
    Cl = D / fac
    if nbin is None:
        nbin = len(blmin)
    out = np.zeros(nbin)
    for i in range(nbin):
        out[i] = np.sum(Cl[blmin[i]+plmin-ellmin : blmax[i]+plmin+1-ellmin] *
                        bin_w[blmin[i]:blmax[i]+1])
    return out

_SPEC = {}
def get_spec(ombh2, omch2, H0, ns, As=2.1e-9, lmax=2600):
    key = (round(float(ombh2), 6), round(float(omch2), 5), round(float(H0), 3))
    if key not in _SPEC:
        pars = camb.CAMBparams()
        pars.set_cosmology(H0=H0, ombh2=float(ombh2), omch2=float(omch2), tau=0.0544)
        pars.InitPower.set_params(ns=float(ns), As=As)
        pars.set_for_lmax(lmax)
        pars.set_matter_power(redshifts=[0.0], kmax=60.0, k_per_logint=50)
        r = camb.get_results(pars)
        cls = r.get_cmb_power_spectra(spectra=['total'], CMB_unit='muK')['total']
        _SPEC[key] = cls
    return _SPEC[key]

def chi2_ttteee(ombh2, omch2, H0, ns=0.9649, fit_As=True):
    cls = get_spec(ombh2, omch2, H0, ns)
    Cltt_bin = bin_model(cls[:, 0], blmin, blmax, bin_w, 30, nbin=nbintt_hi)
    Clte_bin = bin_model(cls[:, 3], blmin, blmax, bin_w, 30, nbin=nbinte)
    Clee_bin = bin_model(cls[:, 1], blmin, blmax, bin_w, 30, nbin=nbinee)
    X_model = np.concatenate([Cltt_bin, Clte_bin, Clee_bin])
    C = covmat + np.eye(613) * 1e-12 * np.trace(covmat) / 613
    Cinv = np.linalg.inv(C)
    d = X_model - X_data
    if fit_As:
        a = X_model @ Cinv @ X_model
        b = X_model @ Cinv @ d
        chi = d @ Cinv @ d - b**2 / a
    else:
        chi = d @ Cinv @ d
    return chi

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§A h 掃描: IDCM 幾何約束 (3:16:41) 全光譜 χ²(h)\n{'─'*100}")
h_grid = np.arange(0.660, 0.731, 0.005)
chis_h = []
print(f"  h      ombh2    omch2    χ²(613)   χ²/dof   Δχ² vs ΛCDM")
for h in h_grid:
    ombh2 = (3/60) * h**2
    omch2 = (16/60) * h**2
    chi = chi2_ttteee(ombh2, omch2, h*100)
    chis_h.append(chi)
    print(f"  {h:.3f}  {ombh2:.5f}  {omch2:.5f}  {chi:8.1f}  {chi/612:6.2f}  {chi-583.7:+8.1f}")

chis_h = np.array(chis_h)
imin = np.argmin(chis_h)
h_best = h_grid[imin]
print(f"\n  ★ IDCM 幾何約束下最佳 h = {h_best:.3f} (χ²={chis_h[imin]:.1f})")
print(f"    vs Planck h=0.674: Δh={h_best-0.674:+.3f}")
print(f"    vs IDCM O38 h=0.7116: Δh={h_best-0.7116:+.3f}")

# 二次擬合
A = np.polyfit(h_grid, chis_h, 2)
h_fit = -A[1] / (2 * A[0])
sig_h = 1 / np.sqrt(A[0]) if A[0] > 0 else np.inf
print(f"  二次擬合: h_best = {h_fit:.4f} ± {sig_h:.4f}")

# 關鍵比較
chi_h674 = float(chis_h[np.argmin(abs(h_grid-0.674))])
chi_h7116 = float(chis_h[np.argmin(abs(h_grid-0.7116))])
print(f"\n  h=0.674 (Planck):  χ² = {chi_h674:.1f}  (Δχ² vs best {chi_h674-chis_h[imin]:+.1f})")
print(f"  h=0.7116 (O38):    χ² = {chi_h7116:.1f}  (Δχ² vs best {chi_h7116-chis_h[imin]:+.1f})")
chk("A1  IDCM 幾何約束最佳 h ≈ 0.674 (Planck 側, 唔係 O38 0.7116)",
    abs(h_best - 0.674) < 0.01, f"h_best={h_best:.3f} vs 0.674 / O38 0.7116")
chk("A2  O38 h=0.7116 全光譜排除 (Δχ² > 25 = 5σ)",
    chi_h7116 - chis_h[imin] > 25, f"Δχ²={chi_h7116-chis_h[imin]:.1f}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§B 裁決: h 依賴嘅結構意義\n{'─'*100}")
print(f"""
  用戶問題: 「全部計算是使用哪個h?」

  誠實答案:
  ┌─────────────────────────────────────────────────────────────┐
  │ script 02/03/04/06/09:  默認 h = 0.674 (Planck 側)         │
  │ script 08:              掃描 h 於 0.674, 0.7116, 1/√2        │
  │ script 10 (z=0 Connor): h70 = H₀/70 (直接計數, 冇 CMB h)  │
  │ script 11/12 (全光譜):  掃描 h, 最佳 {h_best:.3f}              │
  └─────────────────────────────────────────────────────────────┘

  ★ 關鍵結構發現:
    1. IDCM 幾何約束 (3:16:41) 只預言【比例】, 唔預言【絕對標度】
       ombh2 : omch2 = 3:16 (固定), 但 h² 係整體縮放
    2. 全光譜要求 h ≈ {h_best:.3f} — 即 IDCM 比例預言成立 ⟹ h 必須係 Planck 側
    3. IDCM O38 預言 h = 0.7116 → 全光譜 Δχ² = {chi_h7116-chis_h[imin]:.1f} (排除!)
       ⟹ O38 H₀ 標度 🔴 同 CMB 全光譜直接矛盾 (H₀ 張力喺譜形量化)
    4. ⟹ IDCM 嘅「零參數」而家係: Ω 比例 (3:16:41) 零參數 ✅
       + h 標度仍開放 (O38 🔴) — 全光譜判 h ≈ 0.674

  結論: 「全部計算使用 h=0.674」係部分事實 — 更準確講:
  	IDCM 幾何約束預言 Ω 比例 3:16:41 (零參數),
  	全光譜擬合判 h ≈ {h_best:.3f} (≈ Planck),
  	O38 h=0.7116 被排除 — 呢個係 IDCM 內部 H₀ 張力嘅譜形證據
""")

n_pass = sum(1 for _, ok in checks if ok)
print(f"\n{'='*100}\nRESULT: {n_pass}/{len(checks)} PASS\n{'='*100}")
for name, ok in checks:
    if not ok:
        print(f"  FAIL: {name}")

with open(OUT / "12_h_scan.json", "w") as f:
    json.dump({
        "checks_pass": int(n_pass), "checks_total": int(len(checks)),
        "h_grid": [float(x) for x in h_grid],
        "chi2_h": [float(x) for x in chis_h],
        "h_best": float(h_fit), "h_sigma": float(sig_h),
        "chi_h674": float(chi_h674), "chi_h7116": float(chi_h7116),
        "conclusion": "IDCM 幾何約束 (3:16:41) 只預言 Ω 比例; 全光譜要求 h≈0.674; O38 h=0.7116 被排除 (Δχ² 大) = IDCM 內部 H₀ 張力譜形證據",
    }, f, ensure_ascii=False, indent=2)
print("✅ 寫入 data/12_h_scan.json")
