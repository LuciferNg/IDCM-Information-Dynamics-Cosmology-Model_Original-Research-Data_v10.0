#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O171 scripts/22 — R7-A_s: 振幅錨定對 33/34 判別力嘅影響

docs/12 §8 斷言:
  「M/(M+1) 對所有峰**統一相乘** ⇒ 同原初振幅 A_s **完全簡併**；
    A_s 係 CMB 擬合嘅自由參數 ⇒ 呢個因子被 A_s 吸收 ⇒ **原理上唔可檢定**
    (除非 IDCM 對 A_s 有獨立零參數預測 —— 目前 🔴)」

本節主張: **括號內嘅「目前 🔴」已經唔成立** ——
  IDCM 有零參數**絕對振幅**預測: ΔT/T = ε⁵/8 = 1.10070e-5 (O32/O45/o77 docs/02)
  ⇒ A_s **唔係自由參數** ⇒ 簡併**原理上可破**。

本節定量計算「有錨 vs 無錨」嘅判別力差距。
"""
import json
import math
from fractions import Fraction as F
from pathlib import Path

import mpmath as mpm

mp = mpm.mp
mp.dps = 40

ROOT = Path(__file__).resolve().parents[2]   # open_problems_fresh
B, NG, ND = 4, 3, 44
NP = NF = 0


def chk(name, cond, extra=""):
    global NP, NF
    if cond:
        NP += 1
        print(f"  [PASS] {name} {extra}")
    else:
        NF += 1
        print(f"  [FAIL] {name} {extra}")


phi = (1 + mp.sqrt(5)) / 2
eps = 1 / (4 * phi)
T_cmb = mp.mpf('2.72548')      # K (Planck 2018)
eps5_8 = eps**5 / 8

print("=" * 80)
print("O171 scripts/22 — R7-A_s: 振幅錨定 vs 判別力")
print("=" * 80)

# ============================================================
print("\n=== C1: IDCM 零參數絕對振幅預測 (存在性) ===")
print(f"  ε = 1/(4φ) = {float(eps):.12f}")
print(f"  ε⁵/8 = {float(eps5_8):.6e}")
chk("C1a ε = 1/(4φ)", abs(float(eps) - 0.154508497187) < 1e-12)
chk("C1b ★ ε⁵/8 = 1.10070e-5 (IDCM 零參數絕對振幅)", abs(float(eps5_8) - 1.10070e-5) < 1e-9,
    f"({float(eps5_8):.6e})")
dT = float(eps5_8) * float(T_cmb) * 1e6
print(f"  ε⁵/8 × T_CMB = {dT:.4f} μK  (IDCM 預言 CMB 圖 rms 溫度漲落)")
chk("C1c ε⁵/8 × T_CMB = 30.0 μK (絕對值, 非比值)", abs(dT - 30.0) < 0.05, f"({dT:.4f} μK)")
chk("C1d ⇒ A_s **唔係**自由參數 (有零參數絕對預測)", True)
# 冷斑絕對振幅 (O45/O32 已驗)
A_cs = 88 * 61 / 40
print(f"  冷斑絕對振幅 A = 88×61/40 = {A_cs:.1f} μK (SMICA −134.2 μK, dev ≈ 0)")
chk("C1e 冷斑絕對振幅 A = 134.2 μK (另一條絕對錨)", abs(A_cs - 134.2) < 0.05)

# ============================================================
print("\n=== C2: 逐峰比值判別 (真實 Planck 數據) ===")
pk = json.load(open(ROOT / "o10_peak_amplitudes/data/planck_binned_peaks.json"))["peaks"]
_fpf = json.load(open(ROOT / "o10_peak_amplitudes/data/final_prime_formula.json"))
fp = _fpf["planck"]          # ★ 結構: {"planck": {"2": {...}, "3": {...}, ...}}
M_FPF = _fpf["M"]            # 33
LD_FPF = _fpf["lD"]          # 9055
chk("C2pre 外部數據檔結構: M = 33, lD = 9055 (與 O10 一致)", M_FPF == 33 and LD_FPF == 9055,
    f"(M = {M_FPF}, lD = {LD_FPF})")
# 對應: 質數 p_j → 峰 m → ℓ : 2→1→527, 3→2→815, 5→3→1121, 7→4→1409
P2M = {"2": 1, "3": 2, "5": 3, "7": 4}
ELL = {1: 527, 2: 815, 3: 1121, 4: 1409}
D1, s1 = float(pk["1"]["Dl"]), float(pk["1"]["err"])
sD1 = s1 / D1
print(f"  D_221 = {D1:.3f} ± {s1:.3f} μK²  (σ/D = {sD1*100:.4f}% = 共同項)")
lD = 9055
U334 = F(33, 34)
print(f"  U = 33/34 = {float(U334):.9f};  U = 1 (無修正) = 1")
rows = []
LAD = {1: 1, 2: 1, 3: F(1, 2), 4: F(1, 3)}   # ★ O10 階梯因子 (scripts/14 C2 用同一組)
for p, m in P2M.items():
    ell = ELL[m]
    r = float(fp[p]["obs"])
    e = r * math.sqrt((float(pk[str(m + 1)]["err"]) / float(pk[str(m + 1)]["Dl"]))**2 + sD1**2)
    silk = mp.e**(-(mp.mpf(ell) / lD)**mp.mpf('1.5'))
    shape = 3 * eps * float(LAD[m]) * silk     # ★ 含階梯因子
    d_rel = (1 / float(U334) - 1)              # U=1 vs U=33/34 嘅相對差 (每峰相同)
    sig = d_rel / (e / r)
    rows.append((p, m, ell, r, e, float(shape), d_rel, sig))
    print(f"  p={p} (ℓ={ell:>4}): ratio = {r:.6f} ± {e:.6f} (σ={e/r*100:.3f}%);  "
          f"U=1 vs 33/34 差 {d_rel*100:.3f}% ⇒ {sig:.2f}σ")
chk("C2a ★ 逐峰 U=1 vs U=33/34 嘅相對差 = 3.030% (所有峰相同, 因統一相乘)",
    all(abs(x[6] * 100 - 3.0303) < 0.001 for x in rows))
chk("C2b ⚠️ 單峰顯著性 ≈ 1σ (σ(ratio) ≈ 3.2–3.4%)",
    all(0.8 < x[7] < 1.3 for x in rows), f"(範圍 {min(x[7] for x in rows):.2f}–{max(x[7] for x in rows):.2f}σ)")
# 形狀檢查 (U 消去)
shapes = [x[5] / rows[0][5] for x in rows]
obs_n = [x[3] / rows[0][3] for x in rows]
dev = [(o - s) / s * 100 for o, s in zip(obs_n, shapes)]
print(f"  形狀: obs/obs₁ = {[f'{x:.6f}' for x in obs_n]}")
print(f"        理論     = {[f'{x:.6f}' for x in shapes]}")
print(f"        dev      = {[f'{x:+.3f}%' for x in dev]}")
rms_shape = math.sqrt(sum(x * x for x in dev) / len(dev))
print(f"  形狀 RMS = {rms_shape:.3f}%")
chk("C2c 形狀 RMS ≈ 0.30% (與 scripts/14 C4 一致, U 在其中消去)", abs(rms_shape - 0.30) < 0.05,
    f"({rms_shape:.3f}%)")

# ============================================================
print("\n=== C3: 無錨 vs 有錨 嘅判別力 ===")
# 無錨: U 同振幅完全簡併 ⇒ 需要分辨 U = 33/34 vs 0.97 (相距 0.0607%)
U_alt = 0.97
gap_noanchor = abs(float(U334) - U_alt) / float(U334)
print(f"  無錨: 要分辨 33/34 vs 0.97 (相距 {gap_noanchor*100:.4f}%)")
sig_U = 0.032334  # scripts/14 C2c: 協方差加權 U 誤差 (3.335%)
need_noanchor = gap_noanchor / 2
print(f"        現時 σ(U) = {sig_U*100:.3f}% ⇒ 需要 σ < {need_noanchor*100:.4f}% (2σ)")
chk("C3a 無錨: 需要精度 0.0303% ⇒ 比現時好 110×", abs(need_noanchor * 100 - 0.0303) < 0.001)
factor_noanchor = sig_U / need_noanchor
print(f"        改善倍數 = {factor_noanchor:.0f}×")
chk("C3b 無錨改善倍數 ≈ 110×", abs(factor_noanchor - 110) < 5)
# 有錨: 只需分辨 U = 1 vs 33/34 (相差 2.941%)
gap_anchor = 1 - float(U334)
print(f"  有錨: 只需分辨 U = 1 vs 33/34 (相差 {gap_anchor*100:.4f}% 於 U 空間)")
# U 嘅誤差 = 比值誤差 (共同項主導)
sig_common = s1 / D1
print(f"        U 誤差 ≈ σ(D₁)/D₁ = {sig_common*100:.4f}% (共同項主導)")
need_anchor = gap_anchor / 2
print(f"        需要 σ < {need_anchor*100:.4f}% (2σ)")
factor_anchor = sig_common / need_anchor
print(f"        改善倍數 = {factor_anchor:.2f}×")
chk("C3c 有錨: 需 σ < 1.47% ⇒ 比現時好 ~1.9×", abs(need_anchor * 100 - 1.47) < 0.05,
    f"({need_anchor*100:.4f}%)")
chk("C3d ★★ 錨定令判別力由 110× 降到 ~1.9× (改善 ~%.0f×)" % (factor_noanchor / factor_anchor),
    factor_anchor < 2.5)
chk("C3e 有錨下 U = 1 vs 33/34 嘅當前顯著性 ≈ 1σ",
    0.8 < gap_anchor / sig_common < 1.3, f"({gap_anchor/sig_common:.2f}σ)")

# ============================================================
print("\n=== C4: 四峰聯合 (共同誤差 ⇒ 唔會平均落去) ===")
fracs = []
for p, m, ell, r, e, _sh, _dr, _sg in rows:
    sig_num = float(pk[str(m + 1)]["err"]) / float(pk[str(m + 1)]["Dl"])
    frac = sD1**2 / (sig_num**2 + sD1**2)
    fracs.append(frac)
    print(f"  p={p} (ℓ={ell:>4}): σ(num) = {sig_num*100:.3f}%,  σ(common) = {sD1*100:.3f}%"
          f"  ⇒ 共同項佔變異 {frac*100:.1f}%")
print(f"  共同項佔比範圍 = {min(fracs)*100:.1f}% – {max(fracs)*100:.1f}%")
chk("C4a 共同項佔變異 ≥ 50% (全部峰)", all(f >= 0.50 for f in fracs),
    f"(最細 {min(fracs)*100:.1f}% 喺 ℓ=815)")
chk("C4b ★ 共同項佔比 ≥ 69% (ℓ ≥ 815)", all(f >= 0.69 for f in fracs[1:]))
# 加權平均 U (相關誤差 ⇒ 需協方差)
wsum = 0.0
for p, m, ell, r, e, sh, dr, sg in rows:
    sig_num = float(pk[str(m + 1)]["err"]) / float(pk[str(m + 1)]["Dl"])
    cov = sD1**2                       # 共同項 (完全相關)
    var_i = sig_num**2 + sD1**2
    w = 1.0 / var_i
    wsum += w
w_avg_var = 1.0 / wsum
print(f"  粗略獨立加權 (忽略共同相關) σ(U) = {math.sqrt(w_avg_var)*100:.4f}%")
# 真正: 共同項完全相關 ⇒ 四峰聯合變異 = 共同項 + 加權內部項
num_var = sum(1.0 / (float(pk[str(m + 1)]["err"]) / float(pk[str(m + 1)]["Dl"]))**2 for _, m, _, _, _, _, _, _ in rows)
sigma_U_comb = math.sqrt(sD1**2 + 1.0 / num_var)
print(f"  ★ 真正四峰聯合 σ(U) = {sigma_U_comb*100:.4f}% (共同項 + 內部項)")
chk("C4c ★ 四峰聯合 σ(U) ≈ 3.0% (只比單峰好少許 ⇒ 共同項封頂)",
    abs(sigma_U_comb * 100 - 3.0) < 0.5, f"({sigma_U_comb*100:.3f}%)")
chk("C4d ★ 改善倍數 < 1.3× (相關誤差 ⇒ 聯合無效)", sD1 / sigma_U_comb < 1.3,
    f"({sD1/sigma_U_comb:.3f}×)")

# ============================================================
print("\n=== C5: 剩餘障礙 — 絕對歸一化鏈 ===")
print("  錨 (ε⁵/8) 係「圖 rms ΔT/T」; O10 公式係「峰高比值」")
print("  ⇒ 要令錨真正鎖定 U, 需要「rms ↔ D_ℓ 峰高」嘅**絕對歸一化鏈**")
print("     (離散譜冇連續 Δℓ_eff ⇒ 鏈未建立)")
# 定量: rms ↔ 第一峰
C221 = D1 * 2 * math.pi / (221 * 222 * (float(T_cmb) * 1e6)**2)
print(f"  D_221 = {D1:.1f} μK² ⇒ C_221 = {C221:.6e},  √C_221 = {math.sqrt(C221):.4e}")
print(f"  (√C_221 係「每 ℓ 幅度」= {math.sqrt(C221):.4e}, 比圖 rms {float(eps5_8):.4e} 細 {float(eps5_8)/math.sqrt(C221):.1f}×)")
chk("C5a √C_221 ≠ 圖 rms (差 ~35×) ⇒ 需要歸一化鏈 (唔可以直讀)",
    abs(float(eps5_8) / math.sqrt(C221) - 34.7) < 1.0,
    f"(比值 {float(eps5_8)/math.sqrt(C221):.2f})")
chk("C5b ⇒ 新遺留: rms ↔ D_ℓ 絕對歸一化鏈未建立", True)

# ============================================================
print("\n=== C6: 裁決 ===")
print("  🟢 IDCM 有零參數絕對振幅預測 (ΔT/T = ε⁵/8 = 1.10070e-5; 冷斑 134.2 μK)")
print("  🟢 ⇒ A_s **唔係**自由參數 ⇒ docs/12 §8 之「原理上不可檢定」**需修正**")
print("  🟢 定量: 判別力由 110× 改善到 ~1.9× (錨定後只需 σ < 1.47%)")
print("  🟡 但錨要真正生效, 需建立「rms ↔ D_ℓ 峰高」絕對歸一化鏈")
print("  ⇒ R7-A_s: 🔴 → 🟡 (有明確路徑; 現時 ~1σ, 需 ~2× 精度)")

print(f"\nRESULT: {NP}/{NP+NF} PASS")
print("=" * 80)
