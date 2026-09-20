#!/usr/bin/env python3
"""
O206 — Script 11: F6 — M₀ 之關係 (方向 2)
=========================================================
★ 本 script 首先解決一個【命名碰撞】:
   O38 之 M₀ (W-field 凝聚標度)      ≈ 27.900915 MeV
   O136/O206 映射之截距 (質量譜標度) ≈ 1.363e-6 MeV
   兩者係【唔同物理量】但同名 ⟹ O136 docs/37 之「內部不一致」係關於 O38 之 M₀,
   同 O206 映射層之標度無關。F6 之前從未正確提問。

  §A 命名碰撞釐清 + 兩個標度各自之定義驗證
  §B 獨立重現 O136 docs/37 之內部不一致 (H₀ 需求 vs O170)
  §C 映射截距 m₀ 之結構關係檢驗 (池子 + null)
  §D F6 裁決: O38 公式需否重寫?
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from o206_lib import (NC, ND, MU2, A5_MODES, LM, MASS, E_ring44, V_position,
                      logscore, sum_V2_dE)

OUT = Path(__file__).parent.parent / "data"
checks = []


def chk(name, cond, detail=""):
    checks.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"   {detail}" if detail else ""))


PAIR = [(1, "t"), (2, "b"), (3, "tau"), (4, "c"), (5, "mu"), (7, "s"), (9, "d"), (11, "u"), (13, "e")]
dm = sum_V2_dE(E_ring44(), V_position())
ldm = np.array([math.log(dm[A5_MODES.index(n)]) for n, _ in PAIR])
lm = np.array([math.log(MASS[p]) for _, p in PAIR])

# ── 常數 (O136 docs/37 慣例) ──
M_P = 1.220910e22          # MeV
HBAR = 6.582119569e-22     # MeV·s
MPC = 3.0856775814913673e22  # m
CY3 = 134
E_kchain_claimed = 4.060265e-9   # MeV (= 4.060265 meV; 1 meV = 1e-9 MeV) ⚠️ 修正: 初版寫 4.060265e-3 (差 1e6)
M0_O38 = 27.900915               # MeV


def sqrt_MP_hbar_H0(H0):
    """√(M_P·ħ·H₀) in MeV"""
    H0_si = H0 * 1e3 / MPC          # km/s/Mpc -> 1/s
    return math.sqrt(M_P * HBAR * H0_si)


print("=" * 100)
print("O206 Script 11: F6 — M₀ 之關係")
print("=" * 100)

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§A ★ 命名碰撞釐清: 兩個「M₀」\n{'─'*100}")
b, pred = np.column_stack([np.ones(9), ldm]), None
beta, *_ = np.linalg.lstsq(b, lm, rcond=None)
m0_map = math.exp(beta[0])
alpha = beta[1]
print(f"""
  ┌ 量 A: O38 之 M₀ (W-field 凝聚標度)      = {M0_O38} MeV      [W-field 場論標度]
  └ 量 B: O136/O206 映射截距 m₀             = {m0_map:.6e} MeV  [質量譜標度]
     兩者比 M₀(O38)/m₀ = {M0_O38/m0_map:.4e}  ⟹ 差 {math.log10(M0_O38/m0_map):.2f} 個數量級
  ⟹ 【唔同物理量】— O136 docs/37 之「內部不一致」係關於量 A, 與映射層無關
""")
chk("C1 [命名] 兩個 M₀ 相差 > 6 個數量級 ⟹ 確認係唔同量 (F6 之前提問有誤)",
    math.log10(M0_O38 / m0_map) > 6, f"比值 = {M0_O38/m0_map:.3e}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§B 獨立重現 O136 docs/37 之內部不一致\n{'─'*100}")
f_pre = 1 - CY3 / (ND + 1) ** 2
print(f"  (1 − CY₃/45²) = 1 − 134/2025 = {f_pre:.12f}   [= 1891/2025]")
chk("C2 [恆等] 1 − 134/2025 = 1891/2025 精確",
    abs(f_pre - 1891 / 2025) < 1e-15, f"{f_pre:.12f} vs {1891/2025:.12f}")

H0_IDCM = 71.157
E_with_IDCM = sqrt_MP_hbar_H0(H0_IDCM) * f_pre          # MeV
print(f"\n  √(M_P ħ H₀) @ H₀ = {H0_IDCM}: {sqrt_MP_hbar_H0(H0_IDCM)*1e9:.6f} meV")
print(f"  ⟹ E_kchain = {E_with_IDCM*1e9:.6f} meV   (聲稱值 = {E_kchain_claimed*1e9:.6f} meV)")
print(f"  Δ = {abs(E_with_IDCM-E_kchain_claimed)/E_kchain_claimed*100:.4f}%")
H0_needed = (E_kchain_claimed / f_pre) ** 2 / (M_P * HBAR) * MPC * 1e-3
print(f"\n  反解所需 H₀ = {H0_needed:.4f} km/s/Mpc")
print(f"  IDCM O170 H₀ = {H0_IDCM}  ⟹ Δ = {abs(H0_needed-H0_IDCM)/H0_IDCM*100:.4f}%")
chk("C3 [重現] O38 公式所需 H₀ ≠ O170 之 H₀ (Δ ≈ 2%) ⟹ 內部不一致確認",
    abs(H0_needed - H0_IDCM) / H0_IDCM > 0.015,
    f"所需 {H0_needed:.4f} vs O170 {H0_IDCM} (Δ {abs(H0_needed-H0_IDCM)/H0_IDCM*100:.4f}%)")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§C 映射截距 m₀ 之結構關係 (池子 + null)\n{'─'*100}")
E_k = E_with_IDCM                # MeV (⚠️ 修正: 初版錯用 *1e3)
rhoL = 2.246e-9                  # MeV (= 2.246 meV; ⚠️ 修正: 初版用 2.246 MeV)
ratios = {
    "M₀(O38)/m₀": M0_O38 / m0_map,
    "E_kchain/m₀": E_k / m0_map,
    "ρ_Λ^(1/4)/m₀": rhoL / m0_map,
    "m₀ (MeV)": m0_map,
    "E_kchain (MeV)": E_k,
}
print(f"\n  {'比值':>16} {'值':>14} {'log₁₀':>9} {'log_φ':>10}")
print("  " + "-" * 54)
for k, v in ratios.items():
    print(f"  {k:>16} {v:>14.6e} {math.log10(v):>9.4f} {math.log(v)/math.log(1.6180339887):>10.4f}")

x_M0 = math.log(M0_O38 / m0_map) / math.log(1.6180339887)
print(f"\n  ★ M₀(O38)/m₀ = φ^{x_M0:.6f}")
print(f"    對照 docs/36 之指數 47 + 37/528 = {47+37/528:.6f}  ⟹ 唔同 (唔可以直接比較, 因為")
print(f"    量 A 與量 B 唔同)")

# 池子 null: m₀ 係唔係 φ^(-整數) × E_kchain ?
POOL = {"E_kchain": E_k, "rhoL": rhoL, "M0_O38": M0_O38}
phipow = {f"phi^{k:+d}": E_k * 1.6180339887 ** k for k in range(-60, 61)}
best = min(phipow.items(), key=lambda kv: abs(kv[1] - m0_map))
print(f"\n  E_kchain·φ^k 最接近 m₀ 之 k: {best[0]} ⟹ {best[1]:.6e} vs {m0_map:.6e} "
      f"(Δ {abs(best[1]-m0_map)/m0_map*100:.3f}%)")
# null: 掃 1000 個隨機 m₀ 值, 睇 φ^(-k) 級數幾密
rng = np.random.default_rng(11)
dists = []
for _ in range(2000):
    m_rand = m0_map * math.exp(rng.uniform(-1, 1))
    d = min(abs(v - m_rand) / m_rand for v in phipow.values())
    dists.append(d)
p_phi = float(np.mean(np.array(dists) <= abs(best[1] - m0_map) / m0_map))
print(f"  ★ null: 隨機 m₀ (±1 e-fold) 之 φ^(-k) 最近距離 中位 = {np.median(dists)*100:.3f}%")
print(f"    P(隨機距離 ≤ 觀測 {abs(best[1]-m0_map)/m0_map*100:.3f}%) = {p_phi:.4f}")
chk("C4 [池子 null] φ^k 級數密度高 ⟹ m₀ 之 φ-冪命中唔構成證據",
    p_phi > 0.05, f"P = {p_phi:.4f} (級數 121 點覆蓋 ~121 e-folds)")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§D F6 裁決\n{'─'*100}")
print(f"""
  ① ★ 命名碰撞: O38 之 M₀ (W-field 標度, {M0_O38} MeV) ≠ 映射截距 m₀ ({m0_map:.3e} MeV)
     ⟹ F6 之原問題「ω_n 逐模式 ⟹ M₀ 公式需否重寫?」= 提問有誤 (混淆兩個量)
  ② O136 docs/37 之內部不一致【獨立重現】(所需 H₀ = {H0_needed:.3f} vs O170 {H0_IDCM})
  ③ 映射截距 m₀ 係【錨】, 唔係導出量 (由 α 同一個質量點定出)
  ④ m₀ 之 φ-冪關係命中被池子 null 排除 (P = {p_phi:.4f})
  ⟹ F6 裁決:
     (i)  O38 之 M₀ 公式【唔需要】因 O206 之結果而重寫 (兩者唔同量)
     (ii) 映射層之標度 m₀ 係【獨立錨】— 與 O38 之 M₀ 無結構關係 (本輪無發現)
     (iii) O136 docs/37 之內部不一致維持 🔴 (需 H₀ = {H0_needed:.2f} vs O170 {H0_IDCM})
""")

n_pass = sum(1 for _, ok in checks if ok)
print(f"{'='*100}\nRESULT: {n_pass}/{len(checks)} PASS\n{'='*100}")
for name, ok in checks:
    if not ok:
        print(f"  FAIL: {name}")

with open(OUT / "11_m0_relation.json", "w") as f:
    json.dump({
        "m0_mapping_intercept_MeV": m0_map, "M0_O38_MeV": M0_O38,
        "ratio": M0_O38 / m0_map, "log10_ratio": math.log10(M0_O38 / m0_map),
        "E_kchain_with_IDCM_meV": E_k, "E_kchain_claimed_meV": E_kchain_claimed * 1e3,
        "H0_needed": H0_needed, "H0_IDCM_O170": H0_IDCM,
        "H0_discrepancy_pct": abs(H0_needed - H0_IDCM) / H0_IDCM * 100,
        "phi_power_best_k": best[0], "phi_power_dev_pct": abs(best[1] - m0_map) / m0_map * 100,
        "phi_null_p": p_phi,
        "checks_pass": int(n_pass), "checks_total": len(checks),
    }, f, ensure_ascii=False, indent=2)
print("✅ 寫入 data/11_m0_relation.json")
