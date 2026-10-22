#!/usr/bin/env python3
"""
O100-A (v2): BOSS DR12 全 k 範圍 P(k) 對照 — 正確 wiggle 方法
==============================================================
數據: Gil-Marín 2016 官方 (CMASS zeff=0.57 55 bins, LOWZ zeff=0.32 53 bins, k≤0.30)
方法 (v2, 與 sync_bump_analysis 同源): logP gaussian_filter1d(σ=3 bins) → wiggle=P/P_smooth−1
      → cubic 插值 500 點 → 再平滑 → 導數零點 → 峰位

三層判決:
  [1] wiggle 峰位 vs IDCM 9 線 (k_h = ℓ_m·0.00036 h/Mpc)
  [2] 形狀: IDCM 平滑線譜 × b² vs BOSS (k∈[0.05,0.30], 模型支援區)
  [3] σ8: 全範圍星系值 + b∈[1.7,2.2]×growth(z_eff→0) → 0.748 喺唔喺範圍內
"""
import json
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.interpolate import interp1d

WORK = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o100_cl_to_pk"
DATA = f"{WORK}/data/gilmarin16"
h = 0.6727
R8 = 8.0

def load_measurement(path):
    k, p, e = [], [], []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            try:
                kk, pp = float(parts[0]), float(parts[1])
                ee = float(parts[2]) if len(parts) > 2 else None
            except ValueError:
                continue
            k.append(kk); p.append(pp); e.append(ee)
    return np.array(k), np.array(p), np.array(e)

def find_wiggle_peaks(k, P, kmin=0.02, kmax=0.30, amp_thresh=0.004):
    """v2 方法: logP 平滑 → wiggle → 插值 → 導數零點"""
    logP = np.log(P)
    Ps = np.exp(gaussian_filter1d(logP, sigma=3, mode="nearest"))
    wig = P / Ps - 1
    k_fine = np.linspace(k.min(), k.max(), 500)
    wf = interp1d(k, wig, kind="cubic")(k_fine)
    ws = gaussian_filter1d(wf, sigma=2)
    dw = np.gradient(ws, k_fine)
    peaks = []
    for i in range(1, len(dw) - 1):
        if dw[i-1] > 0 >= dw[i] and ws[i] > amp_thresh:
            if kmin <= k_fine[i] <= kmax:
                peaks.append(float(k_fine[i]))
    return np.array(peaks), k_fine, ws

def top_hat(x):
    return 3 * (np.sin(x) - x * np.cos(x)) / x**3

def sigma8_int(k_arr, p_arr, klo, khi):
    m = (k_arr > klo) & (k_arr < khi)
    kk = k_arr[m]; pp = p_arr[m]
    x = kk * R8
    W = top_hat(x)
    integrand = kk**2 * pp * W**2 / (2 * np.pi**2)
    return np.sqrt(abs(np.trapezoid(integrand, kk)))

res = []
def fc(lbl, ok, dt=""):
    res.append({"label": lbl, "ok": bool(ok), "detail": str(dt)})
    print(("PASS" if ok else "FAIL") + " | " + lbl + (("  " + dt) if dt else ""))

# IDCM 線譜
lines = np.loadtxt(f"{WORK}/data/P3D_lines.dat")
k_h = lines[:, 3]; ell_m = lines[:, 0]
print(f"IDCM 線: ℓ={np.round(ell_m).astype(int).tolist()}")
print(f"         k_h = {np.round(k_h, 4).tolist()}")

# A. Δk_chain 預言 (半整數諧和): Δk = Δk_chain/2·h⁻¹?? — 用 v2 同款 dk_pred
R_world = 4129.64          # Mpc (c/H₀)
dk_chain = 88 / R_world    # Mpc⁻¹
dk_pred = dk_chain / h     # h/Mpc — 注意: Δk_chain = 88/R_world 喺 Mpc⁻¹ → /h
print(f"\nIDCM Δk_chain = {dk_chain:.5f} Mpc⁻¹ = {dk_pred:.5f} h/Mpc (半整數: 峰距 Δk_pred/2 = {dk_pred/2:.5f})")

results = {}
for name, fname, zeff in [
    ("CMASS", "post-recon/cmass/GilMarin_2016_CMASSDR12_measurement_monopole_post_recon.txt", 0.57),
    ("LOWZ",  "post-recon/lowz/GilMarin_2016_LOWZDR12_measurement_power_spectrum_monopole_post_recon.txt", 0.32),
]:
    k, P, e = load_measurement(f"{DATA}/{fname}")
    print(f"\n{'='*62}\n{name} (zeff={zeff}): {len(k)} bins, k∈[{k.min():.4f}, {k.max():.3f}]\n{'='*62}")

    # [1] wiggle 峰位
    peaks, kf, ws = find_wiggle_peaks(k, P)
    print(f"wiggle 峰位 ({len(peaks)}): " + ", ".join(f"{p:.4f}" for p in peaks))
    # dip (負極值) 都列
    dips = []
    dw = np.gradient(gaussian_filter1d(interp1d(k, P/np.exp(gaussian_filter1d(np.log(P), sigma=3, mode='nearest')) - 1, kind='cubic')(kf), sigma=2), kf)
    ws2 = gaussian_filter1d(interp1d(k, P/np.exp(gaussian_filter1d(np.log(P), sigma=3, mode='nearest')) - 1, kind='cubic')(kf), sigma=2)
    for i in range(1, len(dw) - 1):
        if dw[i-1] < 0 <= dw[i] and ws2[i] < -0.004 and 0.02 <= kf[i] <= 0.30:
            dips.append(float(kf[i]))
    print(f"wiggle dip ({len(dips)}): " + ", ".join(f"{p:.4f}" for p in dips))

    # IDCM 線 vs 峰: |Δ|/k < 0.08
    matches = []
    for i, kl in enumerate(k_h):
        if kl > 0.31:
            continue
        best = None
        for p_pos in list(peaks) + dips:
            if abs(kl - p_pos) / p_pos < 0.08:
                if best is None or abs(kl - p_pos) < abs(kl - best):
                    best = p_pos
        if best is not None:
            matches.append((i + 1, kl, best, 100 * (kl - best) / best))
            print(f"  線{i+1} k={kl:.4f} ↔ wiggle {'峰' if min([abs(kl-p) for p in peaks], default=9) < min([abs(kl-d) for d in dips], default=9) else 'dip'}@{best:.4f} (Δ={100*(kl-best)/best:+.1f}%)")
        else:
            print(f"  線{i+1} k={kl:.4f} ↔ 無近距極值")
    results[name] = {"peaks": peaks.tolist(), "dips": dips, "matches": matches}

    # [2] 形狀 (bias 擬合, k∈[0.05,0.30])
    ks = np.linspace(0.01, 0.32, 700)
    P_sm = np.zeros_like(ks)
    P_id_h = lines[:, 6] / h**3
    for kk, dd in zip(k_h, P_id_h):
        P_sm += dd * np.exp(-0.5 * ((ks - kk) / 0.02) ** 2)
    mask = (k > 0.05) & (k < 0.30)
    kk = k[mask]; pp = P[mask]
    P_int = np.interp(kk, ks, P_sm)
    ok = np.isfinite(P_int) & (P_int > 0) & (pp > 0)
    b2 = np.median(pp[ok] / P_int[ok])
    ratio = pp[ok] / (b2 * P_int[ok])
    rms_log = np.std(np.log(ratio))
    wins = []
    for lo, hi in [(0.05, 0.12), (0.12, 0.20), (0.20, 0.30)]:
        m2 = (kk[ok] >= lo) & (kk[ok] < hi)
        wins.append([lo, hi, float(np.median(ratio[m2])), int(m2.sum())] if m2.sum() else [lo, hi, None, 0])
        print(f"    k∈[{lo},{hi}]: median={np.median(ratio[m2]):.2f} (n={m2.sum()})" if m2.sum() else f"    k∈[{lo},{hi}]: 無點")
    print(f"   b² = {b2:.2f}   rms(log) = {rms_log:.3f}")
    results[name]["shape"] = {"b2": float(b2), "rms_log": float(rms_log), "windows": wins}
    fc(f"形狀 {name}: k∈[0.05,0.30] rms(log)<0.40", rms_log < 0.40, f"b²={b2:.2f} rms={rms_log:.3f}")

    # [3] σ8
    s8_full = sigma8_int(k, P, 0.0015, 0.30)
    s8_trunc = sigma8_int(k, P, 0.0159, 0.145)
    print(f"   σ8,gal(全範圍 0.0015–0.30) = {s8_full:.3f}")
    print(f"   σ8,gal(截斷 0.0159–0.145) = {s8_trunc:.3f}   [O99/13 參考 0.783]")
    growth = 1.32  # D(0)/D(z_eff≈0.57), Ωm=0.31 — standard
    lo = s8_full / 2.2 * growth
    hi = s8_full / 1.7 * growth
    print(f"   σ8,matter(0) = σ8,gal/b×growth: b∈[1.7,2.2] → [{lo:.3f}, {hi:.3f}]")
    results[name]["sigma8"] = {"full": float(s8_full), "trunc": float(s8_trunc),
                               "matter_range": [float(lo), float(hi)]}
    fc(f"σ8 {name}: 0.748 ∈ b/growth 範圍", lo <= 0.748 <= hi, f"[{lo:.3f}, {hi:.3f}]")

n_hit = sum(1 for n in results.values() for m in n["matches"])
print(f"\n─── 總結 ───")
print(f"線譜命中: {n_hit} 條 (共 3 條 k≤0.31)")
npass = sum(1 for c in res if c["ok"])
print(f"判決: {npass}/{len(res)} PASS")
with open(f"{WORK}/data/04_boss_gm16_v2.json", "w") as f:
    json.dump({"results": results, "checks": res}, f, indent=2, default=str)
print("寫入 data/04_boss_gm16_v2.json")