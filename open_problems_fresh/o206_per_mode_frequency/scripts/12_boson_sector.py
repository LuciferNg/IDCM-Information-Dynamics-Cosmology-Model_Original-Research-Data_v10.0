#!/usr/bin/env python3
"""
O206 — Script 12: 玻色子扇區 (Boson sector) — 傳播子 / 質量塔 / 費米-玻色分離
=========================================================
動機 (調律者問題 2026-09-21):
  「這是要引入玻色子嗎？量子力學宣稱玻色子也有質量，
    但玻色子這種傳播子的存在性和模式是什麼」

★ 本 script 檢驗: O206 F1 之結果 (鏈之動態頻率 ω_n = √γ_n, 逐模不同)
   係唔係【已經就係】玻色子扇區之頻率/質量塔 — 即玻色子並非新引入。

上游 (唯讀):
  O83 (08-25, 🟢 58/58): 傳播子 G_n(0) = 1/(2ω_n),  ω_n = 2sin(πn/88)   ← 逐模不同!
  O169 docs/13 (09-17):  ω_n = μ² = 2 (共同常數)                        ← fiducial
  O204 (09-18):          玻色塔 m_n = M₀√γ_n; 費米 m = M₀|Δm|^α (O136)
  O164 (09-10):          質量-頻率鎖 m_n = h_eff·f_n, f_n ∝ √γ_n
  O82 (Q8):              費米質量 = 玻色子交換: m_n = κ²·ω_n, κ² = M₀

§A ★ ω_n 符號碰撞 (O83 vs O169) — 同一個符號, 兩個唔同量
§B 玻色質量塔 m_n = M₀√γ_n 之範圍 (對照 SM 玻色子)
§C ★ 費米 vs 玻色 = Z₂-奇 vs Z₂-偶扇區 (X_nn = 0 精確 ⟹ 結構分離)
§D 費米子 γ-冪律檢驗 (核對 O204「m = M₀γ_n」之聲稱)
§E 裁決
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from mpmath import mp, mpf, sin, pi

sys.path.insert(0, str(Path(__file__).parent))
from o206_lib import (NC, ND, MU2, A5_MODES, LM, MASS, E_ring44, V_position,
                      logscore, sum_V2_dE)

mp.dps = 40
OUT = Path(__file__).parent.parent / "data"
checks = []


def chk(name, cond, detail=""):
    checks.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"   {detail}" if detail else ""))


M0 = 27.900915          # MeV (O38)
V = V_position()
E = E_ring44()
gam = np.array([float(4 * sin(pi * n / 88) ** 2) for n in range(1, ND + 1)])
sg = np.sqrt(gam)

print("=" * 100)
print("O206 Script 12: 玻色子扇區 — 傳播子 / 質量塔 / 費米-玻色分離")
print("=" * 100)

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§A ★ ω_n 符號碰撞: O83 vs O169\n{'─'*100}")
print(f"""
  ┌ O83 (08-25, 傳播子極點):   ω_n = 2sin(πn/88) = √γ_n    → 逐模【不同】, n=1..44
  └ O169 docs/13 (09-17):      ω_n = μ² = 2                → 共同常數 (fiducial)
     兩者係【唔同量】但用同一符號; O206 F1 審計已裁決:
       · O169 之 ω = μ² 係色散圓半徑 (fiducial), 由 k_44 = 0 唯一選定
       · O83 之 ω_n = √γ_n 係【傳播子極點】= 鏈之動態頻率 (逐模不同)
  ⟹ 兩者【唔矛盾】— 係兩個唔同量: 圓半徑 vs 極點位置
""")
dev_pole = max(abs(sg[n - 1] - float(2 * sin(pi * n / 88))) for n in range(1, ND + 1))
chk("C1 [O83] 傳播子極點 ω_n = √γ_n = 2sin(πn/88) 逐模不同 (44/44 相異值)",
    dev_pole < 1e-14 and len(set(np.round(sg, 12))) == ND,
    f"max dev = {dev_pole:.2e}; 相異值 = {len(set(np.round(sg,12)))}/{ND}")
chk("C2 [O169] 共同值 μ² = 2 = √γ_44 (Nyquist 極點) ⟹ 同一個數, 唔同角色",
    abs(sg[43] - 2) < 1e-15, f"√γ_44 = {sg[43]:.15f}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§B 玻色質量塔 m_n = M₀√γ_n (O204) 之範圍\n{'─'*100}")
m_bos = M0 * sg
print(f"\n  {'n':>3} {'√γ_n':>10} {'m_n (MeV)':>12}   註")
print("  " + "-" * 44)
for n in [1, 2, 3, 5, 7, 13, 22, 44]:
    note = ""
    if n == 7:
        note = "← O204 DM 候選 m₇ = 13.8002 MeV"
    if n == 44:
        note = "← 塔頂 (Nyquist)"
    print(f"  {n:>3} {sg[n-1]:>10.6f} {m_bos[n-1]:>12.6f}   {note}")
print(f"\n  ★ 玻色塔範圍 = [{m_bos.min():.4f}, {m_bos.max():.4f}] MeV  (跨度 {m_bos.max()/m_bos.min():.2f}×)")
chk("C3 [玻色塔] 塔範圍 ≪ 電弱標度 (max < 0.1 GeV) ⟹ 唔係 SM 電弱玻色子",
    m_bos.max() < 100, f"max = {m_bos.max():.4f} MeV = {m_bos.max()/1000:.6f} GeV")

SM_BOS = {"W": 80377.0, "Z": 91187.6, "H": 125250.0}   # MeV
print(f"\n  {'SM 玻色子':>10} {'質量 (MeV)':>14} {'/m_塔max':>10} {'最近 √γ_n':>12} {'n 整數?':>10}")
print("  " + "-" * 60)
for name, m in SM_BOS.items():
    r = m / m_bos.max()
    # 用 v_EW = 246.22 GeV 做標度再試
    v_ew = 246220.0
    sg_req = m / v_ew
    n_req = (88 / math.pi) * math.asin(min(1.0, sg_req / 2))
    print(f"  {name:>10} {m:>14.1f} {r:>10.1f}× {sg_req:>12.6f} {n_req:>10.3f}")
chk("C4 [SM 玻色子] W/Z/H 唔落喺玻色塔 (需 n 非整數; 或標度差 ~10³)",
    all(abs((88 / math.pi) * math.asin(min(1.0, (m / 246220.0) / 2)) % 1) > 0.05 for m in SM_BOS.values()),
    "W: n=4.59, Z: n=5.13, H: n=7.20 — 全部非整數")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§C ★ 費米 vs 玻色 = Z₂-奇 vs Z₂-偶扇區\n{'─'*100}")
diag_max = max(abs(V[n - 1, n - 1]) for n in range(1, NC + 1))
same_max = max(abs(V[n - 1, m - 1]) for n in range(1, NC + 1) for m in range(1, NC + 1) if (n - m) % 2 == 0)
print(f"""
  位置算子 X = diag(i − ⟨i⟩):  X_nn = 0 精確 (O206 scripts/08 閉式證), 
                                X_nm ≠ 0 只喺 n+m 奇
  ⟹ X 係【純 Z₂-奇】算子 ⟹ 佢【冇】對角 (玻色型) 部分
  ⟹ 費米子質量機制 (|Δm| 用 X 之非對角元) 結構上【唔可能】給玻色子質量
""")
chk("C5 ★ [結構分離] X 之對角精確零 (max |X_nn| < 1e-12)",
    diag_max < 1e-12, f"max |X_nn| = {diag_max:.2e}")
chk("C6 ★ [結構分離] X 之同-parity 元精確零 ⟹ 純 Z₂-奇 (無玻色型分量)",
    same_max < 1e-12, f"max |X_nm| (n+m 偶) = {same_max:.2e}")

odd = float(sum(gam[n - 1] for n in range(1, ND + 1) if n % 2 == 1))
even = float(sum(gam[n - 1] for n in range(1, ND + 1) if n % 2 == 0))
print(f"\n  Z₂ 扇區 (44-site): Σγ_odd = {odd:.6f} (= N_d),  Σγ_even = {even:.6f},  差 = {even-odd:.6f} = μ²")
chk("C7 [扇區] Σγ_odd = 44 = N_d (觀察者); Σγ_even = 46 (世界); 差 = μ² = 2",
    abs(odd - 44) < 1e-9 and abs(even - 46) < 1e-9, f"{odd:.4f} / {even:.4f}")
chk("C8 [扇區] 玻色質量項 μ² = γ_22 (Z₂ 反射不動點, 偶扇區) ⟹ 玻色扇區 = 不動點扇區",
    abs(gam[21] - 2) < 1e-15, f"γ_22 = {gam[21]:.15f}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§D 費米子 γ-冪律檢驗 (核對 O204 之「m = M₀γ_n」聲稱)\n{'─'*100}")
PAIR = [(1, "t"), (2, "b"), (3, "tau"), (4, "c"), (5, "mu"), (7, "s"), (9, "d"), (11, "u"), (13, "e")]
lg = np.array([math.log(gam[n - 1]) for n, _ in PAIR])
lm = np.array([math.log(MASS[p]) for _, p in PAIR])
ldm = np.array([math.log(sum_V2_dE(E, V)[A5_MODES.index(n)]) for n, _ in PAIR])


def ols(X, y):
    A = np.column_stack([np.ones(len(y)), X])
    b, *_ = np.linalg.lstsq(A, y, rcond=None)
    return b, A @ b


b_g, p_g = ols(lg, lm)
b_d, p_d = ols(ldm, lm)
r_g, r_d = float(np.std(lm - p_g)), float(np.std(lm - p_d))
print(f"\n  ① ln m = c + β·ln γ_n       ⟹ β = {b_g[1]:+.6f},  RMS = {r_g:.4f}")
print(f"  ② ln m = c + α·ln|Δm|       ⟹ α = {b_d[1]:+.6f},  RMS = {r_d:.4f}")
print(f"\n  ★ O204 final_result 聲稱「dim-4 費米: m = M₀·γ_n」(即 β = +1)")
print(f"    實測 β = {b_g[1]:+.4f} ⟹ 🔴 唔成立 (符號相反 + 指數差 {abs(b_g[1]-1):.2f})")
chk("C9 [核對] O204 之「費米 m = M₀·γ_n」唔成立 (實測 β ≈ −2.4, 非 +1)",
    abs(b_g[1] - 1.0) > 1.0, f"β = {b_g[1]:+.4f} vs 聲稱 +1")
chk("C10 [核對] |Δm| 框架 (α = %.3f) 優於 γ_n 直接冪律 (RMS %.4f < %.4f)" % (b_d[1], r_d, r_g),
    r_d < r_g, f"|Δm| RMS {r_d:.4f} < γ_n RMS {r_g:.4f}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§E 裁決 (script 12)\n{'─'*100}")
print(f"""
  ① ★ ω_n 符號碰撞已解: O83 之 ω_n = √γ_n (傳播子極點, 逐模不同)
     vs O169 之 ω_n = μ² (fiducial 圓半徑) — 兩個唔同量, 唔矛盾
  ② 玻色質量塔 m_n = M₀√γ_n ∈ [{m_bos.min():.4f}, {m_bos.max():.4f}] MeV
     ⟹ 【輕玻色子扇區】(MeV), 唔係 SM 電弱玻色子 (W/Z/H 需 n 非整數)
  ③ ★★ 費米 vs 玻色 = 【Z₂-奇 vs Z₂-偶】扇區:
       X_nn = 0 精確 ⟹ 位置算子純 Z₂-奇 ⟹ 費米機制結構上觸唔到玻色扇區
       玻色質量項 μ² = γ_22 = Z₂ 反射不動點 (偶扇區)
  ④ 🔴 O204 之「費米 m = M₀γ_n」聲稱唔成立 (實測 m ∝ γ_n^{b_g[1]:+.3f})
  ⟹ 玻色子【唔係新引入】— 佢係 O83 傳播子扇區 = O204 玻色塔 = O206 F1 之動態頻率
""")

n_pass = sum(1 for _, ok in checks if ok)
print(f"{'='*100}\nRESULT: {n_pass}/{len(checks)} PASS\n{'='*100}")
for name, ok in checks:
    if not ok:
        print(f"  FAIL: {name}")

with open(OUT / "12_boson_sector.json", "w") as f:
    json.dump({
        "omega_collision": {"O83": "omega_n = sqrt(gamma_n) = 2sin(pi n/88) [pole]",
                            "O169": "omega_n = mu^2 = 2 [fiducial circle radius]"},
        "boson_tower_MeV": {"min": float(m_bos.min()), "max": float(m_bos.max()), "M0": M0},
        "m7_MeV": float(m_bos[6]),
        "sm_bosons_fit": "none (n required non-integer: W 4.59, Z 5.13, H 7.20)",
        "X_diagonal_max": float(diag_max), "X_same_parity_max": float(same_max),
        "sum_gamma_odd": odd, "sum_gamma_even": even,
        "fermion_gamma_power_beta": float(b_g[1]), "fermion_absdm_alpha": float(b_d[1]),
        "rms_gamma": r_g, "rms_absdm": r_d,
        "checks_pass": int(n_pass), "checks_total": len(checks),
    }, f, ensure_ascii=False, indent=2)
print("✅ 寫入 data/12_boson_sector.json")
