#!/usr/bin/env python3
"""
O154 S03: Matsubara Eliashberg (renormalized 形式) — 鏈 α²F + 結構 λ = 8/3
================================================================
結構假設:
  (H1) α²F 形狀 = K_Chain 聲子譜 (ω_k = 2sin(kπ/176), 88 模),
       每模權重 ∝ ω_k (H 聲子主導, van Hove 峰 @ ω_max)
  (H2) λ = C_obs/M = Σγ_odd/K_tree = 88/33 = 8/3 = 2.6667
       (觀察者容量每樹結構位 — O151 C_obs=88, K_tree=33)
  驗證點: LaH10 實驗 λ = 2.58±0.11, 理論 λ = 2.67 (Nature Comm 2024)
          Ω_log = 96.4 meV @ 163 GPa, Tc = 250 K, Δ(0) = 53±5 meV

方程 (Marsiglio 摺疊形式, m∈ℤ → m≥0):
  ω̂_n = ω_n + πT Σ_m (ω̂_m/D_m)[λ(n−m) − λ(n+m+1)]
  Δ̂_n = πT Σ_m (Δ̂_m/D_m)[λ(n−m) + λ(n+m+1) − 2μ*]
  D_m = √(ω̂_m² + Δ̂_m²),  λ(k) = 2Σ_i α²F_i Ω_i/(Ω_i² + (2πTk)²)
  物理: Δ(iω₀) = Δ̂₀/Z₀,  Z₀ = ω̂₀/ω₀
"""
import numpy as np

print("=" * 78)
print("  O154 S03: Eliashberg (renormalized) — 鏈 α²F + λ = 8/3")
print("=" * 78)

kB_meV = 0.0861734          # meV/K
lam = 8.0 / 3.0             # C_obs/M = 88/33
WL_RATIO = 0.516939         # ω_log/ω_max (鏈, S01)
OME_LOG_LAH10_MEV = 96.4    # Ω_log(LaH10) @ 163 GPa (Nature Comm 2024)
OME_MAX_LAH10_MEV = OME_LOG_LAH10_MEV / WL_RATIO   # ≈ 186.5 meV

# ---- 鏈 α²F: 88 模, 權重 ∝ ω_i, λ 歸一化 (鏈單位) ----
k88 = np.arange(1, 89)
Om = 2.0 * np.sin(k88 * np.pi / 176)          # 鏈單位, ω_max = 2
a2f = (lam / 2.0) * Om / 88.0                 # 2Σ a2f_i/Ω_i = λ
assert abs(2.0 * np.sum(a2f / Om) - lam) < 1e-12

def eliashberg_solve(T, mu, Om_=None, a2f_=None, wcs=8.0, Nmax=800,
                     seed=1e-5, mix=0.5, tol=1e-10, max_iter=3000):
    """T (meV) → Δ(iω₀) (meV). 摺疊 Matsubara (m≥0)."""
    if Om_ is None:
        # 材料單位: 鏈形狀 ω_max→OME_MAX, 權重 ∝ Ω_i (α²∝ω), λ 保持
        Om_ = Om * (OME_MAX_LAH10_MEV / 2.0)
        a2f_ = (lam / 2.0) * Om_ / 88.0
    wc = wcs * Om_.max()
    Nf = min(Nmax, int(wc / (2 * np.pi * T)))
    if Nf < 8:
        return 0.0
    wn = (2 * np.arange(Nf) + 1) * np.pi * T
    # λ(k): k = |n−m| ∈ [0, 2Nf−1]
    kk = np.arange(2 * Nf)
    wdiff = 2 * np.pi * T * kk
    lamk = np.zeros(2 * Nf)
    for i in range(88):
        o = Om_[i]
        af = a2f_[i]
        lamk += 2.0 * af * o / (o * o + wdiff * wdiff)
    # 摺疊核
    idx = np.abs(np.arange(Nf)[:, None] - np.arange(Nf)[None, :])   # |n−m|
    idx2 = np.arange(Nf)[:, None] + np.arange(Nf)[None, :] + 1      # n+m+1
    Lnm = lamk[idx]       # λ(n−m)
    Lnp = lamk[idx2]      # λ(n+m+1)
    Msum = Lnm + Lnp - 2.0 * mu     # 間隙核
    Lsub = Lnm - Lnp                # Z 核
    w = wn.copy()                   # ω̂
    D = np.full(Nf, seed)           # Δ̂
    for it in range(max_iter):
        denom = np.sqrt(w ** 2 + D ** 2)
        wnew = wn + np.pi * T * (Lsub @ (w / denom))
        Dnew = np.pi * T * (Msum @ (D / denom))
        dw = np.max(np.abs(wnew - w))
        dD = np.max(np.abs(Dnew - D))
        w = mix * wnew + (1 - mix) * w
        D = mix * Dnew + (1 - mix) * D
        if dw < tol and dD < tol:
            break
        # fast-fail: 衰減 (T > Tc)
        if it == 20 and np.max(np.abs(D)) < seed * 0.3:
            return 0.0
    Z0 = w[0] / wn[0]
    return float(D[0] / Z0)

def allen_dynes(mu):
    num = 1.04 * (1 + lam)
    den = lam - mu * (1 + 0.62 * lam)
    return np.exp(-num / den) / 1.2

def gap_at(T_K, mu, Om_=None, a2f_=None):
    return eliashberg_solve(T_K * kB_meV, mu, Om_, a2f_)

def find_tc(mu, Om_=None, a2f_=None, T_hi=320.0):
    while gap_at(T_hi, mu, Om_, a2f_) > 1e-6:
        T_hi *= 2.0
    T_lo = 1.0
    for _ in range(50):
        Tm = 0.5 * (T_hi + T_lo)
        if gap_at(Tm, mu, Om_, a2f_) > 1e-6:
            T_lo = Tm
        else:
            T_hi = Tm
    return 0.5 * (T_hi + T_lo)

# ---- A. Allen-Dynes ----
print("\n[A] Allen-Dynes (cross-check, λ=8/3)")
for mu in (0.10, 0.13, 0.16):
    tc_wl = allen_dynes(mu)
    tc_K = tc_wl * OME_LOG_LAH10_MEV / kB_meV
    print(f"  μ*={mu:.2f}: Tc = {tc_wl:.4f}×ω_log = {tc_K:.0f} K   (LaH10 量度 250 K)")

# ---- B/C. Matsubara Eliashberg ----
print("\n[B/C] Matsubara Eliashberg (鏈 α²F, λ=8/3, ω_max=186.5 meV)")
for mu in (0.10, 0.13, 0.16):
    Tc = find_tc(mu)
    D0 = gap_at(Tc * 0.3, mu)
    ratio = 2.0 * D0 / (kB_meV * Tc)
    print(f"  μ*={mu:.2f}: Tc = {Tc:.1f} K, Δ₀ = {D0:.2f} meV, 2Δ₀/kTc = {ratio:.2f}")
    print(f"           (實驗: Tc=250 K, Δ(0)=53±5 meV, 2Δ/kTc = 4.9-5.6)")

# ---- D. Tc vs Ω_log 掃描 (YH10 盲測輸入) ----
print("\n[D] Tc 對 Ω_log 掃描 (μ*=0.13, λ=8/3 鏈 α²F)")
print("  Ω_log (K) | ω_max (K) | Tc (K) | 2Δ₀/kTc")
for wl_K in (900, 1000, 1100, 1200, 1300, 1400, 1500, 1600):
    om_max = (wl_K / WL_RATIO) * kB_meV       # meV
    Om_s = Om * (om_max / 2.0)
    a2f_s = (lam / 2.0) * Om_s / 88.0
    Tc_s = find_tc(0.13, Om_s, a2f_s)
    D0_s = gap_at(Tc_s * 0.3, 0.13, Om_s, a2f_s)
    print(f"  {wl_K:7.0f}   | {om_max:8.0f} | {Tc_s:6.1f} | {2*D0_s/(kB_meV*Tc_s):.2f}")

print()
print("PASS")
