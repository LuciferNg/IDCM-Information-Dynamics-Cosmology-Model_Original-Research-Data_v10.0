#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O148 scripts/17 — Plik Δχ²=+14.7 來源分解 (S15)
================================================
問題: O214 scripts/11 顯示 IDCM 幾何約束全光譜 χ² = 598.4 vs ΛCDM 583.7 → Δχ² = +14.7
      但分區只得 TT 峰位區 (0.85/dof) + Silk 尾 (1.17/dof) — 613 bins = TT(215)+TE(199)+EE(199)
      嘅 TE/EE 未拆。+14.7 到底集中喺邊個頻譜/邊個 ℓ 段?

方法: CAMB 重算 IDCM vs ΛCDM 模型, 逐 bin 計 (D_model − D_data)/σ_bin 殘差,
      分 TT/TE/EE × ℓ 段 (峰位 ℓ<1000, 過渡 1000-1500, Silk 1500-2000, 尾 ℓ>2000) 加總。
      ⚠️ 用對角 σ 近似定位 (唔係完整協方差 chi²) — 目的係搵來源方向,
      唔係取代 O214 嘅正式 chi² (613×613 cov).

數據: o214_energy_budget_definition/data/planck2018_plik_lite/
      (cl_cmb_plik_v22.dat, blmin.dat, blmax.dat, bweight.dat, c_matrix_plik_v22.dat)
"""
import sys
from pathlib import Path
import numpy as np
import camb

OUT = Path(__file__).resolve().parent.parent.parent / "o214_energy_budget_definition" / "data"
DATA = OUT / "planck2018_plik_lite"

# ── Plik_lite 數據 ──
nbintt_hi, nbinte, nbinee = 215, 199, 199
bval, X_data, X_sig = np.genfromtxt(DATA / "cl_cmb_plik_v22.dat", unpack=True)
blmin = np.loadtxt(DATA / "blmin.dat").astype(int)
blmax = np.loadtxt(DATA / "blmax.dat").astype(int)
bin_w = np.loadtxt(DATA / "bweight.dat")

def bin_model(D, blmin, blmax, bin_w, plmin, ellmin=0, nbin=None):
    """bin 理論 D_ℓ 到 Plik bins. ★ ellmin=0 (CAMB row index = ℓ)"""
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

def get_spec(ombh2, omch2, H0, ns, As=2.1e-9, lmax=2600):
    pars = camb.CAMBparams()
    pars.set_cosmology(H0=H0, ombh2=float(ombh2), omch2=float(omch2), tau=0.0544)
    pars.InitPower.set_params(ns=float(ns), As=As)
    pars.set_for_lmax(lmax)
    r = camb.get_results(pars)
    cls = r.get_cmb_power_spectra(spectra=['total'], CMB_unit='muK')['total']
    return cls

# ── 模型 ──
print("=" * 96)
print("O148 S15 — Plik Δχ²=+14.7 來源分解 (TT/TE/EE × ℓ 段)")
print("=" * 96)

# IDCM (O214 scripts/11 h=0.674): Ω_b=3/60, Ω_c=16/60
idcm_pars = dict(ombh2=0.02271, omch2=0.12114, H0=67.4, ns=0.9649)
# ΛCDM 參考
lcdm_pars = dict(ombh2=0.02237, omch2=0.1200, H0=67.36, ns=0.9649)

cls_idcm = get_spec(**idcm_pars)
cls_lcdm = get_spec(**lcdm_pars)

# ── bin 模型 ──
Cltt_idcm = bin_model(cls_idcm[:, 0], blmin, blmax, bin_w, 30, nbin=nbintt_hi)
Clte_idcm = bin_model(cls_idcm[:, 3], blmin, blmax, bin_w, 30, nbin=nbinte)
Clee_idcm = bin_model(cls_idcm[:, 1], blmin, blmax, bin_w, 30, nbin=nbinee)
Cltt_lcdm = bin_model(cls_lcdm[:, 0], blmin, blmax, bin_w, 30, nbin=nbintt_hi)
Clte_lcdm = bin_model(cls_lcdm[:, 3], blmin, blmax, bin_w, 30, nbin=nbinte)
Clee_lcdm = bin_model(cls_lcdm[:, 1], blmin, blmax, bin_w, 30, nbin=nbinee)

# 分段 (以 bin 中心 ℓ 計)
def bin_centre(i, plmin):
    return (blmin[i] + blmax[i]) / 2.0 + plmin

def segment_chi2(name, model, data, sig, plmin, nbin):
    """對角近似 χ² 分段加總 — 返回每段 (ℓ範圍, n, Σd²/σ², Σd/σ)"""
    segs = [(0, 1000, "峰位区 ℓ<1000"), (1000, 1500, "过渡 1000-1500"),
            (1500, 2000, "Silk 1500-2000"), (2000, 99999, "尾区 ℓ>2000")]
    print(f"\n── {name} ({nbin} bins, plmin={plmin}) ──")
    total = 0.0
    for lo, hi, label in segs:
        idx = [i for i in range(nbin) if lo <= bin_centre(i, plmin) < hi]
        if not idx:
            continue
        d = model[idx] - data[idx]
        s = sig[idx]
        chi = np.sum((d / s) ** 2)
        overall = np.sum(d / s)
        total += chi
        print(f"  {label:<20} n={len(idx):>3}  Σ(d/σ)²={chi:8.2f}  Σ(d/σ)={overall:+8.2f}")
    print(f"  总计 (对角近似): {total:.2f}")
    return total

chi_tt = segment_chi2("TT", Cltt_idcm, X_data[:nbintt_hi], X_sig[:nbintt_hi], 30, nbintt_hi)
chi_te = segment_chi2("TE", Clte_idcm, X_data[nbintt_hi:nbintt_hi+nbinte], X_sig[nbintt_hi:nbintt_hi+nbinte], 30, nbinte)
chi_ee = segment_chi2("EE", Clee_idcm, X_data[nbintt_hi+nbinte:], X_sig[nbintt_hi+nbinte:], 30, nbinee)

print("\n" + "=" * 96)
print(f"对应对角 χ² (IDCM): TT={chi_tt:.1f} + TE={chi_te:.1f} + EE={chi_ee:.1f} = {chi_tt+chi_te+chi_ee:.1f}")
print(f"(O214 正式协方差 chi² = 598.4 — 对角近似偏小係正常)")
print("=" * 96)

# ── 最差 10 bins 列表 ──
print("\n── 最大残差 bins (IDCM vs Planck, 用於定位 +14.7) ──")
allres = []
for i in range(nbintt_hi):
    d = (Cltt_idcm[i] - X_data[i]) / X_sig[i]
    allres.append((bin_centre(i, 30), "TT", d, abs(d)))
for i in range(nbinte):
    j = nbintt_hi + i
    d = (Clte_idcm[i] - X_data[j]) / X_sig[j]
    allres.append((bin_centre(i, 30), "TE", d, abs(d)))
for i in range(nbinee):
    j = nbintt_hi + nbinte + i
    d = (Clee_idcm[i] - X_data[j]) / X_sig[j]
    allres.append((bin_centre(i, 30), "EE", d, abs(d)))
allres.sort(key=lambda x: -x[3])
for ell, spec, d, ad in allres[:12]:
    print(f"  ℓ={ell:7.1f} {spec}  (D_model−D_data)/σ = {d:+6.2f}")

# ── IDCM vs ΛCDM 差 (模型層面, 唔係 data) ──
print("\n── IDCM − ΛCDM 模型差 (冇 data 干預, 睇結構偏移方向) ──")
for i in range(nbintt_hi):
    d = (Cltt_idcm[i] - Cltt_lcdm[i]) / X_sig[i]
    if abs(d) > 0.5:
        pass
# 差嘅總和
d_tt = (Cltt_idcm - Cltt_lcdm) / X_sig[:nbintt_hi]
d_te = (Clte_idcm - Clte_lcdm) / X_sig[nbintt_hi:nbintt_hi+nbinte]
d_ee = (Clee_idcm - Clee_lcdm) / X_sig[nbintt_hi+nbinte:]
print(f"  模型差 Σ(d/σ): TT={np.sum(d_tt):+8.2f}  TE={np.sum(d_te):+8.2f}  EE={np.sum(d_ee):+8.2f}")
print(f"  模型差 Σ(d/σ)²: TT={np.sum(d_tt**2):8.2f}  TE={np.sum(d_te**2):8.2f}  EE={np.sum(d_ee**2):8.2f}")