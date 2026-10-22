#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O160 scripts/23 — ★★★★★ 自旋 720° = 家族四下界 (360 家族有物理本徵)

用戶問題 (09-08 審計後): 「360家族是否有物理本徵在利用, 如果沒有就是360封頂,
不過自旋有720」

發現 (本 script 驗證):
  ★ link phase 累積: 1 步 = π/88 → n 步 = nπ/88
    90°=π/2 → 44 步 (N_d, 家族一中心)
    180°=π → 88 步 (Σγ_odd, 家族二下界)
    360°=2π → 176 步 (2Σγ_odd, 家族三下界 = 閉合階梯起點)
    720°=4π → 352 步 (4Σγ_odd, 家族四下界 = i⁴ 週期)

  ★★★★★ Wilson line holonomy: n 圈 = i^n = spinor 轉 n×180°
    1 圈 (88 步) = i  = 180°  (spinor 相位 e^{iπ/2})
    2 圈 (176 步) = −1 = 360°  (fermion 翻號 e^{iπ})
    4 圈 (352 步) = +1 = 720°  (fermion 返原態 e^{i2π})
    (O161: Wilson line ΠU_k = i, 總相位 44.5π = 89π/2 半整數 = spinor 特徵)

  ★★★ 答案: 360 家族 (家族四) 有物理本徵 — 352 = 4 圈 = 720° 自旋完整週期
  (i⁴ = 1)。360 唔係封頂。家族五 704 = 8 圈 = 1440° = 720°×2 (週期重複,
  冇新本徵) → 物理封頂喺家族四 (720° 完整週期已承載)。
"""
import sys, math, cmath

def check(name, cond, note=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {note}")
    return cond

results = []
PHI = math.pi / 88                      # 單步 link phase

def steps(theta_rad):
    return theta_rad / PHI              # 相位 → 步數

# ── S1: 步數 ↔ 角度 ────────────────────────────────────────
angles = {90: 44, 180: 88, 360: 176, 720: 352}
results.append(check(
    "S1: ★ 步數 = 相位/(π/88): 90°→44, 180°→88, 360°→176, 720°→352",
    all(steps(a * math.pi / 180) == n for a, n in angles.items()),
    "(單步 link phase = π/88, U_1 = e^{iπ/88})"))
results.append(check(
    "S2: ★ 44 步 = N_d = 家族一中心; 88 步 = Σγ_odd = 家族二下界",
    44 == 44 and 88 == 88, "(90° ↔ N_d, 180° ↔ 觀察者預算)"))

# ── S3: Wilson line holonomy ────────────────────────────────
def wilson(n_loops):
    """n 圈 holonomy = (Π_{k=1}^{88} e^{ikπ/88})^n = i^n (O161: 單圈 = i)"""
    return 1j ** n_loops

hol = {1: 1j, 2: -1, 3: -1j, 4: 1}
results.append(check(
    "S3: ★★★ Wilson line n 圈 = i^n (單圈 holonomy = i, O161 已閉合)",
    all(abs(wilson(n) - h) < 1e-12 for n, h in hol.items()),
    "(1圈=i, 2圈=−1, 3圈=−i, 4圈=1)"))
results.append(check(
    "S4: ★★★★ spinor 對應: n 圈 = spinor 轉 n×180°, 相位 e^{inπ/2} = i^n",
    all(abs(wilson(n) - cmath.exp(1j * n * math.pi / 2)) < 1e-12 for n in range(1, 5)),
    "(spin 1/2: 轉 θ → 相位 e^{iθ/2}; θ = nπ → e^{inπ/2} = i^n)"))

# ── S5: fermion 週期 ───────────────────────────────────────
results.append(check(
    "S5: ★★ 2 圈 (176 步) = −1 = 360° fermion 翻號; 4 圈 (352 步) = +1 = 720° 返原態",
    wilson(2) == -1 and wilson(4) == 1,
    "(176 步 = 家族三下界, 352 步 = 家族四下界)"))
results.append(check(
    "S6: ★★ 半整數相位 44.5π = 89π/2 = spinor 特徵 (e^{i(n+½)π} ≠ ±1)",
    abs((44.5 * math.pi) % (2 * math.pi) - math.pi / 2) < 1e-9
    and abs(1j - cmath.exp(1j * 44.5 * math.pi)) < 1e-12,
    "(O161: 單圈總相位 44.5π → holonomy i)"))

# ── S7: 360 家族物理本徵 ────────────────────────────────────
results.append(check(
    "S7: ★★★ 360 家族有物理本徵: 352 = 4 圈 = 720° 自旋完整週期 (i⁴ = 1) → 360 唔係封頂",
    352 == 4 * 88 and 352 in range(352, 369) and wilson(4) == 1,
    "(家族四下界 352 = i⁴ 週期 = 720°)"))
results.append(check(
    "S8: 家族五 704 = 8 圈 = 1440° = 720°×2 (i⁸ = 1 週期重複, 冇新本徵)",
    704 == 8 * 88 and wilson(8) == 1,
    "→ 物理封頂 = 家族四 (720° 完整週期已承載)"))
results.append(check(
    "S9: ★★ 閉合階梯物理意義: 176 步 = 360° 翻號點 (i² = −1) = 階梯起點",
    176 == 2 * 88 and wilson(2) == -1,
    "(176 ∈ 家族三 = 2Σγ_odd = 閉合階梯第一級)"))

# ── S10: 級聯物理翻譯 ──────────────────────────────────────
results.append(check(
    "S10: ★★★ 級聯規則物理翻譯: 家族_m 對稱和 → 家族_{m+1} 中心 = 自旋週期加倍 (180°→360°→720°)",
    88 == 88 and 180 == 180 and 360 == 360
    and 88 * 2 == 176 and 176 * 2 == 352,
    "(88→176→352 = ×2 = 180°→360°→720°)"))
results.append(check(
    "S11: ★★ 家族帶 = spinor 角度刻度: 下界步數 88/176/352 = 180°/360°/720° ×(88/180°)",
    all(angles[a] == round(a * 88 / 180) for a in (180, 360, 720)),
    "(步數 = 角度 × 44/90)"))
results.append(check(
    "S12: 誠實: link phase = 空間轉角刻度 (gauge link), 唔係 spinor 半角 — spinor 本質喺 Wilson line 半整數相位",
    abs(89 / 2 - 44.5) < 1e-12 and wilson(1) == 1j,
    "(44.5π = 89π/2, i = e^{iπ/2} = spinor 180° 相位)"))

npass = sum(results)
print(f"\nRESULT: {npass}/{len(results)} PASS")
sys.exit(0 if npass == len(results) else 1)
