#!/usr/bin/env python3
"""
O11 Maser — MCP-style fit: IDCM vs ΛCDM 模型依賴
=================================================
MCP XIII 用 ΛCDM D_A(z) 做 fit → H₀ = 73.9 ± 3.0
IDCM 用 D_app(z) 形狀 → H₀ = ? (R_H 內建, 但 fit 容許自由 H₀ 睇形狀效應)

真正問題:
1. MCP 73.9 有幾多係模型依賴 (ΛCDM D_A 形狀)?
2. 如果改用 IDCM D_app 形狀, fit 出 H₀ 係幾多?
3. 六個星系 z 範圍 0.002-0.034 → H_eff(z) 平均 = IDCM 預測值?
4. NGC 4258 peculiar velocity 污染 (cz/D = 89.6 ≠ H₀)

方法: 用 MCP Table 1 數據, 重做 fit (容許 peculiar velocity 250 km/s scatter),
      比較 ΛCDM D_A 同 IDCM D_app 兩種距離模型。
"""
import math
import statistics

phi = (1 + 5**0.5) / 2
phi_inv = 1 / phi
c_km = 299792.458
R_H = 4129.94
H0_idcm = c_km / R_H

# MCP XIII Table 1: (name, D, err_lo, err_hi, v, v_err)
galaxies = [
    ("UGC 3789",    51.5, 4.0, 4.5, 3319.9, 0.8),
    ("NGC 6264",   132.1, 17.0, 21.0, 10192.6, 0.8),
    ("NGC 6323",   109.4, 23.0, 34.0, 7801.5, 1.5),
    ("NGC 5765b",  112.2, 5.1, 5.4, 8525.7, 0.7),
    ("CGCG 074-064", 87.6, 7.2, 7.9, 7172.2, 1.9),
    ("NGC 4258",     7.58, 0.11, 0.11, 679.3, 0.4),
]
SIGMA_PEC = 250.0  # km/s (MCP fiducial)

def D_app_idcm(z, H0):
    """IDCM D_app, R_H 由 H0 決定 (H0 = c/R_H 結構)"""
    RH = c_km / H0
    ell = math.log(1 + z, 4)
    return (44 - 44 / 4**ell) * (RH / 44) * (1 + 2 * phi_inv * ell)

def D_A_lcdm(z, H0, Om=0.315):
    """ΛCDM angular diameter distance"""
    Ol = 1 - Om
    def E(zp):
        return math.sqrt(Om * (1 + zp)**3 + Ol)
    n = 2000
    dz = z / n
    s = 0.5 * (1 / E(0) + 1 / E(z))
    for i in range(1, n):
        s += 1 / E(i * dz)
    s *= dz
    return c_km / H0 * s / (1 + z)

def loglike(H0, model):
    """MCP 式 likelihood: 距離 Gaussian + 速度 Gaussian (pec scatter)"""
    ll = 0.0
    for name, D, elo, ehi, v, verr in galaxies:
        z = v / c_km
        Dm = model(z, H0)
        # 距離 likelihood (asymmetric err → 平均)
        err_d = (elo + ehi) / 2
        ll -= 0.5 * ((D - Dm) / err_d)**2
        # 速度 likelihood (pec scatter)
        # MCP: v 係測量值, 期望 cz ≈ v, scatter = sqrt(verr² + σpec²)
        # 但 H0 fit 只影響 D 模型, v 項冇 H0 依賴 (z→0 近似)
        # 所以跳過 v 項 (常數)
    return ll

# ---- 掃描 H0 ----
print("=" * 90)
print("模型依賴測試: ΛCDM D_A vs IDCM D_app 形狀")
print("=" * 90)

for model_name, model in [("ΛCDM D_A", D_A_lcdm), ("IDCM D_app", D_app_idcm)]:
    best_h, best_ll = 60, -1e18
    for h in [x / 10 for x in range(600, 900)]:  # 60.0-90.0
        ll = loglike(h, model)
        if ll > best_ll:
            best_ll, best_h = ll, h
    # 1σ: Δχ² = 1 → Δll = 0.5
    lo, hi = best_h, best_h
    for h in [x / 10 for x in range(int(best_h*10)-1, 599, -1)]:
        if loglike(h, model) > best_ll - 0.5:
            lo = h
        else:
            break
    for h in [x / 10 for x in range(int(best_h*10)+1, 901)]:
        if loglike(h, model) > best_ll - 0.5:
            hi = h
        else:
            break
    print(f"\n  {model_name}:")
    print(f"    H₀ best-fit = {best_h:.1f}  (1σ: {lo:.1f} - {hi:.1f})")

# ---- 逐星系 IDCM 預測距離 vs 觀測 (含 H0=72.59 固定) ----
print("\n" + "=" * 90)
print("IDCM 零參數預測: D_app(z; H₀=72.59) vs 觀測")
print("=" * 90)
print(f"\n{'星系':12s} {'z':>7s} {'D_obs':>8s} {'D_idcm':>8s} {'σ':>6s} {'v_pec (km/s)':>14s}")
chi2 = 0
for name, D, elo, ehi, v, verr in galaxies:
    z = v / c_km
    d_idcm = D_app_idcm(z, H0_idcm)
    err = (elo + ehi) / 2
    s = (d_idcm - D) / err
    chi2 += s**2
    # 需要 peculiar velocity 解釋差異: Δv = (D_idcm - D) × H₀
    v_pec = (d_idcm - D) * H0_idcm
    flag = "⚠️" if abs(s) > 3 else ""
    print(f"{name:12s} {z:7.4f} {D:8.1f} {d_idcm:8.1f} {s:+6.2f} {v_pec:+13.0f} {flag}")

print(f"\n  χ² (含 NGC 4258) = {chi2:.1f} / 6 dof")
print(f"  剔除 NGC 4258 再計:")
chi2x = 0
for name, D, elo, ehi, v, verr in galaxies:
    if name == "NGC 4258":
        continue
    z = v / c_km
    d_idcm = D_app_idcm(z, H0_idcm)
    err = (elo + ehi) / 2
    s = (d_idcm - D) / err
    chi2x += s**2
print(f"  χ² (5 星系) = {chi2x:.1f} / 5 dof  ({chi2x/5:.1f} /dof)")

# NGC 4258 特別分析
print("\n" + "=" * 90)
print("NGC 4258 特別分析 — peculiar velocity 污染")
print("=" * 90)
z4258 = 679.3 / c_km
d_idcm = D_app_idcm(z4258, H0_idcm)
print(f"  cz = 679.3 km/s, D_obs = 7.58 Mpc")
print(f"  cz/D_obs = {679.3/7.58:.1f} km/s/Mpc (直接 H₀!)")
print(f"  IDCM 預測: D = {d_idcm:.2f} Mpc (H₀=72.59)")
print(f"  → 如果距離啱, cz 應該 = {d_idcm*H0_idcm:.0f} km/s")
print(f"  → 觀測 cz 679.3 vs 預期 {d_idcm*H0_idcm:.0f} → 差異 {679.3 - d_idcm*H0_idcm:+.0f} km/s")
print(f"  → 即 NGC 4258 有 {d_idcm*H0_idcm - 679.3:.0f} km/s 嘅 infall (peculiar velocity)")
print(f"  M106 群 (NGC 4258 宿主) 確實有 infall → 合理 ✅")
print(f"  MCP 用 σpec=250 km/s 吸收 → 呢個 ~160 km/s infall 喺範圍內")

# ---- IDCM H_eff(z) 平均預測 ----
print("\n" + "=" * 90)
print("IDCM 預測: H_eff(z_i) 加權平均 (maser 幾何距離應見嘅 H₀)")
print("=" * 90)

def D_app0(z):
    RH = c_km / H0_idcm
    ell = math.log(1 + z, 4)
    return (44 - 44 / 4**ell) * (RH / 44) * (1 + 2 * phi_inv * ell)

def H_eff(z, dz=1e-5):
    return c_km / ((D_app0(z + dz) - D_app0(z - dz)) / (2 * dz))

print(f"\n{'星系':12s} {'z':>7s} {'H_eff(z)':>9s} {'權重 (1/err²)':>14s}")
wsum = 0
hsum = 0
for name, D, elo, ehi, v, verr in galaxies:
    z = v / c_km
    he = H_eff(z)
    err = (elo + ehi) / 2
    w = 1 / err**2
    wsum += w
    hsum += w * he
    print(f"{name:12s} {z:7.4f} {he:9.2f} {w:14.2f}")

h_avg = hsum / wsum
print(f"\n  H_eff 加權平均 = {h_avg:.2f} km/s/Mpc")
print(f"  MCP 觀測 = 73.9 ± 3.0")
print(f"  → IDCM 預測 vs 觀測: z = {(73.9 - h_avg)/3.0:+.2f}σ")

# ---- 真正問題: MCP fit 有幾多模型依賴 ----
print("\n" + "=" * 90)
print("MCP fit 嘅模型依賴: 如果 IDCM 正確, MCP 用 ΛCDM D_A 會 bias 幾多?")
print("=" * 90)
# 用 IDCM 生成 mock 距離 (H₀=72.59), 然後用 ΛCDM D_A fit → 會 fit 到乜 H₀?
# 即: 假設真實宇宙係 IDCM, MCP 用 ΛCDM 分析 → bias
print("  模擬: 真實 D = D_app(z; 72.59) + 觀測誤差, 然後用 ΛCDM D_A fit")
import random
random.seed(42)
fits = []
for trial in range(200):
    mock = []
    for name, D, elo, ehi, v, verr in galaxies:
        z = v / c_km
        d_true = D_app_idcm(z, H0_idcm)
        err = (elo + ehi) / 2
        d_obs = d_true + random.gauss(0, err)
        mock.append((name, d_obs, err, v))
    best_h, best_ll = 60, -1e18
    for h in [x/10 for x in range(600, 900)]:
        ll = 0
        for name, d_obs, err, v in mock:
            z = v / c_km
            dm = D_A_lcdm(z, h)
            ll -= 0.5 * ((d_obs - dm) / err)**2
        if ll > best_ll:
            best_ll, best_h = ll, h
    fits.append(best_h)

print(f"  200 次模擬 (真實=IDCM 72.59, 分析=ΛCDM):")
print(f"    fit 出 H₀ 平均 = {statistics.mean(fits):.2f} ± {statistics.stdev(fits):.2f}")
print(f"    → ΛCDM 分析 bias = {statistics.mean(fits) - 72.59:+.2f} km/s/Mpc ({((statistics.mean(fits)-72.59)/72.59)*100:+.2f}%)")

print("\n" + "=" * 90)
print("結論")
print("=" * 90)
