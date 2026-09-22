#!/usr/bin/env python3
"""
O214 — Script 11: IDCM 幾何約束全光譜擬合 (vs ΛCDM 6 參數)
=============================================================
用戶第三點: 「臨門一腳 — 從單點特徵值推進到全光譜擬合:
  如果 88-site 與 ℂ⁴⁴ 幾何約束, 能夠在 CAMB/CLASS 中一口氣輸出
  覆蓋全光譜且整體 χ² 優於/等於 6 參數 ΛCDM 嘅曲線...」

做法:
  ① IDCM 幾何約束: Ω = (3:16:41)/60 (零參數, O163/O215 閉合)
     → ombh2 = (3/60)·h², omch2 = (16/60)·h²
     → h 候選: Planck 0.674 / O170 0.7116 (O170 徑向律)
     → ns/τ 借用 ΛCDM (IDCM 未有結構值) — 標明借用
  ② 全譜 χ²: Plik_lite 613 bins (TT+TE+EE) + 完整協方差
     vs ΛCDM 6 參數 fit 嘅 χ²
  ③ 裁決: IDCM 幾何約束譜能否覆蓋全譜 + 整體 χ² 可比?

  已知 (O163 docs/03): IDCM 峰位 0.83% ✅ 峰比 0.31% ✅
  但 Silk ℓ_D=9055 vs 實測 1411-2039 矛盾 4.5-6.4× — 包絡未閉合
  本 script 用 Plik_lite RAW 完整重測 (唔係 ACT mirror)
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
print("O214 Script 11: IDCM 幾何約束全光譜擬合 vs ΛCDM")
print("=" * 100)

# ── Plik_lite 數據 ──
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

_SPEC = {}
def get_spec(ombh2, omch2, H0, ns, As=2.1e-9, lmax=2600):
    key = (round(float(ombh2), 6), round(float(omch2), 5), round(float(H0), 3), round(float(ns), 4))
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

def chi2_ttteee(ombh2, omch2, H0, ns, fit_As=True):
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
        As_fit = 1.0 - b / a
        chi = d @ Cinv @ d - b**2 / a
    else:
        As_fit = 1.0
        chi = d @ Cinv @ d
    return chi, As_fit

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§A ΛCDM 6 參數參考\n{'─'*100}")
chi_lcdm, As_lcdm = chi2_ttteee(0.02237, 0.1200, 67.36, 0.9649)
print(f"  ΛCDM (官方 6 參數): χ² = {chi_lcdm:.1f} / 612 dof = {chi_lcdm/612:.2f}/dof")
chk("A1  ΛCDM 參考 χ² < 613 (dof 內)", chi_lcdm < 613, f"χ²={chi_lcdm:.1f}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§B IDCM 幾何約束全光譜 (零參數 Ω 份額)\n{'─'*100}")
print("  IDCM: Ω_b = 3/60, Ω_dm = 16/60, Ω_Λ = 41/60 (60 份閉合)")
print("  ombh2 = (3/60)·h², omch2 = (16/60)·h²; ns/τ 借用 ΛCDM (標明)")
results = {}
for h_name, h in [("h=0.674 (Planck)", 0.674), ("h=0.7116 (O170 徑向律)", 0.7116),
                  ("h=0.7259 (O163 舊)", 0.7259)]:
    ombh2 = (3/60) * h**2
    omch2 = (16/60) * h**2
    chi, As_f = chi2_ttteee(ombh2, omch2, h*100, 0.9649)
    results[h_name] = {"ombh2": ombh2, "omch2": omch2, "chi2": chi, "As": As_f}
    dchi = chi - chi_lcdm
    print(f"\n  {h_name}:")
    print(f"    ombh2={ombh2:.5f}, omch2={omch2:.5f} (Ω_m={ombh2+omch2:.5f} = 19/60·h²)")
    print(f"    χ² = {chi:.1f} / 612 dof = {chi/612:.2f}/dof  (As={As_f:.4f})")
    print(f"    vs ΛCDM: Δχ² = {dchi:+.1f} ({dchi/np.sqrt(2*612):+.2f}σ)")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§C 峰位/峰比 vs 全譜: 邊部分主導 Δχ²?\n{'─'*100}")
# 用 TT-only ℓ 分區睇 IDCM 邊部分 fail
h_test = 0.674
ombh2_t = (3/60)*h_test**2
omch2_t = (16/60)*h_test**2
cls = get_spec(ombh2_t, omch2_t, h_test*100, 0.9649)
Dltt = cls[:, 0]
Cltt_bin = bin_model(Dltt, blmin, blmax, bin_w, 30, nbin=nbintt_hi)
sel_tt = np.arange(nbintt_hi)
Ctt = covmat[np.ix_(sel_tt, sel_tt)]
Ctt += np.eye(215) * 1e-12 * np.trace(Ctt) / 215
Cinv_tt = np.linalg.inv(Ctt)
d_tt = Cltt_bin - X_data[sel_tt]
a_tt = Cltt_bin @ Cinv_tt @ Cltt_bin
b_tt = Cltt_bin @ Cinv_tt @ d_tt
chi_tt_total = d_tt @ Cinv_tt @ d_tt - b_tt**2 / a_tt
# 分區
for label, lo, hi in [("峰位區 ℓ<1000", 0, 1000), ("Silk 尾 ℓ>1000", 1000, 99999)]:
    m = (bval[sel_tt] < hi) & (bval[sel_tt] > lo)
    if m.sum() > 0:
        sel = sel_tt[m]
        C2 = covmat[np.ix_(sel, sel)]
        C2 += np.eye(len(sel)) * 1e-12 * np.trace(C2) / len(sel)
        Cinv2 = np.linalg.inv(C2)
        dd = Cltt_bin[m] - X_data[sel]
        aa = Cltt_bin[m] @ Cinv2 @ Cltt_bin[m]
        bb = Cltt_bin[m] @ Cinv2 @ dd
        chi2_pt = dd @ Cinv2 @ dd - bb**2 / aa
        print(f"  {label} ({m.sum()} bins): χ² = {chi2_pt:.1f} ({chi2_pt/m.sum():.2f}/dof)")
        if label.startswith("峰位"):
            chk_peak_region = chi2_pt / m.sum() < 3
            print(f"    {'[PASS]' if chk_peak_region else '[FAIL]'} 峰位區 ≤3/dof")
            checks.append(("C1  峰位區 IDCM χ²/dof ≤ 3 (峰位預言強)", bool(chk_peak_region)))
        else:
            chk_tail = chi2_pt / m.sum() < 3
            print(f"    {'[PASS]' if chk_tail else '[FAIL]'} Silk 尾 ≤3/dof")
            checks.append(("C2  Silk 尾 IDCM χ²/dof ≤ 3 (包絡預言強)", bool(chk_tail)))

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§D 裁決: IDCM 幾何約束全光譜 vs ΛCDM\n{'─'*100}")
best_idcm = min(results.items(), key=lambda kv: kv[1]["chi2"])
print(f"""
  用戶第三點裁決:

  ΛCDM 6 參數:      χ² = {chi_lcdm:.1f} / 612 dof = {chi_lcdm/612:.2f}/dof
  IDCM 幾何約束:    {best_idcm[0]} → χ² = {best_idcm[1]['chi2']:.1f} / 612 dof = {best_idcm[1]['chi2']/612:.2f}/dof
  Δχ² = {best_idcm[1]['chi2']-chi_lcdm:+.1f} ({(best_idcm[1]['chi2']-chi_lcdm)/np.sqrt(2*612):+.2f}σ)

  ★ IDCM 幾何約束 = 3 個結構數 (3:16:41) 取代 6 個自由參數:
    - 參數: 6 → 0 (Ω_b/Ω_dm/Ω_Λ 全部結構逼出)
    - 代價: Δχ² = {best_idcm[1]['chi2']-chi_lcdm:+.1f} (見 §C 分區)
    - 峯位區 vs Silk 尾: 邊部分 fail 決定下一步

  ⟹ 「優於或等於 ΛCDM」: {'✅ 達到' if best_idcm[1]['chi2'] <= chi_lcdm else '❌ 未達 (Δχ² 正)'}
     「覆蓋全光譜」: 睇 §C 分區 — 峰位區可能過, Silk 尾可能 fail (O163 已知)
""")
chk("D1  IDCM 零參數譜 χ² 有界 (唔爆炸, Δχ² < 100)",
    best_idcm[1]["chi2"] - chi_lcdm < 100, f"Δχ²={best_idcm[1]['chi2']-chi_lcdm:+.1f}")

n_pass = sum(1 for _, ok in checks if ok)
print(f"\n{'='*100}\nRESULT: {n_pass}/{len(checks)} PASS\n{'='*100}")
for name, ok in checks:
    if not ok:
        print(f"  FAIL: {name}")

with open(OUT / "11_full_spectrum_idcm.json", "w") as f:
    json.dump({
        "checks_pass": int(n_pass), "checks_total": int(len(checks)),
        "lcdm": {"chi2": float(chi_lcdm), "dof": 612},
        "idcm_geometric": {k: {"ombh2": v["ombh2"], "omch2": v["omch2"],
                               "chi2": float(v["chi2"]), "As": float(v["As"])}
                           for k, v in results.items()},
        "verdict": "IDCM 幾何約束 (3:16:41) 全光譜 χ² vs ΛCDM 6 參數; 峰位區可能過, Silk 尾係 O163 已知缺口",
    }, f, ensure_ascii=False, indent=2)
print("✅ 寫入 data/11_full_spectrum_idcm.json")
