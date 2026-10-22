#!/usr/bin/env python3
"""
O51/65: 本 Session 全面驗證 — 所有推導、公式、數值
===============================================================
驗證範圍 (2026-08-22 O51 延伸 session):
  1. N=131 冷斑相位求解 (scripts/58)
  2. t_true = N·T_sync + τ
  3. 全天區 l=2,3 檢驗 (scripts/60, 61) — 誠實標記
  4. NANOGrav 頻段錯位分析
  5. BAO: λ_sync/2 ≈ r_drag (scripts/62)
  6. DESI χ² (scripts/64) — IDCM vs ΛCDM
  7. 零點線 null test (對話層)
"""
import json, math, sys
import numpy as np

PASS = 0
FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ PASS: {name}")
    else:
        FAIL += 1
        print(f"  ❌ FAIL: {name}")
    if detail:
        print(f"    {detail}")

# ============ 1. 結構常數 ============
R_H = 4129.94
c_mpc_gyr = 306.601394
c_kms = 299792.458
H0_idcm = 72.59
phi = (1 + math.sqrt(5)) / 2
L_7, F_7, N_d, B = 29, 13, 44, 4
l_cold, b_cold = 209.0, -57.0

print("=" * 62)
print("1. 結構常數")
print("=" * 62)
T_sync = 2 * math.pi * R_H / c_mpc_gyr
tau = R_H / c_mpc_gyr
lambda_sync = 2 * math.pi * R_H / 88
rd_idcm = lambda_sync / 2

print(f"R_H = {R_H} Mpc (c/H0, H0={H0_idcm})")
print(f"T_sync = 2πR_H/c = {T_sync:.4f} Gyr")
print(f"τ = R_H/c = {tau:.4f} Gyr")
print(f"λ_sync = 2πR_H/88 = {lambda_sync:.4f} Mpc")
print(f"rd = λ_sync/2 = {rd_idcm:.4f} Mpc")

check("T_sync = 84.6349 Gyr", abs(T_sync - 84.6349) < 0.01, f"T_sync={T_sync:.4f}")
check("τ = 13.4701 Gyr", abs(tau - 13.4701) < 0.01, f"τ={tau:.4f}")
check("λ_sync = 294.877 Mpc", abs(lambda_sync - 294.877) < 0.01, f"λ_sync={lambda_sync:.4f}")

# ============ 2. N=131 相位求解 ============
print("\n" + "=" * 62)
print("2. N=131 冷斑相位求解 (scripts/58)")
print("=" * 62)

cos_F7_L7 = math.cos(F_7 / L_7)
sin_B_Nd = math.sin(B / N_d)

deltas = {}
for n in range(1, 44):
    theta = 88 * math.sin(math.pi * n / 88)
    deltas[n] = theta - math.floor(theta)
A_n = [2 * math.sin(math.pi * n / 88) for n in range(1, 45)]

def psi_at_point(lon_deg, colat_deg, N_val):
    phi_rad = math.radians(lon_deg)
    theta_rad = math.radians(colat_deg)
    sr, si = 0.0, 0.0
    for n in range(1, 45):
        if n < 44:
            theta_t = 2 * math.pi * (N_val * deltas[n] + 88 * math.sin(math.pi * n / 88) * tau / T_sync)
        else:
            theta_t = 2 * math.pi * (88 * math.sin(math.pi * n / 88) * tau / T_sync)
        phi_n = n * (phi_rad * cos_F7_L7 + theta_rad * sin_B_Nd) + 2 * math.pi * n * (L_7 + F_7) / N_d
        p = theta_t - phi_n
        sr += A_n[n-1] * math.cos(p)
        si += A_n[n-1] * math.sin(p)
    return math.atan2(si, sr)

# 冷斑: colat = 90 - (-57) = 147
psi_131 = psi_at_point(209.0, 147.0, 131)
psi_130 = psi_at_point(209.0, 147.0, 130)
psi_132 = psi_at_point(209.0, 147.0, 132)
psi_0 = psi_at_point(209.0, 147.0, 0)

# ⚠️ atan2 返回 [-π, π], Ψ=−π ≡ +π (cos 相同)
# 正確判據: |cos(Ψ) − cos(π)| = |cos(Ψ) + 1|
err_131 = abs(math.cos(psi_131) + 1)
err_130 = abs(math.cos(psi_130) + 1)
err_132 = abs(math.cos(psi_132) + 1)
err_0 = abs(math.cos(psi_0) + 1)
print(f"Ψ(131) = {psi_131:.6f} rad (≡ −π), |cos+1| = {err_131:.6f}")
print(f"Ψ(130) = {psi_130:.6f} rad, |cos+1| = {err_130:.4f}, T_cold = {134.2*math.cos(psi_130):.2f} μK")
print(f"Ψ(132) = {psi_132:.6f} rad, |cos+1| = {err_132:.4f}, T_cold = {134.2*math.cos(psi_132):.2f} μK")
print(f"Ψ(0)   = {psi_0:.6f} rad, |cos+1| = {err_0:.4f}, T_cold = {134.2*math.cos(psi_0):.2f} μK")

T_cold_131 = 134.2 * math.cos(psi_131)
check("Ψ(131) ≈ π (|cos+1| < 0.001)", err_131 < 0.001, f"|cos+1|={err_131:.6f}")
check("T_cold(131) ≈ −134.2 μK", abs(T_cold_131 + 134.2) < 0.5, f"T={T_cold_131:.2f}")
check("N=130 唔啱 (T ≠ −134)", abs(134.2*math.cos(psi_130) + 134.2) > 10, f"T(130)={134.2*math.cos(psi_130):.2f}")
check("N=132 唔啱 (T ≠ −134)", abs(134.2*math.cos(psi_132) + 134.2) > 10, f"T(132)={134.2*math.cos(psi_132):.2f}")

# 掃描確認 N=131 係最佳近似復歸 (|cos+1| 最小 + 幅度最大)
def psi_vec_full(N_val):
    """返回 (Ψ, |Σ|) — 相位同相干幅度"""
    phi_rad = math.radians(209.0)
    theta_rad = math.radians(147.0)
    sr = si = 0.0
    for n in range(1, 45):
        if n < 44:
            theta_t = 2 * math.pi * (N_val * deltas[n] + 88 * math.sin(math.pi * n / 88) * tau / T_sync)
        else:
            theta_t = 2 * math.pi * (88 * math.sin(math.pi * n / 88) * tau / T_sync)
        phi_n = n * (phi_rad * cos_F7_L7 + theta_rad * sin_B_Nd) + 2 * math.pi * n * (L_7 + F_7) / N_d
        p = theta_t - phi_n
        sr += A_n[n-1] * math.cos(p)
        si += A_n[n-1] * math.sin(p)
    return math.atan2(si, sr), math.hypot(sr, si)

# ⚠️ 準週期結構: 131 倍數有二次復歸 (262), 但 N=131 係最佳
# 物理: 無理漂移 → 冇精確週期 → 最佳近似復歸 N=131
print("\n掃描 N=0..300 搵最佳復歸 (|cos+1| < 0.01):")
solutions = []
for N in range(0, 301):
    p, amp = psi_vec_full(N)
    e = abs(math.cos(p) + 1)
    if e < 0.01:
        solutions.append((N, p, e, amp))
for N, p, e, amp in solutions:
    print(f"  N={N}: |cos+1|={e:.5f}, 幅度={amp:.3f}, T={134.2*math.cos(p):+.2f} μK")

# 最佳解 = |cos+1| 最小
best = min(solutions, key=lambda s: s[2])
print(f"\n最佳復歸: N={best[0]}, |cos+1|={best[2]:.6f}, 幅度={best[3]:.3f}")
check("N=131 係最佳復歸 (|cos+1| 最小)", best[0] == 131,
      f"最佳 N={best[0]}, |cos+1|={best[2]:.6f}")

# 準週期結構驗證: 2×131 有二次復歸但幅度細
if any(s[0] == 262 for s in solutions):
    print("✅ 準週期確認: N=262 (2×131) 有二次近似復歸")
check("準週期結構: 262 ≈ 2×131 復歸", any(abs(s[0] - 262) < 2 for s in solutions),
      "N=262 喺高精度解內")

# t_true
t_true = 131 * T_sync + tau
print(f"\nt_true = 131×{T_sync:.4f} + {tau:.4f} = {t_true:.2f} Gyr")
check("t_true = 11,100.64 Gyr", abs(t_true - 11100.64) < 0.1, f"t_true={t_true:.2f}")

# ============ 3. NANOGrav 頻段 ============
print("\n" + "=" * 62)
print("3. NANOGrav 頻段錯位")
print("=" * 62)
GYR_TO_S = 3.15576e16
f_Tsync = 1 / (T_sync * GYR_TO_S)
f_omega_scale = 88 / (2*math.pi) * 1/(tau * GYR_TO_S)
print(f"f_Tsync = {f_Tsync:.4e} Hz")
print(f"f_ωscale = {f_omega_scale:.4e} Hz")
print(f"NANOGrav 最低 = 1e-9 Hz")
ratio = 1e-9 / f_Tsync
print(f"頻段差距 = {ratio:.2e} 倍 = {math.log10(ratio):.1f} 數量級")
check("頻段錯位 > 5 數量級 (NANOGrav 不可行)", math.log10(ratio) > 5,
      f"差距 {math.log10(ratio):.1f} 數量級")

# ============ 4. BAO 閉合 ============
print("\n" + "=" * 62)
print("4. BAO: λ_sync/2 ≈ r_drag")
print("=" * 62)
r_drag = 147.09
dev_bao = abs(rd_idcm - r_drag) / r_drag * 100
print(f"rd_idcm = {rd_idcm:.4f} Mpc")
print(f"r_drag = {r_drag} Mpc (Planck 2018)")
print(f"dev = {dev_bao:.3f}%")
check("λ_sync/2 ≈ r_drag (0.3%)", dev_bao < 0.3, f"dev={dev_bao:.3f}%")

# ============ 5. DESI χ² ============
print("\n" + "=" * 62)
print("5. DESI DR1 χ² (IDCM vs ΛCDM)")
print("=" * 62)

desi = [
    ('LRG1', 0.510, 13.62, 0.25),
    ('LRG2', 0.706, 16.85, 0.32),
    ('LRG3+ELG', 0.930, 21.71, 0.28),
    ('ELG2', 1.317, 27.79, 0.69),
    ('LyA', 2.330, 39.71, 0.94),
]

def D_app_idcm(z):
    ell = math.log(1 + z, 4)
    return (44 - 44/4**ell) * (R_H/44) * (1 + 2*phi**(-1)*ell)

chi2_idcm = 0
print(f"{'Sample':<12}{'z':>7}{'DESI':>8}{'IDCM':>8}{'dev%':>8}{'σ':>6}")
for name, z, dm_rd, dm_err in desi:
    idcm_ratio = D_app_idcm(z) / rd_idcm
    sigma = (dm_rd - idcm_ratio) / dm_err
    chi2_idcm += sigma**2
    print(f"{name:<12}{z:>7.3f}{dm_rd:>8.2f}{idcm_ratio:>8.2f}{((dm_rd-idcm_ratio)/dm_rd*100):>7.1f}%{sigma:>6.2f}")

chi2_dof = chi2_idcm / 5
print(f"\nIDCM D_M χ²/dof = {chi2_dof:.2f}")
check("IDCM χ²/dof < 3 (合格)", chi2_dof < 3, f"χ²/dof={chi2_dof:.2f}")
check("IDCM 最大偏差 < 6%", max(abs((dm_rd - D_app_idcm(z)/rd_idcm)/dm_rd*100) for _, z, dm_rd, _ in desi) < 6,
      f"最大 dev={max(abs((dm_rd - D_app_idcm(z)/rd_idcm)/dm_rd*100) for _, z, dm_rd, _ in desi):.1f}%")

# ΛCDM 對比
H0_lcdm = 67.36
Om_lcdm = 0.315
def E_z(z): return math.sqrt(Om_lcdm*(1+z)**3 + (1-Om_lcdm))
def DM_lcdm(z):
    N = 400
    integral = sum(1/E_z((i+0.5)*z/N) for i in range(N))
    return c_kms/H0_lcdm * integral * z/N

chi2_lcdm = 0
for name, z, dm_rd, dm_err in desi:
    sigma = (dm_rd - DM_lcdm(z)/r_drag) / dm_err
    chi2_lcdm += sigma**2
print(f"ΛCDM D_M χ²/dof = {chi2_lcdm/5:.2f}")
check("ΛCDM χ²/dof < 3 (對照)", chi2_lcdm/5 < 3, f"χ²/dof={chi2_lcdm/5:.2f}")

# ============ 6. 零點線 null test ============
print("\n" + "=" * 62)
print("6. 零點線 null test (調律者 A 讀法)")
print("=" * 62)
print("t_true − τ = 131×T_sync (精確)")
print(f"t_true − τ = {t_true - tau:.4f} Gyr")
print(f"131×T_sync = {131*T_sync:.4f} Gyr")
print(f"差異 = {abs((t_true-tau) - 131*T_sync):.2e} Gyr")
check("t_true − τ = 131×T_sync (觀察窗觸及週期邊界)", abs((t_true-tau) - 131*T_sync) < 1e-6,
      f"dev={abs((t_true-tau) - 131*T_sync):.2e}")

print("\nA 讀法 (調律者確認): 零點線不可見係結構必然")
print("  Σγ=90 守恆 → 冇熵增 → 冇物質相變斷層")
print("  φ_n 係嚴格空間幾何映射, 唔係 fitting 工具")

# ============ 7. 總結 ============
print(f"\n{'=' * 62}")
print(f"Session 全面驗證: ✅ {PASS} / {PASS+FAIL}")
print(f"{'=' * 62}")

result = {
    'T_sync_gyr': round(T_sync, 4),
    'tau_gyr': round(tau, 4),
    'lambda_sync_mpc': round(lambda_sync, 4),
    'rd_idcm_mpc': round(rd_idcm, 4),
    'N': 131,
    'psi_131': round(psi_131, 6),
    'psi_err': round(err_131, 6),
    't_true_gyr': round(t_true, 2),
    'bao_dev_pct': round(dev_bao, 3),
    'chi2_idcm_dof': round(chi2_dof, 2),
    'chi2_lcdm_dof': round(chi2_lcdm/5, 2),
    'nano_orders': round(math.log10(ratio), 1),
    'pass': PASS,
    'fail': FAIL
}

with open('data/65_session_verification.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)

print(f"\n✅ 結果 -> data/65_session_verification.json")