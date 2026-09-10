"""
O164 P1 — K_Chain 頻率階梯嘅譜身份 (Spectral Identity of the Frequency Ladder)
============================================================================
問題: K_chain 頻率 ~1e-17 Hz 點解係呢個值? 基頻 = f(88, N_d, γ_max)?

核心宣稱 (全部精確代數身份, 高精度 mpmath 驗證):
  C1. omega_scale = 88c/R_world = 88·omega_ring        (O40)
  C2. omega_n     = omega_scale·sin(pi·n/88)           (kchain_wave_params.py)
  C3. omega_n     = N_d·omega_ring·sqrt(gamma_n)       ★ 頻率 = 44 × 環角頻率 × 譜振幅
       (sqrt(gamma_n) = 2sin(pi·n/88), gamma_n = 4sin^2(pi·n/88))
  C4. f_n         = (c/2·lambda_sync)·sqrt(gamma_n)    ★ 頻率階梯 = 譜 × (c/2·lambda_sync)
  C5. f_44        = 88·f_ring = c/lambda_sync           Nyquist 模 = 同步波長頻率 ("1e-17 Hz")
  C6. f_1         = (omega_ring/2)·sinc(pi/88)         基頻 ≈ 半環角頻率 (dev 0.02%)
  C7. T_1         = 2/omega_ring = 2R_world/c = 26.94 Gyr  基頻周期 = 世界直徑光穿越時間
  C8. T_1/2       = R_world/c = 13.47 Gyr                   半周期 = 半徑光穿越 (vs ΛCDM 年齡, P2)
"""
import math
from mpmath import mp, mpf, sin, cos, pi, sqrt

mp.dps = 60

# ---- 基本常數 (src/kchain_wave_params.py 一致) ----
R_world = mpf('4129.94')          # Mpc
Nd      = 44
c       = mpf('299792.458')       # km/s
omega_ring_km = mpf('72.59')      # (km/s)/Mpc  — 儲存值 (O73)
Mpc_to_km = mpf('3.085677581e19')
Gyr_s   = mpf('3.15576e16')       # s/Gyr

# ---- 導出 ----
omega_ring = omega_ring_km / Mpc_to_km                 # rad/s (儲存值)
c_over_R   = c / (R_world * Mpc_to_km)                 # s^-1 = c/R_world (幾何值)
omega_scale  = 88 * c / (R_world * Mpc_to_km)          # rad/s
f_ring    = omega_ring / (2*pi)
L_ring    = 2 * pi * R_world
lambda_sync = L_ring / 88
T_ring    = L_ring / c * Mpc_to_km / Gyr_s             # Gyr

print("=" * 72)
print("O164 P1 — 頻率階梯譜身份 (mpmath 60 位)")
print("=" * 72)
print(f"omega_ring (儲存) = {float(omega_ring):.6e} rad/s")
print(f"c/R_world  (幾何) = {float(c_over_R):.6e} s^-1  [rounding dev {float(abs(c_over_R/omega_ring-1))*100:.4f}%]")
print(f"T_ring            = {float(T_ring):.4f} Gyr")
print(f"lambda_sync       = {float(lambda_sync):.4f} Mpc")
print()

results = []
def check(name, cond, info=""):
    results.append((name, cond))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {info}")

# C1: omega_scale = 88·omega_ring (代數構造: omega_scale = 88c/R_world; omega_ring = c/R_world 幾何)
ws_geom = 88 * c_over_R
check("C1 omega_scale = 88·omega_ring (幾何值)", abs(ws_geom/omega_ring - 88) < mpf('1e-4'),
      f"|ratio-88| = {float(abs(ws_geom/omega_ring - 88)):.3e} (stored rounding)")

# C2-C3: omega_n = N_d·omega_ring·sqrt(gamma_n) — 44/44 精確
maxdev = mpf(0)
for n in range(1, Nd+1):
    gamma_n = 4 * sin(pi*n/88)**2
    w_n_scale = omega_scale * sin(pi*n/88)
    w_n_ident = Nd * omega_ring * sqrt(gamma_n)     # 幾何值版本
    w_n_ident2 = Nd * c_over_R * sqrt(gamma_n)
    d = abs(w_n_ident2 / w_n_scale - 1)
    if d > maxdev: maxdev = d
check("C2/C3 omega_n = N_d·omega_ring·sqrt(gamma_n) (44/44)", maxdev < mpf('1e-12'),
      f"max dev = {float(maxdev):.2e}")

# C4: f_n = (c/2·lambda_sync)·sqrt(gamma_n)
maxdev = mpf(0)
c_2ls = c / (2 * lambda_sync * Mpc_to_km)     # km/s ÷ km = s^-1 = Hz
for n in range(1, Nd+1):
    gamma_n = 4 * sin(pi*n/88)**2
    f_n = omega_scale * sin(pi*n/88) / (2*pi)        # Hz
    f_n_id = c_2ls * sqrt(gamma_n)
    d = abs(f_n_id/f_n - 1)
    if d > maxdev: maxdev = d
check("C4 f_n = (c/2·lambda_sync)·sqrt(gamma_n) (44/44)", maxdev < mpf('1e-12'),
      f"max dev = {float(maxdev):.2e}")

# C5: f_44 = 88·f_ring = c/lambda_sync
f_44 = omega_scale * sin(pi*44/88) / (2*pi)
f_44b = 88 * f_ring
c_ls = c / (lambda_sync * Mpc_to_km)               # km/s ÷ km = s^-1 = Hz
check("C5a f_44 = 88·f_ring", abs(f_44/f_44b - 1) < mpf('1e-6'),
      f"dev = {float(abs(f_44/f_44b-1)*100):.5f}% (stored rounding)")
check("C5b f_44 = c/lambda_sync", abs(f_44/c_ls - 1) < mpf('1e-12'),
      f"dev = {float(abs(f_44/c_ls-1)):.2e}")

# C6: f_1 = (omega_ring/2)·sinc(pi/88)
f_1 = omega_scale * sin(pi*1/88) / (2*pi)
sinc88 = sin(pi/88) / (pi/88)
f_1_id = (omega_ring/2) * sinc88
check("C6 f_1 = (omega_ring/2)·sinc(pi/88)", abs(f_1/f_1_id - 1) < mpf('1e-6'),
      f"dev = {float(abs(f_1/f_1_id-1)*100):.4f}% | sinc = {float(sinc88):.8f}")

# C7: T_1 = 2/(omega_ring·sinc(pi/88)) — 精確 (幾何值); T_1 ≈ 2/omega_ring (dev 0.021% = sinc 修正)
T_1 = 1/f_1 / Gyr_s
T_1_id = 2 / (c_over_R * sinc88) / Gyr_s
check("C7 T_1 = 2/(omega_ring·sinc(pi/88)) [幾何]", abs(T_1/T_1_id - 1) < mpf('1e-12'),
      f"T_1 = {float(T_1):.4f} Gyr | 2/omega_ring = {float(2/omega_ring/Gyr_s):.4f} Gyr (sinc dev {float(T_1*Gyr_s/(2/omega_ring)-1)*100:.3f}%)")
print()

print("=" * 72)
print("頻率標度階梯 (世界 = 拍子)")
print("=" * 72)
print(f"{'量':<28}{'值 (Hz)':>14}{'周期 (Gyr)':>14}{'身份':>22}")
rows = [
    ("f_ring (環頻率)",        f_ring,            T_ring,    "omega_ring/2pi"),
    ("f_1 (基頻模)",           f_1,               T_1,       "~omega_ring/2"),
    ("f_22 (中階梯)",          omega_scale*sin(pi*22/88)/(2*pi), 0, "c/(√2·lambda_sync)"),
    ("f_44 (Nyquist/標度)",    f_44,              0,         "c/lambda_sync"),
    ("f_scale = 88·f_ring",    88*f_ring,         0,         "88·omega_ring/2pi"),
]
for name, f, T, ident in rows:
    if T > 0:
        print(f"{name:<28}{float(f):>14.4e}{float(T):>14.4f}{ident:>22}")
    else:
        print(f"{name:<28}{float(f):>14.4e}{'—':>14}{ident:>22}")

print()
print(f"f_scale = 88·f_ring = {float(88*f_ring):.4e} Hz  ← 問題陳述嘅 '~1e-17 Hz'")
print(f"f_1     = {float(f_1):.4e} Hz  ← 基頻 = omega_ring/2·sinc")
print(f"omega_ring = {float(omega_ring):.4e} rad/s (= c/R_world, 舊讀法 'H₀')")
print()
print("PASS/FAIL 摘要:")
npass = sum(1 for _, c in results if c)
print(f"  {npass}/{len(results)} PASS")

# 額外: 88-site 對偶鏈版本 (k=1..88) 嘅 Nyquist 一致性
gamma_max88 = 4 * sin(pi*88/176)**2   # = 4 = B
f_scale_alt = Nd * f_ring * sqrt(gamma_max88)   # N_d·f_ring·√γ_max
print(f"\n檢查: f_scale = N_d·f_ring·√γ_max = 44·f_ring·2 = 88·f_ring:")
print(f"  N_d·f_ring·sqrt(gamma_max) = {float(f_scale_alt):.4e} Hz vs 88·f_ring = {float(88*f_ring):.4e} Hz")
print(f"  gamma_max (Nyquist, k=88) = {float(gamma_max88)} = B ✓")
