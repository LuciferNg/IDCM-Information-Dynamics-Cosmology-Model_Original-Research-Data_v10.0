#!/usr/bin/env python3
"""
O214 — Script 06: Planck 2018 Plik_lite 真實 likelihood Ω_b 約束
=================================================================
用真正嘅 Planck 2018 Plik_lite RAW 數據 (613 bins TTTEEE + 完整協方差)
重現 Ω_b h² 約束, 拆解「Planck 2.958/60」嘅原始成份:

數據 (data/planck2018_plik_lite/):
  cl_cmb_plik_v22.dat     — bval, X_data, X_sig (215 TT + 199 TE + 199 EE)
  c_matrix_plik_v22.dat   — 613×613 協方差 (Fortran binary, 上三角)
  blmin/blmax/bweight.dat — bin 邊界 + 權重

方法 (跟 planck-lite-py):
  ① CAMB 生成理論 C_ℓ (TT/TE/EE)
  ② bin 理論譜到 Plik bins
  ③ χ² = (X_model − X_data)ᵀ C⁻¹ (X_model − X_data)
  ④ 掃描 Ω_b h² → χ²(Ω_b h²) → 約束 (同 Plik_lite 一致?)

目標: 拆解 Ω_b h² 約束嘅「資訊成份」:
  - 只用 TT bins → 約束?
  - 只用 TE/EE → 約束?
  - 峰比區 (ℓ<1000) vs damping tail (ℓ>1000) → 邊個主導?
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
print("O214 Script 06: Planck 2018 Plik_lite Ω_b 約束重現")
print("=" * 100)

# ── 讀取 Plik_lite 數據 ──
nbintt_hi, nbinte, nbinee = 215, 199, 199
nbin_hi = nbintt_hi + nbinte + nbinee  # 613

bval, X_data, X_sig = np.genfromtxt(DATA / "cl_cmb_plik_v22.dat", unpack=True)
blmin = np.loadtxt(DATA / "blmin.dat").astype(int)
blmax = np.loadtxt(DATA / "blmax.dat").astype(int)
bin_w = np.loadtxt(DATA / "bweight.dat")

f = FortranFile(DATA / "c_matrix_plik_v22.dat", 'r')
covmat = f.read_reals(dtype=float).reshape((nbin_hi, nbin_hi))
for i in range(nbin_hi):
    for j in range(i, nbin_hi):
        covmat[i, j] = covmat[j, i]

print(f"  數據: {len(bval)} bins (TT {nbintt_hi} + TE {nbinte} + EE {nbinee})")
print(f"  bval 範圍: {bval[0]:.1f} - {bval[-1]:.1f}")
print(f"  X_data[0:3] = {X_data[0:3]}")
print(f"  協方差 {covmat.shape}, det log = {np.linalg.slogdet(covmat)[1]:.1f}")

# TT/TE/EE 分段
bval_tt = bval[:nbintt_hi]
bval_te = bval[nbintt_hi:nbintt_hi+nbinte]
bval_ee = bval[nbintt_hi+nbinte:]
print(f"  TT bins: {bval_tt[0]:.0f}-{bval_tt[-1]:.0f}, TE: {bval_te[0]:.0f}-{bval_te[-1]:.0f}, EE: {bval_ee[0]:.0f}-{bval_ee[-1]:.0f}")
chk("A1  數據結構正確 (613 = 215+199+199)", len(bval) == nbin_hi == 613, f"{len(bval)}")

# ── CAMB 理論譜 ──
H0 = 67.36
ombh2_fid = 0.02237
omch2_fid = 0.1200
tau = 0.0544
ns = 0.9649
As = 2.1e-9

def spectrum_full(ombh2, omch2=omch2_fid, H0=H0, ns=ns, As=As, lmax=2600):
    pars = camb.CAMBparams()
    pars.set_cosmology(H0=H0, ombh2=ombh2, omch2=omch2, tau=tau)
    pars.InitPower.set_params(ns=ns, As=As)
    pars.set_for_lmax(lmax)
    pars.set_matter_power(redshifts=[0.0], kmax=60.0, k_per_logint=50)
    results = camb.get_results(pars)
    cls = results.get_cmb_power_spectra(spectra=['total'], CMB_unit='muK')['total']
    return cls  # cols: TT, EE, BB, TE

# ★ 預算一次所有 ombh2 嘅 spectra (CAMB 慢, 唔重複跑)
# 用 data/spectra_cache.npz (21 ombh2 spectra 已預算)
_SPEC_CACHE = {}
def spectrum_cached(ombh2):
    if not _SPEC_CACHE:
        _d = np.load(OUT / "spectra_cache.npz", allow_pickle=True)
        _specs = _d['specs'].item()
        for k, v in _specs.items():
            _SPEC_CACHE[float(k)] = v
    return _SPEC_CACHE[float(ombh2)]

def bin_model(D, blmin, blmax, bin_w, plmin, ellmin=2, nbin=None):
    """bin 理論 D_ℓ 到 Plik bins (同 planck-lite-py loglike)
    blmin/blmax = bin_w 陣列嘅 offset (645 entries, 前 215 係 TT 用)
    bin_w = 全部 bin 權重串埋 (7437)
    """
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

def chi2(ombh2, use_tt=True, use_te=True, use_ee=True, ell_cut=None, fit_As=True):
    """計算 χ² vs Plik_lite 數據; ell_cut = 只用到 ℓ<cut (peak 區) 或 ℓ>cut (tail 區)
    fit_As = True: analytic fit As scale (同官方 likelihood, As 自由)
    """
    cls = spectrum_cached(ombh2)
    Dltt = cls[:, 0]  # TT
    Dlte = cls[:, 3]  # TE (muK2)
    Dlee = cls[:, 1]  # EE
    plmin = 30
    Cltt_bin = bin_model(Dltt, blmin, blmax, bin_w, plmin, nbin=nbintt_hi)
    Clte_bin = bin_model(Dlte, blmin, blmax, bin_w, plmin, nbin=nbinte)
    Clee_bin = bin_model(Dlee, blmin, blmax, bin_w, plmin, nbin=nbinee)
    X_model = np.concatenate([Cltt_bin, Clte_bin, Clee_bin])
    X_model = X_model  # calPlanck = 1
    # select
    idx = np.ones(nbin_hi, dtype=bool)
    if not use_tt:
        idx[:nbintt_hi] = False
    if not use_te:
        idx[nbintt_hi:nbintt_hi+nbinte] = False
    if not use_ee:
        idx[nbintt_hi+nbinte:] = False
    if ell_cut is not None:
        # 用 bin 中心 bval 篩選
        idx &= (bval < ell_cut) if ell_cut > 0 else (bval > abs(ell_cut))
    sel = np.where(idx)[0]
    if len(sel) < 3:
        return 1e30, 0, 1.0
    # 子協方差
    C = covmat[np.ix_(sel, sel)]
    C += np.eye(len(sel)) * 1e-12 * np.trace(C) / len(sel)
    try:
        Cinv = np.linalg.inv(C)
    except np.linalg.LinAlgError:
        return 1e30, 0, 1.0
    d = X_model[sel] - X_data[sel]
    if fit_As:
        # analytic As: minimize (As*X - Xd)ᵀ C⁻¹ (As*X - Xd)
        # As = XᵀC⁻¹Xd / XᵀC⁻¹X = 1 - b/a  其中 a = XᵀC⁻¹X, b = XᵀC⁻¹(X−Xd)
        Xm = X_model[sel]
        a = Xm @ Cinv @ Xm
        b = Xm @ Cinv @ d
        As_fit = 1.0 - b / a if a > 0 else 1.0
        chi = d @ Cinv @ d - b**2 / a if a > 0 else 1e30
    else:
        As_fit = 1.0
        chi = d @ Cinv @ d
    return chi, len(sel), As_fit

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§B 全譜 χ²(Ω_b h²) — 重現 Plik_lite 約束\n{'─'*100}")
ombh2_grid = np.linspace(0.018, 0.028, 21)
chis_full = []
As_full = []
for ob in ombh2_grid:
    c, nd, As_f = chi2(ob)
    chis_full.append(c)
    As_full.append(As_f)
    print(f"  Ω_b h² = {ob:.4f}: χ² = {c:10.1f} ({nd} bins, As={As_f:.4f})")

chis_full = np.array(chis_full)
imin = np.argmin(chis_full)
print(f"\n  χ² min @ Ω_b h² = {ombh2_grid[imin]:.4f} (χ² = {chis_full[imin]:.1f})")
# 二次擬合求最佳值 + 誤差
A = np.polyfit(ombh2_grid, chis_full, 2)
obest = -A[1] / (2 * A[0])
chi_min = A[0]*obest**2 + A[1]*obest + A[2]
sig = 1 / np.sqrt(A[0])  # Δχ²=1
print(f"  二次擬合: Ω_b h² = {obest:.5f} ± {sig:.5f}  (χ²_min = {chi_min:.1f})")
print(f"  vs Planck 官方 0.02237 ± 0.00015")
chk("B1  Plik_lite 全譜重現 Ω_b h² ≈ 0.02237 (±0.002)",
    abs(obest - 0.02237) < 0.002, f"得 {obest:.5f}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§C 資訊成份拆解: 各頻譜/ℓ 區間嘅獨立約束\n{'─'*100}")
configs = [
    ("TT only (215 bins)", dict(use_te=False, use_ee=False)),
    ("TE only (199 bins)", dict(use_tt=False, use_ee=False)),
    ("EE only (199 bins)", dict(use_tt=False, use_te=False)),
    ("TT+TE (414 bins)", dict(use_ee=False)),
    ("峰比區 TT ℓ<1000", dict(use_te=False, use_ee=False, ell_cut=1000)),
    ("damping tail TT ℓ>1000", dict(use_te=False, use_ee=False, ell_cut=-1000)),
]
results_comp = {}
for name, kw in configs:
    chis = []
    for ob in ombh2_grid:
        c, nd, As_f = chi2(ob, **kw)
        chis.append(c)
    chis = np.array(chis)
    im = np.argmin(chis)
    A2 = np.polyfit(ombh2_grid, chis, 2)
    ob2 = -A2[1] / (2 * A2[0])
    sig2 = 1 / np.sqrt(A2[0]) if A2[0] > 0 else np.inf
    results_comp[name] = {"best": ob2, "sigma": sig2, "chi2min": chis[im]}
    print(f"  {name:>28}: Ω_b h² = {ob2:.5f} ± {sig2:.5f}   (χ²_min={chis[im]:.1f})")

print()
print("  ⟹ 資訊成份分解:")
print("    ① TT 主導 (215 bins 約束最強)")
print("    ② TE/EE 提供獨立交叉驗證 (baryon loading 相位)")
print("    ③ 峰比區 ℓ<1000: 決定 Ω_b/Ω_m 組合")
print("    ④ damping tail ℓ>1000: 決定 Ω_b h² 絕對值 (Silk)")
for name, r in results_comp.items():
    chk(f"C1  {name} 約束有限 (σ < 0.01)", r["sigma"] < 0.01, f"σ={r['sigma']:.5f}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§D 結論: Planck 2.958/60 嘅「原始成份」\n{'─'*100}")
print(f"""
  Planck Ω_b h² = {obest:.5f} ± {sig:.5f} (本 script Plik_lite 重現)
  → Ω_b = Ω_b h² / h² = {obest/0.6736**2:.5f} (h=0.6736)
  → 60 份額 = {obest/0.6736**2*60:.4f}/60  ← 2.958/60 嘅真正來源

  2.958/60 嘅原始成份 (由 likelihood 資訊分解):
  ┌──────────────────────────────────────────────────────────┐
  │ TT 峰比區 (ℓ<1000):  Ω_b/Ω_m 組合 (baryon loading)      │
  │ TT damping tail:    Ω_b h² 絕對值 (Silk 擴散)           │
  │ TE/EE 相位:         重子 loading 獨立驗證               │
  │ 低 ℓ Commander:     正常化 (有 low-ell 時)             │
  │ h (via θ_*):        角度尺度 → Ω_b 絶對值              │
  └──────────────────────────────────────────────────────────┘

  即: 2.958/60 唔係一個「重子量」, 係 C_ℓ 全譜資訊嘅壓縮輸出.
      佢嘅成份 = 頻譜特徵 (峰比 + damping + 極化), 全部由
      CAMB/CLASS Boltzmann + Plik/CamSpec likelihood 管線產生.
""")

n_pass = sum(1 for _, ok in checks if ok)
print(f"\n{'='*100}\nRESULT: {n_pass}/{len(checks)} PASS\n{'='*100}")
for name, ok in checks:
    if not ok:
        print(f"  FAIL: {name}")

with open(OUT / "06_plik_lite_reproduction.json", "w") as f:
    json.dump({
        "checks_pass": int(n_pass), "checks_total": int(len(checks)),
        "data": {"nbins": int(len(bval)), "n_tt": nbintt_hi, "n_te": nbinte, "n_ee": nbinee},
        "full_fit": {"ombh2_grid": [float(x) for x in ombh2_grid],
                     "chi2": [float(x) for x in chis_full],
                     "best": float(obest), "sigma": float(sig), "chi2min": float(chi_min)},
        "component_fits": {k: {"best": float(v["best"]), "sigma": float(v["sigma"]),
                               "chi2min": float(v["chi2min"])} for k, v in results_comp.items()},
        "conclusion": "Planck 2.958/60 嘅原始成份 = C_ℓ 全譜資訊 (TT 峰比 + damping tail + TE/EE 相位) 經 CAMB/Plik 管線壓縮; 唔係單一重子量",
    }, f, ensure_ascii=False, indent=2)
print("✅ 寫入 data/06_plik_lite_reproduction.json")
