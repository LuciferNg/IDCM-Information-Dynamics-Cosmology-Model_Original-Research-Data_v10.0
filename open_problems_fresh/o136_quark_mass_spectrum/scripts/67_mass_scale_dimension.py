#!/usr/bin/env python3
"""
O136 — Script 67: 質量標度之維度結構 — √(M_P ħ H₀) 為何係幾何平均?
================================================================
既有公式 (O38):
  M₀ = √(M_P·ħ·H₀) · φ^(47+37/528) · (1 − CY₃/(N_d+1)²)
  E_kchain = √(M_P·ħ·H₀) · (1 − CY₃/45²) = 4.060265 meV

★★ docs/36 已判: 指數 47+37/528 係【過度吻合】⟹ 事後反解
⟹ 本輪檢驗【前因子】√(M_P ħ H₀)·(1−CY₃/45²) 是否同樣

本 script:
  (A) 用標準常數計算 √(M_P ħ H₀) (多個 H₀ 慣例)
  (B) 反解所需 √(M_P ħ H₀) 與 (1−CY₃/45²) 之吻合度
  (C) ★★ 過度吻合判準應用 (docs/36 §五)
  (D) ★ 幾何平均之結構身份: 為何 √(E₁E₂) 而非算術平均?
      — 檢驗 IDCM 中是否存在幾何平均結構
  (E) 裁決
"""
import numpy as np, math, json, itertools
from pathlib import Path

OUT = Path(__file__).parent.parent / "data"
ND, DIMC, B_, CY3 = 44, 3, 4, 134
MPC_m = 3.0856775814913673e22      # m
HBAR_MeVs = 6.582119569e-22        # MeV·s
MP_MeV = 1.220910e22               # MeV (Planck mass)
EKCHAIN_meV = 4.060265
M0_MeV = 27.900915

print("=" * 96)
print("O136 Script 67: 質量標度之維度結構 — √(M_P ħ H₀)")
print("=" * 96)

# ═══ (A) 計算 √(M_P ħ H₀) ════════════════════════════
print(f"\n{'─'*96}\n(A) √(M_P ħ H₀) 計算 (多個 H₀ 慣例)\n{'─'*96}")
H0s = {"Planck 2018 (67.4)": 67.4, "SH0ES (73.04)": 73.04,
       "O170 IDCM (71.157)": 71.157, "Planck TT+lowE (67.27)": 67.27}
print(f"\n  {'H₀ 慣例':>26} {'H₀ (km/s/Mpc)':>14} {'√(M_P ħ H₀) (meV)':>18}")
print("  " + "-"*62)
sq = {}
for k, h in H0s.items():
    H_si = h*1e3/MPC_m
    v = math.sqrt(MP_MeV*HBAR_MeVs*H_si)     # MeV
    sq[k] = v*1e9                            # meV
    print(f"  {k:>26} {h:>14.3f} {v*1e9:>18.6f}")
print(f"\n  ★ 註: 1 meV = 1e−9 MeV (docs/36 §二 單位修正)")

# ═══ (B) 反解所需值 ══════════════════════════════════
print(f"\n{'─'*96}\n(B) 反解所需 √(M_P ħ H₀) 與 (1−CY₃/45²)\n{'─'*96}")
f_pref = 1 - CY3/(ND+1)**2
print(f"\n  (1 − CY₃/(N_d+1)²) = 1 − 134/2025 = {f_pref:.12f}  (= 1891/2025 = {1891/2025:.12f})")
print(f"  E_kchain (聲稱) = {EKCHAIN_meV} meV")
req_sq = EKCHAIN_meV/f_pref
print(f"  ⟹ 所需 √(M_P ħ H₀) = E_kchain/(1−CY₃/45²) = {req_sq:.6f} meV")
print(f"\n  {'H₀ 慣例':>26} {'計算值':>12} {'所需值':>12} {'Δ%':>9}")
print("  " + "-"*62)
devs = {}
for k, v in sq.items():
    d = (v - req_sq)/req_sq*100
    devs[k] = d
    print(f"  {k:>26} {v:>12.6f} {req_sq:>12.6f} {d:>+9.4f}")
print(f"\n  ★ 最小偏差 = {min(abs(d) for d in devs.values()):.4f}% ({min(devs, key=lambda k: abs(devs[k]))})")

# 反解所需 H₀
req_H = (req_sq*1e-9)**2/(MP_MeV*HBAR_MeVs)     # 1/s
req_H_kms = req_H*MPC_m/1e3
print(f"\n  ★ 反解所需 H₀ = {req_H_kms:.4f} km/s/Mpc")
print(f"    (Planck 67.4: Δ{abs(req_H_kms-67.4)/67.4*100:.3f}%;  O170 71.157: Δ{abs(req_H_kms-71.157)/71.157*100:.3f}%)")

# ═══ (C) 過度吻合判準 ════════════════════════════════
print(f"\n{'─'*96}\n(C) ★★ 過度吻合判準應用 (docs/36 §五)\n{'─'*96}")
print(f"""
  判準: 若結構讀法之吻合【優於】輸入量精度 ⟹ 必然係事後反解

  ★ 輸入精度:
     M_P: 相對不確定度 < 1e−5 (定義性, 但 G 有 2e−5)
     ħ:   定義性 (精確, 2019 SI)
     H₀:  相對不確定度 ~1e−2 (Planck 67.4±0.5 → 0.7%; SH0ES 73.04±1.04 → 1.4%)
     ⟹ 整體輸入精度 ~1e−2

  ★ 吻合度:
     最佳 H₀ 慣例之偏差 = {min(abs(d) for d in devs.values()):.4f}%
     ⟹ 吻合精度 ~1e−4 .. 1e−2
""")
best_h = min(devs, key=lambda k: abs(devs[k]))
print(f"  ★ 若用 {best_h}: 吻合 {abs(devs[best_h]):.4f}%")
print(f"  ⟹ {'🔴 吻合優於/接近輸入精度 ⟹ 前因子亦係【配合 H₀ 之選擇】' if min(abs(d) for d in devs.values()) < 0.1 else '🟡 吻合與輸入精度同量級'}")

# ═══ (D) 幾何平均之結構身份 ══════════════════════════
print(f"\n{'─'*96}\n(D) ★ 幾何平均之結構身份\n{'─'*96}")
print(f"""
  問題: 為何係 √(M_P·ħH₀) (幾何平均) 而非 (M_P + ħH₀)/2 (算術平均)?

  ★ 幾何平均 = 【對數空間之算術平均】: ln√(E₁E₂) = (ln E₁ + ln E₂)/2

  ★ IDCM 之框架係【對數空間】:
     - φ-冪律: M₀ = E_kchain·φ^x   ⟹ 加法在指數, 乘法在標度
     - 對數質量譜: ln m = ln M₀ + α·ln|Δm|
     - docs/36: 指數 47+37/528 之結構
     ⟹ 幾何平均係 IDCM 之【自然平均】

  ★ 但此為【相容性論證】, 非推導。真正之推導須回答:
     「為何質量標度由兩個極端能量 (UV: M_P, IR: ħH₀) 之對數中點決定?」
     — 此即【全息/紅外-紫外混合】之標準物理圖像
     — IDCM 中是否有對應結構? 待檢驗
""")
# 檢查 IDCM 中是否有其他幾何平均結構
print(f"  ★ 檢查 IDCM 之幾何平均結構:")
tests = {
    "√(M_P · ħH₀) / E_kchain": math.sqrt(MP_MeV*HBAR_MeVs*(71.157e3/MPC_m))*1e9/EKCHAIN_meV,
    "ρ_Λ^(1/4) / E_kchain (2.246 meV)": 2.246/EKCHAIN_meV,
    "E_kchain / ρ_Λ^(1/4)": EKCHAIN_meV/2.246,
    "√(E_kchain · ρ_Λ^(1/4))": math.sqrt(EKCHAIN_meV*2.246),
}
for k, v in tests.items():
    print(f"    {k:>38} = {v:.6f}")
print(f"    ★ E_kchain/ρ_Λ^(1/4) = {EKCHAIN_meV/2.246:.4f}  (vs 1.8? 9/5=1.8? φ+1/φ³=1.854?)")

# ═══ (E) 裁決 ════════════════════════════════════════
print(f"\n{'─'*96}\n(E) 裁決\n{'─'*96}")
print(f"""
  ① (1−CY₃/(N_d+1)²) = 1891/2025 = {f_pref:.12f} ✓ 代數恆等
  ② 所需 √(M_P ħ H₀) = {req_sq:.6f} meV
  ③ 標準 H₀ 慣例之計算值: {min(sq.values()):.4f} – {max(sq.values()):.4f} meV
  ④ ★ 反解所需 H₀ = {req_H_kms:.4f} km/s/Mpc
     ⟹ {'落在已知 H₀ 範圍內 (67.4–73.0)' if 67.0 < req_H_kms < 73.5 else '🔴 超出已知範圍'}
  ⑤ ★★ 過度吻合判準: 吻合 {min(abs(d) for d in devs.values()):.4f}% vs 輸入精度 ~1e−2
     ⟹ {'🟡 同量級 ⟹ 前因子【唔算】過度吻合 (與指數不同)' if min(abs(d) for d in devs.values()) > 0.05 else '🔴 過度吻合'}
  ⑥ ★ 幾何平均: 相容性論證成立 (IDCM 係對數空間框架), 但【非推導】
""")

with open(OUT/"67_mass_scale_dimension.json", "w") as f:
    json.dump({
        "prefactor": f_pref, "prefactor_frac": "1891/2025",
        "ekchain_meV": EKCHAIN_meV,
        "required_sqrt_MP_H0_meV": req_sq,
        "computed_sqrt": sq, "deviations_pct": devs,
        "required_H0_kms": req_H_kms,
        "over_agreement": {"match_pct": min(abs(d) for d in devs.values()),
                           "input_precision": 1e-2},
        "geometric_mean_note": "相容性論證: IDCM 係對數空間框架 ⟹ 幾何平均為自然平均; 但非推導",
        "closure_threshold": 0.05,
    }, f, ensure_ascii=False, indent=2)
print(f"✅ 寫入 data/67_mass_scale_dimension.json")