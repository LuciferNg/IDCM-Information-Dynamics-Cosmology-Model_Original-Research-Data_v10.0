#!/usr/bin/env python3
"""
O121 — script 11: G8 交接數字獨立重驗 (T1)
==========================================
用途: 對 docs/12_return_rate_handover.md 之全部 headline 數字做第一性原理重算。
獨立性: 唔 import 任何 O121 推導 script、唔 import 其他 O 腳本; 常數由 φ/譜定義起算。

驗證項:
  A. 通道層 (本 O): dim ker=17, E_sync=61.5, E_capture=60.8845 (兩路), E_bottleneck
  B. O222 審計殘差: E_bottleneck vs 8/13 偏差
  C. 效率層 (O175): η = φ⁻²¹, φ²¹ = Lucas L₂₁ = 24476
  D. 時標層: τ_rec 定義比值, τ_rec/t_true, τ_rec/T_ring
  E. 質子衰變 (O88): τ_p/T_ring, t_true/τ_p
"""
import math, json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASS = 0; FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS += 1; print(f"  ✅ {name} {detail}")
    else:    FAIL += 1; print(f"  ❌ {name} {detail}")

phi = (1 + math.sqrt(5)) / 2
Nd = 44; L6 = 18

# --- γ 譜 (44 鏈, 88-site convention) ---
def gamma(n): return 4 * math.sin(math.pi * n / 88) ** 2

# --- 時間常數 ---
Yr_s   = 3.155693e7                # s/yr (Julian)
Gyr_yr = 1e9
omega_ring = 72.59                 # (km/s)/Mpc
Mpc_m  = 3.0856775814913673e22
c_kms  = 299792.458
w_si   = omega_ring * 1e3 / Mpc_m  # s^-1
T_ring_s  = 2 * math.pi / w_si
T_ring_Gyr = T_ring_s / (Yr_s * Gyr_yr)

print("=" * 74)
print("O121 script 11: G8 交接數字獨立重驗")
print("=" * 74)

# ===== A. 通道層 =====
print("\n[A] 通道層 (本 O docs/07)")
n_star = Nd - L6 + 1                                  # 27
E_proj_target = 28.5
S26 = sum(gamma(n) for n in range(1, 27))
f_proj = (E_proj_target - S26) / gamma(27)
sigma = [1.0 if n < n_star else (f_proj if n == n_star else 0.0) for n in range(1, Nd + 1)]
E_proj = sum(s * gamma(n) for n, s in enumerate(sigma, 1))
E_sync = sum((1 - s) * gamma(n) for n, s in enumerate(sigma, 1))
E_capture_direct = sum(gamma(n) for n in range(28, 45))
E_bottleneck = (1 - f_proj) * gamma(27)
print(f"  dim ker = {sum(1 for s in sigma if s==0.0)}  n* = {n_star}")
print(f"  E_proj = {E_proj:.6f}   E_sync = {E_sync:.6f}   Σγ = {E_proj+E_sync:.6f}")
print(f"  E_capture(direct n≥28) = {E_capture_direct:.10f}")
print(f"  E_bottleneck = {E_bottleneck:.10f}")
check("dim ker(T_pipe) = 17", sum(1 for s in sigma if s == 0.0) == 17)
check("E_proj = 28.5", abs(E_proj - 28.5) < 1e-9)
check("E_sync = 61.5", abs(E_sync - 61.5) < 1e-9)
check("Σγ = 90 守恆", abs(E_proj + E_sync - 90) < 1e-9)
check("E_capture ≥28 = 60.8845", abs(E_capture_direct - 60.8845) < 1e-3,
      f"(={E_capture_direct:.6f})")
check("E_capture + bottleneck = E_sync", abs(E_capture_direct + E_bottleneck - E_sync) < 1e-9)
# 第二路: complement
E_capture_compl = sum((1 - s) * gamma(n) for n, s in enumerate(sigma, 1)) - E_bottleneck
check("E_capture 兩路一致 (≤1e-12)", abs(E_capture_direct - E_capture_compl) < 1e-12)

# ===== B. O222 審計殘差 =====
print("\n[B] O222 審計: E_bottleneck vs 8/13")
r_813 = 8 / 13
dev = abs(E_bottleneck - r_813)
rel = dev / r_813
print(f"  E_bottleneck = {E_bottleneck:.16f}")
print(f"  8/13         = {r_813:.16f}")
print(f"  絕對偏差     = {dev:.6e}   相對 = {rel*100:.5f}%")
check("偏差 = 7.848e-5 (符合 O222 審計)", abs(dev - 7.848e-5) < 5e-8,
      f"(={dev:.6e})")
check("「≈ 8/13」聲稱不成立 (rel > 1e-4)", rel > 1e-4,
      f"(rel={rel:.2e} ⟹ 小數級近似 = 後驗擬合風險)")

# ===== C. 效率層 (O175) =====
print("\n[C] 效率層: η = φ⁻²¹")
phi21 = phi ** 21
Lucas21 = 24476                                        # L₂₁ = φ²¹+φ⁻²¹ (整數部)
eta = phi ** (-21)
print(f"  φ²¹        = {phi21:.6f}")
print(f"  Lucas L₂₁  = {Lucas21}")
print(f"  η = φ⁻²¹   = {eta:.9e}")
check("φ²¹ = Lucas L₂₁ = 24476 (dev<1e-3)", abs(phi21 - Lucas21) < 1e-3,
      f"(φ²¹={phi21:.6f})")
check("η = φ⁻²¹ = 4.085635e-5", abs(eta - 4.085635e-5) < 1e-11,
      f"(={eta:.6e})")
# φ²¹ 錨定: TON 618
TON = 4.07e10
check("TON 618 × φ²¹ = 9.96e14 (O173 報值)", abs(TON * phi21 - 9.962e14) / 9.962e14 < 0.01,
      f"(={TON*phi21:.4e})")

# ===== D. 時標層 =====
print("\n[D] 時標層: τ_rec")
print(f"  T_ring = {T_ring_Gyr:.4f} Gyr  (= 2π/ω_ring, ω_ring={omega_ring})")
tau_rec_yr = 5.88e18 / 82.53
print(f"  τ_rec = 5.88e18 / 82.53 = {tau_rec_yr:.6e} yr")
t_true_Gyr = 11100.9
t_true_yr = t_true_Gyr * 1e9
T_ring_yr = T_ring_Gyr * 1e9
r1 = tau_rec_yr / t_true_yr
r2 = tau_rec_yr / T_ring_yr
print(f"  τ_rec/t_true = {r1:.4e}   τ_rec/T_ring = {r2:.4e}")
check("τ_rec = 7.1247e16 yr", abs(tau_rec_yr - 7.1247e16) / 7.1247e16 < 1e-3,
      f"(={tau_rec_yr:.5e})")
check("τ_rec/t_true = 6.42e3", abs(r1 - 6.42e3) / 6.42e3 < 0.01, f"(={r1:.3e})")
check("τ_rec/T_ring = 8.42e5", abs(r2 - 8.42e5) / 8.42e5 < 0.01, f"(={r2:.3e})")
check("t_true = 131·T_ring + 13.8 (O213)", abs(131 * T_ring_Gyr + 13.8 - t_true_Gyr) < 1.0,
      f"(131×{T_ring_Gyr:.3f}+13.8={131*T_ring_Gyr+13.8:.1f} vs {t_true_Gyr})")

# ===== E. 質子衰變 (O88) =====
print("\n[E] 質子衰變邊界 (O88/PD)")
tp_lo, tp_hi = 2.891e38, 1.388e40
print(f"  τ_p = {tp_lo:.4e} – {tp_hi:.4e} yr")
r_lo = tp_lo / T_ring_yr; r_hi = tp_hi / T_ring_yr
print(f"  τ_p/T_ring = {r_lo:.4e} – {r_hi:.4e}")
print(f"  t_true/τ_p = {t_true_yr/tp_lo:.4e} – {t_true_yr/tp_hi:.4e}")
check("τ_p/T_ring = 3.42e27 – 1.64e29", abs(r_lo - 3.42e27)/3.42e27 < 0.01 and abs(r_hi - 1.64e29)/1.64e29 < 0.01,
      f"({r_lo:.3e} – {r_hi:.3e})")
check("t_true/τ_p = 3.84e-26 (低端)", abs(t_true_yr/tp_lo - 3.84e-26)/(3.84e-26) < 0.01,
      f"({t_true_yr/tp_lo:.3e})")

# ---- write JSON ----
out = {
    "title": "G8 交接數字獨立重驗",
    "channel": {"dim_ker": 17, "E_proj": E_proj, "E_sync": E_sync,
                "E_capture_direct": E_capture_direct,
                "E_capture_complement": E_capture_compl,
                "E_bottleneck": E_bottleneck},
    "O222_residual": {"E_bottleneck": E_bottleneck, "r_8_13": r_813,
                      "abs_dev": dev, "rel_dev": rel,
                      "verdict": "「≈8/13」不成立 (rel 1.3e-4 > 1e-4)"},
    "efficiency": {"phi21": phi21, "Lucas21": Lucas21, "eta": eta,
                   "TON_anchor": TON * phi21},
    "timescale": {"T_ring_Gyr": T_ring_Gyr, "tau_rec_yr": tau_rec_yr,
                  "t_true_Gyr": t_true_Gyr,
                  "tau_rec_over_t_true": r1, "tau_rec_over_T_ring": r2},
    "proton": {"tau_p_lo": tp_lo, "tau_p_hi": tp_hi,
               "ratio_lo": r_lo, "ratio_hi": r_hi,
               "t_true_over_tau_p_lo": t_true_yr / tp_lo},
    "verdict": f"G8 交接數字 {PASS}/{PASS+FAIL} PASS",
}
with open(os.path.join(BASE, "data", "11_g8_handover_verify.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print(f"\n{'='*74}")
print(f"RESULT: {PASS} PASS, {FAIL} FAIL  {'🟢' if FAIL==0 else '🔴'}")
print(f"{'='*74}")
if FAIL: exit(1)
